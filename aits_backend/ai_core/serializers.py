from rest_framework import serializers
from .models import LLMConfiguration, RAGConfiguration, MCPConfiguration, LLMUsageLog

class LLMConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LLMConfiguration
        fields = '__all__'

class RAGConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RAGConfiguration
        fields = '__all__'

class MCPConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = MCPConfiguration
        fields = '__all__'

class LLMUsageLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = LLMUsageLog
        fields = '__all__'
