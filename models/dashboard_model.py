# models/dashboard_model.py
from config import db
from datetime import datetime

class Dashboard(db.Model):
    __tablename__ = 'dashboard'

    id_dashboard = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    configuracion = db.Column(db.JSON, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=False)

    def __repr__(self):
        return f'<Dashboard {self.nombre}>'
