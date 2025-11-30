from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from django.core.files import File
from user.models import User
from core.models import Employee
from attendenceapp.models import AttendanceSettings, AttendanceLog
from datetime import datetime, timedelta, time
import random
import os
from pathlib import Path


class Command(BaseCommand):
    help = 'Generate demo data: 100 users (10 admins, 90 employees), employees, and attendance logs'

    def handle(self, *args, **options):
        self.stdout.write('Starting demo data generation...')

        with transaction.atomic():
            # Step 1: Clear existing data (optional - comment out if you want to keep existing data)
            self.stdout.write('Clearing existing demo data...')
            AttendanceLog.objects.all().delete()
            Employee.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()

            # Step 2: Create AttendanceSettings
            self.stdout.write('Creating attendance settings...')
            settings, _ = AttendanceSettings.objects.get_or_create(
                pk=1,
                defaults={
                    'start_time': time(9, 0),
                    'end_time': time(18, 0),
                    'late_buffer_minutes': 15
                }
            )

            # Step 3: Create 10 Admin Users
            self.stdout.write('Creating 10 admin users...')
            admins = []
            for i in range(1, 11):
                admin = User.objects.create_user(
                    username=f'admin{i}',
                    email=f'admin{i}@visiontrack.com',
                    password='admin123',
                    first_name=f'Admin{i}',
                    last_name=f'User',
                    phone_number=f'+1234567{i:04d}',
                    role=User.ADMIN
                )
                admins.append(admin)
            self.stdout.write(self.style.SUCCESS(f'Created {len(admins)} admin users'))

            # Step 4: Create 90 Employee Users and Employee records
            self.stdout.write('Creating 90 employee users and employee records...')
            employees = []
            first_names = ['John', 'Sarah', 'Michael', 'Emma', 'David', 'Olivia', 'James', 'Sophia', 'Robert', 'Isabella',
                          'William', 'Mia', 'Richard', 'Charlotte', 'Joseph', 'Amelia', 'Thomas', 'Harper', 'Christopher', 'Evelyn',
                          'Daniel', 'Abigail', 'Matthew', 'Emily', 'Anthony', 'Elizabeth', 'Donald', 'Sofia', 'Mark', 'Avery',
                          'Paul', 'Ella', 'Steven', 'Madison', 'Andrew', 'Scarlett', 'Joshua', 'Victoria', 'Kenneth', 'Aria',
                          'Kevin', 'Grace', 'Brian', 'Chloe', 'George', 'Camila', 'Timothy', 'Penelope', 'Ronald', 'Riley']
            
            last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez',
                         'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin',
                         'Lee', 'Perez', 'Thompson', 'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson',
                         'Walker', 'Young', 'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores',
                         'Green', 'Adams', 'Nelson', 'Baker', 'Hall', 'Rivera', 'Campbell', 'Mitchell', 'Carter', 'Roberts']

            # Find the demo image
            demo_image_path = Path(__file__).resolve().parent.parent.parent.parent / 'media' / 'demo_face.jpg'
            if not demo_image_path.exists():
                self.stdout.write(self.style.WARNING(f'Demo image not found at {demo_image_path}. Creating employees without images.'))
                demo_image_path = None

            for i in range(1, 91):
                first_name = random.choice(first_names)
                last_name = random.choice(last_names)
                
                # Create employee user (bypass validation by using create instead of create_user)
                user = User(
                    username=f'employee{i}',
                    email=f'employee{i}@visiontrack.com',
                    first_name=first_name,
                    last_name=last_name,
                    phone_number=f'+1987654{i:04d}',
                    role=User.EMPLOYEE
                )
                user.set_password('employee123')
                user.save(force_insert=True)  # Skip validation
                
                # Create employee record with demo image
                employee = Employee(user=user)
                
                if demo_image_path:
                    with open(demo_image_path, 'rb') as f:
                        employee.image.save(f'employee_{i}.jpg', File(f), save=False)
                
                employee.save()
                employees.append(employee)
            
            self.stdout.write(self.style.SUCCESS(f'Created {len(employees)} employee users and records'))

            # Step 5: Generate Attendance Logs for the past 30 days
            self.stdout.write('Generating attendance logs for the past 30 days...')
            
            today = timezone.now().date()
            attendance_count = 0
            
            for day_offset in range(30):
                current_date = today - timedelta(days=day_offset)
                
                # Skip weekends
                if current_date.weekday() >= 5:
                    continue
                
                # Each day, 70-85% of employees are present/late, rest are absent
                num_present = random.randint(63, 77)  # 70-85% of 90
                present_employees = random.sample(employees, num_present)
                
                for emp in present_employees:
                    # Generate random checkin time
                    # Most arrive between 8:30 and 9:30
                    hour = random.choice([8, 9])
                    minute = random.randint(0, 59)
                    
                    # Create datetime for that day
                    checkin_dt = timezone.make_aware(
                        datetime.combine(current_date, time(hour, minute))
                    )
                    
                    # Determine status based on settings
                    start_dt = timezone.make_aware(
                        datetime.combine(current_date, settings.start_time)
                    )
                    late_threshold = start_dt + timedelta(minutes=settings.late_buffer_minutes)
                    
                    if checkin_dt > late_threshold:
                        status = AttendanceLog.STATUS_LATE
                    else:
                        status = AttendanceLog.STATUS_PRESENT
                    
                    AttendanceLog.objects.create(
                        employee=emp.user,
                        checkin_time=checkin_dt,
                        status=status
                    )
                    attendance_count += 1
            
            self.stdout.write(self.style.SUCCESS(f'Created {attendance_count} attendance log entries'))

            # Summary
            self.stdout.write(self.style.SUCCESS('\n=== Demo Data Generation Complete ==='))
            self.stdout.write(f'Total Users: {User.objects.count()}')
            self.stdout.write(f'  - Admins: {User.objects.filter(role=User.ADMIN).count()}')
            self.stdout.write(f'  - Employees: {User.objects.filter(role=User.EMPLOYEE).count()}')
            self.stdout.write(f'Total Employee Records: {Employee.objects.count()}')
            self.stdout.write(f'Total Attendance Logs: {AttendanceLog.objects.count()}')
            self.stdout.write(f'  - Present: {AttendanceLog.objects.filter(status=AttendanceLog.STATUS_PRESENT).count()}')
            self.stdout.write(f'  - Late: {AttendanceLog.objects.filter(status=AttendanceLog.STATUS_LATE).count()}')
            self.stdout.write('\nLogin credentials:')
            self.stdout.write('  Admin: admin1@visiontrack.com / admin123')
            self.stdout.write('  Employee: employee1@visiontrack.com / employee123')
