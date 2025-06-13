from sqlalchemy import Column, Integer, Date, DateTime, Numeric, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from . import db

# Tablas de Dimensiones
class DimTiempo(db.Model):
    __tablename__ = 'dim_tiempo'
    __table_args__ = {'schema': 'monitoreo'}
    
    fecha_id = Column(Integer, primary_key=True)
    fecha = Column(Date, nullable=False)
    año = Column(Integer, nullable=False)
    trimestre = Column(Integer, nullable=False)
    mes = Column(Integer, nullable=False)
    semana = Column(Integer, nullable=False)
    dia = Column(Integer, nullable=False)
    dia_semana = Column(String(10), nullable=False)
    es_fin_semana = Column(Boolean, nullable=False)
    nombre_mes = Column(String(20), nullable=False)

class DimSucursal(db.Model):
    __tablename__ = 'dim_sucursal'
    __table_args__ = {'schema': 'monitoreo'}
    
    sucursal_id = Column(Integer, primary_key=True)
    nombre_sucursal = Column(String(100), nullable=False)
    direccion_sucursal = Column(String(150))
    telefono_sucursal = Column(String(20))
    distrito = Column(String(50), nullable=False)
    provincia = Column(String(50), nullable=False)
    departamento = Column(String(50), nullable=False)

class DimProducto(db.Model):
    __tablename__ = 'dim_producto'
    __table_args__ = {'schema': 'monitoreo'}
    
    producto_id = Column(Integer, primary_key=True)
    nombre_producto = Column(String(100), nullable=False)
    descripcion_producto = Column(String(255))
    precio_producto = Column(Numeric(10, 2), nullable=False)
    tipo_producto = Column(String(50), nullable=False)
    estado_producto = Column(String(50), nullable=False)
    proveedor = Column(String(100), nullable=False)
    ruc_proveedor = Column(String(11), nullable=False)

class DimUsuario(db.Model):
    __tablename__ = 'dim_usuario'
    __table_args__ = {'schema': 'monitoreo'}
    
    usuario_id = Column(Integer, primary_key=True)
    nombre_usuario = Column(String(100), nullable=False)
    email_usuario = Column(String(100), nullable=False)
    rol_usuario = Column(String(50), nullable=False)

# Tablas de Hechos
class FactVentas(db.Model):
    __tablename__ = 'fact_ventas'
    __table_args__ = {'schema': 'monitoreo'}
    
    id_fact_ventas = Column(Integer, primary_key=True)
    fecha_id = Column(Integer, ForeignKey('monitoreo.dim_tiempo.fecha_id'), nullable=False)
    sucursal_id = Column(Integer, ForeignKey('monitoreo.dim_sucursal.sucursal_id'), nullable=False)
    producto_id = Column(Integer, ForeignKey('monitoreo.dim_producto.producto_id'), nullable=False)
    usuario_id = Column(Integer, ForeignKey('monitoreo.dim_usuario.usuario_id'), nullable=False)
    cantidad_vendida = Column(Integer, nullable=False)
    monto_venta = Column(Numeric(12, 2), nullable=False)
    costo_producto = Column(Numeric(12, 2), nullable=False)
    margen_utilidad = Column(Numeric(12, 2), nullable=False)
    fecha_proceso = Column(DateTime, default=func.current_timestamp())
    
    # Relationships
    dim_tiempo = relationship("DimTiempo")
    dim_sucursal = relationship("DimSucursal")
    dim_producto = relationship("DimProducto")
    dim_usuario = relationship("DimUsuario")

class FactInventario(db.Model):
    __tablename__ = 'fact_inventario'
    __table_args__ = {'schema': 'monitoreo'}
    
    id_fact_inventario = Column(Integer, primary_key=True)
    fecha_id = Column(Integer, ForeignKey('monitoreo.dim_tiempo.fecha_id'), nullable=False)
    sucursal_id = Column(Integer, ForeignKey('monitoreo.dim_sucursal.sucursal_id'), nullable=False)
    producto_id = Column(Integer, ForeignKey('monitoreo.dim_producto.producto_id'), nullable=False)
    stock_disponible = Column(Integer, nullable=False)
    stock_minimo = Column(Integer, nullable=False)
    estado_stock = Column(String(20), nullable=False)  # 'Normal', 'Bajo', 'Crítico'
    fecha_proceso = Column(DateTime, default=func.current_timestamp())
    
    # Relationships
    dim_tiempo = relationship("DimTiempo")
    dim_sucursal = relationship("DimSucursal")
    dim_producto = relationship("DimProducto")