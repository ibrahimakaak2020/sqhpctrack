from flask import Flask, request, send_from_directory, redirect, url_for, render_template, flash, session, abort
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
import json

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.secret_key = 'supersecretkey'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

users = {
    "admin": generate_password_hash("adminpass")
}

employees = {}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrap

@app.route('/')
@login_required
def index():
    return render_template('index.html', employees=employees)

@app.route('/employee/<int:employee_id>')
@login_required
def employee_details(employee_id):
    employee = employees.get(employee_id)
    if not employee:
        abort(404)
    files = os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], str(employee_id)))
    return render_template('employee.html', employee=employee, files=files)

@app.route('/add_employee', methods=['GET', 'POST'])
@login_required
def add_employee():
    if request.method == 'POST':
        employee_id = len(employees) + 1
        name = request.form['name']
        position = request.form['position']
        employees[employee_id] = {
            'id': employee_id,
            'name': name,
            'position': position
        }
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], str(employee_id)), exist_ok=True)
        flash('Employee added successfully')
        return redirect(url_for('index'))
    return render_template('add_employee.html')

@app.route('/upload/<int:employee_id>', methods=['POST'])
@login_required
def upload_file(employee_id):
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], str(employee_id), filename))
        flash('File successfully uploaded')
        return redirect(url_for('employee_details', employee_id=employee_id))
    else:
        flash('File type not allowed')
        return redirect(request.url)

@app.route('/uploads/<int:employee_id>/<filename>')
@login_required
def uploaded_file(employee_id, filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], str(employee_id)), filename)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and check_password_hash(users[username], password):
            session['username'] = username
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)