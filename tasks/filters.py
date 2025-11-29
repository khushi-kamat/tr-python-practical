"""TaskFilter for filtering tasks by status and priority."""
import django_filters
from tasks.models import Task


class TaskFilter(django_filters.FilterSet):
    """Filter tasks by completion status and priority."""
    status = django_filters.BooleanFilter()
    priority = django_filters.CharFilter()

    class Meta:
        model = Task
        fields = ['status', 'priority']
