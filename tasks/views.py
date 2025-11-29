"""Task API views: list, create, retrieve, update, delete, mark complete/incomplete."""
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView
from tasks.filters import TaskFilter
from tasks.models import Task
from tasks.serializers import TaskSerializer


class TaskListCreateView(APIView):
    """List all tasks or create a new task. Supports filtering via TaskFilter."""
    filter_backends = [DjangoFilterBackend]
    filterset_class = TaskFilter

    def get(self, request):
        """Return a list of tasks, optionally filtered."""
        queryset = Task.objects.all().order_by("-created_at")
        filterset = self.filterset_class(request.GET, queryset=queryset)
        queryset = filterset.qs
        serializer = TaskSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Create a new task."""
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskDetailView(APIView):
    """Retrieve, update, or delete a specific task by ID."""
    def get_object(self, pk):
        """Retrieve a task by primary key or raise NotFound."""
        try:
            return Task.objects.get(pk=pk)
        except Task.DoesNotExist as exc:
            raise NotFound("Task not found.") from exc


    def get(self, request, pk):
        """Get a task by ID."""
        task = self.get_object(pk)
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    def patch(self, request, pk):
        """Partially update a task."""
        task = self.get_object(pk)
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        """Delete a task and return deleted data."""
        task = self.get_object(pk)
        deleted_data = TaskSerializer(task).data
        task.delete()
        return Response({
            "message": "Task deleted successfully",
            "deleted_task": deleted_data
        }, status=200)


class MarkCompleteView(APIView):
    """Mark a task as complete if it has a due date."""
    def post(self, request, pk):
        """Set task status to complete if it has a due date."""
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist as exc:
            raise NotFound("Task not found.") from exc
        if not task.due_date:
            return Response("Completed tasks must have a due date.", status=400)
        task.status = True
        task.save()
        return Response(TaskSerializer(task).data)


class MarkIncompleteView(APIView):
    """Mark a task as incomplete."""
    def post(self, request, pk):
        """Set task status to incomplete."""
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist as exc:
            raise NotFound("Task not found.") from exc
        task.status = False
        task.save()
        return Response(TaskSerializer(task).data)
