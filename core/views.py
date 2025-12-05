from django.shortcuts import render, redirect
from .forms import EmployeeForm

from django.http import JsonResponse
from .models import Employee, Attendance
from attendenceapp.models import AttendanceSettings, AttendanceLog
import cv2
import numpy as np
import base64
import face_recognition
from datetime import date, time, datetime
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone


from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from .models import SiteSettings, Feature, Step, Employee, Attendance
from .serializers import (
    SiteSettingsSerializer, 
    FeatureSerializer, 
    StepSerializer,
    EmployeeSerializer,
    EmployeeCreateSerializer,
    EmployeeStatusSerializer
)
from attendenceapp.permissions import IsAdminOrSuperUser
from rest_framework.permissions import AllowAny
from django.core.files.uploadedfile import InMemoryUploadedFile

def upload_employee(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('upload_success')
    else:
        form = EmployeeForm()
    return render(request, 'core/upload.html', {'form': form})

def upload_success(request):
    return render(request, 'core/upload_success.html')




def mark_attendance(request):
    """
    Accepts POST with 'image' (dataURL). Returns JSON:
    {status: 'success'|'error', message: '...'}
    """
    if request.method == 'POST':
        try:
            img_data = request.POST.get('image')
            if not img_data:
                return JsonResponse({'status': 'error', 'message': 'No image provided'}, status=400)

            # dataURL is like "data:image/jpeg;base64,/9j/4AAQ..."
            if ',' in img_data:
                img_bytes = base64.b64decode(img_data.split(',')[1])
            else:
                img_bytes = base64.b64decode(img_data)

            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                return JsonResponse({'status': 'error', 'message': 'Unable to decode image'}, status=400)

            # Convert to RGB for face_recognition
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # Get face encodings from the image
            unknown_encodings = face_recognition.face_encodings(rgb_img)

            if len(unknown_encodings) == 0:
                return JsonResponse({'status': 'error', 'message': 'No face detected'})

            unknown_encoding = unknown_encodings[0]

            # Load all active employees with encodings and find best match by euclidean distance
            employees = Employee.objects.exclude(face_encoding='').select_related('user').filter(user__is_active=True)
            best_match = None
            best_distance = 1.0

            for emp in employees:
                try:
                    emp_encoding = np.frombuffer(base64.b64decode(emp.face_encoding), dtype=np.float64)
                except Exception:
                    # skip malformed encodings
                    continue

                # Skip inactive users; continue searching for another matching, active employee
                if not emp.user.is_active:
                    continue

                # face_distance returns array, get single value
                distance = face_recognition.face_distance([emp_encoding], unknown_encoding)[0]

                if distance < best_distance:
                    best_distance = distance
                    best_match = emp

            # Strict threshold — tune between ~0.45-0.6 depending on your dataset
            THRESHOLD = 0.48

            if best_match and best_distance < THRESHOLD:
                # Check shift time
                settings = AttendanceSettings.get_solo()
                current_datetime = timezone.now()
                current_time = timezone.localtime(current_datetime).time()
                today = current_datetime.date()
                
                # Check if current time is before shift start
                if current_time < settings.start_time:
                    return JsonResponse({
                        'status': 'error', 
                        'message': f'Too early! Shift starts at {settings.start_time.strftime("%I:%M %p")}'
                    })
                
                # Check if current time is after shift end
                if current_time > settings.end_time:
                    return JsonResponse({
                        'status': 'error', 
                        'message': f'You are late! Shift ended at {settings.end_time.strftime("%I:%M %p")}'
                    })
                
                # Within shift hours - check if already marked today
                already_log = AttendanceLog.objects.filter(
                    employee=best_match.user,
                    checkin_time__date=today
                ).first()

                if not already_log:
                    # Create AttendanceLog entry (automatically determines late/present status)
                    attendance_log = AttendanceLog.create_checkin(best_match.user, current_datetime)
                    
                    # Also create legacy Attendance record for backward compatibility
                    Attendance.objects.create(
                        employee=best_match, 
                        timestamp=current_datetime,
                        attendance_log=attendance_log
                    )
                    
                    status_msg = 'late' if attendance_log.status == AttendanceLog.STATUS_LATE else 'on time'
                    return JsonResponse({
                        'status': 'success', 
                        'message': f'Attendance marked for {best_match.name} ({status_msg})'
                    })
                else:
                    return JsonResponse({
                        'status': 'success', 
                        'message': f'{best_match.name} already marked today'
                    })

            # No suitable match found
            return JsonResponse({'status': 'error', 'message': 'Face not recognized'})

        except Exception as e:
            # Return error message (useful for debugging)
            return JsonResponse({'status': 'error', 'message': 'Server error: ' + str(e)}, status=500)

    # GET -> render page
    return render(request, 'core/attendance.html')



@api_view(['GET'])
def landing_page_data(request):
    settings = SiteSettings.objects.first()
    features = Feature.objects.all()
    steps = Step.objects.all()

    data = {
        "settings": SiteSettingsSerializer(settings).data,
        "features": FeatureSerializer(features, many=True).data,
        "steps": StepSerializer(steps, many=True).data
    }
    return Response(data)


class EmployeePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class EmployeeListCreateView(APIView):
    permission_classes = [IsAdminOrSuperUser]
    parser_classes = [MultiPartParser, FormParser]
    pagination_class = EmployeePagination

    def get(self, request):
        """List and search employees"""
        search_query = request.query_params.get('search', '').strip()
        
        employees = Employee.objects.select_related('user').all()
        
        if search_query:
            employees = employees.filter(
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(user__username__icontains=search_query) |
                Q(user__email__icontains=search_query)
            )
        
        # Paginate results
        paginator = self.pagination_class()
        paginated_employees = paginator.paginate_queryset(employees, request)
        
        serializer = EmployeeSerializer(paginated_employees, many=True, context={'request': request})
        
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        """Create new employee"""
        serializer = EmployeeCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                employee = serializer.save()
                employee_data = EmployeeSerializer(employee, context={'request': request}).data
                
                return Response({
                    'success': True,
                    'data': employee_data,
                    'message': 'Employee created'
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    'success': False,
                    'message': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'success': False,
            'message': 'Validation failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class EmployeeDetailView(APIView):
    permission_classes = [IsAdminOrSuperUser]

    def get_object(self, pk):
        try:
            return Employee.objects.select_related('user').get(user__id=pk)
        except Employee.DoesNotExist:
            return None

    def get(self, request, pk):
        """Get single employee"""
        employee = self.get_object(pk)
        if not employee:
            return Response({
                'success': False,
                'message': 'Employee not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = EmployeeSerializer(employee, context={'request': request})
        return Response(serializer.data)

    def patch(self, request, pk):
        """Toggle employee status"""
        employee = self.get_object(pk)
        if not employee:
            return Response({
                'success': False,
                'message': 'Employee not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = EmployeeStatusSerializer(employee, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            
            return Response({
                'success': True,
                'data': {
                    'id': str(employee.user.id),
                    'status': 'Active' if employee.user.is_active else 'Inactive',
                    'updated_at': employee.user.date_joined.isoformat()
                }
            })
        
        return Response({
            'success': False,
            'message': 'Validation failed',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """Delete employee"""
        employee = self.get_object(pk)
        if not employee:
            return Response({
                'success': False,
                'message': 'Employee not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        employee.user.delete()  # Cascade deletes employee record
        
        return Response({
            'success': True,
            'message': 'Employee deleted'
        })


class EmployeeFaceUploadView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        """Upload an image for a given employee email and store face encoding.
        Expected form fields: email (employee email), image (file)
        Returns: { success, message, data: { userId, name, email, hasEncoding } }
        """
        email = request.data.get('email')
        image_file = request.data.get('image')

        if not email or not image_file:
            return Response({
                'success': False,
                'message': 'Fields "email" and "image" are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Find user with employee role by email
        from user.models import User
        email_str = str(email).strip()
        user_obj = User.objects.filter(email__iexact=email_str, role='employee').first()
        
        if not user_obj:
            return Response({
                'success': False,
                'message': 'Employee user not found with this email.'
            }, status=status.HTTP_404_NOT_FOUND)

        # Get or create Employee record for this user
        employee, created = Employee.objects.get_or_create(user=user_obj)
       
        # Read image into numpy
        try:
            img_bytes = image_file.read()
            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                return Response({'success': False, 'message': 'Unable to decode image'}, status=status.HTTP_400_BAD_REQUEST)
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        except Exception as e:
            return Response({'success': False, 'message': f'Image processing error: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)

        # Compute face encoding
        encodings = face_recognition.face_encodings(rgb_img)
        if not encodings:
            return Response({'success': False, 'message': 'Recapture your image. No face detected in the image.'}, status=status.HTTP_400_BAD_REQUEST)

        encoding = encodings[0]
        employee.face_encoding = base64.b64encode(encoding.tobytes()).decode('utf-8')
        employee.image = image_file
        employee.save()

        return Response({
            'success': True,
            'message': 'Face encoding stored successfully.',
            'data': {
                'userId': str(employee.user.id),
                'name': employee.name,
                'email': employee.user.email,
                'hasEncoding': bool(employee.face_encoding),
            }
        }, status=status.HTTP_200_OK)


class EmployeeCheckView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """Check if employee exists by email.
        Expected form fields: email (employee email)
        Returns: { success, exists, data: { userId, name, email, hasEncoding } or null }
        """
        email = request.data.get('email')

        if not email:
            return Response({
                'success': False,
                'message': 'Field "email" is required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Find user with employee role by email
        from user.models import User
        email_str = str(email).strip()
        user_obj = User.objects.filter(email__iexact=email_str, role='employee').first()
        
        if not user_obj:
            return Response({
                'success': True,
                'exists': False,
                'data': None,
                'message': 'User not found.'
            }, status=status.HTTP_200_OK)
        # Check if Employee record exists
        employee = Employee.objects.filter(user=user_obj).first()
        
        if not employee:
            return Response({
                'success': True,
                'exists': False,
                'data': None,
                'message': 'Employee record not found.'
            }, status=status.HTTP_200_OK)

        return Response({
            'success': True,
            'exists': True,
            'data': {
                'userId': str(employee.user.id),
                'name': employee.name,
                'email': employee.user.email,
                'hasEncoding': bool(employee.face_encoding),
            },
            'message': 'Employee found.'
        }, status=status.HTTP_200_OK)


class UserRoleCheckView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Check authenticated user's role.
        Uses JWT token from Authorization header.
        Returns: { success, data: { userId, email, role } }
        """
        user = request.user
        
        return Response({
            'success': True,
            'data': {
                'userId': str(user.id),
                'email': user.email,
                'role': user.role,
            },
            'message': f'User is {user.role}.'
        }, status=status.HTTP_200_OK)


class EmployeeAttendanceHistoryView(APIView):
    permission_classes = [AllowAny]
    pagination_class = EmployeePagination

    def post(self, request):
        """Get attendance history for an employee by email.
        Request body: { "email": "employee@example.com" }
        Returns paginated attendance records with employee info, or verification message if not found.
        """
        email = request.data.get('email', '').strip() if isinstance(request.data, dict) else ''

        if not email:
            return Response({
                'success': False,
                'message': 'Field "email" is required in request body.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Find employee by email
        from user.models import User
        user_obj = User.objects.filter(email__iexact=email, role='employee').first()
        
        if not user_obj:
            return Response({
                'success': False,
                'verified': False,
                'message': 'You are not verified. Please do face verification first for logs.'
            }, status=status.HTTP_200_OK)

        # Check if employee record exists
        employee = Employee.objects.filter(user=user_obj).first()
        
        if not employee:
            return Response({
                'success': False,
                'verified': False,
                'message': 'You are not verified. Please do face verification first for logs.'
            }, status=status.HTTP_200_OK)

        # Get attendance records (legacy Attendance model)
        attendance_records = Attendance.objects.filter(
            employee=employee
        ).order_by('-timestamp')

        # Paginate results
        paginator = self.pagination_class()
        paginated_records = paginator.paginate_queryset(attendance_records, request)

        # Serialize data
        data = []
        for record in paginated_records:
            data.append({
                'id': record.id,
                'employeeId': str(employee.user.id),
                'employeeName': employee.name,
                'employeeEmail': employee.user.email,
                'timestamp': record.timestamp.isoformat(),
                'date': record.timestamp.date().isoformat(),
                'time': record.timestamp.time().isoformat(),
                'status': record.attendance_log.status if record.attendance_log else 'unknown',
            })

        return paginator.get_paginated_response({
            'success': True,
            'verified': True,
            'data': data,
            'message': f'Found {len(data)} attendance records.'
        })


class FaceRecognitionAttendanceView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """Mark attendance using face recognition.
        Request body: { "image": "data:image/jpeg;base64,..." }
        Returns: { status: 'success'|'error', message: '...', data: {...} }
        """
        try:
            img_data = request.data.get('image')
            if not img_data:
                return Response({
                    'status': 'error',
                    'message': 'No image provided'
                }, status=status.HTTP_400_BAD_REQUEST)

            # dataURL is like "data:image/jpeg;base64,/9j/4AAQ..."
            if ',' in img_data:
                img_bytes = base64.b64decode(img_data.split(',')[1])
            else:
                img_bytes = base64.b64decode(img_data)

            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                return Response({
                    'status': 'error',
                    'message': 'Unable to decode image'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Convert to RGB for face_recognition
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            # Get face encodings from the image
            unknown_encodings = face_recognition.face_encodings(rgb_img)

            if len(unknown_encodings) == 0:
                return Response({
                    'status': 'error',
                    'message': 'No face detected'
                }, status=status.HTTP_200_OK)

            unknown_encoding = unknown_encodings[0]

            # Load only active employees with encodings and find best match by euclidean distance
            employees = Employee.objects.exclude(face_encoding='').select_related('user').filter(user__is_active=True)
            best_match = None
            best_distance = 1.0

            for emp in employees:
                try:
                    emp_encoding = np.frombuffer(base64.b64decode(emp.face_encoding), dtype=np.float64)
                except Exception:
                    # skip malformed encodings
                    continue

                # Defensive: ensure user is active (permission-based status)
                if not emp.user.is_active:
                    continue

                # face_distance returns array, get single value
                distance = face_recognition.face_distance([emp_encoding], unknown_encoding)[0]

                if distance < best_distance:
                    best_distance = distance
                    best_match = emp

            # Strict threshold — tune between ~0.45-0.6 depending on your dataset
            THRESHOLD = 0.48

            if best_match and best_distance < THRESHOLD:
                settings = AttendanceSettings.get_solo()
                current_datetime = timezone.now()
                local_datetime = timezone.localtime(current_datetime)
                today = local_datetime.date()

                # Build aware datetimes for start/end comparisons
                start_dt = timezone.make_aware(datetime.combine(today, settings.start_time), timezone.get_current_timezone())
                end_dt = timezone.make_aware(datetime.combine(today, settings.end_time), timezone.get_current_timezone())

                # Enforce one attendance per day (by employee + date)
                existing_log = AttendanceLog.objects.filter(
                    employee=best_match.user,
                    checkin_time__date=today
                ).order_by('-checkin_time').first()
                if existing_log:
                    return Response({
                        'status': 'error',
                        'message': f'{best_match.name} already marked today',
                        'data': {
                            'employeeId': str(best_match.user.id),
                            'employeeName': best_match.name,
                            'employeeEmail': best_match.user.email,
                            'alreadyMarked': True,
                            'markedAt': existing_log.checkin_time.isoformat(),
                            'status': existing_log.status
                        }
                    }, status=status.HTTP_200_OK)

                # Guard rails: do not mark before start or after end
                if local_datetime < start_dt:
                    return Response({
                        'status': 'error',
                        'message': f'Too early! Shift starts at {settings.start_time.strftime("%I:%M %p")}'
                    }, status=status.HTTP_200_OK)

                if local_datetime > end_dt:
                    return Response({
                        'status': 'error',
                        'message': f'You are late! Shift ended at {settings.end_time.strftime("%I:%M %p")}'
                    }, status=status.HTTP_200_OK)

                # Create AttendanceLog entry (buffer-based late/present handled inside create_checkin)
                attendance_log = AttendanceLog.create_checkin(best_match.user, current_datetime)

                # Also create legacy Attendance record for backward compatibility
                Attendance.objects.create(
                    employee=best_match,
                    timestamp=current_datetime,
                    attendance_log=attendance_log
                )

                status_msg = 'late' if attendance_log.status == AttendanceLog.STATUS_LATE else 'on time'
                return Response({
                    'status': 'success',
                    'message': f'Attendance marked for {best_match.name} ({status_msg})',
                    'data': {
                        'employeeId': str(best_match.user.id),
                        'employeeName': best_match.name,
                        'employeeEmail': best_match.user.email,
                        'status': status_msg,
                        'timestamp': current_datetime.isoformat()
                    }
                }, status=status.HTTP_200_OK)

            # No suitable match found
            return Response({
                'status': 'error',
                'message': 'No user found with this face'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            # Return error message (useful for debugging)
            return Response({
                'status': 'error',
                'message': f'Server error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)