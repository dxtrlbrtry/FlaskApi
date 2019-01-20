from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager


db = SQLAlchemy()
jwt = JWTManager()


if __name__ == '__main__':
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Projects/FlaskApi/database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'key'

    db.init_app(app)
    jwt.init_app(app)

    from Controllers.user_controller import user_blueprint
    from Controllers.data_controller import data_blueprint
    from Controllers.user_data_relationship_controller import user_data_association_blueprint
    app.register_blueprint(user_blueprint)
    app.register_blueprint(data_blueprint)
    app.register_blueprint(user_data_association_blueprint)
    app.run(debug=True, port=5000)
