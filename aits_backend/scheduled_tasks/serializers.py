from rest_framework import serializers
from .models import ScheduledTask, TaskExecutionLog

class ScheduledTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduledTask
        fields = '__all__'

class TaskExecutionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskExecutionLog
        fields = '__all__'
