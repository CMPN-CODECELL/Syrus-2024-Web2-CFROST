from flask import Flask, render_template, request, redirect, session, url_for, abort, jsonify, flash
from flask_bcrypt import Bcrypt
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from functools import wraps
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app,storage
import uuid
import sudoku
from flask_socketio import join_room, leave_room, send, SocketIO
import random
from string import ascii_uppercase
from flask import json
import ast
import functions

secret_word = None
word_set = None
to_display = None
tries = None
blanks = None

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

@app.route('/events')
def event():
    return render_template("event.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")

@app.route('/activity')
def department():
    return render_template("activity.html")

@app.route('/doctor')
def doctor():
    return render_template("doctor.html")

@app.route('/profile')
def profile():
    user = getuserdetails(session['invic_email'])
    session['contact'] = user['contact']
    return render_template("profile.html", username = session["name"], useremail = session['invic_email'], usercontact = session['contact'])

@app.route('/upload/details')
def upload_details():
    return render_template("upload_details.html")

@app.route('/upload/notes')
def upload_notes():
    return render_template("upload_notes.html")


@app.route("/meeting")
@login_required
def meeting():
    default_room_id = "1111"
    room_id = request.args.get("roomID", default_room_id)
    return render_template("meeting.html", username=session["name"], room_id=room_id)




# Chatting
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
    session["name"] = user["name"]
    if room is None or session["name"] is None or groupcode not in rooms:
        return redirect("/user/login")

    return render_template("chatroom.html", code=groupcode, messages=rooms[groupcode]["messages"])

#Games
@app.route('/game/sudoku/<string:level>')
def hello(level):
	# sudokuMatrix = sudokugen.genSudoku()
	# Create Medium Level Sudoku using Github Sudoku Library https://github.com/JoeKarlsson/Python-Sudoku-Generator-Solver
	sudokuMatrix = sudoku.main(level)
	return render_template('sudoku.html', sudokuMatrix=sudokuMatrix)


memory_users = {}

@app.route("/game/memory")
def index():
	return render_template("memory.html",username="shree"), 200

@app.route("/intro", methods = ["POST"])
def intro():
	post_obj = request.json
	post_obj["board"] = make_board(post_obj["level"])
	memory_users[post_obj["username"]] = post_obj
	return json.dumps(post_obj), 200

@app.route("/card", methods = ["POST"])
def card():
	post_obj = request.json
	choice = post_obj["choice"]
	choice = ast.literal_eval(choice) # converts the str to dict
	client_name = post_obj["username"]
	client = memory_users[client_name]
	client_board = client["board"]
	info = {}
	info["value"] = client_board[int(choice["bigBox"])][int(choice["smallerBox"])]
	info["id"] = choice["id"]
	return json.dumps(info), 200


def make_board(size):
	double = size * size
	pool = []
	pool_two = []
	board = []
	for i in range(int(double / 2)):
		pool.append(i)
		pool_two.append(i)
	larger_pool = []
	for i in range(double):
		if len(pool) != 0:
			random_draw = pool[random.randint(0, len(pool) - 1)]
			pool.remove(random_draw)
			larger_pool.append(random_draw)
		elif len(pool) == 1:
			random_draw = pool[0]
			pool.remove(random_draw)
			larger_pool.append(random_draw)
		if len(pool_two) != 0:
			random_draw = pool_two[random.randint(0, len(pool_two) - 1)]
			pool_two.remove(random_draw)
			larger_pool.append(random_draw)
		elif len(pool_two) == 1:
			random_draw = pool_two[0]
			pool_two.remove(random_draw)
			larger_pool.append(random_draw)

	for i in range(size):	
		mini_board = []
		for j in range(size):
			mini_board.append(larger_pool[0])
			larger_pool.remove(larger_pool[0])
		board.append(mini_board)	
	return board

@app.route('/game/hangman/<string:level>')
def game(level):
	global secret_word
	global word_set
	global to_display
	global tries
	global blanks	
	secret_word = functions.get_random_word("dictionary/text" + level + ".txt")
	word_set = "abcdefghijklmnopqrstuvwxyz"
	blanks = 0
	to_display = []
	for i,char in enumerate(secret_word):
		if char==" ":
			to_display.append(" ")
			
		else:
			to_display.append("_")
			blanks+=1

	tries = 0
	return render_template('hangman.html',to_display=to_display,word_set=word_set,tries="/static/hangman/img/hangman%d.png"%tries)


@app.route('/add_char',methods=["POST"])
def add_char():
	global secret_word
	global word_set
	global to_display
	global tries
	global blanks	

	letter = request.form["letter"]
	
	chance_lost = True
	for i,char in enumerate(secret_word):
		if char==letter:
			chance_lost = False
			to_display[i] = letter
			blanks-=1

	word_set = word_set.replace(letter,'')
	print("blanks",blanks)
	if chance_lost==True:
		tries += 1
		if tries==6:
			return redirect('/game_lost')

	if blanks==0:
		return redirect('/game_won')

	return render_template('hangman.html',to_display=to_display,word_set=word_set,tries="/static/hangman/img/hangman%d.png"%tries)

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
    
def upload_pdf_to_storage(pdf_file):
    if pdf_file:
        # Get the PDF filename
        filename = f"{uuid.uuid4()}.pdf"
        # Initialize Firebase Storage bucket
        bucket = storage.bucket()
        # Create a blob object in the storage bucket
        blob = bucket.blob(f'Pdfs/{filename}')
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

@app.route('/update_game_data', methods=['POST'])
def update_game_data():
    data = request.get_json()
    if data:
        # Get the game data from the request
        stats = data.get('stats')
        game = data.get('game')
        # Get the user from the request
        user = session.get('invic_email')
        # Update the user in the database
        user = users.find_one({'email': user})
        if "games" in user:
            user["games"][game].append(stats)
            users.update_one({'email': user['email']}, {'$set': {'games': user['games']}})
        else:
            user["games"] = {game: [stats]}
            users.update_one({'email': user['email']}, {'$set': {'games': user['games']}})
        return jsonify({'message': 'success'})
    return jsonify({'message': 'failure'})

if __name__ == '__main__':
    app.run(debug=True)

