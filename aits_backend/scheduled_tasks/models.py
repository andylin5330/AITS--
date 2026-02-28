from django.db import models
from projects.models import Project

class ScheduledTask(models.Model):
    TASK_TYPES = (
        ('api_suite', 'API套件'),
        ('web_suite', 'Web套件')
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='scheduled_tasks')
    name = models.CharField(max_length=100)
    task_type = models.CharField(max_length=50, choices=TASK_TYPES)
    target_id = models.IntegerField(help_text="对应套件的ID")
    cron_expression = models.CharField(max_length=50, help_text="如: 0 0 * * *")
    is_active = models.BooleanField(default=True)
    celery_task_id = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.project.name} - {self.name}"

class TaskExecutionLog(models.Model):
    STATUS_CHOICES = (
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('error', 'Error')
    )
    scheduled_task = models.ForeignKey(ScheduledTask, on_delete=models.CASCADE, related_name='execution_logs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    output = models.TextField(blank=True, null=True)
    executed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.scheduled_task.name} - {self.status} at {self.executed_at}"
