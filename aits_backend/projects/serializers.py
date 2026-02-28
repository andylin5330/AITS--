from rest_framework import serializers
from .models import Project, ProjectMember, Environment, UploadedFile
from users.serializers import UserSerializer

class EnvironmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Environment
        fields = '__all__'

class ProjectMemberSerializer(serializers.ModelSerializer):
    user_detail = UserSerializer(source='user', read_only=True)

    class Meta:
        model = ProjectMember
        fields = ['id', 'project', 'user', 'user_detail', 'role', 'created_at']

class ProjectSerializer(serializers.ModelSerializer):
    created_by_detail = UserSerializer(source='created_by', read_only=True)
    environments = EnvironmentSerializer(many=True, read_only=True)
    members_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'created_by', 'created_by_detail', 'created_at', 'updated_at', 'environments', 'members_count']
        read_only_fields = ['created_by']

    def get_members_count(self, obj):
        return obj.members.count()

class UploadedFileSerializer(serializers.ModelSerializer):
    uploaded_by_detail = UserSerializer(source='uploaded_by', read_only=True)

    class Meta:
        model = UploadedFile
        fields = ['id', 'project', 'file', 'file_name', 'file_hash', 'uploaded_by', 'uploaded_by_detail', 'created_at']
        read_only_fields = ['file_hash', 'uploaded_by', 'file_name']
