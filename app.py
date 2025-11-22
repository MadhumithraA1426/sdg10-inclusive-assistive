import os
import io
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, send_file, flash
from werkzeug.security import generate_password_hash, check_password_hash
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import nltk
import pdfplumber
from gtts import gTTS

nltk.download('punkt')
nltk.download('stopwords')

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Change this for production

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DATABASE = 'db.sqlite3'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Create tables
def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        pdf_filename TEXT,
        summary TEXT,
        audio BLOB,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    conn.commit()
    conn.close()

init_db()

def extract_text_from_pdf(filepath):
    text = ""
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def summarize_text(text, max_points=5):
    stop_words = set(stopwords.words("english"))
    words = word_tokenize(text)
    freq_table = dict()
    for word in words:
        word = word.lower()
        if word in stop_words or not word.isalpha():
            continue
        freq_table[word] = freq_table.get(word, 0) + 1
    sentences = sent_tokenize(text)
    sentence_scores = dict()
    for sentence in sentences:
        for word in word_tokenize(sentence.lower()):
            if word in freq_table:
                sentence_scores[sentence] = sentence_scores.get(sentence, 0) + freq_table[word]
    ranked_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)
    summary = ranked_sentences[:max_points]
    return summary

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            flash("Username and password required.")
            return redirect(url_for('register'))
        hashed_pw = generate_password_hash(password)
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
            conn.commit()
            flash("Registration successful. Please login.")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Username already exists.")
            return redirect(url_for('register'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash("Logged in successfully!")
            return redirect(url_for('upload_file'))
        else:
            flash("Invalid credentials.")
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have logged out.")
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    summary = None
    error = None
    if request.method == 'POST':
        if 'file' not in request.files:
            error = "No file part"
        else:
            file = request.files['file']
            if file.filename == '':
                error = "No selected file"
            else:
                filename = file.filename
                save_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(save_path)
                text = extract_text_from_pdf(save_path)
                if text.strip():
                    summary_sentences = summarize_text(text)
                    summary = summary_sentences

                    # Generate TTS audio bytes
                    tts = gTTS(text=' '.join(summary), lang='en')
                    audio_fp = io.BytesIO()
                    tts.write_to_fp(audio_fp)
                    audio_fp.seek(0)
                    audio_data = audio_fp.read()

                    # Save to DB history
                    conn = get_db()
                    cursor = conn.cursor()
                    cursor.execute('''INSERT INTO history (user_id, pdf_filename, summary, audio)
                                      VALUES (?, ?, ?, ?)''',
                                   (session['user_id'], filename, '\n'.join(summary), audio_data))
                    conn.commit()
                else:
                    error = "No text could be extracted from the PDF."

    # Fetch user history
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, pdf_filename, summary FROM history WHERE user_id = ? ORDER BY id DESC", (session['user_id'],))
    history = cursor.fetchall()

    return render_template('index.html', summary=summary, error=error, history=history)

@app.route('/history_audio/<int:history_id>')
def history_audio(history_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT audio FROM history WHERE id = ? AND user_id = ?", (history_id, session['user_id']))
    row = cursor.fetchone()
    if row:
        return send_file(io.BytesIO(row['audio']), mimetype='audio/mpeg', as_attachment=False, download_name='summary.mp3')
    return "Audio not found", 404

if __name__ == '__main__':
    app.run(debug=True)
