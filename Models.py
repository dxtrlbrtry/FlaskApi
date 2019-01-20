from run import db


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
