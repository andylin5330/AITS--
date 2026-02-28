import json
from channels.generic.websocket import AsyncWebsocketConsumer

class LogConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # We can pass room_name via URL, e.g., /ws/logs/<task_id>/
        self.task_id = self.scope['url_route']['kwargs'].get('task_id', 'general')
        self.room_group_name = f'log_{self.task_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        
        # Send a connection success message to the client
        await self.send(text_data=json.dumps({
            'message': f'Connected to log stream for task: {self.task_id}'
        }))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from room group
    async def log_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
