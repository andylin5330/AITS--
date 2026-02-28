from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .models import APISpecification, APIEndpoint, APITestCase, APITestSuite, APITestExecution
from .serializers import (
    APISpecificationSerializer, APIEndpointSerializer,
    APITestCaseSerializer, APITestSuiteSerializer, APITestExecutionSerializer
)
from .tasks import run_api_test_suite

class APISpecificationViewSet(viewsets.ModelViewSet):
    queryset = APISpecification.objects.all()
    serializer_class = APISpecificationSerializer
    permission_classes = [IsAuthenticated]

class APIEndpointViewSet(viewsets.ModelViewSet):
    queryset = APIEndpoint.objects.all()
    serializer_class = APIEndpointSerializer
    permission_classes = [IsAuthenticated]

class APITestCaseViewSet(viewsets.ModelViewSet):
    queryset = APITestCase.objects.all()
    serializer_class = APITestCaseSerializer
    permission_classes = [IsAuthenticated]

class APITestSuiteViewSet(viewsets.ModelViewSet):
    queryset = APITestSuite.objects.all()
    serializer_class = APITestSuiteSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def execute(self, request, pk=None):
        suite = self.get_object()
        
        # Create execution record
        execution = APITestExecution.objects.create(
            suite=suite,
            status='pending',
            start_time=timezone.now()
        )
        
        # Trigger celery task
        run_api_test_suite.delay(execution.id)
        
        serializer = APITestExecutionSerializer(execution)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class APITestExecutionViewSet(viewsets.ModelViewSet):
    queryset = APITestExecution.objects.all()
    serializer_class = APITestExecutionSerializer
    permission_classes = [IsAuthenticated]
