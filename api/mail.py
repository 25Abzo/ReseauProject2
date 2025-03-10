import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import imaplib
import email
from email.header import decode_header

def send_email(my_email, password, email_destinataire, subject, body):
    message = MIMEMultipart()
    message["From"] = my_email
    message["To"] = email_destinataire
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("172.24.182.63", 587) as connection:
            connection.ehlo("mail.smarttech.sn")
            connection.starttls()
            connection.login(user=my_email, password=password)
            connection.sendmail(from_addr=my_email, to_addrs=email_destinataire, msg=message.as_string())
            print("Email envoyé avec succès.")
    except smtplib.SMTPRecipientsRefused as e:
        print(f"Erreur : Destinataire refusé : {e}")
    except smtplib.SMTPException as e:
        print(f"Erreur SMTP : {e}")
    except Exception as e:
        print(f"Erreur inattendue : {e}")




def receive_email(imap_server, imap_port, email_user, email_password):
    try:
        mail = imaplib.IMAP4_SSL(imap_server, imap_port)
        mail.login(email_user, email_password)
        mail.select("inbox")

        status, messages = mail.search(None, "UNSEEN")
        email_ids = messages[0].split()

        emails = []
        if email_ids:
            print(f"{len(email_ids)} nouvel(s) email(s) trouvé(s).")
            for email_id in email_ids:
                status, data = mail.fetch(email_id, "(RFC822)")
                for response_part in data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject = msg["subject"]
                        sender = msg["from"]
                        print(f"De: {sender}")
                        print(f"Sujet: {subject}")

                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == "text/plain":
                                    body = part.get_payload(decode=True).decode()
                                    print(f"Contenu: {body}")
                        else:
                            body = msg.get_payload(decode=True).decode()
                            print(f"Contenu: {body}")
                        emails.append({"subject": subject, "sender": sender, "body": body})
        else:
            print("Aucun nouvel email.")
        mail.logout()
        return emails
    except Exception as e:
        print(f"Erreur lors de la réception des emails : {e}")
        return []