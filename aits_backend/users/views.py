from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model

from .serializers import UserSerializer, UserCreateSerializer

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAuthenticated()]
