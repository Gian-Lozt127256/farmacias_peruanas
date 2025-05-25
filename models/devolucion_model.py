from config import db

class Devolucion(db.Model):
    __tablename__ = 'devolucion'
    id_devolucion = db.Column(db.Integer, primary_key=True)
    id_venta = db.Column(db.Integer, db.ForeignKey('venta.id_venta'), nullable=False)
    id_producto = db.Column(db.Integer, db.ForeignKey('producto.id_producto'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.DateTime, nullable=False)
    motivo = db.Column(db.String(255))
