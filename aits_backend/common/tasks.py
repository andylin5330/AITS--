import time
import json
from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@shared_task
def test_websocket_log_task(task_id, iterations=5):
    """
    A dummy task that sends simulated log messages to a WebSocket channel group.
    """
    channel_layer = get_channel_layer()
    group_name = f'log_{task_id}'
    
    # Notify start
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'log_message',
            'message': f'[Celery] 🚀 Task Execution Started for {task_id}.'
        }
    )
    
    for i in range(1, iterations + 1):
        time.sleep(2) # pretend doing some work...
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'log_message',
                'message': f'[Celery] Working on iteration {i}/{iterations}...'
            }
        )
    
    # Notify end
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'log_message',
            'message': f'[Celery] ✅ Task Execution Completed for {task_id}.'
        }
    )
    
    return f"Completed {iterations} iterations for {task_id}."
