import os
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers, models, applications, optimizers
from tensorflow.keras.preprocessing import image_dataset_from_directory
import datetime


DATA_DIR = 'master_veriseti' 
IMG_SIZE = (96, 96)
BATCH_SIZE = 32
EPOCHS = 30
LR = 0.0001

print("📂 Veri seti yükleniyor...")
train_ds = image_dataset_from_directory(
    DATA_DIR, validation_split=0.2, subset="training", seed=123,
    image_size=IMG_SIZE, batch_size=BATCH_SIZE, label_mode='categorical'
)
val_ds = image_dataset_from_directory(
    DATA_DIR, validation_split=0.2, subset="validation", seed=123,
    image_size=IMG_SIZE, batch_size=BATCH_SIZE, label_mode='categorical'
)


class_names = train_ds.class_names
num_classes = len(class_names)



def get_models():
    models_dict = {}

    
    base_cnn = models.Sequential([
        layers.Input(shape=(96, 96, 3)),
        layers.Rescaling(1./255),
        layers.Conv2D(32, 3, activation='relu'),
        layers.MaxPooling2D(),
        layers.Conv2D(64, 3, activation='relu'),
        layers.MaxPooling2D(),
        layers.Flatten(),
        layers.Dense(128, activation='relu'),
        layers.Dense(num_classes, activation='softmax')
    ])
    models_dict['Basit_CNN'] = base_cnn

    
    base_mobilenet = applications.MobileNetV2(include_top=False, weights='imagenet')
    base_mobilenet.trainable = True 
    m_net = models.Sequential([
        layers.Input(shape=(96, 96, 3)),
        layers.Rescaling(1./127.5, offset=-1), 
        base_mobilenet,
        layers.GlobalAveragePooling2D(),
        layers.Dense(num_classes, activation='softmax')
    ])
    models_dict['MobileNetV2'] = m_net

    
    base_eff = applications.EfficientNetB0(include_top=False, weights='imagenet')
    base_eff.trainable = True
    e_net = models.Sequential([
        layers.Input(shape=(96, 96, 3)),
        
        base_eff, 
        layers.GlobalAveragePooling2D(),
        layers.Dense(num_classes, activation='softmax')
    ])
    models_dict['EfficientNetB0'] = e_net

    
    base_resnet = applications.ResNet50V2(include_top=False, weights='imagenet')
    base_resnet.trainable = True
    r_net = models.Sequential([
        layers.Input(shape=(96, 96, 3)),
        layers.Rescaling(1./127.5, offset=-1), 
        base_resnet,
        layers.GlobalAveragePooling2D(),
        layers.Dense(num_classes, activation='softmax')
    ])
    models_dict['ResNet50V2'] = r_net

    return models_dict


all_results = []
models_to_test = get_models()

for name, model in models_to_test.items():
    print(f"\n🚀 {name} eğitiliyor...")
    
    model.compile(
        optimizer=optimizers.Adam(learning_rate=LR),
        loss='categorical_crossentropy',
        metrics=['accuracy', tf.keras.metrics.Precision(name='precision'), tf.keras.metrics.Recall(name='recall')]
    )

    
    early_stop = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

    start_time = datetime.datetime.now()
    history = model.fit(train_ds, validation_data=val_ds, epochs=EPOCHS, callbacks=[early_stop], verbose=1)
    end_time = datetime.datetime.now()

   
    best_epoch = history.history['val_accuracy'].index(max(history.history['val_accuracy']))
    
    res = {
        'Algoritma': name,
        'Accuracy (%)': round(history.history['val_accuracy'][best_epoch] * 100, 2),
        'Precision (%)': round(history.history['val_precision'][best_epoch] * 100, 2),
        'Recall (%)': round(history.history['val_recall'][best_epoch] * 100, 2),
        'Eğitim Süresi (Dakika)': round((end_time - start_time).total_seconds() / 60, 2),
        'Durdurulan Epoch': best_epoch + 1
    }
    all_results.append(res)
    print(f"✅ {name} tamamlandı! Doğruluk: %{res['Accuracy (%)']}")


df = pd.DataFrame(all_results)
df.to_excel('yeni_karsilastirmali_sonuclar.xlsx', index=False)
print("\n📊 Tüm deneyler bitti! Sonuçlar 'yeni_karsilastirmali_sonuclar.xlsx' dosyasına kaydedildi.")