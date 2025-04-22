from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ADMIN = 'admin'
    JOB_SEEKER = 'job_seeker'
    RECRUITER = 'recruiter'

    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (JOB_SEEKER, 'Job Seeker'),
        (RECRUITER, 'Recruiter'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=JOB_SEEKER)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    preferences = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"
