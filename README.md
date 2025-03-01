# 📧 Client Web Mail avec Django et iRedMail

## 📌 Description
Ce projet est une interface web permettant d'envoyer, recevoir et consulter des emails en utilisant iRedMail comme serveur de messagerie. Développé avec Django (backend), TailwindCSS (frontend) et Python, il vise à fournir une solution simple et efficace pour la gestion des emails.

## 🚀 Technologies utilisées
- **Python** 🐍 (Backend & logique métier)
- **Django** 🎯 (Framework Web)
- **Tailwind CSS** 🎨 (Stylisation de l'interface)
- **iRedMail** 📩 (Serveur de messagerie)

## 📋 Prérequis
Avant d'installer le projet, assure-toi d'avoir les logiciels suivants :

- Python `3.13.1`
- Tailwind CSS
- iRedMail

## 🛠 Installation

Clone le projet et installe les dépendances :
```bash
# Cloner le dépôt
git clone https://github.com/ton-repo/ReseauProject.git
cd ReseauProject

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows : venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

## ⚙️ Configuration
Crée un fichier `.env` à la racine du projet et ajoute les paramètres suivants :
```ini
EMAIL_HOST=name.smarttech.sn
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tonemail@smarttech.sn
EMAIL_HOST_PASSWORD=(A fournir !)
```

## ▶️ Utilisation

Démarre le serveur Django :
```bash
python run.py runserver
```
Puis accède à l’interface via `http://127.0.0.1:5000`.

## ✨ Fonctionnalités
- 📩 Envoi et réception d’emails
- 📥 Consultation des messages reçus
- 🛠 Gestion des paramètres utilisateur
- 🔒 Sécurisation des communications (SSL/TLS)

## 📷 Captures d'écran (optionnel)
![image](https://github.com/user-attachments/assets/58a6d79c-5e4a-4321-af34-e6ab81b57897)

## 📜 Licence
Ce projet est sous licence **MIT** 📜. Tu es libre de l’utiliser et de le modifier.
