from sqlalchemy import Column, Integer, Date, DateTime, Numeric, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from . import db

class Inventario(db.Model):
    __tablename__ = 'inventario'
    __table_args__ = (
        UniqueConstraint('fecha', 'id_sucursal', 'id_producto'),
        {'schema': 'comercial'}
    )
    
    id_inventario = Column(Integer, primary_key=True)
    fecha = Column(Date, nullable=False, default=func.current_date())
    id_sucursal = Column(Integer, ForeignKey('sistema.sucursal.id_sucursal'), nullable=False)
    id_producto = Column(Integer, ForeignKey('sistema.producto.id_producto'), nullable=False)
    stock_disponible = Column(Integer, nullable=False)
    
    # Relationships
    sucursal = relationship("Sucursal")
    producto = relationship("Producto")

class Venta(db.Model):
    __tablename__ = 'venta'
    __table_args__ = {'schema': 'comercial'}
    
    id_venta = Column(Integer, primary_key=True)
    fecha = Column(DateTime, nullable=False, default=func.current_timestamp())
    id_sucursal = Column(Integer, ForeignKey('sistema.sucursal.id_sucursal'), nullable=False)
    id_usuario = Column(Integer, ForeignKey('sistema.usuario.id_usuario'), nullable=False)
    total = Column(Numeric(10, 2), nullable=False)
    
    # Relationships
    sucursal = relationship("Sucursal")
    usuario = relationship("Usuario")
    detalles = relationship("DetalleVenta", back_populates="venta")
    devoluciones = relationship("Devolucion", back_populates="venta")

class DetalleVenta(db.Model):
    __tablename__ = 'detalleventa'
    __table_args__ = {'schema': 'comercial'}
    
    id_detalleventa = Column(Integer, primary_key=True)
    id_venta = Column(Integer, ForeignKey('comercial.venta.id_venta'), nullable=False)
    id_producto = Column(Integer, ForeignKey('sistema.producto.id_producto'), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Numeric(10, 2), nullable=False)
    subtotal = Column(Numeric(10, 2), nullable=False)
    
    # Relationships
    venta = relationship("Venta", back_populates="detalles")
    producto = relationship("Producto")

class Devolucion(db.Model):
    __tablename__ = 'devolucion'
    __table_args__ = {'schema': 'comercial'}
    
    id_devolucion = Column(Integer, primary_key=True)
    id_venta = Column(Integer, ForeignKey('comercial.venta.id_venta'), nullable=False)
    id_producto = Column(Integer, ForeignKey('sistema.producto.id_producto'), nullable=False)
    cantidad = Column(Integer, nullable=False)
    fecha = Column(DateTime, nullable=False, default=func.current_timestamp())
    motivo = Column(String(255))
    
    # Relationships
    venta = relationship("Venta", back_populates="devoluciones")
    producto = relationship("Producto")