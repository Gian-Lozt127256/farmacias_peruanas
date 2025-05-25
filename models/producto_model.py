from config import db

class Producto(db.Model):
    __tablename__ = 'producto'
    id_producto = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.String(255))
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    stock_actual = db.Column(db.Integer, nullable=False)
    stock_minimo = db.Column(db.Integer, nullable=False)
    id_tipoproducto = db.Column(db.Integer)
    id_estadoproducto = db.Column(db.Integer)
    id_proveedor = db.Column(db.Integer)

class ImagenProducto(db.Model):
    __tablename__ = 'imagenproducto'
    id_imagen = db.Column(db.Integer, primary_key=True)
    id_producto = db.Column(db.Integer, db.ForeignKey('producto.id_producto'), nullable=False)
    url_imagen = db.Column(db.String(255), nullable=False)
