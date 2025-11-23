from django.db import models
import numpy as np
import base64
from PIL import Image

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
