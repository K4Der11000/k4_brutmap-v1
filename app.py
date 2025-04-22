from flask import Flask, render_template, request, redirect, session, send_file
import threading
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Default credentials
USERNAME = 'admin'
PASSWORD = 'kader11000'

# Global state
attack_running = False
pause_attack = False
found_password = None
stop_keyword = None
password_list = []

# Load initial wordlist
def load_wordlist():
    global password_list
    try:
        with open('wordlist.txt', 'r') as f:
            password_list = [line.strip() for line in f if line.strip()]
    except:
        password_list = []

load_wordlist()

# Save wordlist after editing
def save_wordlist():
    with open('wordlist.txt', 'w') as f:
        for pw in password_list:
            f.write(pw + '\n')

# Attack function
def brute_force():
    global attack_running, found_password, pause_attack
    attack_running = True
    with open('logs.txt', 'a') as log:
        for password in password_list:
            while pause_attack:
                time.sleep(0.5)
            if not attack_running:
                break
            log.write(f"Trying: {password}\n")
            log.flush()
            if stop_keyword and stop_keyword in password:
                found_password = password
                attack_running = False
                break
            time.sleep(0.3)
    attack_running = False

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == USERNAME and request.form['password'] == PASSWORD:
            session['logged_in'] = True
            return redirect('/dashboard')
    return render_template('login.html')

@app.route('/dashboard', methods=['GET'])
def dashboard():
    if not session.get('logged_in'):
        return redirect('/')
    return render_template('dashboard.html', passwords=password_list, found_password=found_password)

@app.route('/start_attack', methods=['POST'])
def start_attack():
    global stop_keyword
    if not session.get('logged_in'):
        return redirect('/')
    stop_keyword = request.form.get('stop_keyword')
    if not attack_running:
        threading.Thread(target=brute_force).start()
    return redirect('/dashboard')

@app.route('/pause_attack', methods=['POST'])
def pause():
    global pause_attack
    pause_attack = True
    return redirect('/dashboard')

@app.route('/resume_attack', methods=['POST'])
def resume():
    global pause_attack
    pause_attack = False
    return redirect('/dashboard')

@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    return redirect('/')

@app.route('/upload_wordlist', methods=['POST'])
def upload_wordlist():
    file = request.files['file']
    if file:
        content = file.read().decode('utf-8')
        with open('wordlist.txt', 'w') as f:
            f.write(content)
        load_wordlist()
    return redirect('/dashboard')

@app.route('/update_wordlist', methods=['POST'])
def update_wordlist():
    global password_list
    password_list = request.form.getlist('words')
    save_wordlist()
    return redirect('/dashboard')

if __name__ == '__main__':
    app.run(debug=True)
