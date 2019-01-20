from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager


db = SQLAlchemy()
jwt = JWTManager()


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Projects/FlaskAPI/database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'key'

    db.init_app(app)
    jwt.init_app(app)

    from Controllers.user_controller import user_blueprint
    from Controllers.data_controller import data_blueprint
    from Controllers.user_data_relation_controller import user_data_association_blueprint
    app.register_blueprint(user_blueprint)
    app.register_blueprint(data_blueprint)
    app.register_blueprint(user_data_association_blueprint)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
