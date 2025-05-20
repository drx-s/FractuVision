import numpy as np
import pandas as pd
import os.path
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras.optimizers import Adam

# === Chargement des images pour construire et entraîner le modèle ===

def charger_chemins_images(chemin, partie):
    """
    Charge les images de radiographie depuis le dossier donné.
    """
    dataset = []
    for dossier in os.listdir(chemin):
        dossier_complet = os.path.join(chemin, dossier)
        if os.path.isdir(dossier_complet):
            for sous_dossier in os.listdir(dossier_complet):
                if sous_dossier == partie:
                    chemin_partie = os.path.join(dossier_complet, sous_dossier)
                    for id_patient in os.listdir(chemin_partie):
                        chemin_patient = os.path.join(chemin_partie, id_patient)
                        for etat in os.listdir(chemin_patient):
                            if etat.split('_')[-1] == 'positive':
                                etiquette = 'fractured'
                            elif etat.split('_')[-1] == 'negative':
                                etiquette = 'normal'
                            chemin_etat = os.path.join(chemin_patient, etat)
                            for image in os.listdir(chemin_etat):
                                chemin_image = os.path.join(chemin_etat, image)
                                dataset.append({
                                    'partie_os': sous_dossier,
                                    'id_patient': id_patient,
                                    'label': etiquette,
                                    'chemin_image': chemin_image
                                })
    return dataset


# === Fonction pour entraîner le modèle sur une partie spécifique du corps (Main, Coude, Épaule) ===

def entrainer_modele(partie):
    DOSSIER_COURANT = os.path.dirname(os.path.abspath(__file__))
    dossier_images = os.path.join(DOSSIER_COURANT, 'Dataset')
    data = charger_chemins_images(dossier_images, partie)
    etiquettes = []
    chemins_images = []

    for ligne in data:
        etiquettes.append(ligne['label'])
        chemins_images.append(ligne['chemin_image'])

    chemins_images = pd.Series(chemins_images, name='CheminImage').astype(str)
    etiquettes = pd.Series(etiquettes, name='Étiquette')
    images = pd.concat([chemins_images, etiquettes], axis=1)

    # Division des données : 90% pour l'entraînement, 10% pour le test
    train_df, test_df = train_test_split(images, train_size=0.9, shuffle=True, random_state=1)

    generateur_ent = tf.keras.preprocessing.image.ImageDataGenerator(
        horizontal_flip=True,
        preprocessing_function=tf.keras.applications.resnet50.preprocess_input,
        validation_split=0.2
    )

    generateur_test = tf.keras.preprocessing.image.ImageDataGenerator(
        preprocessing_function=tf.keras.applications.resnet50.preprocess_input
    )

    images_train = generateur_ent.flow_from_dataframe(
        dataframe=train_df,
        x_col='CheminImage',
        y_col='Étiquette',
        target_size=(224, 224),
        color_mode='rgb',
        class_mode='categorical',
        batch_size=64,
        shuffle=True,
        seed=42,
        subset='training'
    )

    images_validation = generateur_ent.flow_from_dataframe(
        dataframe=train_df,
        x_col='CheminImage',
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
        x_col='CheminImage',
        y_col='Étiquette',
        target_size=(224, 224),
        color_mode='rgb',
        class_mode='categorical',
        batch_size=32,
        shuffle=False
    )

    # Utilisation du modèle ResNet50 pré-entraîné
    modele_preentraine = tf.keras.applications.resnet50.ResNet50(
        input_shape=(224, 224, 3),
        include_top=False,
        weights='imagenet',
        pooling='avg'
    )
    modele_preentraine.trainable = False

    entree = modele_preentraine.input
    x = tf.keras.layers.Dense(128, activation='relu')(modele_preentraine.output)
    x = tf.keras.layers.Dense(50, activation='relu')(x)
    sortie = tf.keras.layers.Dense(2, activation='softmax')(x)
    modele = tf.keras.Model(entree, sortie)

    print("-------Entraînement du modèle pour :", partie, "-------")

    modele.compile(optimizer=Adam(learning_rate=0.0001),
                   loss='categorical_crossentropy',
                   metrics=['accuracy'])

    callbacks = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=3, restore_best_weights=True)

    historique = modele.fit(images_train, validation_data=images_validation, epochs=25, callbacks=[callbacks])

    # Sauvegarde du modèle
    modele.save(DOSSIER_COURANT + "/weights/ResNet50_" + partie + "_frac.h5")

    # Évaluation sur le test
    resultats = modele.evaluate(images_test, verbose=0)
    print(f"{partie} - Résultats : {resultats}")
    print(f"Précision sur test : {np.round(resultats[1] * 100, 2)}%")

    # Graphique de précision
    plt.plot(historique.history['accuracy'])
    plt.plot(historique.history['val_accuracy'])
    plt.title('Précision du modèle')
    plt.ylabel('Précision')
    plt.xlabel('Époch')
    plt.legend(['entraînement', 'validation'], loc='upper left')
    figAcc = plt.gcf()
    chemin_image = os.path.join(DOSSIER_COURANT, f"./plots/FractureDetection/{partie}/_Accuracy.jpeg")
    figAcc.savefig(chemin_image)
    plt.clf()

    # Graphique de perte
    plt.plot(historique.history['loss'])
    plt.plot(historique.history['val_loss'])
    plt.title('Perte du modèle')
    plt.ylabel('Perte')
    plt.xlabel('Époch')
    plt.legend(['entraînement', 'validation'], loc='upper left')
    figLoss = plt.gcf()
    chemin_image = os.path.join(DOSSIER_COURANT, f"./plots/FractureDetection/{partie}/_Loss.jpeg")
    figLoss.savefig(chemin_image)
    plt.clf()

# === Entraînement du modèle pour chaque partie du corps ===

categories_parties = ["Elbow", "Hand", "Shoulder"]
for partie in categories_parties:
    entrainer_modele(partie)
