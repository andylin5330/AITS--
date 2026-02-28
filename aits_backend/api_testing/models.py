from django.db import models
from projects.models import Project

class APISpecification(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='api_specs')
    name = models.CharField(max_length=100)
    openapi_version = models.CharField(max_length=20, default='3.0.0')
    content = models.JSONField(help_text="Swagger/OpenAPI JSON/YAML的解析内容")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.project.name} - {self.name}"

class APIEndpoint(models.Model):
    spec = models.ForeignKey(APISpecification, on_delete=models.CASCADE, related_name='endpoints')
    path = models.CharField(max_length=255)
    method = models.CharField(max_length=10) # GET, POST, etc.
    summary = models.CharField(max_length=255, blank=True, null=True)
    parameters = models.JSONField(default=list, blank=True)
    request_body = models.JSONField(default=dict, blank=True)
    responses = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.method} {self.path}"

class APITestCase(models.Model):
    CASE_TYPES = (
        ('endpoint', '单接口'),
        ('scenario', '场景链路')
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='api_test_cases')
    endpoint = models.ForeignKey(APIEndpoint, on_delete=models.SET_NULL, null=True, blank=True, help_text="关联的端点（端点类型用例适用）")
    name = models.CharField(max_length=255)
    case_type = models.CharField(max_length=20, choices=CASE_TYPES)
    request_data = models.JSONField(default=dict, help_text="包含headers, body, params等")
    assertions = models.JSONField(default=list, help_text="断言规则列表")
    is_ai_generated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class APITestSuite(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='api_test_suites')
    name = models.CharField(max_length=100)
    cases = models.ManyToManyField(APITestCase, related_name='suites')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class APITestExecution(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('passed', 'Passed'),
        ('failed', 'Failed'),
        ('error', 'Error')
    )
    suite = models.ForeignKey(APITestSuite, on_delete=models.CASCADE, related_name='executions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    report_data = models.JSONField(default=dict, blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
