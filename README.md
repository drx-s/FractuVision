
# FractuVision 🦴🔍

FractuVision est une application de diagnostic assisté par l’intelligence artificielle, conçue pour détecter automatiquement les fractures de la main, du coude et de l’épaule à partir d’images médicales (radiographies). Ce projet a été développé dans le cadre d’un Projet de Fin d’Études (PFE) à la Faculté des Sciences Appliquées Ait Melloul, année universitaire 2024/2025.

## 👨‍⚕️ Objectif du projet

- Automatiser la détection de fractures osseuses à l’aide de réseaux de neurones convolutifs (CNN).
- Fournir une aide rapide, fiable et accessible au diagnostic pour les professionnels de santé.
- Proposer une interface utilisateur moderne permettant l’importation d’images, l’analyse par IA et la génération de rapports médicaux.

## 📸 Données utilisées

Le modèle est entraîné sur **MURA**, une base de données publique d’images radiographiques musculosquelettiques proposée par Stanford.

- Parties du corps utilisées : **main**, **coude**, **épaule**.
- Catégories : **normale** / **fracturée**.
- Prétraitement : redimensionnement (224x224), normalisation, et augmentation des données.

## 🧠 Modèles IA

Deux approches ont été implémentées :

- **CNN simple** : architecture personnalisée pour les premiers tests.
- **ResNet50** : modèle pré-entraîné sur ImageNet, adapté au transfert learning pour les images médicales.

Un **classificateur de type d’os** permet de rediriger automatiquement les images vers le bon modèle (main, coude, épaule).

## 🖥️ Interface utilisateur

Développée avec **CustomTkinter** pour une expérience utilisateur fluide et moderne.
## 🖼️ Aperçu de l'interface utilisateur
<div align="center">
<img src="https://github.com/drx-s/FractuVision/blob/main/assets/interface_main.jpg?raw=true " alt="FractuVision Interface" width="800" />
</div>

### Fonctionnalités :
- Importation d’une radiographie.
- Prédiction automatique du type d’os et du statut (fracturé / normal).
- Affichage des résultats en temps réel.
- Génération d’un rapport PDF personnalisé avec les données du patient.
- Aide intégrée à l’utilisation.

## 📊 Résultats

Les performances varient selon le type d’os, avec une **accuracy moyenne > 85%** :

| Modèle         | Accuracy Entraînement | Accuracy Validation |
|----------------|------------------------|----------------------|
| Main           | 83%                    | 78%                  |
| Coude          | 90%                    | 75-78%               |
| Épaule         | 82%                    | 75%                  |
| Body Part Classifier | >99%             | >99%                 |

## ⚙️ Bibliothèques utilisées

- `TensorFlow`, `Keras` – Entraînement et déploiement des CNN.
- `NumPy`, `Pandas` – Manipulation des données.
- `Matplotlib` – Visualisation.
- `Pillow` – Chargement et traitement des images.
- `CustomTkinter` – Interface graphique.
- `python-docx`, `docx2pdf` – Génération des rapports.
- `datetime`, `Colorama` – Utilitaires et logs.

## 📁 Structure du dépôt

```

FractuVision/
├── models/               # Modèles entraînés
├── dataset/              # Dossier contenant des radiographies (MURA)
├── ui/                   # Code de l'interface graphique
├── utils/                # Fonctions de prétraitement, prédiction, rapport
├── main.py               # Lancement de l'application
├── requirements.txt      # Dépendances Python
└── README.md             # Fichier de description

```

## 📈 Perspectives

- Amélioration des modèles (EfficientNet, DenseNet).
- Déploiement en ligne via Flask ou Streamlit.
- Intégration dans des systèmes hospitaliers (PACS/DICOM).
- Ajout de modules d’explicabilité (Grad-CAM).
- Extension vers d’autres types d’os ou pathologies.

## 👨‍🎓 Auteurs

- AFTAH Hassan  
- BEN LARBI Ahmed  
- BERDAOUZ Lahcen  

### Encadré par :  
**Mr. Mohammed HSAISSOUNE**

---

> Ce projet est une contribution au développement de solutions intelligentes dans le domaine de la santé, en visant à assister les professionnels tout en améliorant l'accès aux soins pour tous.

## 📎 Licence

Ce projet est open source — [Voir la licence du dépôt](LICENSE) pour plus de détails.


