# models/sucursal_model.py

from config import db

class Sucursal(db.Model):
    __tablename__ = 'sucursal'

    id_sucursal = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(150))
    telefono = db.Column(db.String(20))
    id_distrito = db.Column(db.Integer, db.ForeignKey('distrito.id_distrito'), nullable=False)

    def __repr__(self):
        return f'<Sucursal {self.nombre}>'
