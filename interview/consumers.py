import base64
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .ai_processor import InterviewAI
from .models import OngoingInterviewSession, CompletedInterviewSession
from django.core.cache import cache
from .emotion_weights import EMOTION_SCORE_WEIGHTS, EMOTION_LIST
from asgiref.sync import sync_to_async
import time

ai_engine = InterviewAI()

SESSION_MAX_TIME = 60.0 * 15.0 # 15 minutes.

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
        
        self.session = await self.try_claim_session()

        if not self.session:
            await self.close(code=4404)
            print("Session not found.")
            return

        self.session_completed = False
        self.marked_complete = False
        self.session_start = time.monotonic() - self.session.elapsed_time

        await self.accept()
        await self.send(text_data=json.dumps({"type": "time", "elapsed_time": time.monotonic() - self.session_start}))
        print("Authorized client connected.")

    @database_sync_to_async
    def try_claim_session(self):
        try:
            session = self.scope["user"].ongoing_session
        except OngoingInterviewSession.DoesNotExist:
            return None

        lock_key = f"session_lock:{self.scope["user"].id}"
        claimed = cache.add(lock_key, 1, timeout=SESSION_MAX_TIME)
        if not claimed:
            return None

        return session

    @database_sync_to_async
    def release_session(self):
        if self.session and not self.session_completed:
            self.session.elapsed_time = time.monotonic() - self.session_start
            self.session.save(update_fields=["elapsed_time"])
        cache.delete(f"session_lock:{self.scope["user"].id}")

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

            if message["type"] == "finish" and time.monotonic() - self.session_start > 60:
                self.marked_complete = True

            elif message["type"] == "ping":
                await self.send(text_data=json.dumps({"type": "pong"}))

async def process_image(self, image_bytes: bytes) -> dict:
        
        result = await sync_to_async(ai_engine.process_frame)(image_bytes)
        
        newAvgs = await self.add_result(result)

        if self.marked_complete or time.monotonic() - self.session_start > SESSION_MAX_TIME:
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

        frame_count = max(self.session.frame_count, 1)

        # -- Total scores, feedback and durations. -- #
        emotion_score = round(self.session.emotion_score_total / frame_count, 1)
        eye_score = round(self.session.eye_score_total / frame_count, 1)
        total_score = round((emotion_score + eye_score) / 2, 1)

        duration = time.monotonic() - self.session_start

        feedback = create_feedback_for_score("emotion", emotion_score) + create_feedback_for_score("eye", eye_score)
        past_analysis_feedback = ""

        if latest_session:
            past_analysis_feedback = create_comparison_for_score("emotion", latest_session.emotion_score, emotion_score) + create_comparison_for_score("eye", latest_session.eye_score, eye_score)
        # ------------------------------------------- #

        # -- Individual emotion distributions. -- #
        distributions = {}
        total_accounted = 0
        for emotion_name in EMOTION_LIST:
            emotion_frames = getattr(self.session, emotion_name)
            total_accounted += emotion_frames
            distributions[emotion_name] = emotion_frames / frame_count
        distributions["unknown"] = (frame_count - total_accounted) / frame_count
        # ---------------------------------------- #

        completed_session = CompletedInterviewSession.objects.create(**distributions, user=self.scope["user"], emotion_score=emotion_score, eye_score=eye_score, total_score=total_score, feedback=feedback, past_analysis_feedback=past_analysis_feedback, duration=duration)
        self.session.delete()
        return completed_session.id

    @database_sync_to_async
    def add_result(self, result):
        if "error" not in result:
            # There was no error, update session scores.
            self.session.frame_count+=1
            self.session.emotion_score_total+=EMOTION_SCORE_WEIGHTS[result["emotion"]]
            self.session.eye_score_total+=result["eye_contact_score"]

            if result["emotion"] == "unknown":
                self.session.save(update_fields=["frame_count", "emotion_score_total", "eye_score_total"])
            else:
                setattr(self.session, result["emotion"], getattr(self.session, result["emotion"]) + 1)
                self.session.save(update_fields=["frame_count", "emotion_score_total", "eye_score_total", result["emotion"]])
            
        return [round(self.session.emotion_score_total / self.session.frame_count, 1), round(self.session.eye_score_total / self.session.frame_count, 1)]

