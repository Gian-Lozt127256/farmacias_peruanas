# models/prediccion_model.py
from config import db

class PrediccionDemanda(db.Model):
    __tablename__ = 'predicciondemanda'

    id_prediccion = db.Column(db.Integer, primary_key=True)
    id_producto = db.Column(db.Integer)
    id_sucursal = db.Column(db.Integer)
    fechaprediccion = db.Column(db.Date)
    cantidad_prevista = db.Column(db.Integer)
    confianza = db.Column(db.Float)
