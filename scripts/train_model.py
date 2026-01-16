

import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dropout, Flatten, Dense, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
import json

print("="*60)
print("ENTRAÎNEMENT MODÈLE DÉTECTION ÉMOTIONS FACIALES")
print("="*60)

# ============================================================
# 1. CHARGEMENT ET PRÉPARATION DES DONNÉES
# ============================================================

csv_path = "data/fer2013.csv"

if not os.path.exists(csv_path):
    print("\n❌ ERREUR: Fichier fer2013.csv non trouvé!")
    print("\n📥 Télécharge le dataset depuis:")
    print("   https://www.kaggle.com/datasets/msambare/fer2013")
    print("\n   Puis place-le dans: data/fer2013.csv")
    exit()

print("\n📂 Chargement du dataset FER2013...")
data = pd.read_csv(csv_path)

print(f"   • Total d'images: {len(data)}")
print(f"   • Distribution des émotions:")
emotion_map = {
    0: "angry", 1: "disgust", 2: "fear", 3: "happy",
    4: "sad", 5: "surprise", 6: "neutral"
}
for idx, count in data['emotion'].value_counts().sort_index().items():
    print(f"      {emotion_map[idx]}: {count}")

# ============================================================
# 2. CONVERSION PIXELS → IMAGES
# ============================================================

def pixels_to_image(pixels_str):
    """Convertit string de pixels en image 48x48"""
    pixels = np.fromstring(pixels_str, dtype=int, sep=' ')
    return pixels.reshape(48, 48, 1)

print("\n🔄 Conversion des pixels en images...")

X = np.stack(data['pixels'].apply(pixels_to_image).values)
y = data['emotion'].values

# Normalisation
X = X.astype('float32') / 255.0

# Split train/val/test
X_train, X_temp, y_train, y_temp = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)
X_val, X_test, y_val, y_test = train_test_split(
    X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp
)

# One-hot encoding
num_classes = 7
y_train_cat = to_categorical(y_train, num_classes)
y_val_cat = to_categorical(y_val, num_classes)
y_test_cat = to_categorical(y_test, num_classes)

print(f"   • Train: {X_train.shape[0]} images")
print(f"   • Validation: {X_val.shape[0]} images")
print(f"   • Test: {X_test.shape[0]} images")

# ============================================================
# 3. CONSTRUCTION DU MODÈLE CNN
# ============================================================

print("\n🏗️  Construction du modèle CNN...")

model = Sequential([
    # Bloc 1
    Conv2D(32, (3,3), activation='relu', padding='same', input_shape=(48,48,1)),
    BatchNormalization(),
    Conv2D(32, (3,3), activation='relu', padding='same'),
    BatchNormalization(),
    MaxPooling2D(pool_size=(2,2)),
    Dropout(0.25),
    
    # Bloc 2
    Conv2D(64, (3,3), activation='relu', padding='same'),
    BatchNormalization(),
    Conv2D(64, (3,3), activation='relu', padding='same'),
    BatchNormalization(),
    MaxPooling2D(pool_size=(2,2)),
    Dropout(0.25),
    
    # Bloc 3
    Conv2D(128, (3,3), activation='relu', padding='same'),
    BatchNormalization(),
    Conv2D(128, (3,3), activation='relu', padding='same'),
    BatchNormalization(),
    MaxPooling2D(pool_size=(2,2)),
    Dropout(0.25),
    
    # Bloc 4
    Conv2D(256, (3,3), activation='relu', padding='same'),
    BatchNormalization(),
    MaxPooling2D(pool_size=(2,2)),
    Dropout(0.25),
    
    # Couches denses
    Flatten(),
    Dense(512, activation='relu'),
    BatchNormalization(),
    Dropout(0.5),
    Dense(256, activation='relu'),
    BatchNormalization(),
    Dropout(0.5),
    Dense(num_classes, activation='softmax')
])

model.compile(
    loss='categorical_crossentropy',
    optimizer=Adam(learning_rate=0.001),
    metrics=['accuracy']
)

model.summary()

# ============================================================
# 4. DATA AUGMENTATION
# ============================================================

print("\n📊 Configuration de la data augmentation...")

datagen = ImageDataGenerator(
    rotation_range=15,
    width_shift_range=0.15,
    height_shift_range=0.15,
    zoom_range=0.15,
    horizontal_flip=True,
    fill_mode='nearest'
)

datagen.fit(X_train)

# ============================================================
# 5. CALLBACKS
# ============================================================

os.makedirs("models", exist_ok=True)

checkpoint = ModelCheckpoint(
    "models/emotion_model_best.h5",
    monitor="val_accuracy",
    save_best_only=True,
    mode='max',
    verbose=1
)

early_stop = EarlyStopping(
    monitor="val_loss",
    patience=15,
    restore_best_weights=True,
    verbose=1
)

reduce_lr = ReduceLROnPlateau(
    monitor='val_loss',
    factor=0.5,
    patience=5,
    min_lr=0.00001,
    verbose=1
)

# ============================================================
# 6. ENTRAÎNEMENT
# ============================================================

print("\n🚀 Démarrage de l'entraînement...")
print("   (Cela peut prendre 30-60 minutes selon ta machine)\n")

batch_size = 64
epochs = 80

history = model.fit(
    datagen.flow(X_train, y_train_cat, batch_size=batch_size),
    validation_data=(X_val, y_val_cat),
    epochs=epochs,
    callbacks=[checkpoint, early_stop, reduce_lr],
    verbose=1
)

# ============================================================
# 7. ÉVALUATION
# ============================================================

print("\n📈 Évaluation sur le test set...")

test_loss, test_acc = model.evaluate(X_test, y_test_cat, verbose=0)

print(f"\n✅ Résultats finaux:")
print(f"   • Test Loss: {test_loss:.4f}")
print(f"   • Test Accuracy: {test_acc:.4f} ({test_acc*100:.2f}%)")

# ============================================================
# 8. SAUVEGARDE FINALE
# ============================================================

model.save("models/emotion_model.h5")

# Sauvegarde du mapping des émotions
with open("models/emotion_labels.json", "w", encoding='utf-8') as f:
    json.dump(emotion_map, f, ensure_ascii=False, indent=2)

print("\n💾 Modèle sauvegardé:")
print("   • models/emotion_model.h5")
print("   • models/emotion_labels.json")

print("\n" + "="*60)
print("✅ ENTRAÎNEMENT TERMINÉ AVEC SUCCÈS!")
print("="*60)
