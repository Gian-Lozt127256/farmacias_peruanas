from sqlalchemy import Column, Integer, Date, DateTime, Numeric, String, Boolean, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from . import db

# Dimensiones Normalizadas para Tiempo
class DimAño(db.Model):
    __tablename__ = 'dim_año'
    __table_args__ = {'schema': 'reportes'}
    
    id_año = Column(Integer, primary_key=True)
    año = Column(Integer, nullable=False, unique=True)
    
    # Relationships
    trimestres = relationship("DimTrimestre", back_populates="dim_año")

class DimTrimestre(db.Model):
    __tablename__ = 'dim_trimestre'
    __table_args__ = (
        UniqueConstraint('trimestre', 'id_año'),
        {'schema': 'reportes'}
    )
    
    id_trimestre = Column(Integer, primary_key=True)
    trimestre = Column(Integer, nullable=False)
    id_año = Column(Integer, ForeignKey('reportes.dim_año.id_año'), nullable=False)
    
    # Relationships
    dim_año = relationship("DimAño", back_populates="trimestres")
    meses = relationship("DimMes", back_populates="dim_trimestre")

class DimMes(db.Model):
    __tablename__ = 'dim_mes'
    __table_args__ = (
        UniqueConstraint('mes', 'id_trimestre'),
        {'schema': 'reportes'}
    )
    
    id_mes = Column(Integer, primary_key=True)
    mes = Column(Integer, nullable=False)
    nombre_mes = Column(String(20), nullable=False)
    id_trimestre = Column(Integer, ForeignKey('reportes.dim_trimestre.id_trimestre'), nullable=False)
    
    # Relationships
    dim_trimestre = relationship("DimTrimestre", back_populates="meses")
    tiempo_detalles = relationship("DimTiempoDetalle", back_populates="dim_mes")

class DimTiempoDetalle(db.Model):
    __tablename__ = 'dim_tiempo_detalle'
    __table_args__ = {'schema': 'reportes'}
    
    id_tiempo_detalle = Column(Integer, primary_key=True)
    fecha = Column(Date, nullable=False, unique=True)
    dia = Column(Integer, nullable=False)
    dia_semana = Column(String(10), nullable=False)
    semana = Column(Integer, nullable=False)
    es_fin_semana = Column(Boolean, nullable=False)
    id_mes = Column(Integer, ForeignKey('reportes.dim_mes.id_mes'), nullable=False)
    
    # Relationships
    dim_mes = relationship("DimMes", back_populates="tiempo_detalles")

# Dimensiones Normalizadas para Ubicación
class DimDepartamento(db.Model):
    __tablename__ = 'dim_departamento'
    __table_args__ = {'schema': 'reportes'}
    
    id_dim_departamento = Column(Integer, primary_key=True)
    nombre_departamento = Column(String(50), nullable=False, unique=True)
    
    # Relationships
    provincias_detalle = relationship("DimProvinciaDetalle", back_populates="dim_departamento")

class DimProvinciaDetalle(db.Model):
    __tablename__ = 'dim_provincia_detalle'
    __table_args__ = (
        UniqueConstraint('nombre_provincia', 'id_dim_departamento'),
        {'schema': 'reportes'}
    )
    
    id_provincia_detalle = Column(Integer, primary_key=True)
    nombre_provincia = Column(String(50), nullable=False)
    id_dim_departamento = Column(Integer, ForeignKey('reportes.dim_departamento.id_dim_departamento'), nullable=False)
    
    # Relationships
    dim_departamento = relationship("DimDepartamento", back_populates="provincias_detalle")
    distritos_detalle = relationship("DimDistritoDetalle", back_populates="provincia_detalle")

class DimDistritoDetalle(db.Model):
    __tablename__ = 'dim_distrito_detalle'
    __table_args__ = (
        UniqueConstraint('nombre_distrito', 'id_provincia_detalle'),
        {'schema': 'reportes'}
    )
    
    id_distrito_detalle = Column(Integer, primary_key=True)
    nombre_distrito = Column(String(50), nullable=False)
    id_provincia_detalle = Column(Integer, ForeignKey('reportes.dim_provincia_detalle.id_provincia_detalle'), nullable=False)
    
    # Relationships
    provincia_detalle = relationship("DimProvinciaDetalle", back_populates="distritos_detalle")
    sucursales_detalle = relationship("DimSucursalDetalle", back_populates="distrito_detalle")

class DimSucursalDetalle(db.Model):
    __tablename__ = 'dim_sucursal_detalle'
    __table_args__ = {'schema': 'reportes'}
    
    id_sucursal_detalle = Column(Integer, primary_key=True)
    id_sucursal = Column(Integer, nullable=False)
    nombre_sucursal = Column(String(100), nullable=False)
    direccion = Column(String(150))
    telefono = Column(String(20))
    id_distrito_detalle = Column(Integer, ForeignKey('reportes.dim_distrito_detalle.id_distrito_detalle'), nullable=False)
    
    # Relationships
    distrito_detalle = relationship("DimDistritoDetalle", back_populates="sucursales_detalle")

# Dimensiones Normalizadas para Producto
class DimCategoriaProducto(db.Model):
    __tablename__ = 'dim_categoria_producto'
    __table_args__ = {'schema': 'reportes'}
    
    id_categoria = Column(Integer, primary_key=True)
    tipo_producto = Column(String(50), nullable=False, unique=True)
    
    # Relationships
    productos_detalle = relationship("DimProductoDetalle", back_populates="categoria")

class DimProveedorDetalle(db.Model):
    __tablename__ = 'dim_proveedor_detalle'
    __table_args__ = {'schema': 'reportes'}
    
    id_proveedor_detalle = Column(Integer, primary_key=True)
    razonsocial = Column(String(100), nullable=False)
    ruc = Column(String(11), nullable=False, unique=True)
    
    # Relationships
    productos_detalle = relationship("DimProductoDetalle", back_populates="proveedor_detalle")

class DimProductoDetalle(db.Model):
    __tablename__ = 'dim_producto_detalle'
    __table_args__ = {'schema': 'reportes'}
    
    id_producto_detalle = Column(Integer, primary_key=True)
    id_producto = Column(Integer, nullable=False)
    nombre_producto = Column(String(100), nullable=False)
    descripcion = Column(String(255))
    precio = Column(Numeric(10, 2), nullable=False)
    estado = Column(String(50), nullable=False)
    id_categoria = Column(Integer, ForeignKey('reportes.dim_categoria_producto.id_categoria'), nullable=False)
    id_proveedor_detalle = Column(Integer, ForeignKey('reportes.dim_proveedor_detalle.id_proveedor_detalle'), nullable=False)
    
    # Relationships
    categoria = relationship("DimCategoriaProducto", back_populates="productos_detalle")
    proveedor_detalle = relationship("DimProveedorDetalle", back_populates="productos_detalle")

# Dimensión Algoritmo de Predicción
class DimAlgoritmo(db.Model):
    __tablename__ = 'dim_algoritmo'
    __table_args__ = {'schema': 'reportes'}
    
    id_algoritmo = Column(Integer, primary_key=True)
    nombre_algoritmo = Column(String(50), nullable=False)
    version = Column(String(20), nullable=False)
    parametros = Column(JSON)
    descripcion = Column(String(255))
    
    # Relationships
    predicciones = relationship("FactPrediccion", back_populates="algoritmo")

# Tabla de Hechos Principal - Predicciones
class FactPrediccion(db.Model):
    __tablename__ = 'fact_prediccion'
    __table_args__ = {'schema': 'reportes'}
    
    id_fact_prediccion = Column(Integer, primary_key=True)
    dim_tiempo_id = Column(Integer, ForeignKey('reportes.dim_tiempo_detalle.id_tiempo_detalle'), nullable=False)
    dim_sucursal_detalle_id = Column(Integer, ForeignKey('reportes.dim_sucursal_detalle.id_sucursal_detalle'), nullable=False)
    dim_producto_detalle_id = Column(Integer, ForeignKey('reportes.dim_producto_detalle.id_producto_detalle'), nullable=False)
    dim_algoritmo_id = Column(Integer, ForeignKey('reportes.dim_algoritmo.id_algoritmo'), nullable=False)
    cantidad_prevista = Column(Numeric(10, 2), nullable=False)
    confianza = Column(Numeric(5, 2), nullable=False)
    cantidad_real = Column(Integer)
    precision_prediccion = Column(Numeric(5, 2))
    fecha_prediccion = Column(DateTime, default=func.current_timestamp())
    
    # Relationships
    tiempo_detalle = relationship("DimTiempoDetalle")
    sucursal_detalle = relationship("DimSucursalDetalle")
    producto_detalle = relationship("DimProductoDetalle")
    algoritmo = relationship("DimAlgoritmo", back_populates="predicciones")
    comentarios = relationship("ComentarioPrediccion", back_populates="prediccion")

# Comentarios de Predicciones
class ComentarioPrediccion(db.Model):
    __tablename__ = 'comentario_prediccion'
    __table_args__ = {'schema': 'reportes'}
    
    id_comentario = Column(Integer, primary_key=True)
    id_fact_prediccion = Column(Integer, ForeignKey('reportes.fact_prediccion.id_fact_prediccion'), nullable=False)
    descripcion = Column(String(255), nullable=False)
    fecha = Column(DateTime, default=func.current_timestamp())
    id_usuario = Column(Integer, ForeignKey('sistema.usuario.id_usuario'), nullable=False)
    
    # Relationships
    prediccion = relationship("FactPrediccion", back_populates="comentarios")
    usuario = relationship("Usuario")

# Dashboard Configurables
class Dashboard(db.Model):
    __tablename__ = 'dashboard'
    __table_args__ = {'schema': 'reportes'}
    
    id_dashboard = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    tipo = Column(String(50), nullable=False)
    configuracion = Column(JSON, nullable=False)
    fecha_creacion = Column(DateTime, default=func.current_timestamp())
    id_usuario = Column(Integer, ForeignKey('sistema.usuario.id_usuario'), nullable=False)
    
    # Relationships
    usuario = relationship("Usuario")

# Sistema de Alertas
class Alerta(db.Model):
    __tablename__ = 'alerta'
    __table_args__ = {'schema': 'reportes'}
    
    id_alerta = Column(Integer, primary_key=True)
    tipo = Column(String(50), nullable=False)
    mensaje = Column(String(255), nullable=False)
    fecha = Column(DateTime, default=func.current_timestamp())
    estado = Column(String(20), nullable=False, default='ACTIVA')
    id_sucursal = Column(Integer, ForeignKey('sistema.sucursal.id_sucursal'))
    id_producto = Column(Integer, ForeignKey('sistema.producto.id_producto'))
    id_usuario = Column(Integer, ForeignKey('sistema.usuario.id_usuario'))
    
    # Relationships
    sucursal = relationship("Sucursal")
    producto = relationship("Producto")
    usuario = relationship("Usuario")