"""
Niraj Byanjankar - Portfolio Website
Flask Application

GMAIL SETUP INSTRUCTIONS:
--------------------------
To enable the contact form to send emails via Gmail:

1. Go to your Google Account → Security
2. Enable "2-Step Verification" if not already enabled
3. Search for "App Passwords" in the search bar
4. Select App: "Mail", Device: "Other (Custom name)" → type "Portfolio"
5. Google will generate a 16-character password (e.g., "abcd efgh ijkl mnop")
6. Copy that password (remove spaces) into your .env file as GMAIL_APP_PASSWORD
7. Set GMAIL_USER to your Gmail address (nirajbjk@gmail.com)

Then create a .env file (copy from .env.example) and fill in your credentials.
"""

from flask import Flask, render_template, request, jsonify
from flask_mail import Mail, Message
from prometheus_flask_exporter import PrometheusMetrics
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Portfolio application info', version='1.0.0')

# ─── Flask-Mail Configuration ─────────────────────────────────────────────────
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('GMAIL_USER', 'nirajbjk@gmail.com')
app.config['MAIL_PASSWORD'] = os.getenv('GMAIL_APP_PASSWORD', '')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('GMAIL_USER', 'nirajbjk@gmail.com')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-this')

mail = Mail(app)


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/contact', methods=['POST'])
def contact():
    """Handle contact form submission and send email via Gmail."""
    try:
        data = request.get_json()
        name    = data.get('name', '').strip()
        email   = data.get('email', '').strip()
        subject = data.get('subject', '').strip()
        message = data.get('message', '').strip()

        # Basic validation
        if not all([name, email, subject, message]):
            return jsonify({'success': False, 'error': 'All fields are required.'}), 400

        # Compose the email
        msg = Message(
            subject=f"[Portfolio Contact] {subject}",
            recipients=[app.config['MAIL_USERNAME']],
            reply_to=email,
            body=f"""
New message from your portfolio website:

Name:    {name}
Email:   {email}
Subject: {subject}

Message:
{message}

---
Sent via nirajbyanjankar.com portfolio contact form
""",
            html=f"""
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;
            background:#0d1117; color:#c9d1d9; padding:30px; border-radius:8px;
            border: 1px solid #00d4ff;">
  <h2 style="color:#00d4ff; border-bottom:1px solid #00d4ff; padding-bottom:10px;">
    📬 New Portfolio Message
  </h2>
  <table style="width:100%; margin:20px 0;">
    <tr><td style="color:#8b949e; width:80px;"><strong>Name</strong></td>
        <td style="color:#c9d1d9;">{name}</td></tr>
    <tr><td style="color:#8b949e;"><strong>Email</strong></td>
        <td><a href="mailto:{email}" style="color:#00d4ff;">{email}</a></td></tr>
    <tr><td style="color:#8b949e;"><strong>Subject</strong></td>
        <td style="color:#c9d1d9;">{subject}</td></tr>
  </table>
  <div style="background:#161b22; padding:20px; border-radius:6px;
              border-left:3px solid #00d4ff; margin-top:16px;">
    <p style="margin:0; line-height:1.7; white-space:pre-wrap;">{message}</p>
  </div>
  <p style="color:#8b949e; font-size:12px; margin-top:20px; text-align:center;">
    Sent via your portfolio contact form
  </p>
</div>
"""
        )

        mail.send(msg)
        return jsonify({'success': True, 'message': 'Your message has been sent successfully!'})

    except Exception as e:
        # If mail is not configured, return a friendly error
        error_msg = str(e)
        if 'Authentication' in error_msg or 'Username' in error_msg or 'password' in error_msg.lower():
            return jsonify({
                'success': False,
                'error': 'Email service not configured yet. Please check the README for Gmail setup instructions.'
            }), 500
        return jsonify({'success': False, 'error': 'Failed to send message. Please try again later.'}), 500


# ─── Run ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
