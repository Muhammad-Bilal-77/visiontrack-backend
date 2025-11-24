from django.db import models
import numpy as np
import base64
from PIL import Image
from django.utils import timezone

class Employee(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='employee_images/')
    face_encoding = models.TextField(blank=True)  # Store encoding as base64 string

    def save(self, *args, **kwargs):
        # Import inside save to avoid errors during migrations
        import face_recognition

        if self.image and not self.face_encoding:
            # Open image
            img = Image.open(self.image)
            img = np.array(img)

            # Detect face encoding
            encodings = face_recognition.face_encodings(img)
            if encodings:
                # Convert numpy array to base64 string
                self.face_encoding = base64.b64encode(encodings[0].tobytes()).decode('utf-8')
            else:
                self.face_encoding = ''  # No face detected

        super().save(*args, **kwargs)



class Attendance(models.Model):
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.employee.name} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
    
    
    

class SiteSettings(models.Model):
    site_name = models.CharField(max_length=150, default="VisionTrack")
    hero_title = models.CharField(max_length=255)
    hero_subtitle = models.TextField()
    hero_image = models.ImageField(upload_to="hero/")
    cta_primary_text = models.CharField(max_length=100)
    cta_primary_link = models.CharField(max_length=200)
    cta_secondary_text = models.CharField(max_length=100, blank=True, null=True)
    cta_secondary_link = models.CharField(max_length=200, blank=True, null=True)

    accuracy_rate = models.CharField(max_length=20, default="99.9%")
    recognition_time = models.CharField(max_length=20, default="2s")
    uptime = models.CharField(max_length=20, default="24/7")

    footer_text = models.CharField(max_length=255, default="© 2024 VisionTrack. AI-Powered Face Attendance System.")

    def __str__(self):
        return "Global Site Settings"


class Feature(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    icon_name = models.CharField(max_length=100)  # Example: "Scan", "Clock", "BarChart3"

    def __str__(self):
        return self.title


class Step(models.Model):
    step_number = models.IntegerField()
    title = models.CharField(max_length=150)
    description = models.TextField()

    class Meta:
        ordering = ['step_number']

    def __str__(self):
        return f"Step {self.step_number}: {self.title}"