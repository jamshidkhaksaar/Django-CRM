import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.urls import reverse
from .models import Notification

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        
        if not self.user.is_authenticated:
            await self.close()
            return

        self.room_name = f"user_{self.user.id}_notifications"
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_name'):
            await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            if data.get('type') == 'mark_read':
                success = await self.mark_notification_read(data.get('notification_id'))
                await self.send(text_data=json.dumps({
                    'type': 'notification_marked_read',
                    'success': success,
                    'notification_id': data.get('notification_id')
                }))
        except json.JSONDecodeError:
            pass

    async def notification(self, event):
        """Handle new notification event"""
        notification = event.get('notification', {})
        
        # Add any additional data needed for the frontend
        if notification.get('record_id'):
            notification['record_url'] = reverse('website:record_detail', 
                                              args=[notification['record_id']])

        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': notification
        }))

    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        """Mark a notification as read"""
        try:
            notification = Notification.objects.get(
                id=notification_id, 
                user=self.user,
                is_read=False
            )
            notification.is_read = True
            notification.save(update_fields=['is_read'])
            return True
        except Notification.DoesNotExist:
            return False

    @database_sync_to_async
    def get_notification_count(self):
        """Get unread notification count for the user"""
        return Notification.objects.filter(
            user=self.user,
            is_read=False
        ).count()
 