import sqlite3
from flask import g, Flask #global variable

DATABASE = "database.db"

def get_db(): # get the database
    db = getattr(g, 'db', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def close_connection():
    db = getattr(g, 'db', None)
    if db is not None:
        g.db.close()

# -------------------------------------
# sign up
    
def add_user(email, password, first_name, family_name, gender, city, country): # Adds a new user to the database with the provided details (email, password, first name, family name, gender, city, country).
    c = get_db()
    try :
        c.execute("insert into Users values (?,?,?,?,?,?,?)", (email, password, first_name, family_name, gender, city, country))
        c.commit()
        return True
    except Exception as e:
        print(e)
        return False
    
def check_user_exist(email): # Checks if a user with the provided email exists in the database. If found, returns True; otherwise, returns False.
    c = get_db()
    try:
        cursor = c.execute("select * from Users where email = ?", [email])
        rows = cursor.fetchall()
        if rows:
            return True
        else: 
            return False
    except Exception as e:
        print(e)
        return False
    
# sign in 
def check_password(email): # Retrieves the password associated with the provided email from the database. If successful, returns the password; otherwise, returns False.
    c = get_db()
    try:
        cursor = c.execute("select password from Users where email = ?", [email])
        rows = cursor.fetchall()
        cursor.close()
        return rows[0][0]
    except Exception as e:
        print(e)
        return False
    
def get_user_by_email(email): # Retrieves user information associated with the provided email from the database. If found, returns user details (email, first name, family name, gender, city, country); otherwise, returns False.
    c = get_db()
    try:
        cursor = c.execute("select email, first_name, family_name, gender, city, country from Users where email = ?", [email])
        rows = cursor.fetchall()
        if rows:
            res = rows[0]
            cursor.close()
            return res
        else: 
            return False
    except Exception as e:
        print(e)
        return False
    
def get_login_user_by_email(email): # Retrieves login user information associated with the provided email from the database. If found, returns login user details; otherwise, returns False.
    c = get_db()
    try:
        cursor = c.execute("select * from LoginUsers where email = ?", [email])
        rows = cursor.fetchall()
        if rows:
            res = rows[0]
            cursor.close()
            return res
        else: 
            return False
    except Exception as e:
        print(e)
        return False
    
def check_token(token): # Checks if the provided token exists in the database. If found, returns True; otherwise, returns False.
    c = get_db()
    try:
        cursor = c.execute("select * from LoginUsers where token = ?", [token])
        rows = cursor.fetchall()
        if rows:
            return True
        else: 
            return False
    except Exception as e:
        print(e)
        return False
        
def get_email_by_token(token): # Retrieves the email associated with the provided token from the database. If found, returns the email; otherwise, returns False.
    c = get_db()
    try:
        cursor = c.execute("select email from LoginUsers where token = ?", [token])
        rows = cursor.fetchall()
        if rows:
            email = rows[0][0]
            cursor.close()
            return email
        else: 
            return False
    except Exception as e:
        print(e)
        return False
    
def get_login_user_by_token(token): # Retrieves login user information associated with the provided token from the database. If found, returns login user details; otherwise, returns False.
    c = get_db()
    try:
        cursor = c.execute("select * from LoginUsers where token = ?", [token])
        rows = cursor.fetchall()
        if rows:
            email = rows[0][0]
            cursor.close()
            return get_login_user_by_email(email)
        else: 
            return False
    except Exception as e:
        print(e)
        return False
    

def add_login_user(email, token): # Adds a new login user with the provided email and token to the database. If successful, returns True; otherwise, returns False.
    c = get_db()
    try:
        c.execute("insert into LoginUsers values (?,?)", [email, token])
        c.commit()
        return True
    except Exception as e:
        print(e)
        return False

def change_password(token, password): # Updates the password associated with the user's email retrieved using the provided token in the database. If successful, returns True; otherwise, returns False.
    c = get_db()
    try:
        cursor = c.execute("select * from LoginUsers where token = ?", [token])
        rows = cursor.fetchall()
        c.execute("update Users set password = ? where email = ?", [password, rows[0][0]])
        c.commit()
        return True
    except Exception as e:
        print(e)
        return False

def remove_login_user(token): # Removes the login user associated with the provided token from the database. If successful, returns True; otherwise, returns False.
    c = get_db()
    try:
        c.execute("delete from LoginUsers where token = ?", [token])
        c.commit()
        return True
    except Exception as e:
        print(e)
        return False

def post_message(toEmail, token, message, latitude, longitude): # Posts a message from the user associated with the provided token to the specified recipient email, with the message content, latitude, and longitude. If successful, returns True; otherwise, returns False.
    c = get_db()
    try:
        cursor = c.execute("select * from LoginUsers where token like ?", [token]) # get the fromEmail (sender's email)
        rows = cursor.fetchall()
        cursor.close()
        fromEmail = rows[0][0]
        c.execute("insert into Messages (fromEmail, toEmail, message, latitude, longitude) values (?,?,?,?,?)", [fromEmail, toEmail, message, latitude, longitude]) 
        c.commit()
        return True
    except Exception as e:
        print(e)
        return False

def get_user_messages(email): # Retrieves messages sent to the user with the provided email from the database. If successful, returns a list of message details including the writer's email, message content, latitude, and longitude; otherwise, returns False.
    c = get_db()
    try:
        cursor = c.execute("select fromEmail, message, latitude, longitude from Messages where toEmail = ?", [email])
        rows = cursor.fetchall()
        cursor.close()
        result = []
        for index in range(len(rows)):
            result.append({'writer' : rows[index][0], 'content' : rows[index][1], 'latitude':rows[index][2], 'longitude':rows[index][3]})
        return result
    except Exception as e:
        print(e)
        return False


#DATABASE
#signup_table
#login_table
#(user)_msg_table