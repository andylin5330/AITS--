from django.db import models
from django.conf import settings

class LLMConfiguration(models.Model):
    PROVIDER_CHOICES = (
        ('openai', 'OpenAI'),
        ('deepseek', 'DeepSeek'),
        ('ollama', 'Ollama'),
        ('qwen', 'Qwen'),
        ('custom', 'Custom')
    )
    name = models.CharField(max_length=50, unique=True, verbose_name="配置名称")
    provider = models.CharField(max_length=50, choices=PROVIDER_CHOICES)
    api_key = models.CharField(max_length=255, blank=True, null=True)
    api_base = models.CharField(max_length=255, blank=True, null=True)
    is_vision_model = models.BooleanField(default=False, help_text="是否为视觉大模型")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.provider})"

class RAGConfiguration(models.Model):
    DB_TYPES = (
        ('chromadb', 'ChromaDB'),
        ('milvus', 'Milvus')
    )
    name = models.CharField(max_length=50, unique=True)
    db_type = models.CharField(max_length=20, choices=DB_TYPES)
    connection_kwargs = models.JSONField(default=dict, help_text="数据库连接参数配置")

    def __str__(self):
        return self.name

class MCPConfiguration(models.Model):
    name = models.CharField(max_length=50, unique=True)
    server_url = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class LLMUsageLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    configuration = models.ForeignKey(LLMConfiguration, on_delete=models.SET_NULL, null=True)
    tokens_prompt = models.IntegerField(default=0)
    tokens_completion = models.IntegerField(default=0)
    total_tokens = models.IntegerField(default=0)
    cost = models.DecimalField(max_digits=10, decimal_places=6, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        username = self.user.username if self.user else "System"
        return f"{username} used {self.total_tokens} tokens"
