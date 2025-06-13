from flask import Blueprint, render_template, request, jsonify, send_file
from config import db
from sqlalchemy import text, func
from models.producto_model import Producto
from models.prediccion_model import PrediccionDemanda
from models.comentario_prediccion_model import ComentarioPrediccion
from models.sucursal_model import Sucursal
from models.dashboard_model import Dashboard
from models.monitoreo import FactInventario, FactVentas, DimProducto, DimSucursal, DimUsuario, DimTiempo
from datetime import datetime, date
import csv
import io





analista_bp = Blueprint('analista', __name__, template_folder='../templates/analista')

@analista_bp.route('/home')
def home():
    return render_template('analista/home.html')

@analista_bp.route('/monitoreo')
def monitoreo():
    return render_template('analista/monitoreo.html')

@analista_bp.route('/api/inventario')
def get_inventory():
    # Subquery con ROW_NUMBER() por (sucursal_id, producto_id)
    query = (
    db.session.query(
            DimTiempo.fecha,
            DimSucursal.sucursal_id,
            DimSucursal.nombre_sucursal.label('sucursal'),
            DimProducto.producto_id,
            DimProducto.nombre_producto.label('producto'),
            FactInventario.stock_disponible,
            FactInventario.stock_minimo,
            FactInventario.estado_stock
        )
        .join(DimTiempo, DimTiempo.fecha_id == FactInventario.fecha_id)
        .join(DimSucursal, DimSucursal.sucursal_id == FactInventario.sucursal_id)
        .join(DimProducto, DimProducto.producto_id == FactInventario.producto_id)
        .filter(DimTiempo.año == date.today().year)
    ).all()
        
    # Organizar datos por sucursal -> producto -> historial
    inventarios = {}
    
    for row in query:
        if row.sucursal_id not in inventarios:
            inventarios[row.sucursal_id] = {}
        
        if row.producto_id not in inventarios[row.sucursal_id]:
            inventarios[row.sucursal_id][row.producto_id] = []
        
        inventarios[row.sucursal_id][row.producto_id].append({
            'fecha': row.fecha.strftime('%Y-%m-%d'),
            'sucursal': row.sucursal,
            'producto': row.producto,
            'stock_actual': row.stock_disponible,
            'stock_minimo': row.stock_minimo,
            'estado_stock': row.estado_stock
        })
    
    return jsonify(inventarios)

@analista_bp.route('/api/ventas')
def get_ventas():
    query = (
    db.session.query(
            DimTiempo.fecha, DimTiempo.año, DimTiempo.mes, DimTiempo.dia,
            DimSucursal.sucursal_id, DimSucursal.nombre_sucursal.label('sucursal'),
            func.sum(FactVentas.cantidad_vendida).label('cantidad_vendida')
        )
        .join(DimTiempo, DimTiempo.fecha_id == FactVentas.fecha_id)
        .join(DimSucursal, DimSucursal.sucursal_id == FactVentas.sucursal_id)
        .filter(DimTiempo.año == date.today().year)  # Filtrar por el año actual
        .group_by(DimTiempo.fecha, DimTiempo.año, DimTiempo.mes, DimTiempo.dia,
                  DimSucursal.sucursal_id, DimSucursal.nombre_sucursal)
        .order_by(DimTiempo.fecha)
    ).all()

        
    # Organizar datos por sucursal -> fecha -> historial
    ventas = {}
    
    for row in query:
        if row.sucursal_id not in ventas:
            ventas[row.sucursal_id] = []

        ventas[row.sucursal_id].append({
            'fecha': row.fecha.strftime('%Y-%m-%d'),
            'año': row.año,
            'mes': row.mes,
            'dia': row.dia,
            'sucursal': row.sucursal,
            'cantidad_vendida': row.cantidad_vendida
        })

    return jsonify(ventas)















@analista_bp.route('/predicciones')
def predicciones():
    predicciones = db.session.query(PrediccionDemanda).all()
    productos = db.session.query(Producto).all()
    sucursales = db.session.query(Sucursal).all()
    return render_template('analista/predicciones.html',
                           predicciones=predicciones,
                           productos=productos,
                           sucursales=sucursales)


@analista_bp.route('/registrar_prediccion', methods=['POST'])
def registrar_prediccion():
    data = request.json
    try:
        prediccion = PrediccionDemanda(
            ID_Producto=data['id_producto'],
            ID_Sucursal=data['id_sucursal'],
            FechaPrediccion=datetime.strptime(data['fecha'], "%Y-%m-%d"),
            Cantidad_Prevista=float(data['cantidad_prevista']),
            Confianza=float(data['confianza'])
        )
        db.session.add(prediccion)
        db.session.commit()
        return jsonify({'mensaje': 'Predicción registrada con éxito'}), 200
    except Exception as e:
        print("Error al registrar predicción:", e)
        db.session.rollback()
        return jsonify({'error': 'Error al registrar la predicción'}), 500


@analista_bp.route('/comentario_prediccion', methods=['POST'])
def comentario_prediccion():
    data = request.json
    try:
        comentario = ComentarioPrediccion(
            id_prediccion=data['id_prediccion'],
            descripcion=data['descripcion'],
            fecha=datetime.now()
        )
        db.session.add(comentario)
        db.session.commit()
        return jsonify({'mensaje': 'Comentario guardado correctamente'}), 200
    except Exception as e:
        print("Error al guardar comentario:", e)
        db.session.rollback()
        return jsonify({'error': 'No se pudo guardar el comentario'}), 500


@analista_bp.route('/comentarios_json')
def comentarios_json():
    try:
        comentarios = db.session.query(ComentarioPrediccion).order_by(ComentarioPrediccion.fecha.desc()).limit(20).all()
        resultado = [{
            'id_comentario': c.id_comentario,
            'id_prediccion': c.id_prediccion,
            'descripcion': c.descripcion,
            'fecha': c.fecha.strftime("%Y-%m-%d %H:%M:%S")
        } for c in comentarios]
        return jsonify(resultado)
    except Exception as e:
        print("Error al obtener comentarios:", e)
        return jsonify([]), 500


@analista_bp.route('/eliminar_comentario/<int:id>', methods=['DELETE'])
def eliminar_comentario(id):
    try:
        comentario = db.session.query(ComentarioPrediccion).filter_by(id_comentario=id).first()
        if not comentario:
            return jsonify({'error': 'Comentario no encontrado'}), 404
        db.session.delete(comentario)
        db.session.commit()
        return jsonify({'mensaje': 'Comentario eliminado'}), 200
    except Exception as e:
        print("Error al eliminar comentario:", e)
        db.session.rollback()
        return jsonify({'error': 'Error al eliminar comentario'}), 500


@analista_bp.route('/exportar_predicciones')
def exportar_predicciones():
    try:
        predicciones = db.session.query(PrediccionDemanda).all()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Producto', 'Sucursal', 'FechaPrediccion', 'Cantidad_Prevista', 'Confianza'])

        for p in predicciones:
            writer.writerow([
                p.ID_Prediccion,
                p.ID_Producto,
                p.ID_Sucursal,
                p.FechaPrediccion,
                p.Cantidad_Prevista,
                p.Confianza
            ])

        output.seek(0)
        return send_file(io.BytesIO(output.read().encode()),
                         mimetype='text/csv',
                         as_attachment=True,
                         download_name='predicciones.csv')
    except Exception as e:
        print("Error al exportar predicciones:", e)
        return jsonify({'error': 'No se pudo exportar'}), 500


@analista_bp.route('/cargar_predicciones', methods=['POST'])
def cargar_predicciones():
    try:
        archivo = request.files['archivo']
        contenido = archivo.read().decode('utf-8')
        lector = csv.DictReader(io.StringIO(contenido))

        fechas = []
        reales = []
        predichas = []

        for fila in lector:
            if 'Fecha' in fila and 'Real' in fila and 'Prediccion' in fila:
                fechas.append(fila['Fecha'])
                reales.append(float(fila['Real']))
                predichas.append(float(fila['Prediccion']))
            else:
                return jsonify({'error': 'Encabezados incorrectos en el archivo'}), 400

        return jsonify({'fechas': fechas, 'reales': reales, 'predichas': predichas})

    except Exception as e:
        print("Error al cargar CSV:", e)
        return jsonify({'error': 'Error al procesar el archivo'}), 500


@analista_bp.route('/dashboards')
def dashboards():
    return render_template('analista/dashboards.html')


@analista_bp.route('/comentarios')
def comentarios():
    return render_template('analista/comentarios.html')



@analista_bp.route('/guardar_dashboard', methods=['POST'])
def guardar_dashboard():
    from models.dashboard_model import Dashboard
    data = request.json
    try:
        if not all(k in data for k in ('eje_x', 'eje_y', 'tipo_grafica')):
            return jsonify({'error': 'Faltan datos'}), 400

        dashboard = Dashboard(
            nombre=f"Dashboard-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            tipo=data['tipo_grafica'],
            configuracion=data,
            fecha_creacion=datetime.now(),
            id_usuario=2
        )
        db.session.add(dashboard)
        db.session.commit()
        return jsonify({'mensaje': 'Dashboard guardado'})
    except Exception as e:
        print("Error:", e)
        db.session.rollback()
        return jsonify({'error': 'No se pudo guardar'}), 500


@analista_bp.route('/cargar_dashboards')
def cargar_dashboards():
    from models.dashboard_model import Dashboard
    try:
        dashboards = db.session.query(Dashboard).order_by(Dashboard.fecha_creacion.desc()).limit(6).all()
        resultado = [{
            'id_dashboard': d.id_dashboard,
            'nombre': d.nombre,
            'tipo': d.tipo,
            'configuracion': d.configuracion
        } for d in dashboards]
        return jsonify(resultado)
    except Exception as e:
        print("Error al cargar dashboards:", e)
        return jsonify([]), 500


@analista_bp.route('/data_grafica')
def data_grafica():
    x = request.args.get('x')
    y = request.args.get('y')

    try:
        query = f"""
            SELECT {x} AS etiqueta, SUM({y}) AS valor
            FROM (
                SELECT
                    v.fecha::date AS fecha,
                    p.nombre AS nombre_producto,
                    s.nombre AS nombre_sucursal,
                    v.total AS total_ventas,
                    pd.cantidad_prevista,
                    i.stock_disponible,
                    d.cantidad AS cantidad_devuelta
                FROM venta v
                LEFT JOIN detalleventa dv ON dv.id_venta = v.id_venta
                LEFT JOIN producto p ON dv.id_producto = p.id_producto
                LEFT JOIN sucursal s ON v.id_sucursal = s.id_sucursal
                LEFT JOIN inventario i ON i.id_producto = p.id_producto AND i.id_sucursal = s.id_sucursal
                LEFT JOIN devolucion d ON d.id_venta = v.id_venta
                LEFT JOIN predicciondemanda pd ON pd.id_producto = p.id_producto AND pd.id_sucursal = s.id_sucursal
            ) sub
            GROUP BY etiqueta
            ORDER BY etiqueta
            LIMIT 15;
        """
        resultados = db.session.execute(text(query)).fetchall()
        labels = [str(r[0]) for r in resultados]
        values = [float(r[1]) if r[1] is not None else 0 for r in resultados]
        return jsonify({'labels': labels, 'values': values})
    except Exception as e:
        print("Error al cargar datos para gráfica:", e)
        return jsonify({'labels': [], 'values': []}), 500


@analista_bp.route('/eliminar_dashboard/<int:id>', methods=['DELETE'])
def eliminar_dashboard(id):
    try:
        dashboard = db.session.query(Dashboard).filter_by(id_dashboard=id).first()
        if not dashboard:
            return jsonify({'error': 'No encontrado'}), 404
        db.session.delete(dashboard)
        db.session.commit()
        return jsonify({'mensaje': 'Eliminado correctamente'}), 200
    except Exception as e:
        print("Error al eliminar dashboard:", e)
        db.session.rollback()
        return jsonify({'error': 'Error interno'}), 500



@analista_bp.route('/exportar_csv', methods=['GET', 'POST'])
def exportar_csv():
    tablas = {
        'venta': 'Venta',
        'producto': 'Producto',
        'predicciondemanda': 'PrediccionDemanda',
        'detalleventa': 'DetalleVenta',
        'sucursal': 'Sucursal'
    }

    columnas = {}
    data = []

    if request.method == 'POST':
        tabla = request.form.get('tabla')
        columna_filtro = request.form.get('columna')
        valor_filtro = request.form.get('valor')

        if tabla in tablas:
            try:
                # Obtener columnas
                query_cols = text(f"SELECT * FROM {tabla} LIMIT 1")
                resultado = db.session.execute(query_cols)
                columnas = resultado.keys()

                # Obtener data filtrada
                if columna_filtro and valor_filtro:
                    query = text(f"SELECT * FROM {tabla} WHERE {columna_filtro} = :valor")
                    data = db.session.execute(query, {'valor': valor_filtro}).fetchall()
                else:
                    query = text(f"SELECT * FROM {tabla} LIMIT 100")
                    data = db.session.execute(query).fetchall()
            except Exception as e:
                print(f"Error al filtrar tabla {tabla}:", e)

    return render_template('analista/export_csv.html', tablas=tablas, columnas=columnas, data=data)


# -----------------------------
# DESCARGAR CSV MANUAL
# -----------------------------
@analista_bp.route('/descargar_csv_manual', methods=['POST'])
def descargar_csv_manual():
    tabla = request.form.get('tabla')
    columna_filtro = request.form.get('columna')
    valor_filtro = request.form.get('valor')

    try:
        if columna_filtro and valor_filtro:
            query = text(f"SELECT * FROM {tabla} WHERE {columna_filtro} = :valor")
            data = db.session.execute(query, {'valor': valor_filtro}).fetchall()
        else:
            query = text(f"SELECT * FROM {tabla}")
            data = db.session.execute(query).fetchall()

        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow(data[0].keys() if data else ['Sin datos'])

        # Data
        for fila in data:
            writer.writerow(list(fila))

        output.seek(0)
        return send_file(io.BytesIO(output.read().encode()),
                         mimetype='text/csv',
                         as_attachment=True,
                         download_name=f'{tabla}_exportado.csv')
    except Exception as e:
        print("Error al generar CSV manual:", e)
        return jsonify({'error': 'No se pudo exportar el CSV'}), 500
