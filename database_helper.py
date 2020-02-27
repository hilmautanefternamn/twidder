import sqlite3
import random
import math
from flask import g

DATABASE_URI = 'database.db'

def get_db():
    db = getattr(g, 'db', None)
    if db is None:
        db = g.db = sqlite3.connect(DATABASE_URI)
    return db

def disconnect_db():
    db = getattr(g, 'db', None)
    if db is not None:
        g.db.close()
        g.db = None

# SAVE TOKEN
def save_token(token, email):
    try:
        get_db().execute("insert into loggedin_user values (?,?)", [token, email])
        get_db().commit()
        return True
    except:
        return False

# SAVE USER
def save_user(firstname, familyname, gender, city, country, email, password):
    try:
        get_db().execute("insert into user values (?,?,?,?,?,?,?);", [firstname, familyname, gender, city, country, email, password])
        get_db().commit()
        return True
    except:
        return False

# SIGN OUT
def sign_out(token):
    try:
        get_db().execute("delete from loggedin_user where token like ?", [token])
        get_db().commit()
        return True
    except:
        return False

# GET EMAIL BY TOKEN
def get_email_by_token(token):
    user = get_db().execute("select email from loggedin_user where token like ?", [token])
    email = user.fetchall()
    user.close()
    if len(email) == 0:
        return False
    return email[0][0]

# CHANGE PASSWORD
def change_password(newpassword, email):
    try:
        get_db().execute("update user set password = ? where email like ?", [newpassword, email])
        get_db().commit()
        return True
    except:
        return False

# GET USER DATA
def get_user_data(token, email):
    user = get_db().execute("select * from user where email like ?", [email])
    user_data = user.fetchall()
    user.close()
    result = []
    if len(user_data) == 0:
        return False
    for i in range(len(user_data)):
        result.append({'firstname':user_data[i][0], 'familyname':user_data[i][1],
        'gender':user_data[i][2], 'city':user_data[i][3], 'country':user_data[i][4],
        'email':user_data[i][5]})
    if token == None:
        result.append({'password':user_data[i][6]})
        return result
    return result

# GET USER MESSAGES
def get_user_messages(email):
    cursor = get_db().execute("select * from messages where toEmail like ?", [email])
    messages = cursor.fetchall()
    cursor.close()
    if len(messages) == 0:
        return False
    return messages

# POST MESSAGE
def post_message(message, toEmail, fromEmail):
    try:
        get_db().execute("insert into messages values (?,?,?);", [toEmail, fromEmail, message])
        get_db().commit()
        return True
    except:
        return False
