import requests


resim_yolu = "test_yuz.jpg" 


url = "http://127.0.0.1:8000/api/interview/analyze/"

print(f"🤖 Yapay zekaya '{resim_yolu}' gönderiliyor...")

try:
    
    with open(resim_yolu, 'rb') as f:
        files = {'image': f}
        response = requests.post(url, files=files)

    
    if response.status_code == 200:
        print("\n✅ API BAŞARIYLA CEVAP VERDİ:")
        print("-" * 30)
        veri = response.json()
        print(f"Yüz Bulundu mu? : {veri.get('face_detected')}")
        print(f"Göz Teması Skoru: {veri.get('eye_contact_score')}")
        print(f"Duygu Tahmini   : {veri.get('emotion')} (% {veri.get('emotion_confidence')})")
        print("-" * 30)
    else:
        print(f"❌ SUNUCU HATASI ({response.status_code}):", response.text)

except FileNotFoundError:
    print(f"❌ Hata: '{resim_yolu}' adında bir fotoğraf bulunamadı!")
    print("Lütfen proje klasörüne bir fotoğraf koyup adını doğru yazdığından emin ol.")