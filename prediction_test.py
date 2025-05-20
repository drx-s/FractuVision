import os
from colorama import Fore  # Pour colorer les textes affichés dans le terminal
from predictions import predict  # Fonction de prédiction définie dans le fichier predictions.py


# Fonction pour charger toutes les images dans un dossier donné (par exemple, "test/")
def load_path(path):
    dataset = []
    # Pour chaque dossier correspondant à une partie du corps (Elbow, Hand, Shoulder)
    for body in os.listdir(path):
        body_part = body
        path_p = path + '/' + str(body)
        # Pour chaque sous-dossier correspondant à l’étiquette (fractured ou normal)
        for lab in os.listdir(path_p):
            label = lab
            path_l = path_p + '/' + str(lab)
            # Pour chaque image dans le dossier
            for img in os.listdir(path_l):
                img_path = path_l + '/' + str(img)
                # Ajouter les informations dans une liste
                dataset.append({
                    'body_part': body_part,
                    'label': label,
                    'image_path': img_path,
                    'image_name': img
                })
    return dataset


# Catégories utilisées pour les prédictions
categories_parts = ["Elbow", "Hand", "Shoulder"]
categories_fracture = ['fractured', 'normal']


# Fonction qui affiche les prédictions du modèle et compare avec la vérité terrain
def reportPredict(dataset):
    total_count = 0         # Total d’images testées
    part_count = 0          # Prédictions correctes de la partie du corps
    status_count = 0        # Prédictions correctes du statut (fracture ou non)

    # Afficher l’en-tête du tableau
    print(Fore.YELLOW +
          '{0: <28}'.format('Nom') +
          '{0: <14}'.format('Partie réelle') +
          '{0: <20}'.format('Partie prédite') +
          '{0: <20}'.format('Statut réel') +
          '{0: <20}'.format('Statut prédit'))

    # Pour chaque image dans le dataset
    for img in dataset:
        body_part_predict = predict(img['image_path'])  # Prédiction de la partie du corps
        fracture_predict = predict(img['image_path'], body_part_predict)  # Prédiction du statut (fracture)

        # Comparaison avec la vérité terrain (dans le nom du dossier)
        if img['body_part'] == body_part_predict:
            part_count += 1
        if img['label'] == fracture_predict:
            status_count += 1
            color = Fore.GREEN  # Vert si bonne prédiction
        else:
            color = Fore.RED    # Rouge sinon

        # Afficher les résultats pour chaque image
        print(color +
              '{0: <28}'.format(img['image_name']) +
              '{0: <14}'.format(img['body_part']) +
              '{0: <20}'.format(body_part_predict) +
              '{0: <20}'.format(img['label']) +
              '{0: <20}'.format(fracture_predict))

    # Afficher l’exactitude des prédictions
    print(Fore.BLUE + '\nExactitude (partie du corps) : ' + str("%.2f" % (part_count / len(dataset) * 100)) + '%')
    print(Fore.BLUE + 'Exactitude (fracture) : ' + str("%.2f" % (status_count / len(dataset) * 100)) + '%')


# Exécution du script
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))  # Chemin du script actuel
test_dir = THIS_FOLDER + '/test/'  # Chemin du dossier de test
reportPredict(load_path(test_dir))  # Lancer l’analyse
