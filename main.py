from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory, session, abort
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'supersecretkey'

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Login credentials
USERNAME = 'admin'
PASSWORD = 'mypassword123'

# HTML pages
login_page = '''
<h2>Login to Upload Files</h2>
<form method="post">
  <input type="text" name="username" placeholder="Username" required><br><br>
  <input type="password" name="password" placeholder="Password" required><br><br>
  <button type="submit">Login</button>
</form>
'''

upload_page = '''
<h2>Welcome, {{ session['username'] }}</h2>

<form method="post" enctype="multipart/form-data">
  <input type="file" name="file" required>
  <button type="submit">Upload</button>
</form>

<ul>
{% for file in files %}
  <li>
    <a href="{{ url_for('download_file', filename=file) }}" target="_blank">{{ file }}</a>
    <form action="{{ url_for('delete_file', filename=file) }}" method="post" style="display:inline;">
      <button type="submit" onclick="return confirm('Delete this file?')">Delete</button>
    </form>
  </li>
{% else %}
  <li>No files uploaded yet.</li>
{% endfor %}
</ul>

<p><a href="{{ url_for('logout') }}">Logout</a></p>
'''

public_files_page = '''
<h2>Public File Viewer</h2>
<ul>
{% for file in files %}
  <li><a href="{{ url_for('download_file', filename=file) }}" target="_blank">{{ file }}</a></li>
{% else %}
  <li>No files available.</li>
{% endfor %}
</ul>
'''

# Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == USERNAME and request.form['password'] == PASSWORD:
            session['username'] = request.form['username']
            return redirect(url_for('upload'))
        return 'Invalid credentials', 401
    
    return render_template_string(login_page)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            return redirect(url_for('upload'))
    
    files = os.listdir(UPLOAD_FOLDER)
    return render_template_string(upload_page, files=files)

@app.route('/files/<filename>')
def download_file(filename):
    filename = secure_filename(filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(filepath):
        abort(404)
    
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(filepath):
        os.remove(filepath)
    return redirect(url_for('upload'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/')
def home():
    return redirect(url_for('upload'))

@app.route('/files')
def public_files():
    files = os.listdir(UPLOAD_FOLDER)
    return render_template_string(public_files_page, files=files)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
