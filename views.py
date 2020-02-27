from flask import Flask, request, jsonify, current_app
from Twidder import app
import Twidder.database_helper
import uuid
import json

@app.route('/')
def root():
    return current_app.send_static_file('client.html')

@app.teardown_request
def after_request(exception):
    database_helper.disconnect_db()

# SIGN IN
# check if email belongs to signed-up user and get data from database
# compare passwords and if they match create and add token to database
@app.route('/signin', methods = ['POST'])
def sign_in():
    data = request.get_json()
    # check if email and password is in requested data
    if 'email' in data and 'password' in data:
        # make sure data is correctly formatted for database
        if(len(data['email']) <= 50 and len(data['password']) <= 50):
            # check if email is in database
            user = database_helper.get_user_data(None, data['email'])
            if user == False:
                return json.dumps({"success": False, "message" : "Sorry that email is not registered!"}), 500
            # if correct password input create and save token
            if user[1]['password'] == data['password']:
                token = str(uuid.uuid4())
                if database_helper.save_token(token, data['email']):
                    return json.dumps({"success": True, "message" : "Successfully logged in!", "token" : token}), 200
                else: return json.dumps({"success": False, "message" : "Could not log in!"}), 500
            else: return json.dumps({"success": False, "message" : "Password don't match!"}), 500
        else: return '', 400 # if data is not correctly formatted
    else: return '', 400 # if data is not email and password

# SIGN UP
# validate input data and send to database
@app.route('/signup', methods = ['POST'])
def sign_up():
    data = request.get_json()
    # check if all fields are in requested data
    if 'email' in data and 'password' in data and 'firstname' in data and \
    'familyname' in data and 'gender' in data and 'city' in data and 'country' in data:
        # make sure password is not too short
        if len(data['password']) < 6:
            return json.dumps({"message" : "Password too short!"}), 500
        # make sure all inputs are correctly formatted for database
        if len(data['email']) <= 50 and len(data['password']) <= 50 and \
        len(data['firstname']) <= 100 and len(data['familyname']) <= 100 and \
        len(data['gender']) <= 10 and len(data['city']) <= 50 and len(data['country']) <= 50:
            # make sure email is not already registered
            if database_helper.get_user_data(None, data['email']):
                return json.dumps({"success": False, "message" : "Email is already registered!"}), 500
            # send data to database
            result = database_helper.save_user( data['firstname'], data['familyname'],
            data['gender'], data['city'], data['country'], data['email'], data['password'])
            if result is False:
                return json.dumps({"success": False, "message" : "Could not sign up!"}), 500
            else: return json.dumps({"success": True, "message" : "Successfully signed up!"}), 200
        else: return '', 400 # if data is not correctly formatted
    else: return '', 400 # if data is not email and password

# SIGN OUT
# make sure token is valid and call function to remove user from database
@app.route('/signout', methods = ['POST'])
def sign_out():
    data = request.get_json()
    # check if token is in requested data
    if 'token' not in data:
        return json.dumps({"success": False, "message" : "Token not found. Could not sign out!"}), 500
    # call function to remove user from loggedin_user
    result = database_helper.sign_out(data['token'])
    if result == False:
        return json.dumps({"success": False, "message" : "Could not sign out!"}), 500
    else: return json.dumps({"success": True, "message" : "Successfully signed out!"}), 200

# CHANGE PASSWORD
# make sure all password input is correct:
# - newpassword is at least 6 characters but not more than 50
# - oldpassword matches password from database
# - newpassword differs from oldPassword
@app.route('/changepassword', methods = ['POST'])
def change_password():
    data = request.get_json()
    if 'token' in data and 'oldpassword' in data and 'newpassword' in data:
        # validate user as loggedin_user and get users email via token
        email = database_helper.get_email_by_token(data['token'])
        if email == False:
            return json.dumps({"success": False, "message" : "User is not online!"}), 500
        if len(data['newpassword']) < 6:
            return json.dumps({"success": False, "message" : "Password is too short!"}), 500
        if len(data['newpassword']) <= 50:
            # use email to get users current password (token = None gives user data with password)
            user = database_helper.get_user_data(None, email)
            if user[1]['password'] != data['oldpassword']:
                return json.dumps({"success": False, "message" : "Wrong password!"}), 500
            if data['oldpassword'] == data['newpassword']:
                return json.dumps({"success": False, "message" : "New password can't be the same as old!"}), 500
            result = database_helper.change_password(data['newpassword'], email)
        else: return json.dumps({"success": False, "message" : "Password is too long!"}), 500
    else: return json.dumps({"success": False, "message" : "Wrong input data!"}), 500
    if result == False:
        return json.dumps({"success": False, "message" : "Could not change password!"}), 500
    else: return json.dumps({"success": True, "message" : "Successfully changed password!"}), 200

# GET USER DATA BY TOKEN
# get email via token to call get_user_data to get the data
@app.route('/usertoken', methods = ['POST'])
def get_user_data_by_token():
    data = request.get_json()
    if 'token' in data:
        # validate user as loggedin_user and get users email via token
        email = database_helper.get_email_by_token(data['token'])
        if email == False:
            return json.dumps({"success": False, "message" : "Ops you are not online!"}), 500
        # get data
        user_data = database_helper.get_user_data(data['token'], email)
        if user_data == False:
            return json.dumps({"success": False, "message" : "Could not fetch data!"}), 500
        else: return json.dumps({"success": True, "message" : "Data retreived!", "data" : user_data}), 200
    else: return json.dumps({"success": False, "message" : "Wrong input!"}), 500

# GET USER DATA BY EMAIL
# validate user via token and get data from database
@app.route('/useremail', methods = ['POST'])
def get_user_data_by_email():
    data = request.get_json()
    if 'token' in data and 'email' in data:
        # validate user as loggedin_user and get users email via token
        email = database_helper.get_email_by_token(data['token'])
        if email == False:
            return json.dumps({"success": False, "message" : "Ops you are not online!"}), 500
        # get data
        user_data = database_helper.get_user_data(data['token'], data['email'])
        if user_data == False:
            return json.dumps({"success": False, "message" : "Could not fetch data!"}), 500
        else: return json.dumps({"success": True, "message" : "Data retreived!", "data" : user_data}), 200
    else: return json.dumps({"success": False, "message" : "Wrong input!"}), 500

# GET USER MESSAGES BY TOKEN
# validate user via token and get email
# call get_user_messages and get messages from database
@app.route('/messagestoken', methods = ['POST'])
def get_user_messages_by_token():
    data = request.get_json()
    if 'token' in data:
        # validate user as loggedin_user and get users email via token
        email = database_helper.get_email_by_token(data['token'])
        if email == False:
            return json.dumps({"success": False, "message" : "Ops you are not online!"}), 500
        # get messages
        messages = database_helper.get_user_messages(email)
        if messages == False:
            return json.dumps({"success": False, "message" : "No messages found!"}), 500
        else: return json.dumps({"success": True, "message" : "Data retreived!", "data" : messages}), 200
    else: return json.dumps({"success": False, "message" : "Wrong input!"}), 500

# GET USER MESSAGES BY EMAIL
# validate user via token and get messages from database
@app.route('/messagesemail', methods = ['POST'])
def get_user_messages_by_email():
    data = request.get_json()
    if 'token' in data and 'email' in data:
        # validate user as loggedin_user and get users email via token
        email = database_helper.get_email_by_token(data['token'])
        if email == False:
            return json.dumps({"success": False, "message" : "Ops you are not online!"}), 500
        # get messages
        messages = database_helper.get_user_messages(data['email'])
        if messages == False:
            return json.dumps({"success": False, "message" : "No messages found!"}), 500
        else: return json.dumps({"success": True, "message" : "Data retreived!", "data" : messages}), 200
    else: return json.dumps({"success": False, "message" : "Wrong input!"}), 500

# POST MESSAGE
# validate token, message format and recipient
# send message, recipient and writer to database
@app.route('/postmessage', methods = ['POST'])
def post_message():
    data = request.get_json()
    if 'token' in data and 'message' in data:
        fromEmail = database_helper.get_email_by_token(data['token'])
        if fromEmail == False:
            return json.dumps({"success": False, "message" : "Ops you are not online!"}), 500
         # if recipient is given
        if 'email' in data:
            toEmail = data['email']
        # if recipient is not given = post on own wall
        else:
            toEmail = fromEmail
        # validate recipient
        if database_helper.get_user_data(data['token'], toEmail) == False:
            return json.dumps({"success": False, "message" : "No such recipient!"}), 500
        if len(data['message']) <= 280:
            # send data to database
            result = database_helper.post_message(data['message'], toEmail, fromEmail)
            if result == False:
                return json.dumps({"success": False, "message" : "Message could not be posted!"}), 500
            return json.dumps({"success": True, "message" : "Message posted!"}), 200
        else: return json.dumps({"success": False, "message" : "Message is too long!"}), 500
    else: return json.dumps({"success": False, "message" : "Wrong input!"}), 500