import base64
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .ai_processor import InterviewAI

ai_engine = InterviewAI()

class ImageStreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        print("Client connected")

    async def disconnect(self, close_code):
        print(f"Client disconnected: {close_code}")

    async def receive(self, text_data=None, bytes_data=None):
        # Handle binary image data directly
        if bytes_data:
            result = await self.process_image(bytes_data)
            await self.send(text_data=json.dumps({
                "type": "result",
                "data": result
            }))

        # Handle JSON messages (e.g. base64 image or control signals)
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
        # Your image processing logic here
        # e.g. run ML model, extract metadata, etc.
        return ai_engine.process_frame(image_bytes)