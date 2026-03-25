import cv2
import numpy as np
import tensorflow as tf

print("🧠 Yapay Zeka Beyni Yükleniyor... Lütfen Bekleyin...")
# Eğittiğimiz nihai modeli yüklüyoruz
model = tf.keras.models.load_model('mulakat_ai_beyni.h5')

# TensorFlow klasörleri alfabetik sıraya göre okur.
# master_veriseti içindeki klasörlerin alfabetik sırası budur:
duygular = {
    0: 'Kizgin (Anger)', 
    1: 'Igrenme (Disgust)', 
    2: 'Korku (Fear)', 
    3: 'Mutlu (Happy)', 
    4: 'Notr (Neutral)', 
    5: 'Uzgun (Sadness)', 
    6: 'Saskin (Surprise)'
}

# OpenCV'nin hazır yüz tanıma kaskadını (algoritmasını) yüklüyoruz
yuz_algilayici = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Web kamerasını başlat (0 genelde dahili kameradır, harici ise 1 yapabilirsin)
kamera = cv2.VideoCapture(0)

print("📷 Kamera açıldı! Çıkmak için klavyeden 'q' tuşuna bas.")

while True:
    ret, frame = kamera.read()
    if not ret:
        break

    # Yüzü daha kolay bulmak için kareyi siyah-beyaza çeviriyoruz
    gri_kare = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Karedeki yüzleri tespit et
    yuzler = yuz_algilayici.detectMultiScale(gri_kare, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30))

    for (x, y, w, h) in yuzler:
        # Yüzün olduğu bölgeyi (ROI) kes
        yuz_bolgesi = frame[y:y+h, x:x+w]
        
        # Modelimiz RGB (Renkli) eğitildiği için OpenCV'nin BGR formatını RGB'ye çeviriyoruz
        yuz_rgb = cv2.cvtColor(yuz_bolgesi, cv2.COLOR_BGR2RGB)
        
        # Modelin beklediği 96x96 boyutuna getir
        yuz_yeniden_boyut = cv2.resize(yuz_rgb, (96, 96))
        
        # TensorFlow'un beklediği Dizi formatına çevir (1, 96, 96, 3)
        yuz_dizisi = np.expand_dims(yuz_yeniden_boyut, axis=0)

        # YAPAY ZEKA TAHMİN YAPIYOR!
        tahminler = model.predict(yuz_dizisi, verbose=0)
        en_yuksek_ihtimal_indeksi = np.argmax(tahminler[0])
        algilanan_duygu = duygular[en_yuksek_ihtimal_indeksi]
        guven_skoru = tahminler[0][en_yuksek_ihtimal_indeksi] * 100

        # Ekrana yüzün etrafında bir kutu çiz ve duyguyu yaz
        renk = (0, 255, 0) if en_yuksek_ihtimal_indeksi in [3, 4] else (0, 0, 255) # Mutlu/Nötr ise yeşil, değilse kırmızı kutu
        cv2.rectangle(frame, (x, y), (x+w, y+h), renk, 2)
        cv2.putText(frame, f"{algilanan_duygu} (%{guven_skoru:.1f})", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, renk, 2)

    # Görüntüyü ekranda göster
    cv2.imshow('Mülakat Asistanı - Canlı Duygu Testi', frame)

    # 'q' tuşuna basılırsa döngüyü kır ve çık
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Her şeyi kapat ve temizle
kamera.release()
cv2.destroyAllWindows()