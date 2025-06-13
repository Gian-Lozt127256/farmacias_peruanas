from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from . import db

class Departamento(db.Model):
    __tablename__ = 'departamento'
    __table_args__ = {'schema': 'sistema'}
    
    id_departamento = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False)
    
    # Relationships
    provincias = relationship("Provincia", back_populates="departamento")

class Provincia(db.Model):
    __tablename__ = 'provincia'
    __table_args__ = {'schema': 'sistema'}
    
    id_provincia = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False)
    id_departamento = Column(Integer, ForeignKey('sistema.departamento.id_departamento'), nullable=False)
    
    # Relationships
    departamento = relationship("Departamento", back_populates="provincias")
    distritos = relationship("Distrito", back_populates="provincia")

class Distrito(db.Model):
    __tablename__ = 'distrito'
    __table_args__ = {'schema': 'sistema'}
    
    id_distrito = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False)
    id_provincia = Column(Integer, ForeignKey('sistema.provincia.id_provincia'), nullable=False)
    
    # Relationships
    provincia = relationship("Provincia", back_populates="distritos")
    sucursales = relationship("Sucursal", back_populates="distrito")

class Sucursal(db.Model):
    __tablename__ = 'sucursal'
    __table_args__ = {'schema': 'sistema'}
    
    id_sucursal = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    direccion = Column(String(150))
    telefono = Column(String(20))
    id_distrito = Column(Integer, ForeignKey('sistema.distrito.id_distrito'), nullable=False)
    
    # Relationships
    distrito = relationship("Distrito", back_populates="sucursales")

class TipoProducto(db.Model):
    __tablename__ = 'tipoproducto'
    __table_args__ = {'schema': 'sistema'}
    
    id_tipoproducto = Column(Integer, primary_key=True)
    descripcion = Column(String(50), nullable=False)
    
    # Relationships
    productos = relationship("Producto", back_populates="tipo_producto")

class EstadoProducto(db.Model):
    __tablename__ = 'estadoproducto'
    __table_args__ = {'schema': 'sistema'}
    
    id_estadoproducto = Column(Integer, primary_key=True)
    descripcion = Column(String(50), nullable=False)
    
    # Relationships
    productos = relationship("Producto", back_populates="estado_producto")

class Proveedor(db.Model):
    __tablename__ = 'proveedor'
    __table_args__ = {'schema': 'sistema'}
    
    id_proveedor = Column(Integer, primary_key=True)
    razonsocial = Column(String(100), nullable=False)
    ruc = Column(String(11), nullable=False)
    direccion = Column(String(150))
    telefono = Column(String(15))
    
    # Relationships
    productos = relationship("Producto", back_populates="proveedor")

class Producto(db.Model):
    __tablename__ = 'producto'
    __table_args__ = {'schema': 'sistema'}
    
    id_producto = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(255))
    precio = Column(Numeric(10, 2), nullable=False)
    stock_minimo = Column(Integer, nullable=False)
    id_tipoproducto = Column(Integer, ForeignKey('sistema.tipoproducto.id_tipoproducto'), nullable=False)
    id_estadoproducto = Column(Integer, ForeignKey('sistema.estadoproducto.id_estadoproducto'), nullable=False)
    id_proveedor = Column(Integer, ForeignKey('sistema.proveedor.id_proveedor'), nullable=False)
    
    # Relationships
    tipo_producto = relationship("TipoProducto", back_populates="productos")
    estado_producto = relationship("EstadoProducto", back_populates="productos")
    proveedor = relationship("Proveedor", back_populates="productos")
    imagenes = relationship("ImagenProducto", back_populates="producto")

class ImagenProducto(db.Model):
    __tablename__ = 'imagenproducto'
    __table_args__ = {'schema': 'sistema'}
    
    id_imagen = Column(Integer, primary_key=True)
    id_producto = Column(Integer, ForeignKey('sistema.producto.id_producto'), nullable=False)
    url_imagen = Column(String(255), nullable=False)
    
    # Relationships
    producto = relationship("Producto", back_populates="imagenes")

class Rol(db.Model):
    __tablename__ = 'rol'
    __table_args__ = {'schema': 'sistema'}
    
    id_rol = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False)
    
    # Relationships
    usuarios = relationship("Usuario", back_populates="rol")

class Usuario(db.Model):
    __tablename__ = 'usuario'
    __table_args__ = {'schema': 'sistema'}
    
    id_usuario = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    id_rol = Column(Integer, ForeignKey('sistema.rol.id_rol'), nullable=False)
    
    # Relationships
    rol = relationship("Rol", back_populates="usuarios")