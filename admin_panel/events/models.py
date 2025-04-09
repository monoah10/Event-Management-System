from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('organizer', 'Event Organizer'),
        ('attendee', 'Attendee'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='attendee')
    groups = models.ManyToManyField(Group, related_name="custom_user_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="custom_user_permissions", blank=True)

class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    date = models.DateTimeField()
    max_attendees = models.IntegerField()
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="organized_events")
    attendees = models.ManyToManyField(User, related_name="joined_events", blank=True)
