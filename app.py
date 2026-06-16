import os
import re
import json
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import pandas as pd

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'txt', 'csv', 'xlsx', 'xls', 'mp4', 'mov', 'avi', 'mkv'}
USER_DB_FILE = os.path.join(os.path.dirname(__file__), 'users.json')

app = Flask(__name__)
app.secret_key = 'replace-with-a-secure-random-secret'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Helper utilities


def load_users():
    if not os.path.exists(USER_DB_FILE):
        return {}
    with open(USER_DB_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_users(users):
    with open(USER_DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2)


def user_exists(username):
    return username in load_users()


def create_user(username, password):
    users = load_users()
    users[username] = generate_password_hash(password)
    save_users(users)


def verify_user(username, password):
    users = load_users()
    password_hash = users.get(username)
    return password_hash and check_password_hash(password_hash, password)


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if not session.get('username'):
            return redirect(url_for('login'))
        return view(**kwargs)
    return wrapped_view


@app.context_processor
def inject_user():
    return dict(current_user=session.get('username'))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def normalize_transaction(record):
    normalized = {
        'date': record.get('date') or record.get('Date') or record.get('transaction_date') or '',
        'description': record.get('description') or record.get('Description') or record.get('vendor') or '',
        'amount': record.get('amount') or record.get('Amount') or record.get('total') or '',
        'currency': record.get('currency') or record.get('Currency') or 'USD',
        'category': record.get('category') or record.get('Category') or 'unknown',
        'source': record.get('source') or 'uploaded file'
    }
    return normalized


def extract_transactions_from_text(text):
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    transactions = []
    amount_pattern = re.compile(r'\$?([0-9]+(?:\.[0-9]{1,2})?)')
    date_pattern = re.compile(r'\b(\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})\b')
    for line in lines:
        amount_match = amount_pattern.search(line)
        date_match = date_pattern.search(line)
        if amount_match:
            tx = {
                'date': date_match.group(0) if date_match else '',
                'description': line,
                'amount': amount_match.group(1),
                'currency': 'USD',
                'category': 'parsed_text',
                'source': 'text'
            }
            transactions.append(normalize_transaction(tx))
    return transactions


def extract_xlsx_data(filepath):
    try:
        workbook = pd.ExcelFile(filepath)
    except ImportError as e:
        raise ImportError("Missing optional dependency 'openpyxl'. Install it with: pip install openpyxl") from e

    sheets = {}
    for sheet_name in workbook.sheet_names:
        df = pd.read_excel(workbook, sheet_name=sheet_name)
        sheets[sheet_name] = df.fillna('').to_dict(orient='records')
    return sheets


def process_video_file(filepath):
    # Placeholder for Azure Video Indexer or Azure AI Video Analyzer integration
    # In production, send the video to the Azure Video Indexer API and retrieve transcript, frames, and metadata.
    result = {
        'video_file': os.path.basename(filepath),
        'extracted_text': 'Sample transcript or OCR text from video frames',
        'frames': [
            {'timecode': '00:00:05', 'description': 'Detected invoice header', 'image_url': '/static/images/frame1.png'},
            {'timecode': '00:00:12', 'description': 'Detected transaction total', 'image_url': '/static/images/frame2.png'}
        ],
        'transactions': [
            {'date': '2026-06-06', 'description': 'Payment to supplier', 'amount': '152.50', 'currency': 'USD', 'category': 'expense', 'source': 'video'}
        ]
    }
    return result


def store_last_result(result):
    session['last_result'] = json.dumps(result, indent=2)


def get_last_result():
    return json.loads(session.get('last_result', '{}')) if session.get('last_result') else None


# Routes

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload')
@login_required
def upload():
    return render_template('upload.html')


@app.route('/video')
@login_required
def video():
    return render_template('video.html')


@app.route('/text')
@login_required
def text():
    return render_template('text.html')


@app.route('/xlsx')
@login_required
def xlsx():
    return render_template('xlsx.html')


@app.route('/transactions')
@login_required
def transactions():
    return render_template('transactions.html', transactions=get_last_result().get('transactions', []) if get_last_result() else [])


@app.route('/images')
@login_required
def images():
    return render_template('images.html', frames=get_last_result().get('frames', []) if get_last_result() else [])


@app.route('/results')
@login_required
def results():
    return render_template('results.html', result=get_last_result())


@app.route('/settings')
def settings():
    return render_template('settings.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if session.get('username'):
        return redirect(url_for('upload'))

    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not username or not password:
            error = 'Enter both username and password.'
        elif password != confirm_password:
            error = 'Passwords do not match.'
        elif user_exists(username):
            error = 'Username already exists.'
        else:
            create_user(username, password)
            session['username'] = username
            return redirect(url_for('upload'))

    return render_template('signup.html', error=error)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('username'):
        return redirect(url_for('upload'))

    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            error = 'Enter both username and password.'
        elif not verify_user(username, password):
            error = 'Invalid username or password.'
        else:
            session['username'] = username
            return redirect(url_for('upload'))

    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/api/process_text', methods=['POST'])
@login_required
def api_process_text():
    text = request.form.get('text', '')
    transactions = extract_transactions_from_text(text)
    result = {
        'input_type': 'text',
        'original_text': text,
        'transactions': transactions,
        'normalized': [normalize_transaction(tx) for tx in transactions]
    }
    store_last_result(result)
    return redirect(url_for('results'))


@app.route('/api/process_xlsx', methods=['POST'])
@login_required
def api_process_xlsx():
    file = request.files.get('file')
    if not file or not allowed_file(file.filename):
        return redirect(url_for('xlsx'))
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    try:
        sheets = extract_xlsx_data(filepath)
    except ImportError as e:
        # Return the xlsx upload page with a helpful error message when openpyxl is missing
        error_msg = str(e)
        return render_template('xlsx.html', error=error_msg)
    normalized_transactions = []
    for sheet_records in sheets.values():
        for record in sheet_records:
            normalized_transactions.append(normalize_transaction(record))
    result = {
        'input_type': 'xlsx',
        'filename': filename,
        'sheets': sheets,
        'transactions': normalized_transactions
    }
    store_last_result(result)
    return redirect(url_for('results'))


@app.route('/api/process_video', methods=['POST'])
@login_required
def api_process_video():
    file = request.files.get('file')
    if not file or not allowed_file(file.filename):
        return redirect(url_for('video'))
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    result = process_video_file(filepath)
    store_last_result(result)
    return redirect(url_for('results'))


if __name__ == '__main__':
    app.run(debug=True)
