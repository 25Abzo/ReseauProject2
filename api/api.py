from flask import Blueprint, request, jsonify, session
from .db import create_mailbox_user, authenticate_user
from .mail import send_email, receive_email

api_bp = Blueprint('api', __name__)

@api_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    name = data.get('name')
    domain = data.get('domain')
    quota = data.get('quota')

    if not username or not password or not name or not domain or not quota:
        return jsonify({'error': 'All fields are required'}), 400

    create_mailbox_user(username, password, name, domain, quota)
    return jsonify({'message': 'User registered successfully'}), 201

@api_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    if authenticate_user(username, password):
        session['username'] = username
        return jsonify({'message': 'Login successful'}), 200
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@api_bp.route('/send_mail', methods=['POST'])
def send_mail_route():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    my_email = session['username']
    password = data.get('password')
    email_destinataire = data.get('email_destinataire')
    subject = data.get('subject')
    body = data.get('body')

    if not password or not email_destinataire or not subject or not body:
        return jsonify({'error': 'All fields are required'}), 400

    send_email(my_email, password, email_destinataire, subject, body)
    return jsonify({'message': 'Email sent successfully'}), 200

@api_bp.route('/receive_mail', methods=['POST'])
def receive_mail_route():
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    imap_server = data.get('imap_server')
    imap_port = data.get('imap_port')
    email_user = session['username']
    email_password = data.get('email_password')

    if not imap_server or not imap_port or not email_password:
        return jsonify({'error': 'All fields are required'}), 400

    emails = receive_email(imap_server, imap_port, email_user, email_password)
    return jsonify({'emails': emails}), 200

@api_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return jsonify({'message': 'Logout successful'}), 200
