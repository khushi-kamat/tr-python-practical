"""TaskSerializer for validating and serializing Task model data."""
from django.utils import timezone
from rest_framework import serializers
from tasks.models import Priority, Task


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for Task model with validations."""
    class Meta:
        model = Task
        fields = '__all__'

    def validate_title(self, value):
        """Title must be non-empty and ≤ 200 characters."""
        if not value or not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        if len(value) > 200:
            raise serializers.ValidationError("Title is too long (max 200 chars).")
        return value

    def validate_priority(self, value):
        """Priority must be one of the allowed values."""
        allowed = [p.value for p in Priority]
        if value not in allowed:
            raise serializers.ValidationError(
                f"Priority must be one of: {', '.join(allowed)}"
            )
        return value

    def validate_due_date(self, value):
        """Past due date cannot be set."""
        if value is None:
            return value
        now = timezone.now()
        if value < now:
            raise serializers.ValidationError("Due date cannot be in the past.")
        return value

    def validate(self, attrs):
        """
        Validate task rules:
        - Completed tasks must have a due date.
        - Priority cannot be changed for completed tasks.
        """
        # If status is completed but no due_date
        if attrs.get("status") is True and not attrs.get("due_date"):
            raise serializers.ValidationError(
                {"due_date": "Completed tasks should have a due date."}
            )
        # Prevent changing priority of completed tasks
        if self.instance and self.instance.status is True:
            if "priority" in attrs and attrs["priority"] != self.instance.priority:
                raise serializers.ValidationError(
                    "Cannot change priority of a completed task."
                )
        return attrs
