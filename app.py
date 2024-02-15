from flask import (
    Flask, render_template, request, redirect, url_for, flash, session
)
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from functools import wraps
from werkzeug.utils import secure_filename
from flask_cors import CORS
from SecureEncrypt import AESCipher
import MySQLdb.cursors, os, re, secrets, base64, imghdr

app = Flask(__name__)
CORS(app)
bcrypt = Bcrypt(app)

# Configure app secret key and MySQL connection
app.secret_key = os.environ.get('FLASK_SECRET_KEY')
app.config['MYSQL_HOST'] = os.environ.get('MYSQL_HOST')
app.config['MYSQL_USER'] = os.environ.get('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.environ.get('MYSQL_DB')

# Initialize MySQL
mysql = MySQL(app)

# Configure upload folder and allowed file extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Authorization decorator
def authorize(f):
    @wraps(f)
    def decorated_function(*args, **kws):
        if 'loggedin' not in session or not session['loggedin']:
            return redirect(url_for('login'))
        return f(*args, **kws)
    return decorated_function

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Handle form submission
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        email = request.form.get('email')

        # Validate form inputs
        if not (username and password and email):
            flash('Please fill out the form!', 'alert alert-danger')
            return redirect(url_for('register'))
        if password != confirm_password:
            flash('Passwords do not match!', 'alert alert-danger')
            return redirect(url_for('register'))
        if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address!', 'alert alert-danger')
            return redirect(url_for('register'))

        # Check if user already exists
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s OR username = %s', (email, username))
        account = cursor.fetchone()
        if account:
            flash('Account already exists!', 'alert alert-danger')
            return redirect(url_for('register'))

        # Register user
        image_key = secrets.token_hex(16)
        hash_password = bcrypt.generate_password_hash(password).decode('utf-8')
        cursor.execute('INSERT INTO users VALUES (NULL, %s, %s, %s, %s)', (username, hash_password, email, image_key))
        mysql.connection.commit()
        flash('You have successfully registered!', 'alert alert-success')
        return redirect(url_for('login'))

    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        data = cursor.fetchone()

        if data and bcrypt.check_password_hash(data['password'], password):
            session['loggedin'] = True
            session['id'] = data['user_id']
            session['username'] = data['username']
            session['email'] = data['email']
            session['image_key'] = data['image_key']
            flash('Logged in successfully!', 'alert alert-success')
            return redirect(url_for('home'))
        flash('Incorrect email or password!', 'alert alert-danger')

    return render_template('login.html')

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Home route
@app.route('/', methods=['GET'])
@authorize
def home():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM images WHERE user_id = %s', (session['id'],))
    images = cursor.fetchall() or []

    decrypted_images = []
    for image in images:
        cipher = AESCipher(session['image_key'])
        decrypted_image = cipher.decrypt(image['image_data'])
        decrypted_images.append({
            "image_id": image['image_id'],
            "image_data": decrypted_image,
            "image_name": image['filename'],
            "extension": image['filename'].split('.')[-1]
        })

    return render_template('index.html', username=session['username'], images=decrypted_images)

# Upload route
@app.route('/upload', methods=['POST'])
@authorize
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('File type not allowed', 'alert alert-danger')
            return redirect(url_for('home'))
        file = request.files['file']
        
        if imghdr.what(file) not in ALLOWED_EXTENSIONS:
            flash('File type not allowed', 'alert alert-danger')
            return redirect(url_for('home'))
        
        if file.filename == '' or not allowed_file(file.filename):
            flash('File type not allowed', 'alert alert-danger')
            return redirect(url_for('home'))

        filename = secure_filename(file.filename)
        image_base64 = base64.b64encode(file.read()).decode('utf-8')
        cipher = AESCipher(session['image_key'])
        encrypted_image = cipher.encrypt(image_base64)

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO images VALUES (NULL, %s, %s, %s)', (session['id'], filename, encrypted_image))
        mysql.connection.commit()
        flash('File uploaded successfully', 'alert alert-success')
        return redirect(url_for('home'))

    flash('File type not allowed', 'alert alert-danger')
    return redirect(url_for('home'))

# Delete file route
@app.route('/delete', methods=['POST'])
@authorize
def delete_file():
    if request.method == 'POST':
        image_id = request.form.get('image_id')
        if not image_id:
            flash('Please provide an image to delete', 'alert alert-danger')
            return redirect(url_for('home'))

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('DELETE FROM images WHERE image_id = %s AND user_id = %s', (image_id, session['id']))
        mysql.connection.commit()

        if cursor.rowcount == 0:
            flash('Failed to delete the image. Please try again later.', 'alert alert-danger')
        else:
            flash('File deleted successfully', 'alert alert-success')

    return redirect(url_for('home'))

if __name__ == '__main__':
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.run(host='0.0.0.0', port=6969)
    # app.run(host='0.0.0.0', port=6969, debug=True)
