from flask import Flask, render_template, request, redirect, url_for, session, flash
from api.db import create_mailbox_user, authenticate_user, get_db_connection, add_employee_to_database, update_employee_in_database, delete_employee_from_database
from api.mail import send_email, receive_email
import os
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.secret_key = 'b9d025c1f7e0d1f8b24c33970804617d'


app.config['UPLOAD_FOLDER'] = '/home/abzo/upload'
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


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
            flash('Login successful', 'success')
            return redirect(url_for('send_mail'))  
        else:
            flash('Invalid credentials', 'error')
            return redirect(url_for('login'))

    return render_template('send_mail.html')




@app.route('/send_mail', methods=['GET', 'POST'])
def send_mail():
    if 'email' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        my_email = session['email']
        password = request.form['password']
        email_destinataire = request.form['email_destinataire']
        subject = request.form['subject']
        body = request.form['body']

        if not password or not email_destinataire or not subject or not body:
            flash('All fields are required', 'error')
            return redirect(url_for('send_mail'))

        try:
            send_email(my_email, password, email_destinataire, subject, body)
            flash('Email sent successfully', 'success')
        except Exception as e:
            flash(f"Error: {str(e)}", 'error')

    return render_template('send_mail.html')


@app.route('/receive_mail', methods=['GET', 'POST'])
def receive_mail():
    if 'email' not in session:
        return redirect(url_for('login'))

    email_user = session['email']
    email_password = request.form.get('password') or session.get('password')

    try:
        emails = receive_email("mail.smarttech.sn", 993, email_user, email_password)
    except Exception as e:
        flash(f"Error: {str(e)}", 'error')
        emails = []

    return render_template('receive_mail.html', emails=emails)


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
        quota = request.form['quota']  

        if not name or not email or not position or not department or not quota:
            flash('All fields are required', 'error')
            return redirect(url_for('add_employee'))

        try:
            
            add_employee_to_database(name, email, "default_password", position, department, int(quota))

            
            send_email(
                sender="pablo@smarttech.sn", 
                password="#Pablo15",    
                recipient=email,             
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


@app.route('/logout')
def logout():
    session.pop('email', None)
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)