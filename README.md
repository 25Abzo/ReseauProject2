# SmartTech Dashboard

## Description
Cette application web permet la gestion des employés, clients, documents, et emails pour l'entreprise SmartTech.

## Installation
1. Clonez le repository : `git clone https://github.com/25Abzo/ReseauProject2.git`
2. Installez les dépendances : `pip install -r requirements.txt`



## Fonctionnalités Principales
### 1. Gestion des Employés
Liste des Employés : Affiche tous les employés.
Ajout d'Employé : Ajoute un nouvel employé dans les tables employees et mailbox.
Modification d'Employé : Met à jour les informations d'un employé dans les deux tables.
Suppression d'Employé : Supprime un employé des deux tables.
### 2. Messagerie (iRedMail)
Notifications Automatiques : Envoie des notifications par email lors de l'inscription, modification ou suppression d'un employé.
Configuration Requise :
Assurez-vous que iRedMail est correctement configuré.
Utilisez un compte administrateur pour envoyer des emails automatiques.
### 3. FTP
Téléversement de Fichiers : Permet aux utilisateurs de téléverser des fichiers sur le serveur via une interface web.
Configuration Requise :
Installez vsftpd et configurez /etc/vsftpd.conf.
### 4. Services Réseau
DNS (BIND) : Configurez le nom de domaine interne smarttech.sn pour accéder à l'application.
SSH : Connectez-vous aux machines Linux via SSH (port personnalisé : 22).
VNC/NoVNC : Accédez graphiquement aux machines Linux.
RDP : Accédez graphiquement aux machines Windows.








