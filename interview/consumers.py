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

        self._session_completed = False
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
        if self._session_completed:
            return

        # Handle binary image data directly.
        if bytes_data:
            result = await self.process_image(bytes_data)
            if result is not None:
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
                
                if result is not None:
                    await self.send(text_data=json.dumps({
                        "type": "result",
                        "data": result
                    }))

            elif message["type"] == "ping":
                await self.send(text_data=json.dumps({"type": "pong"}))

    async def process_image(self, image_bytes: bytes) -> dict:
        result = ai_engine.process_frame(image_bytes)
        newAvgs = await self.add_result(result)

        if newAvgs is None:
            self._session_completed = True
            await self.send(text_data=json.dumps({"type": "session_complete"}))
            await self.close()
            return None
    
        return {**result, "emotion_avg": newAvgs[0], "eye_avg": newAvgs[1]}

    @database_sync_to_async
    def add_result(self, result):
        if "error" not in result:
            # There was no error, update session scores.
            self.session.frame_count+=1
            self.session.emotion_score_total+=ai_engine.emotion_scores.get(result["emotion"], 0)
            self.session.eye_score_total+=100 # TODO

            # TODO: Change hardcoded frame count. (Low priority)
            if self.session.frame_count > 5 * 5:
                self.session.completed = True
                self.session.save(update_fields=["frame_count", "emotion_score_total", "eye_score_total", "completed"])
                return None
            
            self.session.save(update_fields=["frame_count", "emotion_score_total", "eye_score_total"])
            
        return [round(self.session.emotion_score_total / self.session.frame_count, 1), round(self.session.eye_score_total / self.session.frame_count, 1)]

