from flask import Flask, jsonify, request, send_from_directory, redirect, url_for, render_template, flash, session, abort
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///employees.db'
app.secret_key = 'supersecretkey'

db = SQLAlchemy(app)

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    position = db.Column(db.String(120), nullable=False)

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(120), nullable=False)
    upload_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    employee = db.relationship('Employee', backref=db.backref('files', lazy=True))

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
    employees = Employee.query.all()
    return render_template('index.html', employees=employees)

@app.route('/employee/<int:employee_id>')
@login_required
def employee_details(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    return render_template('employee.html', employee=employee)

@app.route('/add_employee', methods=['GET', 'POST'])
@login_required
def add_employee():
    if request.method == 'POST':
        name = request.form['name']
        position = request.form['position']
        new_employee = Employee(name=name, position=position)
        db.session.add(new_employee)
        db.session.commit()
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], str(new_employee.id)), exist_ok=True)
        flash('Employee added successfully')
        return redirect(url_for('index'))
    return render_template('add_employee.html')
import os

NETWORK_LOCATION = r"\\network\shared\folder"  # or "/mnt/network/folder" on Linux

def check_permissions():
    # Check if the directory exists and is writable
    if not os.path.exists(NETWORK_LOCATION):
        raise Exception("Network location does not exist")
    if not os.access(NETWORK_LOCATION, os.W_OK):
        raise Exception("No write permissions for the network location")

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    try:
        # Check permissions before saving
        check_permissions()

        file_path = os.path.join(NETWORK_LOCATION, file.filename)
        file.save(file_path)
        return jsonify({"message": "File uploaded successfully", "path": file_path}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
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
        upload_date = datetime.utcnow()
        new_file = File(filename=filename, upload_date=upload_date, employee_id=employee_id)
        db.session.add(new_file)
        db.session.commit()
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
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
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
    with app.app_context():
        db.create_all()
    app.run(debug=True)