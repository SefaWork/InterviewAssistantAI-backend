import cv2
import numpy as np
import os
import tensorflow as tf
from tensorflow.keras.models import load_model
from django.conf import settings

class InterviewAI:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        self.model_path = os.path.join(settings.BASE_DIR, 'mulakat_ai_beyni.h5')
        try:
            self.emotion_model = load_model(self.model_path)
            print("✅ Kendi Eğittiğimiz Yapay Zeka Beyni Başarıyla Yüklendi!")
        except Exception as e:
            self.emotion_model = None
            print(f"⚠️ Uyarı: Yapay zeka modeli yüklenemedi. Hata: {e}")

        self.emotion_labels = {
            0: 'Kızgın', 1: 'İğrenme', 2: 'Korku', 3: 'Mutlu', 
            4: 'Nötr', 5: 'Üzgün', 6: 'Şaşkın'
        }

    def process_frame(self, image_data):
        nparr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is None:
            return {"error": "Görüntü okunamadı"}

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)

        face_detected = len(faces) > 0
        face_count = len(faces)
        emotion = "Yüz Bulunamadı"
        confidence = 0.0

        if face_detected and self.emotion_model:
            (x, y, w, h) = faces[0]
            
            
            margin_x = int(w * 0.2)
            margin_y = int(h * 0.2)
            
            x1 = max(0, x - margin_x)
            y1 = max(0, y - int(margin_y * 1.5))
            x2 = min(frame.shape[1], x + w + margin_x)
            y2 = min(frame.shape[0], y + h + margin_y)
            
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
            "eye_contact_score": 100 if face_detected else 0,
            "emotion": emotion,
            "emotion_confidence": confidence 
        }