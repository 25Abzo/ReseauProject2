from flask import Flask, render_template, request, redirect, url_for, session, flash
from api.api import api_bp
from api.db import create_mailbox_user, authenticate_user, get_db_connection
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


@app.route('/employees', methods=['GET'])
def list_employees():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM employees")
        employees = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('employees.html', employees=employees)
    except Exception as e:
        flash(f"Error: {str(e)}", 'error')
        return redirect(url_for('index'))
    

@app.route('/employees/add', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        position = request.form['position']
        department = request.form['department']

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO employees (name, email, position, department) VALUES (%s, %s, %s, %s)",
                (name, email, position, department)
            )
            conn.commit()
            cursor.close()
            conn.close()
            flash('Employee added successfully', 'success')
            return redirect(url_for('list_employees'))
        except Exception as e:
            flash(f"Error: {str(e)}", 'error')

    return render_template('add_employee.html')

@app.route('/employees/<int:id>/edit', methods=['GET', 'POST'])
def edit_employee(id):
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        position = request.form['position']
        department = request.form['department']

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE employees SET name=%s, email=%s, position=%s, department=%s WHERE id=%s",
                (name, email, position, department, id)
            )
            conn.commit()
            cursor.close()
            conn.close()
            flash('Employee updated successfully', 'success')
            return redirect(url_for('list_employees'))
        except Exception as e:
            flash(f"Error: {str(e)}", 'error')

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM employees WHERE id=%s", (id,))
        employee = cursor.fetchone()
        cursor.close()
        conn.close()
        return render_template('edit_employee.html', employee=employee)
    except Exception as e:
        flash(f"Error: {str(e)}", 'error')
        return redirect(url_for('list_employees'))

@app.route('/employees/<int:id>/delete', methods=['POST'])
def delete_employee(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM employees WHERE id=%s", (id,))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Employee deleted successfully', 'success')
    except Exception as e:
        flash(f"Error: {str(e)}", 'error')

    return redirect(url_for('list_employees'))



@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('password', None) 
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
