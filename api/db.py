import mysql.connector
import hashlib
import base64
from mysql.connector import errorcode

# Fonction pour hasher le mot de passe en SSHA512
def hash_password(password):
    """
    Hashage du mot de passe en utilisant SHA512 avec un sel fixe (SSHA512).
    """
    salt = b"mystaticSalt"
    password_salt = password.encode('utf-8') + salt
    hashed_password = hashlib.sha512(password_salt).digest()
    password_with_salt = base64.b64encode(hashed_password + salt).decode('utf-8')
    return f"{{SSHA512}}{password_with_salt}"

# Configuration de la connexion à la base de données
config = {
    'user': 'postmaster',
    'password': 'passer',
    'host': '127.0.0.1',
    'database': 'vmail',  # Base de données principale
}

# Obtenir une connexion à la base de données
def get_db_connection():
    try:
        return mysql.connector.connect(**config)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Erreur d'accès : Nom d'utilisateur ou mot de passe incorrect.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("La base de données n'existe pas.")
        else:
            print(f"Erreur : {err}")
        return None

# Créer un utilisateur dans la table `mailbox`
def create_mailbox_user(username, password, name, domain, quota):
    cnx = None
    cursor = None

    try:
        cnx = get_db_connection()
        cursor = cnx.cursor()

        # Vérifier si le domaine existe
        cursor.execute("SELECT COUNT(*) FROM domain WHERE domain=%s", (domain,))
        domain_exists = cursor.fetchone()[0]
        if not domain_exists:
            print(f"Erreur : Le domaine '{domain}' n'existe pas.")
            return False

        # Hasher le mot de passe
        hashed_password = hash_password(password)

        # Définir le maildir
        maildir = f"{domain}/{username.split('@')[0]}/"

        # Insérer dans la table mailbox
        add_user_query = """
        INSERT INTO mailbox (username, password, name, maildir, quota, domain, isadmin, active)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """
        user_data = (username, hashed_password, name, maildir, quota, domain, 0, 1)  # isadmin=0, active=1
        cursor.execute(add_user_query, user_data)
        cnx.commit()

        print(f"Utilisateur {username} ajouté avec succès dans la table `mailbox`.")
        return True

    except mysql.connector.Error as err:
        print(f"Erreur lors de la création de l'utilisateur : {err}")
        return False
    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()

# Authentification d'un utilisateur
def authenticate_user(username, password):
    cnx = None
    cursor = None

    try:
        cnx = get_db_connection()
        cursor = cnx.cursor()

        # Récupérer le mot de passe stocké
        cursor.execute("SELECT password FROM mailbox WHERE username=%s", (username,))
        result = cursor.fetchone()
        if result:
            stored_password = result[0]
            hashed_password = hash_password(password)

            # Comparer les mots de passe
            if stored_password == hashed_password:
                return True
        return False

    except mysql.connector.Error as err:
        print(f"Erreur lors de l'authentification : {err}")
        return False
    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()

# Ajouter un employé dans les deux tables : employees et mailbox
def add_employee_to_database(name, email, password, position, department, quota):
    cnx = None
    cursor = None

    try:
        cnx = get_db_connection()
        cursor = cnx.cursor()

        # Extraire le domaine de l'email
        domain = email.split('@')[-1]

        # Vérifier si le domaine existe
        cursor.execute("SELECT COUNT(*) FROM domain WHERE domain=%s", (domain,))
        domain_exists = cursor.fetchone()[0]
        if not domain_exists:
            print(f"Erreur : Le domaine '{domain}' n'existe pas.")
            return False

        # Hasher le mot de passe pour la table mailbox
        hashed_password = hash_password(password)

        # Insérer dans la table employees
        add_employee_query = """
        INSERT INTO employees (name, email, position, department)
        VALUES (%s, %s, %s, %s);
        """
        employee_data = (name, email, position, department)
        cursor.execute(add_employee_query, employee_data)

        # Insérer dans la table mailbox
        maildir = f"{domain}/{email.split('@')[0]}/"
        add_mailbox_query = """
        INSERT INTO mailbox (username, password, name, maildir, quota, domain, isadmin, active)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """
        mailbox_data = (email, hashed_password, name, maildir, quota, domain, 0, 1)  # isadmin=0, active=1
        cursor.execute(add_mailbox_query, mailbox_data)

        # Valider la transaction
        cnx.commit()

        print(f"Employé {name} ajouté avec succès dans les tables `employees` et `mailbox`.")
        return True

    except mysql.connector.Error as err:
        if cnx:
            cnx.rollback()  # Annuler en cas d'erreur
        print(f"Erreur lors de l'ajout de l'employé : {err}")
        return False
    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()

# Modifier un employé dans les deux tables : employees et mailbox
def update_employee_in_database(email, new_name, new_position, new_department, new_quota):
    cnx = None
    cursor = None

    try:
        cnx = get_db_connection()
        cursor = cnx.cursor()

        # Mettre à jour la table employees
        update_employee_query = """
        UPDATE employees SET name=%s, position=%s, department=%s WHERE email=%s;
        """
        employee_data = (new_name, new_position, new_department, email)
        cursor.execute(update_employee_query, employee_data)

        # Mettre à jour la table mailbox
        update_mailbox_query = """
        UPDATE mailbox SET name=%s, quota=%s WHERE username=%s;
        """
        domain = email.split('@')[-1]
        maildir = f"{domain}/{email.split('@')[0]}/"
        mailbox_data = (new_name, new_quota * 1024 * 1024, email)  # Quota en octets
        cursor.execute(update_mailbox_query, mailbox_data)

        # Valider la transaction
        cnx.commit()

        print(f"Employé {email} mis à jour avec succès dans les tables `employees` et `mailbox`.")
        return True

    except mysql.connector.Error as err:
        if cnx:
            cnx.rollback()  # Annuler en cas d'erreur
        print(f"Erreur lors de la mise à jour de l'employé : {err}")
        return False
    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()

# Supprimer un employé des deux tables : employees et mailbox
def delete_employee_from_database(email):
    cnx = None
    cursor = None

    try:
        cnx = get_db_connection()
        cursor = cnx.cursor()

        # Supprimer de la table mailbox
        delete_mailbox_query = "DELETE FROM mailbox WHERE username=%s;"
        cursor.execute(delete_mailbox_query, (email,))

        # Supprimer de la table employees
        delete_employee_query = "DELETE FROM employees WHERE email=%s;"
        cursor.execute(delete_employee_query, (email,))

        # Valider la transaction
        cnx.commit()

        print(f"Employé {email} supprimé avec succès des tables `employees` et `mailbox`.")
        return True

    except mysql.connector.Error as err:
        if cnx:
            cnx.rollback()  # Annuler en cas d'erreur
        print(f"Erreur lors de la suppression de l'employé : {err}")
        return False
    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()