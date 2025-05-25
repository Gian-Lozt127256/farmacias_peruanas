from config import db

class Inventario(db.Model):
    __tablename__ = 'inventario'
    id_inventario = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    id_sucursal = db.Column(db.Integer, nullable=False)
    id_producto = db.Column(db.Integer, nullable=False)
    stock_disponible = db.Column(db.Integer, nullable=False)
