import time
import json
from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from openai import OpenAI
from .models import LLMConfiguration

@shared_task
def simulate_agent_generation(task_id, prompt):
    channel_layer = get_channel_layer()
    group_name = f'log_{task_id}'

    def send_event(event_type, message, data=None):
        payload = {
            'type': 'log_message',
            'event': event_type, # status, text_chunk, complete
            'message': message
        }
        if data:
            payload['data'] = data
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'log_message',
                'message': json.dumps(payload)
            }
        )

    send_event('status', '接收到用户测试需求分析任务...')
    
    try:
        config = LLMConfiguration.objects.filter(provider='deepseek').first()
        if not config or not config.api_key:
            send_event('status', '错误：未能找到有效的 DeepSeek 配置或 API Key')
            send_event('chunk', '【系统提示】请先在“AI 核心配置 -> 大模型接入”管理页面中配置 DeepSeek 的 API Key（无需配置 Base URL，默认官方）。\n')
            send_event('complete', 'Agent 任务因缺少配置中止', {'generated': False})
            return f"No deepseek config for {task_id}"

        api_key = config.api_key
        api_base = config.api_base or "https://api.deepseek.com/v1"
        
        client = OpenAI(api_key=api_key, base_url=api_base)

        send_event('status', f'正在连接大模型进行解析...')
        
        system_prompt = """你是一个高级自动测试架构师和测试用例编写专家。
用户会提供一些业务测试场景（例如 UI 操作或 API 接口流程）。
你需要为用户生成详细、专业且结构体清晰的自动化测试用例大纲。
请直接输出 Markdown 格式，包含：
1. 涉及的接口或页面概述
2. 前置条件及测试数据准备
3. 核心场景交互步骤
4. 预期校验点 (Assertions)
不要输出多余的寒暄，直接给出专业大纲。"""

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            stream=True
        )

        send_event('status', '用例生成中...')
        
        for chunk in response:
            if chunk.choices and len(chunk.choices) > 0:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    send_event('chunk', delta.content)
        
        send_event('status', '【步骤完成】格式化导出格式对象')
        send_event('complete', 'Agent 任务执行完毕', {'generated': True})

        return f"Real generation for {task_id} complete."
    except Exception as e:
        send_event('status', f'调用大模型时发生异常: {str(e)}')
        send_event('chunk', f'\n\n[调用错误]: {str(e)}')
        send_event('complete', 'Agent 任务异常退出', {'generated': False})
        return f"Error for {task_id}: {str(e)}"
