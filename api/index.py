from flask import Flask, render_template, request, redirect, session, url_for, abort, jsonify, flash
from flask_bcrypt import Bcrypt
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from functools import wraps

app = Flask(__name__)
app.secret_key = "ucucgrcgcfucf"
bcrypt = Bcrypt(app)
uri = "mongodb+srv://shree:shree@cluster0.szpxxnd.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri, server_api=ServerApi('1'))
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client.test
users = db.users

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'invic_email' not in session:
            # User is not logged in, redirect to login page
            return redirect(url_for('login_register'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/user/login')
def login_register():
    return render_template('login_register.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    login_user = users.find_one({'email' : data['email']})
    if login_user:
        password = bcrypt.check_password_hash(login_user['password'], data['password'])
        if password:
            session['invic_email'] = str(data['email'])
            return jsonify({'message' : 'success'})
        else:
            return jsonify({'message' : 'Invalid Password'})
    return jsonify({'message' : 'Invalid Email'})

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed = bcrypt.generate_password_hash(data['password'])
    curr_user = users.find_one({'email' : data['email']})
    if curr_user:
        return jsonify({'message' : 'User already exists'})
    new_user = users.insert_one({'name' : data['name'], 'email' : data['email'], 'password' : hashed,'contact':data['contact']})
    if(new_user):
        return jsonify({'message' : 'success'})
    else: 
        return jsonify({'message' : 'failure'})

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")

@app.route('/activity')
def department():
    return render_template("activity.html")

@app.route('/doctor')
def doctor():
    return render_template("doctor.html")

if __name__ == '__main__':
    app.run(debug=True)

