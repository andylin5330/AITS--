from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import WebUITestCase, MidSceneScript, WebUITestSuite, WebUITestExecution
from .serializers import (
    WebUITestCaseSerializer, MidSceneScriptSerializer,
    WebUITestSuiteSerializer, WebUITestExecutionSerializer
)

class WebUITestCaseViewSet(viewsets.ModelViewSet):
    queryset = WebUITestCase.objects.all().order_by('-id')
    serializer_class = WebUITestCaseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['project', 'priority', 'test_type']
    search_fields = ['name', 'description']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class MidSceneScriptViewSet(viewsets.ModelViewSet):
    queryset = MidSceneScript.objects.all()
    serializer_class = MidSceneScriptSerializer
    permission_classes = [IsAuthenticated]

class WebUITestSuiteViewSet(viewsets.ModelViewSet):
    queryset = WebUITestSuite.objects.all()
    serializer_class = WebUITestSuiteSerializer
    permission_classes = [IsAuthenticated]

class WebUITestExecutionViewSet(viewsets.ModelViewSet):
    queryset = WebUITestExecution.objects.all()
    serializer_class = WebUITestExecutionSerializer
    permission_classes = [IsAuthenticated]
