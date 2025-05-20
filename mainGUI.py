import os
from tkinter import filedialog
import customtkinter as ctk
from PIL import ImageTk, Image
import pandas as pd
from docx import Document
from docx.shared import Pt
from docx2pdf import convert
from predictions import predict

# Variables globales
dossier_projet = os.path.dirname(os.path.abspath(__file__))
dossier_images = os.path.join(dossier_projet, 'images')
fichier_image = ""

# Configuration des thèmes et couleurs
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Couleurs personnalisées
NOIR_PROFOND = "#121212"
ORANGE_VIF = "#FF5500"
BLEU_LOGO = "#1E90FF"
BLANC = "#FFFFFF"
GRIS_CLAIR = "#E0E0E0"
VERT = "#00C853"
ROUGE = "#FF3D00"


class FenetreInfos(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Informations du patient")
        self.geometry("450x550")
        self.configure(fg_color="#1A1A1A")
        self.resizable(False, False)

        # Titre principal
        ctk.CTkLabel(
            self,
            text="Veuillez entrer les informations",
            font=("Arial", 18, "bold"),
            text_color="white"
        ).pack(pady=(20, 10))

        # Nom du patient
        ctk.CTkLabel(self, text="Nom du patient *", text_color="white", font=("Arial", 14)).pack(anchor="w", padx=30)
        self.entree_patient = ctk.CTkEntry(self, height=35, font=("Arial", 14))
        self.entree_patient.pack(fill="x", padx=30, pady=(0, 15))

        # Âge
        ctk.CTkLabel(self, text="Âge du patient *", text_color="white", font=("Arial", 14)).pack(anchor="w", padx=30)
        self.entree_age = ctk.CTkEntry(self, height=35, font=("Arial", 14))
        self.entree_age.pack(fill="x", padx=30, pady=(0, 15))

        # Genre
        ctk.CTkLabel(self, text="Genre (Homme/Femme) *", text_color="white", font=("Arial", 14)).pack(anchor="w", padx=30)
        self.entree_genre = ctk.CTkEntry(self, height=35, font=("Arial", 14))
        self.entree_genre.pack(fill="x", padx=30, pady=(0, 15))

        # Poids
        ctk.CTkLabel(self, text="Poids (kg)", text_color="white", font=("Arial", 14)).pack(anchor="w", padx=30)
        self.entree_poids = ctk.CTkEntry(self, height=35, font=("Arial", 14))
        self.entree_poids.pack(fill="x", padx=30, pady=(0, 15))

        # Diagnostic (TextBox multiligne)
        ctk.CTkLabel(self, text="Diagnostic *", text_color="white", font=("Arial", 14)).pack(anchor="w", padx=30)
        self.entree_diagnostic = ctk.CTkTextbox(self, height=100, font=("Arial", 14), wrap="word")
        self.entree_diagnostic.pack(fill="x", padx=30, pady=(0, 20))

        # Bouton valider
        ctk.CTkButton(
            self,
            text="Valider et générer le rapport",
            font=("Arial", 14, "bold"),
            height=40,
            fg_color="#1E90FF",
            hover_color="#00C853",
            command=self.generer_rapport
        ).pack(padx=30, fill="x")

    def generer_rapport(self):
        nom_patient = self.entree_patient.get()
        age = self.entree_age.get()
        genre = self.entree_genre.get()
        poids = self.entree_poids.get()
        diagnostic = self.entree_diagnostic.get("1.0", "end").strip()

        if not all([nom_patient, age, genre, diagnostic]):
            self.parent.texte_pied_page.configure(text="⚠ Toutes les informations doivent être remplies.", text_color=ROUGE)
            return

        dossier_modele = os.path.join(dossier_projet, "modele")
        chemin_modele = os.path.join(dossier_modele, "document.docx")

        if not os.path.exists(chemin_modele):
            print("Le modèle Word n'existe pas.")
            return

        try:
            type_os = self.parent.label_type_os.cget('text').replace("Type d'os : ", '')
            statut_diag = self.parent.label_statut.cget('text').replace("Statut : ", '')
            date_now = pd.Timestamp.now().strftime('%d/%m/%Y %H:%M')

            doc = Document(chemin_modele)

            for p in doc.paragraphs:
                if "{{patient}}" in p.text:
                    p.text = p.text.replace("{{patient}}", nom_patient)
                if "{{age}}" in p.text:
                    p.text = p.text.replace("{{age}}", age)
                if "{{genre}}" in p.text:
                    p.text = p.text.replace("{{genre}}", genre)
                if "{{poids}}" in p.text:
                    p.text = p.text.replace("{{poids}}", poids)
                if "{{diagnostic}}" in p.text:
                    p.text = p.text.replace("{{diagnostic}}", diagnostic)
                if "{{type_os}}" in p.text:
                    p.text = p.text.replace("{{type_os}}", type_os)
                if "{{statut}}" in p.text:
                    p.text = p.text.replace("{{statut}}", statut_diag)
                if "{{date}}" in p.text:
                    p.text = p.text.replace("{{date}}", date_now)

                p.style.font.size = Pt(12)

            fichier_temp = os.path.join(dossier_projet, "temp_result.docx")
            doc.save(fichier_temp)

            nom_fichier = f"{nom_patient}_{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}.pdf"
            chemin_pdf = os.path.join(dossier_projet, "PredictResults", nom_fichier)

            convert(fichier_temp, chemin_pdf)
            os.remove(fichier_temp)

            alerte = ctk.CTkLabel(
                master=self.parent,
                text="✓ Rapport généré dans PredictResults",
                font=("Arial", 16, "bold"),
                text_color=VERT,
                fg_color="#222222",
                corner_radius=8,
                width=400,
                height=40
            )
            alerte.place(relx=0.5, rely=0.05, anchor="center")
            self.parent.after(3000, alerte.destroy)
            self.destroy()

        except Exception as e:
            print(f"Erreur: {e}")
            self.parent.texte_pied_page.configure(text=f"Erreur: {e}", text_color=ROUGE)


class Application(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("FractuVision • Diagnostic Radiologique")
        self.geometry("1200x800")
        self.configure(fg_color=NOIR_PROFOND)

        # Barre supérieure
        self.barre_sup = ctk.CTkFrame(self, height=40, fg_color=BLEU_LOGO, corner_radius=0)
        self.barre_sup.pack(fill="x", pady=0)

        self.logo_label = ctk.CTkLabel(
            self.barre_sup,
            text="FractuVision • Diagnostic Radiologique",
            font=("Arial", 14, "bold"),
            text_color=BLANC
        )
        self.logo_label.pack(side="left", padx=10, pady=5)

        icone_info = ctk.CTkImage(Image.open(os.path.join(dossier_images, "info.png")))
        self.bouton_info = ctk.CTkButton(
            master=self.barre_sup,
            text="",
            image=icone_info,
            command=self.ouvrir_fenetre_info,
            width=40,
            height=40
        )
        self.bouton_info.pack(pady=10, padx=10, anchor="nw", side="right")

        # Conteneur principal
        self.conteneur_principal = ctk.CTkFrame(self, fg_color=NOIR_PROFOND)
        self.conteneur_principal.pack(fill="both", expand=True)

        # En-tête centré
        self.titre_principal = ctk.CTkLabel(
            self.conteneur_principal,
            text="FractuVision",
            font=("Arial", 36, "bold"),
            text_color=BLEU_LOGO
        )
        self.titre_principal.pack(pady=(20, 0))

        self.sous_titre = ctk.CTkLabel(
            self.conteneur_principal,
            text="Système avancé de détection de fractures osseuses",
            font=("Arial", 16),
            text_color=GRIS_CLAIR
        )
        self.sous_titre.pack(pady=(0, 20))

        # Zone de contenu
        self.zone_contenu = ctk.CTkFrame(self.conteneur_principal, fg_color=NOIR_PROFOND)
        self.zone_contenu.pack(fill="both", expand=True, padx=20, pady=10)

        # Colonne gauche
        self.colonne_gauche = ctk.CTkFrame(self.zone_contenu, fg_color=NOIR_PROFOND)
        self.colonne_gauche.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.titre_radio = ctk.CTkLabel(
            self.colonne_gauche,
            text="Radiographie",
            font=("Arial", 20, "bold"),
            text_color=BLANC
        )
        self.titre_radio.pack(anchor="w", pady=(0, 10))

        self.cadre_image = ctk.CTkFrame(
            self.colonne_gauche,
            fg_color="#1A1A1A",
            corner_radius=5,
            border_width=2,
            border_color=NOIR_PROFOND,
            height=500
        )
        self.cadre_image.pack(fill="both", expand=True, pady=(0, 10))

        self.label_image = ctk.CTkLabel(self.cadre_image, text="", fg_color="transparent")
        self.label_image.pack(expand=True, fill="both", padx=10, pady=10)

        try:
            image_par_defaut = Image.open(os.path.join(dossier_images, "Question_Mark4.jpg"))
            image_redimensionnee = image_par_defaut.resize((400, 450))
            image_affichee = ImageTk.PhotoImage(image_redimensionnee)
            self.label_image.configure(image=image_affichee)
            self.label_image.image = image_affichee
        except Exception as e:
            print(f"Erreur lors du chargement de l'image par défaut: {e}")
            self.label_image.configure(text="Aucune image")

        self.bouton_importer = ctk.CTkButton(
            self.colonne_gauche,
            text="Importer une radiographie",
            font=("Arial", 14),
            height=40,
            fg_color=BLEU_LOGO,
            hover_color="#0072CE",
            corner_radius=5,
            command=self.importer_image
        )
        self.bouton_importer.pack(fill="x", pady=5)

        # Colonne droite
        self.colonne_droite = ctk.CTkFrame(self.zone_contenu, fg_color=NOIR_PROFOND)
        self.colonne_droite.pack(side="right", fill="both", expand=True, padx=(10, 0))

        self.titre_diagnostic = ctk.CTkLabel(
            self.colonne_droite,
            text="Diagnostic",
            font=("Arial", 20, "bold"),
            text_color=BLANC
        )
        self.titre_diagnostic.pack(anchor="w", pady=(0, 10))

        self.cadre_message = ctk.CTkFrame(
            self.colonne_droite,
            fg_color="#1A1A1A",
            corner_radius=5,
            border_width=2,
            border_color=NOIR_PROFOND,
        )
        self.cadre_message.pack(fill="x", pady=(0, 15), ipady=10)

        self.message_initial = ctk.CTkLabel(
            self.cadre_message,
            text="L'analyse a détecté une fracture osseuse. Veuillez consulter un professionnel de santé pour confirmation et prise en charge.",
            font=("Arial", 14),
            text_color=GRIS_CLAIR,
            justify="center"
        )
        self.message_initial.pack(pady=10, padx=15)

        self.cadre_resultats = ctk.CTkFrame(
            self.colonne_droite,
            fg_color="#1A1A1A",
            corner_radius=5,
            border_width=2,
            border_color=NOIR_PROFOND,
            height=350
        )
        self.cadre_resultats.pack(fill="both", expand=True, pady=(0, 15))

        self.titre_resultats = ctk.CTkLabel(
            self.cadre_resultats,
            text="Résultats de l'analyse",
            font=("Arial", 18, "bold"),
            text_color=BLEU_LOGO
        )
        self.titre_resultats.pack(pady=(20, 10))

        self.label_type_os = ctk.CTkLabel(
            self.cadre_resultats,
            text="🦴 Type d'os : Hand",
            font=("Arial", 20),
            text_color=BLANC
        )
        self.label_type_os.pack(pady=10)

        self.label_statut = ctk.CTkLabel(
            self.cadre_resultats,
            text="Statut : FRACTURE DÉTECTÉE",
            font=("Arial", 20, "bold"),
            text_color=ROUGE
        )
        self.label_statut.pack(pady=10)

        self.frame_boutons = ctk.CTkFrame(self.colonne_droite, fg_color="transparent")
        self.frame_boutons.pack(fill="x", pady=10)

        self.bouton_analyser = ctk.CTkButton(
            self.frame_boutons,
            text="Analyser la radiographie",
            font=("Arial", 14),
            height=40,
            fg_color=VERT,
            hover_color="#00A040",
            corner_radius=5,
            command=self.lancer_prediction
        )
        self.bouton_analyser.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.bouton_analyser.configure(state="disabled")  # Désactivé par défaut

        self.bouton_sauvegarder = ctk.CTkButton(
            self.frame_boutons,
            text="Sauvegarder le rapport",
            font=("Arial", 14),
            height=40,
            fg_color="#3A3A3A",
            hover_color="#505050",
            corner_radius=5,
            border_color=BLEU_LOGO,
            border_width=2,
            command=self.enregistrer_resultat
        )
        self.bouton_sauvegarder.pack(side="right", fill="x", expand=True, padx=(5, 0))

        self.pied_page = ctk.CTkFrame(self.conteneur_principal, height=30, fg_color=NOIR_PROFOND)
        self.pied_page.pack(fill="x", pady=(10, 5))

        self.texte_pied_page = ctk.CTkLabel(
            self.pied_page,
            text="© 2025 FractuVision • Système de diagnostic assisté par IA • Version 2.0",
            font=("Arial", 10),
            text_color="#888888"
        )
        self.texte_pied_page.pack(side="right", padx=20)

        self.cacher_resultats()

    def ouvrir_fenetre_info(self):
        try:
            image = Image.open(os.path.join(dossier_images, "rules.png"))
            image = image.resize((700, 700))
            image.show()
        except Exception as e:
            print(f"Erreur lors de l'ouverture de l'image d'information : {e}")

    def cacher_resultats(self):
        self.message_initial.configure(text="Importez une radiographie et lancez l'analyse pour obtenir un diagnostic.")
        self.label_type_os.configure(text="Type d'os : -")
        self.label_statut.configure(text="Statut : En attente d'analyse", text_color=GRIS_CLAIR)
        self.bouton_sauvegarder.configure(state="disabled")

    def importer_image(self):
        global fichier_image
        types_fichiers = [("Images", ".jpg .jpeg *.png *.bmp"), ("Tous les fichiers", ".*")]
        fichier_image = filedialog.askopenfilename(initialdir=os.path.join(dossier_projet, 'test'),
                                                   filetypes=types_fichiers)
        if not fichier_image:
            return
        try:
            self.cacher_resultats()
            image = Image.open(fichier_image)
            cadre_largeur = self.cadre_image.winfo_width() - 20
            cadre_hauteur = self.cadre_image.winfo_height() - 20
            if cadre_largeur <= 1:
                cadre_largeur, cadre_hauteur = 400, 450
            ratio = min(cadre_largeur / image.width, cadre_hauteur / image.height)
            image_redim = image.resize((int(image.width * ratio), int(image.height * ratio)))
            image_tk = ImageTk.PhotoImage(image_redim)
            self.label_image.configure(image=image_tk)
            self.label_image.image = image_tk
            self.bouton_analyser.configure(state="normal")
        except Exception as e:
            print(f"Erreur: {e}")
            self.label_image.configure(text=f"Erreur : {e}")

    def lancer_prediction(self):
        global fichier_image
        if not fichier_image:
            self.message_initial.configure(text="Veuillez importer une image.")
            return
        try:
            self.bouton_analyser.configure(state="disabled", text="Analyse en cours...")
            self.update()
            type_os = predict(fichier_image)
            diagnostic = predict(fichier_image, type_os)
            self.bouton_analyser.configure(state="normal", text="Analyser la radiographie")
            if diagnostic == "fractured":
                self.message_initial.configure(
                    text="Fracture détectée. Consultez un professionnel de santé.")
                self.label_statut.configure(text="Statut : FRACTURE DÉTECTÉE", text_color=ROUGE)
            else:
                self.message_initial.configure(
                    text="Aucune fracture détectée. Si les symptômes persistent, consultez.")
                self.label_statut.configure(text="Statut : NORMAL", text_color=VERT)
            types_os_fr = {
                "Elbow": "Coude",
                "Hand": "Main",
                "Shoulder": "Épaule"
            }
            type_os_fr = types_os_fr.get(type_os, type_os)
            self.label_type_os.configure(text=f"Type d'os : {type_os_fr}")
            self.bouton_sauvegarder.configure(state="normal")
        except Exception as e:
            print(f"Erreur: {e}")
            self.message_initial.configure(text=f"Erreur: {e}")
            self.bouton_analyser.configure(state="normal", text="Analyser la radiographie")

    def enregistrer_resultat(self):
        FenetreInfos(self)


if __name__ == "__main__":
    app = Application()
    app.mainloop()