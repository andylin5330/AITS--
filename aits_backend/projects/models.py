from django.db import models
from django.conf import settings

class Project(models.Model):
    name = models.CharField(max_length=100, verbose_name="项目名称")
    description = models.TextField(blank=True, null=True, verbose_name="项目描述")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_projects')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class ProjectMember(models.Model):
    ROLE_CHOICES = (
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('editor', 'Editor'),
        ('viewer', 'Viewer'),
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='project_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='viewer')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('project', 'user')

class Environment(models.Model):
    ENV_TYPES = (
        ('api', 'API'),
        ('web', 'Web'),
        ('app', 'App'),
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='environments')
    name = models.CharField(max_length=50, verbose_name="环境名称", help_text="如: 测试环境, 生产环境")
    env_type = models.CharField(max_length=10, choices=ENV_TYPES)
    base_url = models.URLField(blank=True, null=True)
    config = models.JSONField(default=dict, blank=True, help_text="额外的环境变量配置")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.project.name} - {self.name} ({self.env_type})"

class UploadedFile(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='files', null=True, blank=True)
    file = models.FileField(upload_to='uploads/%Y/%m/%d/')
    file_name = models.CharField(max_length=255)
    file_hash = models.CharField(max_length=64, db_index=True, help_text="基于文件内容的SHA256哈希，用于去重")
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
