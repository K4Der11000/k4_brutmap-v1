from flask import Flask, render_template, request, redirect, session, send_file import os import threading import time

app = Flask(name) app.secret_key = 'your_secret_key'

Global Variables

found_password = None is_running = False pause_flag = False password_list = [] current_guess = "" target_url = "https://example.com" TARGET_FILE = "last_target.txt"

Load default wordlist

WORDLIST_FILE = "static/wordlist.txt" if os.path.exists(WORDLIST_FILE): with open(WORDLIST_FILE, 'r') as f: password_list = [line.strip() for line in f.readlines() if line.strip()]

Load last target URL if available

if os.path.exists(TARGET_FILE): with open(TARGET_FILE, 'r') as f: target_url = f.read().strip()

Brute Force Function

def brute_force(): global found_password, is_running, pause_flag, current_guess for password in password_list: while pause_flag: time.sleep(1) if not is_running: break current_guess = password # Simulate request time.sleep(0.5) if "success" in password: found_password = password is_running = False break

@app.route('/') def login(): return render_template('login.html')

@app.route('/auth', methods=['POST']) def auth(): username = request.form['username'] password = request.form['password'] if username == 'admin' and password == 'kader11000': session['logged_in'] = True return redirect('/dashboard') return redirect('/')

@app.route('/logout') def logout(): session.clear() return redirect('/')

@app.route('/dashboard') def dashboard(): if not session.get('logged_in'): return redirect('/') session.setdefault('target_url', target_url) return render_template( 'dashboard.html', passwords=[],  # hide passwords from view found_password=found_password, current_guess=current_guess, target_url=session['target_url'] )

@app.route('/start') def start(): global is_running, pause_flag if not is_running: is_running = True pause_flag = False threading.Thread(target=brute_force).start() return redirect('/dashboard')

@app.route('/pause') def pause(): global pause_flag pause_flag = True return redirect('/dashboard')

@app.route('/resume') def resume(): global pause_flag pause_flag = False return redirect('/dashboard')

@app.route('/stop') def stop(): global is_running is_running = False return redirect('/dashboard')

@app.route('/save_target', methods=['POST']) def save_target(): url = request.form.get('target_url', 'https://example.com') session['target_url'] = url with open(TARGET_FILE, 'w') as f: f.write(url) return '', 204

@app.route('/upload_wordlist', methods=['POST']) def upload_wordlist(): global password_list file = request.files['file'] if file: lines = file.read().decode().splitlines() password_list = [line.strip() for line in lines if line.strip()] with open(WORDLIST_FILE, 'w') as f: f.write('\n'.join(password_list)) return redirect('/dashboard')

if name == 'main': app.run(debug=True)

