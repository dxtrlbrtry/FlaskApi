from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required
from Models import *


data_blueprint = Blueprint('data_blueprint', __name__)


def valid_data(data_object):
    if 'title' in data_object and 'desc' in data_object:
        return True
    return False


@data_blueprint.route('/data/', methods=['POST'])
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


@data_blueprint.route('/data/', methods=['GET'])
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


@data_blueprint.route('/data/<string:_title>', methods=['GET'])
@jwt_required
def get_one_data(_title):
    data = Data.query.filter_by(title=_title).first()
    if data:
        data_object = {}
        data_object['title'] = data.title
        data_object['desc'] = data.desc
        return jsonify({'data': data_object, 'msg': 'API: Get Data Successful'}), 200
    return jsonify({'msg': 'Data not found'}), 404


@data_blueprint.route('/data/<string:_title>', methods=['DELETE'])
@jwt_required
def delete_data(_title):
    data = Data.query.filter_by(title=_title).first()
    if data:
        db.session.delete(data)
        db.session.commit()
        return jsonify({'msg': 'API: Data Deleted Successfully'}), 200
    return jsonify({'msg': 'API: User does not exist'}), 404

