import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


dataset_folder = 'fer2013'
train_folder = os.path.join(dataset_folder, 'train')

print("🔍 Klasör yapısı inceleniyor, resimler sayılıyor...")


if not os.path.exists(train_folder):
    dataset_folder = 'fer2013.csv'
    train_folder = os.path.join(dataset_folder, 'train')

if not os.path.exists(train_folder):
    print(f"❌ HATA: '{train_folder}' yolu bulunamadı!")
    print("Lütfen dosyaya sağ tıklayıp 'Tümünü Ayıkla' dediğinden emin ol.")
else:
  
    emotion_counts = {}
    for emotion in os.listdir(train_folder):
        emotion_path = os.path.join(train_folder, emotion)
        if os.path.isdir(emotion_path):
            
            emotion_counts[emotion] = len(os.listdir(emotion_path))
    
    
    df_counts = pd.Series(emotion_counts).sort_values(ascending=False)
    
    print("\n📊 EĞİTİM (TRAIN) VERİ SETİ ÖZETİ:")
    print("-" * 30)
    print(f"Toplam Görüntü Sayısı: {df_counts.sum()}")
    print("\nDuygu Dağılımları:")
    print(df_counts)
    
   
    plt.figure(figsize=(10, 6))
    sns.barplot(x=df_counts.index, y=df_counts.values, hue=df_counts.index, palette="viridis", legend=False)
    
    plt.title('FER-2013 Eğitim (Train) Verisi Duygu Dağılımı', fontsize=14, fontweight='bold')
    plt.xlabel('Duygular', fontsize=12)
    plt.ylabel('Görüntü Sayısı', fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
   
    plt.savefig('dataset_distribution.png', dpi=300)
    print("\n✅ BAŞARILI: 'dataset_distribution.png' adında grafik kaydedildi!")
    
   
    plt.show()