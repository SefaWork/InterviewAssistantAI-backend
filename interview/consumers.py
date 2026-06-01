import base64
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .ai_processor import InterviewAI
from .models import OngoingInterviewSession, CompletedInterviewSession
from django.core.cache import cache
import time

ai_engine = InterviewAI()

SESSION_COMPLETE_TIME = 60.0

def create_feedback_for_score(score_name, score_value):
    if (score_value < 0.5):
        return f"{score_name}:bad;"
    elif (score_value < 0.75):
        return f"{score_name}:average;"
    else:
        return f"{score_name}:good;"

def create_comparison_for_score(score_name, old_value, new_value):
    if (old_value < new_value):
        return f"{score_name}:better;"
    elif (old_value > new_value):
        return f"{score_name}:worse;"
    else:
        return f"{score_name}:same;"

class ImageStreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if not self.scope["user"] or isinstance(self.scope["user"], AnonymousUser):
            await self.close(code=4401)
            print("Unauthorized client detected.")
            return
        
        session_id = self.scope["url_route"]["kwargs"]["session_id"]
        self.session = await self.try_claim_session(session_id)

        if not self.session:
            await self.close(code=4404)
            print("Session not found.")
            return

        self.session_completed = False
        self.session_start = time.monotonic() - self.session.elapsed_time

        await self.accept()
        print("Authorized client connected.")

    @database_sync_to_async
    def try_claim_session(self, session_id):
        try:
            session = self.scope["user"].interview_sessions.get(id=session_id)
        except OngoingInterviewSession.DoesNotExist:
            return None

        lock_key = f"session_lock:{session_id}"
        claimed = cache.add(lock_key, 1, timeout=3600)
        if not claimed:
            return None

        return session

    @database_sync_to_async
    def release_session(self):
        if not self.session or self.session_completed:
            return
        
        self.session.elapsed_time = time.monotonic() - self.session_start
        self.session.save(update_fields=["elapsed_time"])
        
        cache.delete(f"session_lock:{self.session.id}")

    @database_sync_to_async
    def get_latest_completed_session(self):
        if not self.session:
            return None
        
        try:
            return self.scope["user"].completed_interviews.latest()
        except CompletedInterviewSession.DoesNotExist:
            return None

    async def disconnect(self, close_code):
        await self.release_session()
        print(f"Client disconnected: {close_code}")

    async def receive(self, text_data=None, bytes_data=None):
        if self.session_completed:
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
            completed_session_id = await self.complete_session(await self.get_latest_completed_session())
            if completed_session_id is None:
                await self.send(text_data=json.dumps({"type": "session_complete"}))
            else:
                await self.send(text_data=json.dumps({"type": "session_complete", "id": str(completed_session_id)}))

            await self.close()
            return None
    
        return {**result, "emotion_avg": newAvgs[0], "eye_avg": newAvgs[1]}

    @database_sync_to_async
    def complete_session(self, latest_session):
        if (self.session_completed):
            return None
        self.session_completed = True

        # Create completed interview.
        emotion_score = round(self.session.emotion_score_total / self.session.frame_count, 1)
        eye_score = round(self.session.eye_score_total / self.session.frame_count, 1)
        total_score = round((emotion_score + eye_score) / 2, 1)

        feedback = create_feedback_for_score("emotion", emotion_score) + create_feedback_for_score("eye", eye_score)
        past_analysis_feedback = ""

        if latest_session:
            past_analysis_feedback = create_comparison_for_score("emotion", latest_session.emotion_score, emotion_score) + create_comparison_for_score("eye", latest_session.eye_score, eye_score)
        
        completed_session = CompletedInterviewSession.objects.create(user=self.scope["user"], emotion_score=emotion_score, eye_score=eye_score, total_score=total_score, feedback=feedback, past_analysis_feedback=past_analysis_feedback)
        self.session.delete()
        return completed_session.id

    @database_sync_to_async
    def add_result(self, result):
        if "error" not in result:
            # There was no error, update session scores.
            self.session.frame_count+=1
            self.session.emotion_score_total+=ai_engine.emotion_scores.get(result["emotion"], 0)
            self.session.eye_score_total+=100 # TODO
            self.session.save(update_fields=["frame_count", "emotion_score_total", "eye_score_total"])

            if time.monotonic() - self.session_start > SESSION_COMPLETE_TIME:
                return None
            
        return [round(self.session.emotion_score_total / self.session.frame_count, 1), round(self.session.eye_score_total / self.session.frame_count, 1)]

