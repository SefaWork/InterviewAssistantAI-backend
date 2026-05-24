import base64
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .ai_processor import InterviewAI
from .models import InterviewSession

ai_engine = InterviewAI()

class ImageStreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if not self.scope["user"] or isinstance(self.scope["user"], AnonymousUser):
            await self.close(code=4401)
            print("Unauthorized client detected.")
            return
        
        session_id = self.scope["url_route"]["kwargs"]["session_id"]
        self.session = await self.get_session(session_id)

        if not self.session:
            await self.close(code=4404)
            print("Session not found.")
            return

        await self.accept()
        print("Authorized client connected.")

    @database_sync_to_async
    def get_session(self, session_id):
        try:
            return InterviewSession.objects.get(id=session_id, user=self.scope["user"])
        except InterviewSession.DoesNotExist:
            return None

    async def disconnect(self, close_code):
        print(f"Client disconnected: {close_code}")

    async def receive(self, text_data=None, bytes_data=None):
        # Handle binary image data directly.
        if bytes_data:
            result = await self.process_image(bytes_data)
            await self.send(text_data=json.dumps({
                "type": "result",
                "data": result
            }))
        
        # Handle JSON data.
        elif text_data:
            message = json.loads(text_data)

            if message["type"] == "image":
                image_bytes = base64.b64decode(message["data"])
                result = await self.process_image(image_bytes)
                await self.send(text_data=json.dumps({
                    "type": "result",
                    "data": result
                }))

            elif message["type"] == "ping":
                await self.send(text_data=json.dumps({"type": "pong"}))

    async def process_image(self, image_bytes: bytes) -> dict:
        return ai_engine.process_frame(image_bytes)