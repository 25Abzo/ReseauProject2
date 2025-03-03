# SmartTech Dashboard

## Description
Cette application web permet la gestion des employés, clients, documents, et emails pour l'entreprise SmartTech.

## Installation
1. Clonez le repository : `git clone https://github.com/25Abzo/ReseauProject2.git`
2. Installez les dépendances : `pip install -r requirements.txt`
3. Configurez la base de données MySQL :
   - Créez une base de données nommée `smarttech_db`.
   - Mettez à jour les paramètres de connexion dans `config.py`.
4. Lancez l'application avec Gunicorn : `gunicorn --workers 3 --bind 0.0.0.0:5000 wsgi:application`.

