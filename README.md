# ReseauProject2

# SmartTech Dashboard

## Description
Cette application web permet la gestion des employés, documents, et emails pour l'entreprise SmartTech. Elle inclut également des services réseau comme DNS, FTP, SSH, VNC/NoVNC, et RDP.

## Installation
1. Clonez le repository : `git clone https://github.com/25Abzo/ReseauProject2.git`
2. Installez les dépendances : `pip install -r requirements.txt`
3. Configurez la base de données MySQL.
4. Lancez l'application avec Gunicorn : `gunicorn --workers 3 --bind 0.0.0.0:5000 wsgi:application`.

## Structure du Projet

/SmartTech-Dashboard
app.py # Application Flask principale
wsgi.py # Point d'entrée WSGI
/api # Routes API
/templates # Templates HTML
/static # Fichiers statiques (CSS, JS, images)
requirements.txt # Liste des dépendances Python
