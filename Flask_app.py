from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import datetime

# APP INITIALIZATION
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Zsolt/git_projects/FlaskApi/database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'key'
db = SQLAlchemy(app)
jwt = JWTManager(app)


# DECLARING MODELS

links = db.Table('links',
                db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                db.Column('data_id', db.Integer, db.ForeignKey('data.id')))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(80), unique=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    data = db.relationship('Data', secondary=links, backref=db.backref('data_of', lazy='dynamic'))


class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(16), nullable=False)
    desc = db.Column(db.String(100), nullable=False)


# OBJECT VALIDATION METHODS
def valid_user(user_object):
    if 'username' in user_object and 'password' in user_object:
        return True
    return False


def valid_data(data_object):
    if 'title' in data_object and 'desc' in data_object:
        return True
    return False


# USER API
@app.route('/users/', methods=['POST'])
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


@app.route('/users/', methods=['GET'])
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


@app.route('/users/<string:_username>', methods=['GET'])
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


@app.route('/users/<string:_username>', methods=['DELETE'])
@jwt_required
def delete_user(_username):
    user = User.query.filter_by(username=_username).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'msg': 'API: User Deleted Successfully'}), 200
    return jsonify({'msg': 'API: User does not exist'}), 404


@app.route('/login/', methods=['POST'])
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


@app.route('/users/', methods=['PUT'])
def update_password():
    data = request.get_json()
    if valid_user(data):
        user = User.query.filter_by(username=data['username']).first()
        if user:
            hashed_password = generate_password_hash(data['password'], method='sha256')
            user.password = hashed_password
            db.session.commit()
            return jsonify({'msg': 'API: Reset successful'}), 200
        return jsonify({'msg': 'API: User not found'}), 404
    return jsonify({'msg': 'API: Invalid User Data'}), 400


# DATA API
@app.route('/data/', methods=['POST'])
@jwt_required
def create_data():
    data = request.get_json()
    if valid_data(data):
        if not Data.query.filter_by(title=data['title']).first():
            new_data = Data(title=data['title'], desc=data['desc'])
            db.session.add(new_data)
            db.session.commit()
            return jsonify({'msg': 'API: Data Created Successfully'}), 201
        return jsonify({'msg': 'API: Data Already Exists'}), 409
    return jsonify({'msg': 'API: Error Creating Data'}), 400


@app.route('/data/', methods=['GET'])
@jwt_required
def get_all_data():
    data_list = Data.query.all()
    output = []
    for data in data_list:
        data_object = {}
        data_object['title'] = data.title
        data_object['desc'] = data.desc
        output.append(data_object)
    return jsonify({'data': output, 'msg': 'API: Get All Data Successful'}), 200


@app.route('/data/<string:_title>', methods=['GET'])
@jwt_required
def get_one_data(_title):
    data = Data.query.filter_by(title=_title).first()
    if data:
        data_object = {}
        data_object['title'] = data.title
        data_object['desc'] = data.desc
        return jsonify({'data': data_object, 'msg': 'API: Get Data Successful'}), 200
    return jsonify({'msg': 'Data not found'}), 404


@app.route('/data/<string:_title>', methods=['DELETE'])
@jwt_required
def delete_data(_title):
    data = Data.query.filter_by(title=_title).first()
    if data:
        db.session.delete(data)
        db.session.commit()
        return jsonify({'msg': 'API: Data Deleted Successfully'}), 200
    return jsonify({'msg': 'API: User does not exist'}), 404


@app.route('/data/', methods=['PUT'])
@jwt_required
def add_to_favorites():
    request_data = request.get_json()
    user = User.query.filter_by(username=get_jwt_identity()).first()
    if 'title' in request_data:
        data = Data.query.filter_by(title=request_data['title']).first()
        if data:
            if data not in user.data:
                user.data.append(data)
                db.session.commit()
                return jsonify({'msg': 'API: Data linked to user'}), 200
            return jsonify({'msg': 'API: Data already linked to user'}), 409
        return jsonify({'msg': 'API: Data does not exist'}), 404
    return jsonify({'msg': 'API: Invalid Data Format'}), 400


@app.route('/data/<string:_title>', methods=['PUT'])
@jwt_required
def remove_from_favorites(_title):
    user = User.query.filter_by(username=get_jwt_identity()).first()
    data = Data.query.filter_by(title=_title).first()
    if data:
        if data in user.data:
            user.data.remove(data)
            db.session.commit()
            return jsonify({'msg': 'API: Data unlinked successfully'}), 200
        return jsonify({'msg': 'API: Data not linked to user'}), 404
    return jsonify({'msg': 'API: Data does not exist'}), 404

if __name__ == "__main__":
    app.run(debug=True)
