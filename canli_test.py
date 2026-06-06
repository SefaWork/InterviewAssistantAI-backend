import cv2
import numpy as np
import mediapipe as mp
import tensorflow as tf
import os

# ==========================================
# 1. AYARLAR VE MODEL YÜKLEME
# ==========================================
# Eğittiğin en iyi modelin adını buraya yaz (Örn: best_model.h5)
MODEL_YOLU = "mulakat_ai_beyni.h5" 

# Eğitimdeki alfabetik sınıf sırası (RAF-DB + CK+ Füzyon)
DUYGULAR = ['İğrenme', 'Kızgın', 'Korku', 'Mutlu', 'Nötr', 'Şaşkın', 'Üzüntü']

print("Model yükleniyor, lütfen bekleyin...")
if os.path.exists(MODEL_YOLU):
    model = tf.keras.models.load_model(MODEL_YOLU)
    print("✅ Model başarıyla yüklendi!")
else:
    print(f"⚠️ UYARI: {MODEL_YOLU} bulunamadı! Lütfen model dosyanızın adını koddaki MODEL_YOLU değişkenine doğru yazın.")
    exit()

# Yüz tespiti için OpenCV'nin standart Haar Cascade'i
yuz_kaskadi = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


# ==========================================
# 2. GÖZ TEMASI (MEDIAPIPE) AYARLARI
# ==========================================
import mediapipe as mp

mp_face_mesh = mp.solutions.face_mesh

face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1, 
    refine_landmarks=True, # İris takibi için kritik
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

def goz_temasi_hesapla(landmarks, w, h):
    sol_ic_kose = landmarks[133]
    sol_dis_kose = landmarks[33]
    sol_iris = landmarks[468] 

    ic_x = int(sol_ic_kose.x * w)
    dis_x = int(sol_dis_kose.x * w)
    iris_x = int(sol_iris.x * w)

    goz_genisligi = dis_x - ic_x
    if goz_genisligi == 0: 
        return False
        
    oran = (iris_x - ic_x) / goz_genisligi

    if 0.40 < oran < 0.60:
        return True
    else:
        return False


# ==========================================
# 3. KAMERA DÖNGÜSÜ VE GERÇEK ZAMANLI ANALİZ
# ==========================================
cap = cv2.VideoCapture(0)

print("🎥 Kamera başlatıldı. Çıkmak için 'q' tuşuna basın.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
        
    # Görüntüyü aynala (daha doğal bir web kamerası hissi için)
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    
    # İşlemler için BGR'den RGB'ye ve Gri Tonlamaya çeviriler
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # --- A. GÖZ TEMASI ANALİZİ ---
    results = face_mesh.process(rgb_frame)
    goz_temasi_var_mi = False
    
    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            goz_temasi_var_mi = goz_temasi_hesapla(face_landmarks.landmark, w, h)

    # --- B. DUYGU TANIMA ANALİZİ ---
    yuzler = yuz_kaskadi.detectMultiScale(gray_frame, scaleFactor=1.3, minNeighbors=5)
    
    for (x, y, w_box, h_box) in yuzler:
        # Sadece yüz bölgesini kes
        yuz_roi = rgb_frame[y:y+h_box, x:x+w_box]
        
        try:
            # Modeli beslemek için 96x96 yeniden boyutlandırma
            yuz_yeniden_boyutlu = cv2.resize(yuz_roi, (96, 96))
            # Model, Input(shape=(96, 96, 3)) ve batch boyutu bekliyor
            girdi_tensörü = np.expand_dims(yuz_yeniden_boyutlu, axis=0)
            
            # Tahmin Yap
            tahminler = model.predict(girdi_tensörü, verbose=0)
            en_yuksek_index = np.argmax(tahminler[0])
            tespit_edilen_duygu = DUYGULAR[en_yuksek_index]
            guven_skoru = tahminler[0][en_yuksek_index] * 100
            
            # --- C. EKRANA ÇİZDİRME İŞLEMLERİ ---
            
            # Yüzün etrafına kutu çiz
            renk = (255, 165, 0) # Turuncu tonu
            cv2.rectangle(frame, (x, y), (x+w_box, y+h_box), renk, 2)
            
            # Duygu durumunu yazdır
            duygu_metni = f"{tespit_edilen_duygu} (%{guven_skoru:.1f})"
            cv2.putText(frame, duygu_metni, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, renk, 2)
            
        except Exception as e:
            pass # Beklenmedik boyutlandırma hatalarını atla

    # --- D. GÖZ TEMASI DURUMUNU EKRANA YAZDIRMA ---
    if goz_temasi_var_mi:
        cv2.putText(frame, "Goz Temasi: ONAYLI", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    else:
        cv2.putText(frame, "Goz Temasi: KOPTU!", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

    # Sonuç ekranını göster
    cv2.imshow("YZ Mulakat Asistani", frame)

    # 'q' ile çıkış yap
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Kaynakları serbest bırak
cap.release()
cv2.destroyAllWindows()