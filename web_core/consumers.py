import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = 'clinic_room'
        self.room_group_name = f'chat_{self.room_name}'

        # Thêm vào nhóm
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Xóa khỏi nhóm khi mất kết nối
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']

        # Gửi tin nhắn đến nhóm
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat.message',
                'message': message
            }
        )

    # Nhận tin nhắn từ nhóm
    async def chat_message(self, event):
        message = event['message']

        # Gửi tin nhắn qua WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
