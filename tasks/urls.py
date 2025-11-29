"""
URLs for tasks package.
"""
from django.urls import path
from tasks.views import (
    TaskListCreateView,
    TaskDetailView,
    MarkCompleteView,
    MarkIncompleteView
)


urlpatterns = [
    path('tasks/', TaskListCreateView.as_view()),
    path('tasks/<int:pk>/', TaskDetailView.as_view()),
    path('tasks/<int:pk>/complete/', MarkCompleteView.as_view()),
    path('tasks/<int:pk>/incomplete/', MarkIncompleteView.as_view()),
]
