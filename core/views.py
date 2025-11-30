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
from .models import SiteSettings, Feature, Step
from .serializers import SiteSettingsSerializer, FeatureSerializer, StepSerializer

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

            # Load all employees and find best match by euclidean distance
            employees = Employee.objects.exclude(face_encoding='').all()
            best_match = None
            best_distance = 1.0

            for emp in employees:
                try:
                    emp_encoding = np.frombuffer(base64.b64decode(emp.face_encoding), dtype=np.float64)
                except Exception:
                    # skip malformed encodings
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