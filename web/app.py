from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from api.db import create_mailbox_user, authenticate_user, get_db_connection, add_employee_to_database, update_employee_in_database, delete_employee_from_database
from api.mail import send_email, receive_email
import os
from werkzeug.utils import secure_filename
from datetime import datetime


app = Flask(__name__)
app.secret_key = 'b9d025c1f7e0d1f8b24c33970804617d'
 

app.config['UPLOAD_FOLDER'] = '/home/abzo/upload'
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


from functools import wraps
from flask import redirect, url_for, session, flash

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:  # Vérifie si l'utilisateur est connecté
            flash('Veuillez vous connecter pour accéder à cette page.', 'error')
            return redirect(url_for('login'))  # Redirige vers la page de connexion
        return f(*args, **kwargs)  # Exécute la fonction originale
    return decorated_function



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']  
        password = request.form['password']
        domain = request.form['domain']
        quota = request.form['quota']

        if not name or not email or not password or not domain or not quota:
            flash('All fields are required', 'error')
            return redirect(url_for('register'))

        try:
            add_employee_to_database(name, email, password, "New Employee", "Not Assigned", int(quota))

            send_email("pablo@smarttech.sn", "#Pablo15", email, "Welcome to SmartTech", 
                       f"Hello {name}, your account has been created successfully.")

            flash('User registered successfully', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f"Error: {str(e)}", 'error')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if authenticate_user(username, password):
            session['username'] = username
            session['password'] = password 
            flash('Login successful', 'success')
            return redirect(url_for('send_mail'))  
        else:
            flash('Invalid credentials', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')




@app.route('/send_mail', methods=['GET', 'POST'])
@login_required
def send_mail():
    # if 'username' not in session or 'password' not in session:
    #     return redirect(url_for('login'))

    if request.method == 'POST':
        username = session['username']
        password = request.form['password']
        email_destinataire = request.form['email_destinataire']
        subject = request.form['subject']
        body = request.form['body']

        if not password or not email_destinataire or not subject or not body:
            flash('All fields are required', 'error')
            return redirect(url_for('send_mail'))

        try:
            send_email(username, password, email_destinataire, subject, body)
            flash('Email sent successfully', 'success')
        except Exception as e:
            flash(f"Error: {str(e)}", 'error')

    return render_template('send_mail.html')


@app.route('/receive_mail', methods=['GET', 'POST'])
@login_required
def receive_mail():
    if 'username' not in session or 'password' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        email_user = session['username']
        email_password = session['password']  
        imap_server = 'mail.smarttech.sn'  
        imap_port = 993  

        emails = receive_email(imap_server, imap_port, email_user, email_password)
        return render_template('receive_mail.html', emails=emails)

    # Récupérer automatiquement les emails lors de l'accès à la page
    email_user = session['username']
    email_password = session['password']  
    imap_server = 'mail.smarttech.sn'  
    imap_port = 993  

    emails = receive_email(imap_server, imap_port, email_user, email_password)
    return render_template('receive_mail.html', emails=emails)

    # # Méthode GET
    # email_user = session['username']
    # email_password = session['password']
    # imap_server = 'mail.smarttech.sn'
    # imap_port = 993

    # try:
    #     emails = receive_email(imap_server, imap_port, email_user, email_password)
    #     if not emails:
    #         flash('Aucun email trouvé.', 'info')
    #     return render_template('receive_mail.html', emails=emails)
    # except Exception as e:
    #     flash(f"Erreur : {str(e)}", 'error')
    #     return render_template('receive_mail.html', emails=[])


@app.route('/upload_file', methods=['GET', 'POST'])
@login_required
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
            file.save(file_path)

            flash('File uploaded successfully!', 'success')
            return redirect(url_for('upload_file'))

    return render_template('upload_file.html')


@app.route('/list_uploads', methods=['GET'])
@login_required
def list_uploads():
    upload_dir = app.config['UPLOAD_FOLDER']
    try:
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
            files = []
        else:
            raw_files = os.listdir(upload_dir)
            files = []
            for f in raw_files:
                if allowed_file(f):
                    files.append({
                        'name': f,
                        'size': file_size(f),
                        'last_modified': file_last_modified(f)
                    })
        return render_template('list_uploads.html', files=files)
    except Exception as e:
        flash(f"Erreur : {str(e)}", 'error')
        return redirect(url_for('index'))
    
    
def file_size(filename):
    """
    Renvoie la taille d'un fichier au format lisible (ex: 2.5 MB).
    """
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        size_bytes = os.path.getsize(file_path)
        if size_bytes >= 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.2f} MB"
        elif size_bytes >= 1024:
            return f"{size_bytes / 1024:.2f} KB"
        else:
            return f"{size_bytes} B"
    except FileNotFoundError:
        return "Fichier introuvable"
    


def file_last_modified(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        timestamp = os.path.getmtime(file_path)
        return datetime.fromtimestamp(timestamp).strftime("%d/%m/%Y %H:%M")
    return "N/A"


app.jinja_env.globals.update(
    file_size=file_size,
    file_last_modified=file_last_modified
)

@app.route('/employees', methods=['GET'])
@login_required
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
@login_required
def add_employee():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        position = request.form['position']
        department = request.form['department']
        quota = request.form['quota']  

        if not name or not email or not position or not department or not quota:
            flash('All fields are required', 'error')
            return redirect(url_for('add_employee'))

        try:
            
            add_employee_to_database(name, email, "default_password", position, department, int(quota))

            
            send_email(
                my_email="pablo@smarttech.sn", 
                password="#Pablo15",    
                email_destinataire=email,             
                subject="Welcome to SmartTech", 
                body=f"Hello {name},\n\nYour account has been created successfully.\nPosition: {position}\nDepartment: {department}\nQuota: {quota} MB"
            )

            flash('Employee added successfully and welcome email sent', 'success')
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
        quota = request.form['quota']  

        if not name or not email or not position or not department or not quota:
            flash('All fields are required', 'error')
            return redirect(url_for('edit_employee', id=id))

        try:
            
            update_employee_in_database(email, name, position, department, int(quota))

            
            send_email("admin@smarttech.sn", "your_password", email, "Account Updated", f"Hello {name}, your account has been updated successfully.")

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

        if not employee:
            flash('Employee not found', 'error')
            return redirect(url_for('list_employees'))

        return render_template('edit_employee.html', employee=employee)
    except Exception as e:
        flash(f"Error: {str(e)}", 'error')
        return redirect(url_for('list_employees'))


@app.route('/employees/<int:id>/delete', methods=['POST'])
def delete_employee(id):
    try:
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT email, name FROM employees WHERE id=%s", (id,))
        employee_data = cursor.fetchone()
        cursor.close()
        conn.close()

        if not employee_data:
            flash('Employee not found', 'error')
            return redirect(url_for('list_employees'))

        email = employee_data['email']
        name = employee_data['name']

        
        delete_employee_from_database(email)

        
        send_email("admin@smarttech.sn", "your_password", email, "Account Deleted", f"Hello {name}, your account has been deleted from the system.")

        flash('Employee deleted successfully', 'success')
    except Exception as e:
        flash(f"Error: {str(e)}", 'error')

    return redirect(url_for('list_employees'))


@app.route('/clients', methods=['GET'])
@login_required
def list_clients():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM clients")
        clients = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('clients.html', clients=clients)
    except Exception as e:
        flash(f"Error: {str(e)}", 'error')
        return redirect(url_for('index'))

@app.route('/clients/add', methods=['GET', 'POST'])
@login_required
def add_client():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        company = request.form['company']
        contact_number = request.form['contact_number']

        if not name or not email or not company or not contact_number:
            flash('All fields are required', 'error')
            return redirect(url_for('add_client'))

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO clients (name, email, company, contact_number) VALUES (%s, %s, %s, %s)",
                (name, email, company, contact_number)
            )
            conn.commit()
            cursor.close()
            conn.close()
            flash('Client added successfully', 'success')
            return redirect(url_for('list_clients'))
        except Exception as e:
            flash(f"Error: {str(e)}", 'error')

    return render_template('add_client.html')

@app.route('/clients/<int:id>/edit', methods=['GET', 'POST'])
def edit_client(id):
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        company = request.form['company']
        contact_number = request.form['contact_number']

        if not name or not email or not company or not contact_number:
            flash('All fields are required', 'error')
            return redirect(url_for('edit_client', id=id))

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE clients SET name=%s, email=%s, company=%s, contact_number=%s WHERE id=%s",
                (name, email, company, contact_number, id)
            )
            conn.commit()
            cursor.close()
            conn.close()
            flash('Client updated successfully', 'success')
            return redirect(url_for('list_clients'))
        except Exception as e:
            flash(f"Error: {str(e)}", 'error')

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM clients WHERE id=%s", (id,))
        client = cursor.fetchone()
        cursor.close()
        conn.close()

        if not client:
            flash('Client not found', 'error')
            return redirect(url_for('list_clients'))

        return render_template('edit_client.html', client=client)
    except Exception as e:
        flash(f"Error: {str(e)}", 'error')
        return redirect(url_for('list_clients'))

@app.route('/clients/<int:id>/delete', methods=['POST'])
def delete_client(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM clients WHERE id=%s", (id,))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Client deleted successfully', 'success')
    except Exception as e:
        flash(f"Error: {str(e)}", 'error')

    return redirect(url_for('list_clients'))



@app.route('/upload_file1', methods=['GET', 'POST'])
@login_required

def upload_file1():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)

        file = request.files['file']
        title = request.form.get('title')

        if file.filename == '' or not title:
            flash('Title and file are required', 'error')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Ajouter le document dans la base de données
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO documents (title, file_path, uploaded_by) VALUES (%s, %s, %s)",
                    (title, file_path, session['username'])
                )
                conn.commit()
                cursor.close()
                conn.close()
                flash('File uploaded successfully!', 'success')
                return redirect(url_for('list_documents'))
            except Exception as e:
                flash(f"Error: {str(e)}", 'error')

    return render_template('upload_file1.html')

@app.route('/documents', methods=['GET'])
@login_required

def list_documents():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM documents")
        documents = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('documents.html', documents=documents)
    except Exception as e:
        flash(f"Error: {str(e)}", 'error')
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('email', None)
    session.pop('username', None)
    return redirect(url_for('login'))




@app.route('/download_file/<path:filename>', methods=['GET'])

def download_file(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    except Exception as e:
        flash(f"Error: {str(e)}", 'error')
        return redirect(url_for('list_documents'))

@app.route('/documents/<int:id>/delete', methods=['POST'])

def delete_document(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT file_path FROM documents WHERE id=%s", (id,))
        document_data = cursor.fetchone()

        if document_data:
            file_path = document_data['file_path']
            os.remove(file_path)  # Supprimer le fichier physique
            cursor.execute("DELETE FROM documents WHERE id=%s", (id,))
            conn.commit()

        cursor.close()
        conn.close()
        flash('Document deleted successfully', 'success')
    except Exception as e:
        flash(f"Error: {str(e)}", 'error')

    return redirect(url_for('list_documents'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)