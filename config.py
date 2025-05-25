from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

DATABASE_URI = 'postgresql://postgres:chocopancho65@farmaciasperuanas12.cqp622quwrde.us-east-1.rds.amazonaws.com:5432/farmaciasperuanas12'

def init_app(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = 'clave-super-secreta'
    db.init_app(app)