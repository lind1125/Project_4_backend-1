import models

from flask import Blueprint, jsonify, request, session
from playhouse.shortcuts import model_to_dict
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user, login_required

app_users = Blueprint('app_users','app_users')


@app_users.route('/signup', methods=['POST'])
def signup():
    payload = request.get_json()
    payload['email'].lower()

    try:
        models.AppUser.get(models.AppUser.email == payload['email'])
        return jsonify(data={}, \
                       status={"code": 401, \
                               "message": "A user with that email already exists"})
    except models.DoesNotExist:
        payload['password'] = generate_password_hash(payload['password'])
        app_user = models.AppUser.create(**payload)

        login_user(user=app_user)
        app_user_dict = model_to_dict(app_user)
        del app_user_dict['password']
        return jsonify(data=app_user_dict, \
                       status={"code":201, "message": "Successfully registered"})
    
@app_users.route('/login', methods=['POST'])
def login():
        payload = request.get_json()

        try:
            app_user = models.AppUser.get(models.AppUser.username == payload['username'])
            app_user_dict = model_to_dict(app_user)

            if(check_password_hash(app_user_dict['password'], payload['password'])):
                del app_user_dict['password']
                login_user(user=app_user)
                return jsonify(data=app_user_dict, \
                               status={"code": 200, "message": "Successfully logged in"})
            else:
                return jsonify(data={}, status={"code": 401, "message": "Invalid username or password"})
        except models.DoesNotExist:
            return jsonify(data={}, status={"code": 401, "message": "Invalid username or password"})
            
@app_users.route('/logout', methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    return jsonify(data={}, status={"code": 200, "message": "Successfully logged out"})

@app_users.route('/current', methods=['GET'])
@login_required
def get_current():
    current_dict = model_to_dict(models.AppUser.get_by_id(current_user.id))
    return jsonify(data=current_dict, \
                   status={"code": 200, "message": "Successfully found"})