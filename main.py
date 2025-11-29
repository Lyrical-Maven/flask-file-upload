from flask import Flask, render_template_string, request, redirect, url_for, send_from_directory, session
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "secret123"

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# --------------------- HOME PAGE (public) ---------------------
@app.route('/')
def home():
    files = os.listdir(UPLOAD_FOLDER)
    return render_template_string("""
        <h2>Uploaded Files</h2>
        <ul>
        {% for f in files %}
            <li><a href="/files/{{ f }}" target="_blank">{{ f }}</a></li>
        {% else %}
            <li>No files uploaded yet.</li>
        {% endfor %}
        </ul>

        <br><br>
        <a href="/login">
            <button>Upload Files (Login Required)</button>
        </a>
    """, files=files)


# --------------------- FILE DOWNLOAD ---------------------
@app.route('/files/<filename>')
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


# --------------------- LOGIN ---------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'admin123':
            session['logged_in'] = True
            return redirect('/upload')
        return "Invalid login"
    
    return render_template_string("""
        <h2>Login to Upload Files</h2>
        <form method="post">
            <input name="username" placeholder="Username"><br><br>
            <input name="password" type="password" placeholder="Password"><br><br>
            <button type="submit">Login</button>
        </form>
    """)


# --------------------- UPLOAD PAGE (requires login) ---------------------
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if not session.get("logged_in"):
        return redirect('/login')

    if request.method == 'POST':
        file = request.files['file']
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        return redirect('/')

    return render_template_string("""
        <h2>Upload File</h2>
        <form method="post" enctype="multipart/form-data">
            <input type="file" name="file">
            <button type="submit">Upload</button>
        </form>

        <br><a href="/">Back</a>
    """)


# --------------------- RUN ---------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
