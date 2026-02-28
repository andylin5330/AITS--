from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Project, ProjectMember, Environment, UploadedFile
from .serializers import (
    ProjectSerializer, ProjectMemberSerializer, 
    EnvironmentSerializer, UploadedFileSerializer
)

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().order_by('-created_at')
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class ProjectMemberViewSet(viewsets.ModelViewSet):
    queryset = ProjectMember.objects.all()
    serializer_class = ProjectMemberSerializer
    permission_classes = [IsAuthenticated]

class EnvironmentViewSet(viewsets.ModelViewSet):
    queryset = Environment.objects.all()
    serializer_class = EnvironmentSerializer
    permission_classes = [IsAuthenticated]

class UploadedFileViewSet(viewsets.ModelViewSet):
    queryset = UploadedFile.objects.all()
    serializer_class = UploadedFileSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)
