"""Models for tasks package."""
from django.db import models


class Priority(models.TextChoices):
    """Priority levels for tasks."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Task(models.Model):
    """Task model with title, description, status, priority, timestamps, and due date."""
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.BooleanField(default=False)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title
