from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import ScheduledTask, TaskExecutionLog
from .serializers import ScheduledTaskSerializer, TaskExecutionLogSerializer

class ScheduledTaskViewSet(viewsets.ModelViewSet):
    queryset = ScheduledTask.objects.all().order_by('-created_at')
    serializer_class = ScheduledTaskSerializer
    permission_classes = [IsAuthenticated]

class TaskExecutionLogViewSet(viewsets.ModelViewSet):
    queryset = TaskExecutionLog.objects.all().order_by('-executed_at')
    serializer_class = TaskExecutionLogSerializer
    permission_classes = [IsAuthenticated]
