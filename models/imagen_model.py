from config import db

class ImagenProducto(db.Model):
    __tablename__ = 'imagenproducto'
    __table_args__ = {'extend_existing': True}

    id_imagen = db.Column(db.Integer, primary_key=True)
    id_producto = db.Column(db.Integer, nullable=False)
    url_imagen = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.String(255))

    def __repr__(self):
        return f"<ImagenProducto {self.id_imagen} - Producto {self.id_producto}>"
