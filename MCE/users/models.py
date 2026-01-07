from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username


class UploadImage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # 🔹 Original uploaded image (before cleaning)
    image = models.ImageField(upload_to='uploads/')

    # 🔹 Cleaned image (after cleaning)
    cleaned_image = models.ImageField(
        upload_to='cleaned/',
        null=True,
        blank=True
    )

    latitude = models.FloatField()
    longitude = models.FloatField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    # 🔹 Status flags
    is_completed = models.BooleanField(default=False)
    points_awarded = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {'Completed' if self.is_completed else 'Pending'}"
