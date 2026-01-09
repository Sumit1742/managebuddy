from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

PRIORITY_CHOICES = (
    ('L', 'Low'),
    ('M', 'Medium'),
    ('H', 'High'),
)

class Task(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Completed", "Completed"),
    ]

    # ✅ user is now optional
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField()
    duration = models.IntegerField(help_text="Estimated time in minutes", null=True, blank=True)
    priority = models.CharField(max_length=1, choices=PRIORITY_CHOICES, default='M')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    is_completed = models.BooleanField(default=False)
    reminder_sent = models.BooleanField(default=False)
  
   
    def days_left(self):
        """Return number of days left until due date"""
        delta = (self.deadline.date() - timezone.localdate()).days
        return delta if delta >= 0 else 0

    def __str__(self):
        return f"{self.title} ({self.status})"


class TaskProgress(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="progress")
    date = models.DateField(default=timezone.now)
    is_done = models.BooleanField(default=False)

    class Meta:
        unique_together = ('task', 'date')
    
    def __str__(self):
        return f"{self.task.title} - {self.date} - {'Done' if self.is_done else 'Not Done'}"

from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.user.username
from django.db import models
from django.utils import timezone
from .models import Task  # make sure Task model is imported

class TaskRoadmap(models.Model):
    task = models.OneToOneField(Task, on_delete=models.CASCADE, related_name="roadmap")
    roadmap_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Roadmap for: {self.task.title}"
