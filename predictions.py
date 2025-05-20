import numpy as np
import tensorflow as tf
from keras.preprocessing import image

# Chargement automatique des modèles entraînés lors de l'importation de ce fichier

# Modèles de détection de fractures pour chaque partie du corps
model_elbow_frac = tf.keras.models.load_model("weights/ResNet50_Elbow_frac.h5")       # Coude
model_hand_frac = tf.keras.models.load_model("weights/ResNet50_Hand_frac.h5")         # Main
model_shoulder_frac = tf.keras.models.load_model("weights/ResNet50_Shoulder_frac.h5") # Épaule

# Modèle de classification des parties du corps (Elbow, Hand, Shoulder)
model_parts = tf.keras.models.load_model("weights/ResNet50_BodyParts.h5")

# Catégories pour chaque type de prédiction

#   0 - Coude     1 - Main     2 - Épaule
categories_parts = ["Elbow", "Hand", "Shoulder"]

#   0 - Fracturé     1 - Normal
categories_fracture = ['fractured', 'normal']

# Fonction de prédiction
# img : chemin de l’image à prédire
# model : modèle à utiliser ("Parts" pour prédire la partie du corps ; sinon pour prédire fracture ou non)
def predict(img, model="Parts"):
    taille = 224  # Taille d’image standard (224x224)

    # Choisir le modèle à utiliser
    if model == 'Parts':
        chosen_model = model_parts  # modèle pour détecter la partie du corps
    else:
        if model == 'Elbow':
            chosen_model = model_elbow_frac
        elif model == 'Hand':
            chosen_model = model_hand_frac
        elif model == 'Shoulder':
            chosen_model = model_shoulder_frac

    # Charger l’image avec la bonne taille (224x224) et en couleurs (RGB)
    temp_img = image.load_img(img, target_size=(taille, taille))
    x = image.img_to_array(temp_img)             # Convertir en tableau numpy
    x = np.expand_dims(x, axis=0)                # Ajouter une dimension pour créer un batch de 1 image
    images = np.vstack([x])                      # Empiler (forme : (1, 224, 224, 3))

    # Prédiction du modèle (résultat : tableau de probabilités pour chaque classe)
    prediction = np.argmax(chosen_model.predict(images), axis=1)  # On garde l’indice de la classe avec la plus haute proba

    # Traduction de l’indice en étiquette (texte)
    if model == 'Parts':
        prediction_str = categories_parts[prediction.item()]
    else:
        prediction_str = categories_fracture[prediction.item()]

    return prediction_str  # Retourne la prédiction sous forme de texte (ex : "fractured", "Hand", etc.)
