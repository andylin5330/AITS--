from django.db import models
from django.contrib.auth import get_user_model
from projects.models import Project

User = get_user_model()

class WebUITestCase(models.Model):
    PRIORITY_CHOICES = (
        ('高', '高'),
        ('中', '中'),
        ('低', '低'),
    )
    TEST_TYPE_CHOICES = (
        ('功能测试', '功能测试'),
        ('异常测试', '异常测试'),
        ('边界测试', '边界测试'),
        ('安全测试', '安全测试'),
        ('性能测试', '性能测试'),
    )

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='web_test_cases')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    steps = models.JSONField(default=list, help_text="包含 action, target, value 结构的操作步骤")
    is_ai_generated = models.BooleanField(default=False)
    
    # Newly added fields for the specific UI filtering and representation
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='中')
    test_type = models.CharField(max_length=20, choices=TEST_TYPE_CHOICES, default='功能测试')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='web_test_cases')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class MidSceneScript(models.Model):
    case = models.OneToOneField(WebUITestCase, on_delete=models.CASCADE, related_name='midscene_script')
    script_content = models.TextField(help_text="MidScene 视觉/自然语言测试脚本")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class WebUITestSuite(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='web_test_suites')
    name = models.CharField(max_length=100)
    cases = models.ManyToManyField(WebUITestCase, related_name='suites')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class WebUITestExecution(models.Model):
    STATUS_CHOICES = (
        ('pending', '等待中'),
        ('running', '执行中'),
        ('passed', '通过'),
        ('failed', '失败'),
        ('error', '错误')
    )
    suite = models.ForeignKey(WebUITestSuite, on_delete=models.CASCADE, related_name='executions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    allure_report_url = models.CharField(max_length=255, blank=True, null=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
