import requests
import random

BASE_URL = "http://127.0.0.1:8000/api/auth"

random_number = random.randint(1000, 9999)
email = f"testuser{random_number}@example.com"
password = "TestPassword123!"

print(f"--- 1. TEST: KAYIT OLMA ({email}) ---")
register_data = {
    "email": email,
    "password": password
}

try:
    response = requests.post(f"{BASE_URL}/register/", data=register_data)
    
    if response.status_code == 201:
        print("✅ BAŞARILI: Kullanıcı oluşturuldu!")
        print("Gelen Cevap:", response.json())
    else:
        print("❌ HATA: Kayıt olunamadı.")
        print("Hata Kodu:", response.status_code)
        print("Detay:", response.text)

    print("\n--- 2. TEST: GİRİŞ YAPMA (Token Alma) ---")
    login_data = {
        "email": email,
        "password": password
    }
    
    login_response = requests.post(f"{BASE_URL}/login/", data=login_data)
    
    if login_response.status_code == 200:
        print("✅ BAŞARILI: Giriş yapıldı ve Anahtar (Token) alındı!")
        tokens = login_response.json()
        print(f"Access Token (İlk 20 karakter): {tokens['access'][:20]}...")
    else:
        print("❌ HATA: Giriş yapılamadı.")
        print("Detay:", login_response.text)

except Exception as e:
    print("❌ SUNUCUYA ULAŞILAMADI!")
    print(f"Hata: {e}")