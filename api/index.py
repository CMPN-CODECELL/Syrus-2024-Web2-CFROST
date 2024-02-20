from flask import Flask, render_template, request, redirect, session, url_for, abort, jsonify, flash
from flask_bcrypt import Bcrypt
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from functools import wraps
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app,storage
import uuid

from flask_socketio import join_room, leave_room, send, SocketIO
import random
from string import ascii_uppercase

app = Flask(__name__)
app.secret_key = "ucucgrcgcfucf"

socketio = SocketIO(app)

cred = credentials.Certificate("./config.json")
firebase_admin.initialize_app(cred,{"storageBucket": "https://syrus24-7aecd.appspot.com/"})

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
chatroom = db.messages

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





rooms = {"AAAA": {"members": 0, "messages": []}}

# Chat Room
@app.route("/chat/room/<string:code>")
@login_required
def room(code):
    if code not in rooms:
        rooms[code] = {"members": 0, "messages": []}
    else:
        curr_room = chatroom.find_one({'code' : code})
        if curr_room is None:
            chatroom.insert_one({'code' : code, 'members' : 0, 'messages' : []})
            curr_room = chatroom.find_one({'code' : code})
        rooms[code]["members"] = curr_room['members']
        rooms[code]["messages"] = curr_room['messages']
    groupcode = code
    session["code"] = code
    user = getuserdetails(session['invic_email'])
    print(user)
    session["name"] = user["name"]
    if room is None or session["name"] is None or groupcode not in rooms:
        return redirect("/user/login")

    return render_template("chatroom.html", code=groupcode, messages=rooms[groupcode]["messages"])

@socketio.on("message")
def message(data):
    room = session["code"]
    if room not in rooms:
        return 
    user = getuserdetails(session['invic_email'])
    content = {
        "name": session["name"],
        "message": data["data"]
    }
    send(content, to=room)
    rooms[room]["messages"].append(content)
    chatroom.update_one({'code' : room}, {'$set' : {'members' : rooms[room]["members"], 'messages' : rooms[room]["messages"]}})

@socketio.on("connect")
def connect(auth):
    room = session["code"]
    name = session["name"]
    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return
    
    join_room(room)
    send({"name": name, "message": "is online now"}, to=room)
    rooms[room]["members"] += 1

@socketio.on("disconnect")
def disconnect():
    room = session["room"]
    name = session["name"]
    leave_room(room)

    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <= 0:
            del rooms[room]
    
    send({"name": name, "message": "has left the room"}, to=room)
    print(f"{name} has left the room {room}")


def getuserdetails(email):
    user = users.find_one({'email' : email})
    return user




def upload_image_to_storage(image):
    if image:
        # Get the image filename
        filename = f"{uuid.uuid4()}.jpg"
        # Initialize Firebase Storage bucket
        bucket = storage.bucket()
        # Create a blob object in the storage bucket
        blob = bucket.blob(f'Images/{filename}')
        # Upload the image file to Firebase Storage
        blob.upload_from_file(image)
        # Get the URL for the uploaded image
        blob.make_public()
        image_url = blob.public_url
        return image_url
    
def upload_pdf_to_storage(pdf_file, project_id):
    if pdf_file:
        # Get the PDF filename
        filename = f"{uuid.uuid4()}.pdf"
        # Initialize Firebase Storage bucket
        bucket = storage.bucket()
        # Create a blob object in the storage bucket
        blob = bucket.blob(f'projects/{project_id}/{filename}')
        # Set content type for PDF
        blob.content_type = 'application/pdf'
        # Upload the PDF file to Firebase Storage
        blob.upload_from_file(pdf_file, content_type='application/pdf')
        # Get the URL for the uploaded PDF
        blob.make_public()
        pdf_url = blob.public_url
        return pdf_url
    
def delete_image_from_storage(image_url):
    if image_url:
        # Extract the path from the URL
        path = image_url.split('.com/')[-1]
        # Initialize Firebase Storage bucket
        bucket = storage.bucket()
        # Get the blob reference
        blob = bucket.blob(path)
        # Delete the blob
        blob.delete()
    
def delete_pdf_from_storage(pdf_url):
    if pdf_url:
        # Extract the path from the URL
        path = pdf_url.split('.com/')[-1]
        # Initialize Firebase Storage bucket
        bucket = storage.bucket()
        # Get the blob reference
        blob = bucket.blob(path)
        # Delete the blob
        blob.delete()

if __name__ == '__main__':
    app.run(debug=True)

