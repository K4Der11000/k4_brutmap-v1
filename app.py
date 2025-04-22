from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import threading
import time
import os

app = Flask(__name__)
app.secret_key = "secret_key"

# Default credentials
USERNAME = "admin"
PASSWORD = "kader11000"

# Global states
brute_thread = None
pause_event = threading.Event()
stop_event = threading.Event()
current_guess = None
found_password = None
target_url = ""
captch_enabled = False
stop_on_keyword = None

# Load default wordlist
def load_wordlist():
    with open("static/wordlist.txt", "r") as f:
        return [line.strip() for line in f if line.strip()]

wordlist = load_wordlist()

# Brute force logic
def brute_force():
    global current_guess, found_password
    for word in wordlist:
        if stop_event.is_set():
            break
        while pause_event.is_set():
            time.sleep(0.5)
        current_guess = word
        print(f"Trying: {word}")
        time.sleep(1)  # Simulate guessing delay
        if stop_on_keyword and stop_on_keyword in word:
            found_password = word
            stop_event.set()
            break

@app.route('/')
def index():
    if 'logged_in' in session:
        return redirect('/dashboard')
    return render_template("login.html")

@app.route('/auth', methods=['POST'])
def auth():
    username = request.form['username']
    password = request.form['password']
    if username == USERNAME and password == PASSWORD:
        session['logged_in'] = True
        return redirect('/dashboard')
    return "Unauthorized"

@app.route('/dashboard')
def dashboard():
    if 'logged_in' not in session:
        return redirect('/')
    return render_template("dashboard.html",
                           current_guess=current_guess,
                           found_password=found_password,
                           target_url=target_url)

@app.route('/start')
def start():
    global brute_thread, stop_event, pause_event, found_password
    if 'logged_in' not in session:
        return redirect('/')
    if brute_thread and brute_thread.is_alive():
        return redirect('/dashboard')
    found_password = None
    stop_event.clear()
    pause_event.clear()
    brute_thread = threading.Thread(target=brute_force)
    brute_thread.start()
    return redirect('/dashboard')

@app.route('/pause')
def pause():
    pause_event.set()
    return redirect('/dashboard')

@app.route('/resume')
def resume():
    pause_event.clear()
    return redirect('/dashboard')

@app.route('/stop')
def stop():
    stop_event.set()
    return redirect('/dashboard')

@app.route('/save_target', methods=['POST'])
def save_target():
    global target_url
    target_url = request.form.get("target_url")
    return redirect('/dashboard')

@app.route('/upload_wordlist', methods=['POST'])
def upload_wordlist():
    global wordlist
    file = request.files['file']
    if file and file.filename.endswith(".txt"):
        filepath = os.path.join("static", "wordlist.txt")
        file.save(filepath)
        wordlist = load_wordlist()
    return redirect('/dashboard')

@app.route('/set_stop_keyword', methods=['POST'])
def set_stop_keyword():
    global stop_on_keyword
    stop_on_keyword = request.form.get("keyword")
    return redirect('/dashboard')

@app.route('/toggle_captcha', methods=['GET'])
def toggle_captcha():
    global captch_enabled
    captch_enabled = not captch_enabled
    return redirect('/dashboard')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
