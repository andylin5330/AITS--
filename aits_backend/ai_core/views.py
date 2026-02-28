from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import LLMConfiguration, RAGConfiguration, MCPConfiguration, LLMUsageLog
from .serializers import (
    LLMConfigurationSerializer, RAGConfigurationSerializer,
    MCPConfigurationSerializer, LLMUsageLogSerializer
)

class LLMConfigurationViewSet(viewsets.ModelViewSet):
    queryset = LLMConfiguration.objects.all()
    serializer_class = LLMConfigurationSerializer
    permission_classes = [IsAuthenticated]

class RAGConfigurationViewSet(viewsets.ModelViewSet):
    queryset = RAGConfiguration.objects.all()
    serializer_class = RAGConfigurationSerializer
    permission_classes = [IsAuthenticated]

class MCPConfigurationViewSet(viewsets.ModelViewSet):
    queryset = MCPConfiguration.objects.all()
    serializer_class = MCPConfigurationSerializer
    permission_classes = [IsAuthenticated]

class LLMUsageLogViewSet(viewsets.ModelViewSet):
    queryset = LLMUsageLog.objects.all()
    serializer_class = LLMUsageLogSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
