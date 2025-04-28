from flask import g, Flask, request, jsonify
from flask_sock import Sock
from flask_bcrypt import Bcrypt

import database_helper 
import json
from uuid import uuid4

from threading import Lock

app = Flask(__name__)
bcrypt = Bcrypt(app)

X = 5

sock = Sock(app)
connections = set()

login_email = {} # Used for storing loging account to check the repetition

@app.route('/')
def index(): # Returns the static file "client.html" when accessing the root route ("/").
    return app.send_static_file('client.html')

def check_empty(*args): #check if any argument is empty
    for arg in args:
        if not arg:
            return True
    return False

@app.route("/sign_in", methods=['POST'])
def sign_in(): # Handles user sign-in request, verifies credentials, generates token upon successful authentication, and manages user sessions.
    username = request.json['email']
    password = request.json['password']
    user_data = database_helper.get_user_by_email(username)
    if not user_data: # if the user not exists
        return jsonify({'message': 'user not found'}), 404
    pw_hash = database_helper.check_password(username)
    login = bcrypt.check_password_hash(pw_hash, password)
    if login: # if the password is correct
        if username in login_email.keys() : # if user already logged in
            old_sock = login_email[username]
            if old_sock in connections:
                old_sock.send("close connection") # close the old connection
                connections.remove(old_sock) # remove the old connection socket

        token = str(uuid4()) # generate token
        database_helper.add_login_user(username, token)
        response = jsonify({
            'message': 'Signed in successfully.',
            'data': token
        })
        response.headers['Authorization'] = f'Bearer {token}'
        return response, 201
    else: 
        return jsonify({'message': 'incorrect password.'}), 401

import re

def is_valid_email(email): # check if the email format is valid
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    match = re.match(pattern, email)
    return bool(match)

@app.route('/sign_up',methods = ['POST'])
def sign_up(): # Handles user sign-up request, validates form data, checks email format, password length, and existing user, then securely hashes the password and adds the user to the database.
    email = request.json['email']
    password = request.json['password']
    firstname = request.json['firstname']
    familyname = request.json['familyname']
    gender = request.json['gender']
    city = request.json['city']
    country = request.json['country']
    if check_empty(email, password, firstname, familyname, gender, city, country): 
        return jsonify({'message': 'form data missing', 'data': '-'}), 400
    if not is_valid_email(email): 
        return jsonify({'message': "email format not correct", 'data': '-'}), 400
    if len(password) < X: 
        return jsonify({'message': "Passwords must be at least " + str(X) + " characters long", 'data': '-'}), 400
    if database_helper.check_user_exist(email): 
        return jsonify({'message': 'user already exists', 'data': '-'}), 409
    pw_hash = bcrypt.generate_password_hash(password)
    user = database_helper.add_user(email, pw_hash, firstname, familyname, gender, city, country)
    if user:
        return jsonify({'message': 'Signed up successfully.', 'data': '-'}), 201
    else:
        return jsonify({'message': 'Signed up failed.', 'data': '-'}), 500


@app.route('/sign_out', methods = ['DELETE'])
def sign_out(): # Handles user sign-out request by checking token validity, retrieving user email associated with the token, removing the token from the database, and clearing the user's session.
    authorization_header = request.headers.get('Authorization')
    if authorization_header:
        token = authorization_header.replace('Bearer ', '')
    else:
        return jsonify({'message': 'incorrect token', 'data': '-'}), 401
    if not database_helper.check_token(token):
        return jsonify({'message': "incorrect token"}), 401
    email = database_helper.get_email_by_token(token)
    database_helper.remove_login_user(token)
    del login_email[email]
    return jsonify({'message': "Signed out successfully."}), 200

@app.route('/change_password',methods = ['PUT'])
def change_password(): # Handles user password change request by verifying token validity, checking old password correctness, ensuring the new password meets length requirements, and updating the password in the database.
    authorization_header = request.headers.get('Authorization')
    if authorization_header:
        token = authorization_header.replace('Bearer ', '')
    else:
        return jsonify({'success': False, 'message': 'incorrect token', 'data': '-'}), 401
    
    oldpassword = request.json['old_password']
    newpassword = request.json['new_password']
    user_data = database_helper.get_login_user_by_token(token)
    if not database_helper.check_token(token):
        return jsonify({'success': False, 'message': 'incorrect token'}), 401
    pw_hash = database_helper.check_password(user_data[0])
    check_pw = bcrypt.check_password_hash(pw_hash, oldpassword)
    if not check_pw: # if password is not correct
        print("change password fail")
        return jsonify({'success': False, 'message': 'incorrect oldpassword'}), 409
    if newpassword is not None:
        if len(newpassword) < X:
            return jsonify({'success': False, 'message': 'invalid newpassword'}), 400
        newpw_hash = bcrypt.generate_password_hash(newpassword)
        database_helper.change_password(token, newpw_hash)
        return jsonify({'message': 'Changed password successfully!'}), 201
    else:
        return jsonify({'success': False, 'message': 'invalid newpassword'}), 400

def get_email_by_token(token):# Returns the email associated with the provided token if it exists in the database; otherwise, returns 0.
    user_data = database_helper.get_login_user_by_token(token)
    if user_data:
        return user_data[0] #email
    else:
        return 0

@app.route('/get_user_data_by_token', methods = ['GET'])
def get_user_data_by_token():# Handles a request to retrieve user data using a token for authentication, verifies the token's validity, retrieves the user's email associated with the token, and fetches the user's data from the database based on the email.
    authorization_header = request.headers.get('Authorization')
    if authorization_header:
        token = authorization_header.replace('Bearer ', '')
    else:
        return jsonify({'message': 'incorrect token', 'data': '-'}), 401
    if not database_helper.check_token(token):
        return jsonify({'message': 'incorrect token', 'data': '-'}), 401
    email = get_email_by_token(token)
    user_data = database_helper.get_user_by_email(email)
    if user_data:
        new_data = {
            "email": user_data[0], 
            "firstname": user_data[1],
            "familyname": user_data[2],
            "gender": user_data[3],
            "city": user_data[4],
            "country": user_data[5]
        }
        return jsonify({'message' : 'Got data successfully', 'data': new_data}), 200
    else:
        return jsonify({'message' : 'email not found'}), 500

@app.route('/get_user_data_by_email/<email>', methods = ['GET'])
def get_user_data_by_email(email):# Handles a request to retrieve user data using the user's email as a parameter, verifies the token's validity, and fetches the user's data from the database based on the provided email.
    authorization_header = request.headers.get('Authorization')
    if authorization_header:
        token = authorization_header.replace('Bearer ', '')
    else:
        return jsonify({'success': False, 'message': 'incorrect token', 'data': '-'})
    if not database_helper.check_token(token):
        return jsonify({'success' : False, 'message' : 'incorrect token'})
    user_data = database_helper.get_user_by_email(email)
    if user_data:
        new_data = {
            "email": user_data[0], 
            "firstname": user_data[1],
            "familyname": user_data[2],
            "gender": user_data[3],
            "city": user_data[4],
            "country": user_data[5]
        }
        return jsonify({'message' : 'Got data successfully', 'data': new_data}), 200
    else:
        return jsonify({'message' : 'email not found'}), 404

@app.route('/get_user_messages_by_token', methods = ['GET'])
def get_user_messages_by_token(): # Handles a request to retrieve messages associated with a user using a token for authentication, verifies the token's validity, retrieves the user's email associated with the token, and fetches the user's messages from the database.
    authorization_header = request.headers.get('Authorization')
    if authorization_header:
        token = authorization_header.replace('Bearer ', '')
    else:
        return jsonify({'message': 'incorrect token', 'data': '-'}), 401
    if not database_helper.check_token(token):
        return jsonify({'message' : 'incorrect token'}), 401
    email = database_helper.get_login_user_by_token(token)[0]
    user_msg = database_helper.get_user_messages(email)
    return jsonify({'message' : 'Got messages successfully', 'data': user_msg}), 200

@app.route('/get_user_messages_by_email/<email>', methods = ['GET'])
def get_user_messages_by_email(email): # Handles a request to retrieve messages associated with a user using the user's email as a parameter, verifies the token's validity, and fetches the user's messages from the database based on the provided email.
    authorization_header = request.headers.get('Authorization')
    if authorization_header:
        token = authorization_header.replace('Bearer ', '')
    else:
        return jsonify({'message': 'incorrect token'}), 401
    if not database_helper.check_token(token):
        return jsonify({'message' : 'incorrect token'}), 401
    if not database_helper.get_user_by_email(email):
        print(database_helper.get_user_by_email(email))
        return jsonify({'message' : 'email not found'}), 404
    user_msg = database_helper.get_user_messages(email)
    return jsonify({'message' : 'Got messages successfully', 'data': user_msg}), 200
    
@app.route('/post_message', methods = ['POST'])
def post_message():# Handles a request to post a message, verifies the token's validity, retrieves user data associated with the token, validates the recipient's email, and posts the message to the recipient's inbox in the database.
    authorization_header = request.headers.get('Authorization')
    if authorization_header:
        token = authorization_header.replace('Bearer ', '')
    else:
        return jsonify({'message': 'incorrect token', 'data': '-'}), 401
    user_data = database_helper.get_login_user_by_token(token)
    if not user_data:
        return jsonify({'message' : 'incorrect token'}), 401
    toEmail = request.json['email']
    message = request.json['message']
    latitude = request.json['latitude']
    longitude = request.json['longitude']
    if message is None:
        return jsonify({'message' : 'empty message'}), 400
    if len(message)==0 :
        return jsonify({'message' : 'empty message'}), 400
    if not database_helper.get_user_by_email(toEmail):
        return jsonify({'message' : 'email not found'}), 404
    post = database_helper.post_message(toEmail, token, message, latitude, longitude)
    if post: 
        return jsonify({'message' : 'Posted message successfully'}), 201
    else:
        return jsonify({'message' : 'something went wrong'}), 500
    
#WebSocket
@sock.route('/ws')
def ws(sock): # Defines a WebSocket route where clients can establish connections. Upon connection, adds the socket to the set of active connections and continuously receives messages to maintain the connection, associating the socket with the user's email if a valid token is provided.
    connections.add(sock)
    while True: # Receive messages (if any), this is only used to maintain the connection
        token = sock.receive()
        email = database_helper.get_email_by_token(token)
        if email: 
            login_email[email] = sock
        print(login_email)
                    


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)