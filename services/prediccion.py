from config import db
from models.monitoreo import FactVentas, DimProducto, DimSucursal, DimUsuario, DimTiempo
from models.reportes import DimAlgoritmo, FactPrediccion
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np
import pickle
import json
from datetime import datetime, timedelta

class PredictionService:
    
    def __init__(self):
        self.models = {
            'RandomForest': RandomForestRegressor(n_estimators=100, random_state=42),
            'LinearRegression': LinearRegression()
        }
    
    def get_training_data(self, sucursal_id=None, producto_id=None, limit_days=365):
        """Obtiene datos de entrenamiento de la tabla fact_ventas"""
        query = db.session.query(FactVentas)
        
        # Filtrar por fechas recientes
        fecha_limite = datetime.now() - timedelta(days=limit_days)
        query = query.filter(FactVentas.fecha_proceso >= fecha_limite)
        
        if sucursal_id:
            query = query.filter(FactVentas.sucursal_id == sucursal_id)
        if producto_id:
            query = query.filter(FactVentas.producto_id == producto_id)
            
        ventas = query.all()
        
        # Convertir a DataFrame
        data = []
        for venta in ventas:
            data.append({
                'fecha_id': venta.fecha_id,
                'sucursal_id': venta.sucursal_id,
                'producto_id': venta.producto_id,
                'cantidad_vendida': venta.cantidad_vendida,
                'monto_venta': float(venta.monto_venta),
                'fecha_proceso': venta.fecha_proceso
            })
        
        return pd.DataFrame(data)
    
    def prepare_features(self, df):
        """Prepara características para el modelo"""
        if df.empty:
            return None, None
        
        # Crear features temporales
        df['fecha_proceso'] = pd.to_datetime(df['fecha_proceso'])
        df['dia_semana'] = df['fecha_proceso'].dt.dayofweek
        df['mes'] = df['fecha_proceso'].dt.month
        df['dia_mes'] = df['fecha_proceso'].dt.day
        
        # Agregaciones por producto y sucursal
        df_agg = df.groupby(['sucursal_id', 'producto_id', 'fecha_id']).agg({
            'cantidad_vendida': 'sum',
            'monto_venta': 'sum',
            'dia_semana': 'first',
            'mes': 'first',
            'dia_mes': 'first'
        }).reset_index()
        
        # Features para ML
        features = ['sucursal_id', 'producto_id', 'fecha_id', 'dia_semana', 'mes', 'dia_mes', 'monto_venta']
        X = df_agg[features]
        y = df_agg['cantidad_vendida']
        
        return X, y
    
    def train_model(self, model_name, sucursal_id=None, producto_id=None):
        """Entrena un modelo de predicción"""
        if model_name not in self.models:
            raise ValueError(f"Modelo {model_name} no disponible")
        
        # Obtener datos
        df = self.get_training_data(sucursal_id, producto_id)
        if df.empty:
            raise ValueError("No hay datos suficientes para entrenar")
        
        X, y = self.prepare_features(df)
        if X is None:
            raise ValueError("Error preparando características")
        
        # Dividir datos
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Entrenar modelo
        model = self.models[model_name]
        model.fit(X_train, y_train)
        
        # Evaluar
        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        # Guardar algoritmo en base de datos
        algoritmo = DimAlgoritmo(
            nombre_algoritmo=model_name,
            version="1.0",
            parametros={
                "mae": float(mae),
                "r2_score": float(r2),
                "n_features": len(X.columns),
                "training_samples": len(X_train)
            },
            descripcion=f"Modelo {model_name} entrenado para predicción de demanda"
        )
        
        db.session.add(algoritmo)
        db.session.commit()
        
        return {
            'algoritmo_id': algoritmo.id_algoritmo,
            'mae': mae,
            'r2_score': r2,
            'model': model
        }
    
    def predict_demand(self, algoritmo_id, sucursal_id, producto_id, fecha_id):
        """Realiza predicción de demanda"""
        # Buscar algoritmo
        algoritmo = DimAlgoritmo.query.get(algoritmo_id)
        if not algoritmo:
            raise ValueError("Algoritmo no encontrado")
        
        # Obtener datos históricos para contexto
        df = self.get_training_data(sucursal_id, producto_id, limit_days=30)
        if df.empty:
            raise ValueError("No hay datos históricos suficientes")
        
        # Re-entrenar modelo (en producción podrías cachear esto)
        model_name = algoritmo.nombre_algoritmo
        model_info = self.train_model(model_name, sucursal_id, producto_id)
        model = model_info['model']
        
        # Preparar datos para predicción
        fecha_dt = datetime.strptime(str(fecha_id), '%Y%m%d')
        monto_promedio = df['monto_venta'].mean()
        
        prediction_data = pd.DataFrame({
            'sucursal_id': [sucursal_id],
            'producto_id': [producto_id],
            'fecha_id': [fecha_id],
            'dia_semana': [fecha_dt.weekday()],
            'mes': [fecha_dt.month],
            'dia_mes': [fecha_dt.day],
            'monto_venta': [monto_promedio]
        })
        
        # Realizar predicción
        cantidad_prevista = model.predict(prediction_data)[0]
        
        # Calcular confianza basada en R2 score
        confianza = max(0, min(100, model_info['r2_score'] * 100))
        
        # Guardar predicción
        prediccion = FactPrediccion(
            dim_tiempo_id=fecha_id,
            dim_sucursal_detalle_id=sucursal_id,
            dim_producto_detalle_id=producto_id,
            dim_algoritmo_id=algoritmo_id,
            cantidad_prevista=round(cantidad_prevista, 2),
            confianza=round(confianza, 2)
        )
        
        db.session.add(prediccion)
        db.session.commit()
        
        return {
            'prediccion_id': prediccion.id_fact_prediccion,
            'cantidad_prevista': float(prediccion.cantidad_prevista),
            'confianza': float(prediccion.confianza),
            'algoritmo_usado': algoritmo.nombre_algoritmo
        }
    
    def update_prediction_accuracy(self, prediccion_id, cantidad_real):
        """Actualiza la precisión de una predicción con el valor real"""
        prediccion = FactPrediccion.query.get(prediccion_id)
        if not prediccion:
            raise ValueError("Predicción no encontrada")
        
        prediccion.cantidad_real = cantidad_real
        
        # Calcular precisión (porcentaje de acierto)
        if cantidad_real > 0:
            error_relativo = abs(float(prediccion.cantidad_prevista) - cantidad_real) / cantidad_real
            precision = max(0, (1 - error_relativo) * 100)
        else:
            precision = 0 if prediccion.cantidad_prevista > 0 else 100
        
        prediccion.precision_prediccion = round(precision, 2)
        
        db.session.commit()
        
        return prediccion.to_dict()
    
    def get_algorithm_performance(self, algoritmo_id):
        """Obtiene estadísticas de rendimiento de un algoritmo"""
        predicciones = FactPrediccion.query.filter_by(
            dim_algoritmo_id=algoritmo_id
        ).filter(
            FactPrediccion.cantidad_real.isnot(None)
        ).all()
        
        if not predicciones:
            return None
        
        precisions = [float(p.precision_prediccion) for p in predicciones if p.precision_prediccion]
        
        return {
            'total_predicciones': len(predicciones),
            'precision_promedio': np.mean(precisions) if precisions else 0,
            'precision_mediana': np.median(precisions) if precisions else 0,
            'mejor_precision': max(precisions) if precisions else 0,
            'peor_precision': min(precisions) if precisions else 0
        }