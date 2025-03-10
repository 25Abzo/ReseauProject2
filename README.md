# SmartTech Dashboard

## Description
Cette application web permet la gestion des employés, clients, documents, et emails pour l'entreprise SmartTech.

## Installation
1. Clonez le repository : `git clone https://github.com/25Abzo/ReseauProject2.git`
2. Installez les dépendances : `pip install -r requirements.txt`

## Lancement 
1. tapez py run.py runserver pour lancer le serveur (sous windows)
1. tapez python3 run.py runserver pour lancer le serveur (sous linux)

## Fichiers de Configuration

DNS (BIND) : db.smarttech.sn
Messagerie (iRedMail) : postfix, dovecot
FTP (vsftpd) : vsftpd.conf
SSH (OpenSSH) : sshd_config
VNC/NoVNC : novnc.sh
RDP (xRDP) : xrdp.conf

## 🌐 Fonctionnalités Principales
### 1. Gestion des Employés
Liste des Employés : Affiche tous les employés.
Ajout d'Employé : Crée un compte utilisateur dans la BDD et une boîte email via iRedMail.
Modification/Suppression : Met à jour ou supprime les données dans les tables employees et mailbox.
### 2. Messagerie (iRedMail)
Notifications Automatiques :
📧 Envoie des emails de bienvenue/confirmation lors de l'inscription ou des modifications.
Configuration :
🔑 Utilise un compte administrateur (ex: admin@smarttech.sn).
### 3. Téléversement de Fichiers (FTP)
Interface Web : Permet de téléverser des fichiers via l'URL /upload_file.
Serveur FTP :
📂 Configuré avec vsftpd (fichier vsftpd.conf inclus).
### 4. Services Réseau
DNS (BIND) :
🌐 Nom de domaine smarttech.sn résout vers l'IP du serveur (fichier db.smarttech.sn).
SSH (OpenSSH) :
🔑 Connexion sécurisée via clé SSH (port 22).
VNC/NoVNC :
🖥️ Accès graphique aux machines Linux via http://@serveur:8080/vnc.html.
RDP (xRDP) :
🖥️ Accès graphique aux machines Windows sur le port 3389.
DNS (BIND) : Configurez le nom de domaine interne smarttech.sn pour accéder à l'application.
SSH : Connectez-vous aux machines Linux via SSH (port personnalisé : 22).
VNC/NoVNC : Accédez graphiquement aux machines Linux.
RDP : Accédez graphiquement aux machines Windows.

## 🧪 Tests Réalisés
Scénario Global Validé
✅ Étapes :

Inscription d'un utilisateur.
Connexion via l'interface web.
Ajout/modification/suppression d'un employé.
Envoi d'un email automatique de bienvenue.
Téléversement d'un fichier via l'interface FTP.
Déconnexion sécurisée.
