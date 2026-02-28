"""
URL configuration for aits_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from users.views import UserViewSet
from projects.views import ProjectViewSet, ProjectMemberViewSet, EnvironmentViewSet, UploadedFileViewSet
from api_testing.views import APISpecificationViewSet, APIEndpointViewSet, APITestCaseViewSet, APITestSuiteViewSet, APITestExecutionViewSet
from web_testing.views import WebUITestCaseViewSet, MidSceneScriptViewSet, WebUITestSuiteViewSet, WebUITestExecutionViewSet
from ai_core.views import LLMConfigurationViewSet, RAGConfigurationViewSet, MCPConfigurationViewSet, LLMUsageLogViewSet
from scheduled_tasks.views import ScheduledTaskViewSet, TaskExecutionLogViewSet

router = DefaultRouter()
# Users
router.register(r'users', UserViewSet)
# Projects
router.register(r'projects', ProjectViewSet)
router.register(r'project-members', ProjectMemberViewSet)
router.register(r'environments', EnvironmentViewSet)
router.register(r'files', UploadedFileViewSet)
# API Testing
router.register(r'api-specifications', APISpecificationViewSet)
router.register(r'api-endpoints', APIEndpointViewSet)
router.register(r'api-cases', APITestCaseViewSet)
router.register(r'api-suites', APITestSuiteViewSet)
router.register(r'api-executions', APITestExecutionViewSet)
# Web Testing
router.register(r'web-cases', WebUITestCaseViewSet)
router.register(r'midscene-scripts', MidSceneScriptViewSet)
router.register(r'web-suites', WebUITestSuiteViewSet)
router.register(r'web-executions', WebUITestExecutionViewSet)
# AI Core
router.register(r'llm-configs', LLMConfigurationViewSet)
router.register(r'rag-configs', RAGConfigurationViewSet)
router.register(r'mcp-configs', MCPConfigurationViewSet)
router.register(r'llm-logs', LLMUsageLogViewSet)
# Scheduled Tasks
router.register(r'scheduled-tasks', ScheduledTaskViewSet)
router.register(r'task-logs', TaskExecutionLogViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(router.urls)),
    path('api/common/', include('common.urls')),
    path('api/ai-core/', include('ai_core.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
