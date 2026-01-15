import cv2
import numpy as np
import os

class InterviewAI:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )

    def process_frame(self, image_data):
        nparr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is None:
            return {"error": "Görüntü okunamadı"}

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)

        face_detected = len(faces) > 0
        face_count = len(faces)


        return {
            "face_detected": face_detected,
            "face_count": face_count,
            "eye_contact_score": 100 if face_detected else 0, 
            "emotion": "Neutral" 
        }