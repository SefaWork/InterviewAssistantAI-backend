import os
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers, models, callbacks
from tensorflow.keras.applications import MobileNetV2
from sklearn.metrics import accuracy_score, precision_score, f1_score
from sklearn.utils.class_weight import compute_class_weight
from datetime import datetime


dataset_dir = 'fer2013.csv' 
train_dir = os.path.join(dataset_dir, 'train')
test_dir = os.path.join(dataset_dir, 'test')

img_height, img_width = 96, 96 
batch_size = 64
epochs = 30  
algorithm_name = "Fine Tuning + Class Weights + Checkpoint"

print("🧠 TÜBİTAK NİHAİ PLAN: SINIF AĞIRLIKLANDIRMA VE CHECKPOINT BAŞLATILIYOR...")
print("-" * 50)


print("📥 1/5: Veri seti yükleniyor...")
train_ds = tf.keras.utils.image_dataset_from_directory(
    train_dir, color_mode="rgb", image_size=(img_height, img_width), batch_size=batch_size
)
val_ds = tf.keras.utils.image_dataset_from_directory(
    test_dir, color_mode="rgb", image_size=(img_height, img_width), batch_size=batch_size, shuffle=False
)


print("⚖️ 2/5: Veri dengesizliği çözülüyor (Sınıf ağırlıkları hesaplanıyor)...")

train_labels = []
for images, labels in train_ds:
    train_labels.extend(labels.numpy())

class_weights_array = compute_class_weight('balanced', classes=np.unique(train_labels), y=train_labels)
class_weights = dict(enumerate(class_weights_array))

data_augmentation = tf.keras.Sequential([
  layers.RandomFlip("horizontal"),
  layers.RandomRotation(0.15),
  layers.RandomZoom(0.15),
])


print("🏗️ 3/5: Gelişmiş Model İnşa Ediliyor...")
base_model = MobileNetV2(input_shape=(img_height, img_width, 3), include_top=False, weights='imagenet')


base_model.trainable = True
for layer in base_model.layers[:-70]:
    layer.trainable = False

model = models.Sequential([
    layers.Input(shape=(img_height, img_width, 3)),
    data_augmentation,
    layers.Rescaling(1./127.5, offset=-1), 
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dropout(0.5),
    layers.Dense(256, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.01)),
    layers.BatchNormalization(),
    layers.Dropout(0.5),
    layers.Dense(7, activation='softmax')
])

model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
              loss=tf.keras.losses.SparseCategoricalCrossentropy(),
              metrics=['accuracy'])



lr_scheduler = callbacks.ReduceLROnPlateau(monitor='val_accuracy', factor=0.5, patience=2, verbose=1, min_lr=1e-6)


early_stopping = callbacks.EarlyStopping(monitor='val_accuracy', patience=5, restore_best_weights=True, verbose=1)


model_checkpoint = callbacks.ModelCheckpoint('mulakat_ai_beyni.h5', monitor='val_accuracy', save_best_only=True, verbose=1)


print(f"🚀 4/5: Model Eğitimi Başlıyor (Max {epochs} Tur)...")
history = model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=epochs,
    class_weight=class_weights, 
    callbacks=[lr_scheduler, early_stopping, model_checkpoint]
)


print("\n🧪 5/5: En İyi Model Test Ediliyor...")
y_true, y_pred = [], []
for images, labels in val_ds:
    preds = model.predict(images, verbose=0)
    y_true.extend(labels.numpy())
    y_pred.extend(np.argmax(preds, axis=1))

acc = accuracy_score(y_true, y_pred)
prec = precision_score(y_true, y_pred, average='weighted', zero_division=0)
f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)

print("-" * 30)
print(f"🎯 NİHAİ REKOR SONUÇLAR:")
print(f"Accuracy (Doğruluk) : % {acc * 100:.2f}")
print(f"Precision (Kesinlik): % {prec * 100:.2f}")
print(f"F1-Score            : % {f1 * 100:.2f}")
print("-" * 30)

excel_file = "deney_sonuclari.xlsx"
new_data = pd.DataFrame({
    "Tarih": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
    "Algoritma": [algorithm_name],
    "Epoch Sayısı": [len(history.epoch)],
    "Accuracy (%)": [round(acc * 100, 2)],
    "Precision (%)": [round(prec * 100, 2)],
    "F1-Score (%)": [round(f1 * 100, 2)]
})

if os.path.exists(excel_file):
    existing_data = pd.read_excel(excel_file)
    updated_data = pd.concat([existing_data, new_data], ignore_index=True)
    updated_data.to_excel(excel_file, index=False)
else:
    new_data.to_excel(excel_file, index=False)

print(f"✅ MUHTEŞEM! Sonuçlar '{excel_file}' dosyasına, eğitilmiş beyin ise 'mulakat_ai_beyni.h5' dosyasına kaydedildi!")