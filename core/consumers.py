import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Message, MentorshipSession
from django.db.models import Q


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return
        self.room_name = f'user_{self.user.id}'
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_name'):
            await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        msg_type = data.get('type')

        if msg_type == 'send_message':
            receiver_id = data.get('receiver_id')
            message_text = data.get('message', '').strip()
            if not receiver_id or not message_text:
                return

            has_conn = await self.check_connection(self.user.id, receiver_id)
            if not has_conn:
                await self.send(json.dumps({'type': 'error', 'message': 'No accepted mentorship'}))
                return

            msg = await self.save_message(self.user.id, receiver_id, message_text)
            payload = {
                'type': 'chat_message',
                'message': {
                    'id': msg.id, 'sender_id': self.user.id,
                    'receiver_id': receiver_id, 'message': message_text,
                    'created_at': msg.created_at.isoformat(),
                    'sender_name': self.user.full_display_name,
                    'is_mine': False,
                }
            }

            # Send to receiver
            await self.channel_layer.group_send(f'user_{receiver_id}', payload)
            # Send to self
            payload['message']['is_mine'] = True
            await self.send(json.dumps(payload))

    async def chat_message(self, event):
        await self.send(json.dumps(event))

    @database_sync_to_async
    def check_connection(self, user_id, other_id):
        return MentorshipSession.objects.filter(
            status='accepted'
        ).filter(
            Q(student_id=user_id, mentor_id=other_id) | Q(student_id=other_id, mentor_id=user_id)
        ).exists()

    @database_sync_to_async
    def save_message(self, sender_id, receiver_id, text):
        return Message.objects.create(sender_id=sender_id, receiver_id=receiver_id, message=text)
