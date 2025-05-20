import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras.optimizers import Adam

# === 1. Charger les images depuis le dossier Dataset ===

def charger_images_depuis_dossier(chemin):
    """
    Parcourt le dossier des images et construit une liste avec le chemin des images et leur étiquette.
    """
    dataset = []
    for dossier in os.listdir(chemin):
        chemin_dossier = os.path.join(chemin, dossier)
        if os.path.isdir(chemin_dossier):
            for partie_corps in os.listdir(chemin_dossier):
                chemin_partie = os.path.join(chemin_dossier, partie_corps)
                for patient_id in os.listdir(chemin_partie):
                    chemin_patient = os.path.join(chemin_partie, patient_id)
                    for dossier_label in os.listdir(chemin_patient):
                        if dossier_label.split('_')[-1] == 'positive':
                            etiquette = 'fractured'
                        elif dossier_label.split('_')[-1] == 'negative':
                            etiquette = 'normal'
                        chemin_label = os.path.join(chemin_patient, dossier_label)
                        for img in os.listdir(chemin_label):
                            chemin_img = os.path.join(chemin_label, img)
                            dataset.append({
                                'label': partie_corps,
                                'image_path': chemin_img
                            })
    return dataset


# === 2. Préparation des données ===

DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
chemin_images = os.path.join(DOSSIER_COURANT, 'Dataset')
donnees = charger_images_depuis_dossier(chemin_images)

etiquettes = [item['label'] for item in donnees]
chemins = [item['image_path'] for item in donnees]

df_images = pd.DataFrame({'Chemin': chemins, 'Étiquette': etiquettes})

# Division en jeu d'entraînement et de test
train_df, test_df = train_test_split(df_images, train_size=0.9, shuffle=True, random_state=1)

# === 3. Générateurs de données ===

generateur_train = tf.keras.preprocessing.image.ImageDataGenerator(
    preprocessing_function=tf.keras.applications.resnet50.preprocess_input,
    validation_split=0.2
)

generateur_test = tf.keras.preprocessing.image.ImageDataGenerator(
    preprocessing_function=tf.keras.applications.resnet50.preprocess_input
)

images_train = generateur_train.flow_from_dataframe(
    dataframe=train_df,
    x_col='Chemin',
    y_col='Étiquette',
    target_size=(224, 224),
    color_mode='rgb',
    class_mode='categorical',
    batch_size=64,
    shuffle=True,
    seed=42,
    subset='training'
)

images_val = generateur_train.flow_from_dataframe(
    dataframe=train_df,
    x_col='Chemin',
    y_col='Étiquette',
    target_size=(224, 224),
    color_mode='rgb',
    class_mode='categorical',
    batch_size=64,
    shuffle=True,
    seed=42,
    subset='validation'
)

images_test = generateur_test.flow_from_dataframe(
    dataframe=test_df,
    x_col='Chemin',
    y_col='Étiquette',
    target_size=(224, 224),
    color_mode='rgb',
    class_mode='categorical',
    batch_size=32,
    shuffle=False
)

# === 4. Création du modèle ===

base_model = tf.keras.applications.ResNet50(
    input_shape=(224, 224, 3),
    include_top=False,
    weights='imagenet',
    pooling='avg'
)
base_model.trainable = False

x = tf.keras.layers.Dense(128, activation='relu')(base_model.output)
x = tf.keras.layers.Dense(50, activation='relu')(x)
sortie = tf.keras.layers.Dense(3, activation='softmax')(x)  # 3 classes

model = tf.keras.Model(inputs=base_model.input, outputs=sortie)
model.compile(optimizer=Adam(learning_rate=0.0001), loss='categorical_crossentropy', metrics=['accuracy'])

# === 5. Entraînement ===

callbacks = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)
historique = model.fit(images_train, validation_data=images_val, epochs=25, callbacks=[callbacks])

# === 6. Sauvegarde ===

chemin_sauvegarde = os.path.join(DOSSIER_COURANT, "weights/ResNet50_BodyParts.h5")
model.save(chemin_sauvegarde)

# === 7. Évaluation ===

resultats = model.evaluate(images_test, verbose=0)
print("Résultats :", resultats)
print(f"Précision finale sur le test : {np.round(resultats[1] * 100, 2)}%")

# === 8. Graphiques ===

plt.plot(historique.history['accuracy'])
plt.plot(historique.history['val_accuracy'])
plt.title("Précision du modèle")
plt.ylabel("Précision")
plt.xlabel("Épochs")
plt.legend(['Entraînement', 'Validation'])
plt.show()

plt.plot(historique.history['loss'])
plt.plot(historique.history['val_loss'])
plt.title("Erreur (loss) du modèle")
plt.ylabel("Loss")
plt.xlabel("Épochs")
plt.legend(['Entraînement', 'Validation'])
plt.show()
