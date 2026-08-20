import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from sympy import re
from utils.db import init_db, register_user, validate_user, save_chat_message, get_chat_history, clear_chat_history,get_user_by_username,get_user_by_email,update_user_password
from models.recommender import generate_recommendation_response

# Load environment configurations
load_dotenv()

app = Flask(__name__)

# Basic Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'schemeai-dev-secret-key-12345')
app.config['DEBUG'] = True

# Initialize SQLite database and seed initial schemes
with app.app_context():
    init_db()

@app.route('/')
def home():
    """
    Renders the homepage/landing portal for SchemeAI.
    """
    # Check if user is logged in to dynamically show dashboard options in navbar
    logged_in = 'user_id' in session
    username = session.get('username')
    return render_template('index.html', logged_in=logged_in, username=username)

# --- Authentication Routes ---

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Handles user account registration.
    """
    if 'user_id' in session:
        return redirect(url_for('chat_workspace'))

    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        # Validations
        if not username or not email or not password:
            error = "All fields are required."
        elif len(username) < 3:
            error = "Username must be at least 3 characters long."
        elif len(password) < 6:
            error = "Password must be at least 6 characters long."
        else:
            # Register user
            success = register_user(username, email, password)
            if success:
                # Redirect to login page upon success
                return redirect(url_for('login', registered='success'))
            else:
                error = "Username is already taken. Please choose another."
                
    return render_template('register.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handles user login authentication.
    """
    if 'user_id' in session:
        return redirect(url_for('chat_workspace'))

    error = None
    success_msg = None
    
    # Display registration success alert if navigated from register page
    if request.args.get('registered') == 'success':
        success_msg = "Account " \
        "d successfully! Please log in."

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            error = "Please fill in all fields."
        else:
            # Validate credentials
            user = validate_user(username, password)
            if user:
                # Set session cookies
                session['user_id'] = user['id']
                session['username'] = user['username']
                return redirect(url_for('chat_workspace'))
            else:
                error = "Invalid username or password. Please try again."
                
    return render_template('login.html', error=error, success_msg=success_msg)

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()

        if not email:
            return render_template(
                'forgot_password.html',
                error='Please enter your registered email.'
            )

        user = get_user_by_email(email)

        if not user:
            return render_template(
                'forgot_password.html',
                error='No account found with this email.'
            )

        # Create reset token
        token = os.urandom(32).hex()

        # Store token temporarily in the session
        session['reset_token'] = token
        session['reset_user_id'] = user['id']

        # Create reset link
        reset_link = url_for(
            'reset_password',
            token=token,
            _external=True
        )

        # Create email
        message = EmailMessage()
        message['Subject'] = 'SchemeAI - Password Reset'
        message['From'] = os.environ.get('MAIL_USERNAME')
        message['To'] = email

        message.set_content(
            f"""Hello {user['username']},

We received a request to reset your SchemeAI password.

Click the link below to reset your password:

{reset_link}

If you did not request this password reset, you can ignore this email.

Regards,
SchemeAI Team
"""
        )

        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(
                    os.environ.get('MAIL_USERNAME'),
                    os.environ.get('MAIL_PASSWORD')
                )
                server.send_message(message)

            return render_template(
                'forgot_password.html',
                success_msg='Password reset link has been sent to your email.'
            )

        except Exception as e:
            print(f"Email sending error: {str(e)}")
            return render_template(
                'forgot_password.html',
                error='Could not send the reset email. Please try again later.'
            )

    return render_template('forgot_password.html')
@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if session.get('reset_token') != token:
        return "Invalid or expired password reset link.", 400

    if request.method == 'POST':
        new_password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        if not new_password or not confirm_password:
            return render_template(
                'reset_password.html',
                error='All fields are required.'
            )

        if len(new_password) < 6:
            return render_template(
                'reset_password.html',
                error='Password must be at least 6 characters long.'
            )

        if new_password != confirm_password:
            return render_template(
                'reset_password.html',
                error='Passwords do not match.'
            )

        user_id = session.get('reset_user_id')

        update_user_password(user_id, new_password)

        session.pop('reset_token', None)
        session.pop('reset_user_id', None)

        return redirect(url_for('login', reset='success'))

    return render_template('reset_password.html')
@app.route('/logout')
def logout():
    """
    Logs out the user and clears session tokens.
    """
    session.clear()
    return redirect(url_for('home'))

@app.route('/chat')
def chat_workspace():
    """
    Renders the dedicated chatbot workspace interface.
    Requires user authentication.
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    return render_template('chat.html', username=session['username'])

# --- Chatbot API Routes ---

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """
    Processes chat requests, saves messages to SQLite, and fetches recommendations.
    """
    # 1. Authentication Check
    if 'user_id' not in session:
        return jsonify({
            'status': 'error',
            'message': 'Unauthorized access. Please log in first.'
        }), 401
        
    user_id = session['user_id']
    
    # 2. Parse JSON Data Safely
    data = request.get_json(silent=True)
    if not data or 'message' not in data:
        return jsonify({
            'status': 'error',
            'message': 'Invalid query format. JSON with a message field is required.'
        }), 400
        
    user_message = data['message'].strip()
    
    # 3. Input Validation
    if not user_message:
        return jsonify({
            'status': 'error',
            'message': 'Message cannot be empty.'
        }), 400
        
    try:
        # 4. Save User Message to History Table
        save_chat_message(user_id, 'user', user_message)
        
        # 5. Generate Recommendation Response via matching algorithm
        bot_response_html = generate_recommendation_response(user_message)
        
        # 6. Save Bot Response to History Table
        save_chat_message(user_id, 'bot', bot_response_html)
        
        return jsonify({
            'status': 'success',
            'response': bot_response_html
        })
    except Exception as e:
        # Error handling for unexpected failures
        print(f"Chat API Error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'An unexpected database error occurred while processing your request.'
        }), 500

@app.route('/api/history', methods=['GET'])
def api_history():
    """
    Retrieves the logged-in user's chat history from the database.
    """
    if 'user_id' not in session:
        return jsonify({
            'status': 'error',
            'message': 'Unauthorized access.'
        }), 401
        
    try:
        history = get_chat_history(session['user_id'])
        return jsonify({
            'status': 'success',
            'history': history
        })
    except Exception as e:
        print(f"History Fetch Error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Could not retrieve chat history.'
        }), 500

@app.route('/api/clear', methods=['POST'])
def api_clear():
    """
    Deletes the logged-in user's chat history from the database.
    """
    if 'user_id' not in session:
        return jsonify({
            'status': 'error',
            'message': 'Unauthorized access.'
        }), 401
        
    try:
        clear_chat_history(session['user_id'])
        return jsonify({
            'status': 'success',
            'message': 'Chat history successfully cleared.'
        })
    except Exception as e:
        print(f"History Clear Error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Could not clear chat history.'
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
