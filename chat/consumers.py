import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer #the class we're using
from asgiref.sync import sync_to_async
from . models import Message

class ChatConsumer(AsyncJsonWebsocketConsumer):
    #on connection to websocket channels connetc
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        
        #join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    #on disconnecting from sockets
    async def disconnect(self, close_code):
        #leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    #Recive message from websocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        username = data['username']
        room = data['room']
        
        await self.save_message(username, room, message)
        #send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type':'chat_message',
                'message':message,
                'username':username
            }
        )
    #receive message from room group
    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        
        #send message to WebSocket
        await self.send(text_data = json.dumps({
            'message': message,
            'username': username
        }))
    
    #save messages to databases
    @sync_to_async
    def save_message(self, username, room, message):
        Message.objects.create(username=username,room=room,content=message)   