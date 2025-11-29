
"""
Application configuration for the tasks package.
"""
from django.apps import AppConfig


class TasksConfig(AppConfig):
    """
    Configuration class for the tasks application.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tasks'
