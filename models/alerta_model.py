# models/alerta_model.py
from config import db

class Alerta(db.Model):
    __tablename__ = 'alerta'

    id_alerta = db.Column(db.Integer, primary_key=True)
    mensaje = db.Column(db.String(255))
    nivel = db.Column(db.String(50))
    fecha = db.Column(db.DateTime)
