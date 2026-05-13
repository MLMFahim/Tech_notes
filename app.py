import json
import os
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
ADMIN_PASS = os.environ.get('MY_APP_PASS', 'default_admin')
USER_DATA = {"admin": ADMIN_PASS}
DB_FILE = 'notes.json'
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def load_notes():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_notes(notes):
    with open(DB_FILE, 'w') as f:
        json.dump(notes, f)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u, p = request.form.get('username'), request.form.get('password')
        if u in USER_DATA and USER_DATA[u] == p:
            return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    notes = load_notes()
    # 1. Get the sort type from the button click (?sort=...)
    sort_type = request.args.get('sort', 'date') 

    if request.method == 'POST':
        cat = request.form.get('category')
        title = request.form.get('title')
        content = request.form.get('details') 
        logic_code = request.form.get('code') 
        
        icons = {"PLC & Automation": "🤖", "Python Development": "🐍", "Electrical Eng": "⚡"}
        icon = icons.get(cat, "📝")
        timestamp_str = datetime.now().strftime("%d %b %Y, %H:%M")
        # Hidden ISO key for perfect calendar sorting
        sort_key = datetime.now().isoformat()
        
        if title and content:
            # We store the sort_key at index 5
            notes[title] = [icon, [{"text": content, "time": timestamp_str, "images": []}], timestamp_str, logic_code, cat, sort_key]
            save_notes(notes)
            return redirect(url_for('home'))

    # 2. Sorting Logic
    items = list(notes.items())
    if sort_type == 'title':
        # Sort A-Z by the Title
        items.sort(key=lambda x: x[0].lower())
    else: 
        # Sort by the hidden ISO date (Newest First)
        items.sort(key=lambda x: x[1][5] if len(x[1]) > 5 else "", reverse=True)
            
    return render_template('index.html', notes=items, current_sort=sort_type)

@app.route('/details/<title>', methods=['GET', 'POST'])
def details(title):
    notes = load_notes()
    if title not in notes:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        subnote_text = request.form.get('subnote')
        files = request.files.getlist('images')
        image_paths = []

        for file in files:
            if file and file.filename != '':
                filename = str(uuid.uuid4()) + "_" + secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_paths.append(filename)

        if subnote_text or image_paths:
            timestamp = datetime.now().strftime("%d %b %Y, %H:%M")
            notes[title][1].append({"text": subnote_text, "time": timestamp, "images": image_paths})
            save_notes(notes)
            return redirect(url_for('details', title=title))
            
    data = notes[title]
    return render_template('details.html', title=title, icon=data[0], contents=data[1], logic=data[3])

@app.route('/edit_note/<title>', methods=['GET','POST'])
def edit_note(title):
    notes = load_notes()
    if title not in notes: return redirect(url_for('home'))

    if request.method == 'POST':
        new_title = request.form.get('title')
        content = request.form.get('content')
        logic_code = request.form.get('logic_code')
        
        data = notes.pop(title)
        data[1][0]['text'] = content
        data[3] = logic_code
        notes[new_title] = data
        save_notes(notes)
        return redirect(url_for('home'))

    return render_template('edit.html', title=title, content=notes[title][1][0]['text'], logic=notes[title][3])

@app.route('/delete_main/<title>')
def delete_main(title):
    notes = load_notes()
    if title in notes:
        del notes[title]
        save_notes(notes)
    return redirect(url_for('home'))

@app.route('/edit_subnote/<title>/<int:index>', methods=['POST'])
def edit_subnote(title, index):
    notes = load_notes()
    if title in notes:
        notes[title][1][index]['text'] = request.form.get('new_text')
        save_notes(notes)
    return redirect(url_for('details', title=title))

@app.route('/delete_subnote/<title>/<int:index>')
def delete_subnote(title, index):
    notes = load_notes()
    if title in notes:
        notes[title][1].pop(index)
        save_notes(notes)
    return redirect(url_for('details', title=title))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
