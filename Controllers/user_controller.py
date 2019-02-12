from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import datetime
from Models import *

user_blueprint = Blueprint('user_blueprint', __name__)


def valid_user(user_object):
    if 'username' in user_object and 'password' in user_object:
        return True
    return False


@user_blueprint.route('/users/', methods=['POST'])
def create_user():
    data = request.get_json()
    if valid_user(data):
        if not User.query.filter_by(username=data['username']).first():
            hashed_password = generate_password_hash(data['password'], method='sha256')
            public_id = str(uuid.uuid4())
            new_user = User(public_id=public_id, username=data['username'], password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            return jsonify({'msg': 'API: Created Successfully'}), 201
        return jsonify({'msg': 'API: User Already Exists'}), 409
    return jsonify({'msg': 'API: Error Creating User'}), 400


@user_blueprint.route('/users/', methods=['GET'])
def get_all_users():
    users = User.query.all()
    output = []
    for user in users:
        user_data = {}
        user_data['public_id'] = user.public_id
        user_data['username'] = user.username
        user_data['password'] = user.password
        user_data['data'] = [{'title': dt.title, 'desc': dt.desc} for dt in user.data]
        output.append(user_data)
    return jsonify({'users': output, 'msg': 'API: Get Users Successful'}), 200


@user_blueprint.route('/users/<string:_username>', methods=['GET'])
def get_one_user(_username):
    user = User.query.filter_by(username=_username).first()
    if user:
        user_data = {}
        user_data['public_id'] = user.public_id
        user_data['username'] = user.username
        user_data['password'] = user.password
        user_data['data'] = [{'title': dt.title, 'desc': dt.desc} for dt in user.data]
        return jsonify({'user': user_data, 'msg': 'API: Get User Successful'}), 200
    return jsonify({'msg': 'User not found'}), 404


@user_blueprint.route('/users/me/', methods=['GET'])
@jwt_required
def get_current_user():
    user = User.query.filter_by(username=get_jwt_identity()).first()
    if user:
        user_data = {}
        user_data['public_id'] = user.public_id
        user_data['username'] = user.username
        user_data['password'] = user.password
        user_data['data'] = [{'title': dt.title, 'desc': dt.desc} for dt in user.data]
        return jsonify({'user': user_data, 'msg': 'API: Get User Successful'}), 200
    return jsonify({'msg': 'User not found'}), 404


@user_blueprint.route('/users/', methods=['DELETE'])
@jwt_required
def delete_current_user():
    user = User.query.filter_by(username=get_jwt_identity()).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'msg': 'API: User Deleted Successfully'}), 200
    return jsonify({'msg': 'API: User does not exist'}), 404


@user_blueprint.route('/users/<string:_public_id>', methods=['DELETE'])
def delete_user(_public_id):
    user = User.query.filter_by(public_id=_public_id).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'msg': 'API: User Deleted Successfully'}), 200
    return jsonify({'msg': 'API: User does not exist'}), 404


@user_blueprint.route('/login/', methods=['POST'])
def login():
    data = request.get_json()
    if valid_user(data):
        user = User.query.filter_by(username=data['username']).first()
        if user:
            if check_password_hash(user.password, data['password']):
                token = create_access_token(identity=data['username'], expires_delta=datetime.timedelta(minutes=30))
                return jsonify({'token': token, 'msg': 'API: Login Successful'}), 200
            return jsonify({'msg': 'API: Invalid password'}), 400
        return jsonify({'msg': 'API: User does not exist'}), 404
    return jsonify({'msg': 'API: Invalid User Data'}), 400


@user_blueprint.route('/users/', methods=['PUT'])
def update_password():
    data = request.get_json()
    if valid_user(data):
        user = User.query.filter_by(username=data['username']).first()
        if user:
            hashed_password = generate_password_hash(data['password'], method='sha256')
            user.password = hashed_password
            db.session.commit()
            return jsonify({'msg': 'API: Update successful'}), 200
        return jsonify({'msg': 'API: User not found'}), 404
    return jsonify({'msg': 'API: Invalid User Data'}), 400
