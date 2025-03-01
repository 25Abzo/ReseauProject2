import mysql.connector
import hashlib
import base64
from mysql.connector import errorcode

def hash_password(password):
    """
    Hashage du mot de passe en utilisant SHA512 avec un sel fixe (SSHA512).
    """
    salt = b"mystaticSalt"
    password_salt = password.encode('utf-8') + salt
    hashed_password = hashlib.sha512(password_salt).digest()
    password_with_salt = base64.b64encode(hashed_password + salt).decode('utf-8')
    return f"{{SSHA512}}{password_with_salt}"

config = {
    'user': 'postmaster',
    'password': 'passer',
    'host': '127.0.0.1',
    'database': 'vmail',
}

def get_db_connection():
    return mysql.connector.connect(**config)

def create_mailbox_user(username, password, name, domain, quota):
    cnx = None
    cursor = None

    try:
        cnx = get_db_connection()
        cursor = cnx.cursor()

        cursor.execute("SELECT COUNT(*) FROM domain WHERE domain=%s", (domain,))
        domain_exists = cursor.fetchone()[0]
        if not domain_exists:
            print(f"Erreur : Le domaine '{domain}' n'existe pas.")
            return

        hashed_password = hash_password(password)
        maildir = f"{domain}/{username.split('@')[0]}/"

        add_user_query = """
        INSERT INTO mailbox (username, password, name, maildir, quota, domain, isadmin, active)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """
        user_data = (username, hashed_password, name, maildir, quota, domain, 0, 1)

        cursor.execute(add_user_query, user_data)
        cnx.commit()

        print(f"Utilisateur {username} ajouté avec succès dans la table `mailbox`.")

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Erreur d'accès : Nom d'utilisateur ou mot de passe incorrect.")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("La base de données n'existe pas.")
        else:
            print(f"Erreur : {err}")
    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()

def authenticate_user(username, password):
    cnx = None
    cursor = None

    try:
        cnx = get_db_connection()
        cursor = cnx.cursor()

        cursor.execute("SELECT password FROM mailbox WHERE username=%s", (username,))
        result = cursor.fetchone()
        if result:
            stored_password = result[0]
            hashed_password = hash_password(password)
            print(f"Stored password: {stored_password}")
            print(f"Hashed password: {hashed_password}")
            if stored_password == hashed_password:
                return True
        return False

    except mysql.connector.Error as err:
        print(f"Erreur : {err}")
        return False
    finally:
        if cursor:
            cursor.close()
        if cnx:
            cnx.close()
