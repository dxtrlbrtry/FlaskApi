from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from Models import *


user_data_association_blueprint = Blueprint('user_data_association_blueprint', __name__)


@user_data_association_blueprint.route('/user_data_relation/', methods=['POST'])
@jwt_required
def add_to_favorites():
    request_data = request.get_json()
    user = User.query.filter_by(username=get_jwt_identity()).first()
    if 'id' in request_data:
        data = Data.query.filter_by(id=request_data['id']).first()
        if data:
            if data not in user.data:
                user.data.append(data)
                db.session.commit()
                return jsonify({'msg': 'API: Data linked to user'}), 200
            return jsonify({'msg': 'API: Data already linked to user'}), 409
        return jsonify({'msg': 'API: Data does not exist'}), 404
    return jsonify({'msg': 'API: Invalid Data Format'}), 400


@user_data_association_blueprint.route('/user_data_relation/<int:_id>', methods=['DELETE'])
@jwt_required
def remove_from_favorites(_id):
    user = User.query.filter_by(username=get_jwt_identity()).first()
    data = Data.query.filter_by(id=_id).first()
    if data:
        if data in user.data:
            user.data.remove(data)
            db.session.commit()
            return jsonify({'msg': 'API: Data unlinked successfully'}), 200
        return jsonify({'msg': 'API: Data not linked to user'}), 404
    return jsonify({'msg': 'API: Data does not exist'}), 404
