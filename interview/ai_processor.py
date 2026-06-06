import cv2
import numpy as np
import os
import base64
import tensorflow as tf
from tensorflow.keras.models import load_model
import mediapipe as mp
from django.conf import settings

class InterviewAI:
    def __init__(self):
        print("🚀 InterviewAI Başlatılıyor... Modeller RAM'e yükleniyor (Singleton).")
        
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        self.model_path = os.path.join(settings.BASE_DIR, 'mulakat_ai_beyni.h5')
        try:
            self.emotion_model = load_model(self.model_path)
            print("ML model loaded.")
        except Exception as e:
            self.emotion_model = None
            print(f"ML model failed to load. Error: {e}")

        self.emotion_labels = {
            0: 'angry', 1: 'disgusted', 2: 'scared', 3: 'happy', 
            4: 'neutral', 5: 'sad', 6: 'shocked'
        }
        
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1, 
            refine_landmarks=True, 
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def _check_eye_contact(self, landmarks, w, h):
        """Mediapipe landmarklarından iris konumunu hesaplar."""
        ic_x = int(landmarks[133].x * w)
        dis_x = int(landmarks[33].x * w)
        iris_x = int(landmarks[468].x * w)
        
        goz_genisligi = dis_x - ic_x
        if goz_genisligi == 0: 
            return False
            
        oran = (iris_x - ic_x) / goz_genisligi
        return 0.40 < oran < 0.60

    def process_frame(self, image_data):
        if isinstance(image_data, str) and ',' in image_data:
            image_data = image_data.split(',')[1]
            img_bytes = base64.b64decode(image_data)
        else:
            img_bytes = image_data 
            
        nparr = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is None:
            return {"error": "Couldn't read input image."}

        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        face_detected = False
        face_count = 0
        eye_contact = False
        emotion = "unknown"
        confidence = 0.0

        mesh_results = self.face_mesh.process(rgb_frame)
        if mesh_results.multi_face_landmarks:
            landmarks = mesh_results.multi_face_landmarks[0].landmark
            eye_contact = self._check_eye_contact(landmarks, w, h)

        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) > 0:
            face_detected = True
            face_count = len(faces)
            
            if self.emotion_model:
                (x, y, w_box, h_box) = faces[0]
                
                margin_x = int(w_box * 0.2)
                margin_y = int(h_box * 0.2)
                
                x1 = max(0, x - margin_x)
                y1 = max(0, y - int(margin_y * 1.5))
                x2 = min(frame.shape[1], x + w_box + margin_x)
                y2 = min(frame.shape[0], y + h_box + margin_y)
                
                face_roi = frame[y1:y2, x1:x2]
                face_rgb = cv2.cvtColor(face_roi, cv2.COLOR_BGR2RGB)
                
                cv2.imwrite("ai_ne_gordu.jpg", cv2.cvtColor(face_rgb, cv2.COLOR_RGB2BGR))
                
                resized_face = cv2.resize(face_rgb, (96, 96))
                img_array = np.array(resized_face, dtype=np.float32)
                img_array = np.expand_dims(img_array, axis=0) 
                
                predictions = self.emotion_model.predict(img_array, verbose=0)
                max_index = np.argmax(predictions[0])
                
                emotion = self.emotion_labels[max_index]
                confidence = round(float(predictions[0][max_index]) * 100, 2)

        return {
            "face_detected": face_detected,
            "face_count": face_count,
            "eye_contact_score": 100 if eye_contact else 0, 
            "emotion": emotion,
            "emotion_confidence": confidence 
        }
