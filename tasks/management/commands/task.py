"""Task Manager CLI: list, create, update, delete, complete/incomplete tasks."""
import textwrap
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from tasks.models import Task
from datetime import datetime

MAX_TITLE_WIDTH = 40


class Command(BaseCommand):
    """CLI command for managing tasks."""
    help = "Task Manager CLI"

    def add_arguments(self, parser):
        """Define CLI commands and their arguments."""
        subparsers = parser.add_subparsers(dest="command")

        # LIST
        list_parser = subparsers.add_parser("list")
        list_parser.add_argument("--status", choices=["true", "false"], help="Filter by completion status")
        list_parser.add_argument("--priority", choices=["low", "medium", "high"], help="Filter by priority")

        # CREATE
        create = subparsers.add_parser("create")
        create.add_argument("--title", required=True)
        create.add_argument("--description", default="")
        create.add_argument("--priority", default="Medium")
        create.add_argument("--due", required=False)

        # UPDATE
        update = subparsers.add_parser("update")
        update.add_argument("id", type=int)
        update.add_argument("--title")
        update.add_argument("--description")
        update.add_argument("--priority")
        update.add_argument("--status", choices=["true", "false"])
        update.add_argument("--due")

        # DELETE
        delete = subparsers.add_parser("delete")
        delete.add_argument("id", type=int)

        # COMPLETE
        complete = subparsers.add_parser("complete")
        complete.add_argument("id", type=int)

        # INCOMPLETE
        incomplete = subparsers.add_parser("incomplete")
        incomplete.add_argument("id", type=int)

    def wrap_text(self, text):
        """Wrap long text for display."""
        return textwrap.wrap(text, width=MAX_TITLE_WIDTH) or [""]

    def parse_due_date(self, due):
        """Parse string to timezone-aware datetime."""
        if not due:
            return None
        try:
            return timezone.make_aware(
                datetime.strptime(due, "%Y-%m-%d %H:%M"),
                timezone.get_current_timezone()
            )
        except:
            self.stdout.write("Invalid date format! Use: YYYY-MM-DD HH:MM")
            return "ERR"

    def list_tasks_paginated(self, options):
        """List tasks with optional filtering and pagination."""
        tasks = Task.objects.all().order_by("-created_at")
        # Filters
        if options.get("status"):
            status = options["status"] == "true"
            tasks = tasks.filter(status=status)
        if options.get("priority"):
            tasks = tasks.filter(priority=options["priority"])
        tasks = list(tasks)
        if not tasks:
            self.stdout.write("No tasks found.")
            return
        batch_size = settings.BATCH_SIZE if hasattr(settings, "BATCH_SIZE") else 50
        index = 0
        while index < len(tasks):
            batch = tasks[index:index + batch_size]
            id_width = 4
            title_width = description_width = MAX_TITLE_WIDTH
            priority_width = completed_width = due_width = 10
            # Display Header
            header = (
                f"{'ID':<{id_width}} "
                f"{'Title':<{title_width}} "
                f"{'Description':<{description_width}} "
                f"{'Priority':<{priority_width}} "
                f"{'Completed':<{completed_width}} "
                f"{'Due Date':<{due_width}}"
            )
            self.stdout.write("")
            self.stdout.write(header)
            self.stdout.write("_" * (len(header) + 10))
            # Display Rows
            for task in batch:
                due = task.due_date.strftime("%Y-%m-%d %H:%M") if task.due_date else "None"
                wrapped_titles = self.wrap_text(task.title)
                wrapped_description = self.wrap_text(task.description)
                max_lines = max(len(wrapped_titles), len(wrapped_description))
                for line in range(max_lines):
                    # Pick line, else blank
                    title_line = wrapped_titles[line] if line < len(wrapped_titles) else ""
                    description_line = wrapped_description[line] if line < len(wrapped_description) else ""
                    if line == 0:
                        # For first line, print full row
                        self.stdout.write(
                            f"{str(task.id):<{id_width}} "
                            f"{title_line:<{title_width}} "
                            f"{description_line:<{description_width}} "
                            f"{task.priority:<{priority_width}} "
                            f"{str(task.status):<{completed_width}} "
                            f"{due:<{due_width}}"
                        )
                    else:
                        # For continuation lines, print empty other columns
                        self.stdout.write(
                            f"{'':<{id_width}} "
                            f"{title_line:<{title_width}} "
                            f"{description_line:<{description_width}} "
                            f"{'':<{priority_width}} "
                            f"{'':<{completed_width}} "
                            f"{'':<{due_width}}"
                        )
                self.stdout.write("_" * (len(header) + 10))
            # Break if entire data is printed else give user input prompt
            index += batch_size
            if index >= len(tasks):
                break
            self.stdout.write("\n--- Press ENTER for more | q to quit ---")
            user_input = input()
            if user_input.lower() == "q":
                break
        self.stdout.write("")

    def create_task(self, options):
        """Create a new task."""
        due = self.parse_due_date(options["due"])
        if due == "ERR":
            return
        task = Task.objects.create(
            title=options["title"],
            description=options["description"],
            priority=options["priority"],
            due_date=due
        )
        self.stdout.write(f"Created task {task.id} -- {task.title}")

    def update_task(self, options):
        """Update an existing task while respecting validations."""
        try:
            task = Task.objects.get(id=options["id"])
        except Task.DoesNotExist:
            return self.stdout.write("Task not found.")
        updated = False
        if options["due"]:
            due = self.parse_due_date(options["due"])
            if due == "ERR":
                return
            task.due_date = due
            updated = True
        if options["status"]:
            status = options["status"] == "true"
            if status and not (options["due"] or task.due_date):
                return self.stdout.write(
                    "Update failed: Completed tasks should have a due date."
                )
            task.status = status
            updated = True
        for field in ["title", "description", "priority"]:
            if options.get(field):
                if field == "priority" and task.status:
                    self.stdout.write("Cannot change priority of a completed task.")
                    continue
                setattr(task, field, options[field])
                updated = True
        if updated:
            task.save()
            self.stdout.write(f"Task {task.id} -- {task.title} updated.")
        else:
            self.stdout.write("No changes applied to the task.")

    def delete_task(self, options):
        """Delete a task by ID."""
        count, _ = Task.objects.filter(id=options["id"]).delete()
        if count == 0:
            return self.stdout.write("Task not found.")
        self.stdout.write(f"Task deleted. Task ID: {options['id']}")

    def set_completion_status(self, task_id, status: bool):
        """Mark a task as complete or incomplete."""
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            self.stdout.write("Task not found.")
            return
        if status and not task.due_date:
            self.stdout.write("Update failed: Completed tasks should have a due date.")
            return
        task.status = status
        task.save()
        state = "complete" if status else "incomplete"
        self.stdout.write(f"Task {task.id} -- {task.title} marked {state}.")

    def handle(self, *args, **options):
        """Dispatch CLI commands."""
        command = options["command"]
        if command == "list":
            return self.list_tasks_paginated(options)
        if command == "create":
            return self.create_task(options)
        if command == "update":
            return self.update_task(options)
        if command == "delete":
            return self.delete_task(options)
        if command == "complete":
            return self.set_completion_status(options["id"], True)
        if command == "incomplete":
            return self.set_completion_status(options["id"], False)
