from flask import Flask, render_template, request, redirect, url_for, session, flash
from api.api import api_bp
from api.db import create_mailbox_user, authenticate_user
from api.mail import send_email, receive_email
import os
from ftplib import FTP
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.secret_key = 'b9d025c1f7e0d1f8b24c33970804617d'  
app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        domain = request.form['domain']
        quota = request.form['quota']

        if not username or not password or not name or not domain or not quota:
            flash('All fields are required', 'error')
            return redirect(url_for('register'))

        create_mailbox_user(username, password, name, domain, quota)
        flash('User registered successfully', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if authenticate_user(username, password):
            session['username'] = username
            session['password'] = password  # Stockez le mot de passe dans la session
            return redirect(url_for('send_mail'))  # Rediriger vers la page d'envoi d'email
        else:
            flash('Invalid credentials', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/send_mail', methods=['GET', 'POST'])
def send_mail():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        my_email = session['username']
        password = request.form['password']
        email_destinataire = request.form['email_destinataire']
        subject = request.form['subject']
        body = request.form['body']

        if not password or not email_destinataire or not subject or not body:
            flash('All fields are required', 'error')
            return redirect(url_for('send_mail'))

        send_email(my_email, password, email_destinataire, subject, body)
        flash('Email sent successfully', 'success')
        return redirect(url_for('send_mail'))

    return render_template('send_mail.html')

@app.route('/receive_mail', methods=['GET', 'POST'])
def receive_mail():
    if 'username' not in session or 'password' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        email_user = session['username']
        email_password = session['password']  # Utilisez le mot de passe stocké dans la session
        imap_server = 'mail.smarttech.sn'  # Utilisez le serveur IMAP par défaut
        imap_port = 993  # Utilisez le port IMAP par défaut

        emails = receive_email(imap_server, imap_port, email_user, email_password)
        return render_template('receive_mail.html', emails=emails)

    # Récupérer automatiquement les emails lors de l'accès à la page
    email_user = session['username']
    email_password = session['password']  # Utilisez le mot de passe stocké dans la session
    imap_server = 'mail.smarttech.sn'  # Utilisez le serveur IMAP par défaut
    imap_port = 993  # Utilisez le port IMAP par défaut

    emails = receive_email(imap_server, imap_port, email_user, email_password)
    return render_template('receive_mail.html', emails=emails)


app.config['UPLOAD_FOLDER'] = '/home/abzo/upload'
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

# # Assurez-vous que le répertoire existe
# if not os.path.exists(app.config['UPLOAD_FOLDER']):
#     os.makedirs(app.config['UPLOAD_FOLDER'])

# Vérifier les extensions autorisées
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print(f"Saving file to {file_path}")
            file.save(file_path)

            flash('File uploaded successfully!', 'success')
            return redirect(url_for('upload_file'))

    return render_template('upload_file.html')



@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('password', None) 
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
