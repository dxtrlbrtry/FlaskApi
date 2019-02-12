from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
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
            new_data = Data(title=data['title'], desc=data['desc'], created_by=get_jwt_identity())
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
        data_object['id'] = data.id
        data_object['title'] = data.title
        data_object['desc'] = data.desc
        output.append(data_object)
    return jsonify({'data': output, 'msg': 'API: Get All Data Successful'}), 200


@data_blueprint.route('/data/<int:_id>', methods=['GET'])
@jwt_required
def get_one_data(_id):
    data = Data.query.filter_by(id=_id).first()
    if data:
        data_object = {}
        data_object['id'] = data.id
        data_object['title'] = data.title
        data_object['desc'] = data.desc
        return jsonify({'data': data_object, 'msg': 'API: Get Data Successful'}), 200
    return jsonify({'msg': 'Data not found'}), 404


@data_blueprint.route('/data/<int:_id>', methods=['DELETE'])
@jwt_required
def delete_data(_id):
    data = Data.query.filter_by(id=_id).first()
    if data:
        db.session.delete(data)
        db.session.commit()
        return jsonify({'msg': 'API: Data Deleted Successfully'}), 200
    return jsonify({'msg': 'API: User does not exist'}), 404


@data_blueprint.route('/data/<int:_id>', methods=['PUT'])
@jwt_required
def update_data(_id):
    request_data = request.get_json()
    if valid_data(request_data):
        data = Data.query.filter_by(id=_id).first()
        if data:
            data.title = request_data['title']
            data.desc = request_data['desc']
            db.session.commit()
            return jsonify({'msg': 'API: Data Updated successfully'}), 200
        return jsonify({'msg': 'API: Data not found'}), 404
    return jsonify({'msg': 'Invalid Data'}), 400

