from flask import Blueprint, render_template, jsonify, send_file
from config import db
from sqlalchemy import text
import csv
import io

gerente_bp = Blueprint('gerente', __name__, template_folder='../templates/gerente')

# ======================
# Home del Gerente
# ======================
@gerente_bp.route('/dashboard')
def dashboard():
    return render_template('gerente/home.html')

# ======================
# Visualización de Dashboards (solo lectura)
# ======================
@gerente_bp.route('/visualizacion')
def visualizacion():
    return render_template('gerente/visualizacion.html')

@gerente_bp.route('/cargar_dashboards_gerente')
def cargar_dashboards_gerente():
    try:
        dashboards = db.session.execute(text("SELECT * FROM dashboard ORDER BY fecha_creacion DESC LIMIT 6")).fetchall()
        resultado = [
            {
                'id_dashboard': d.id_dashboard,
                'nombre': d.nombre,
                'tipo': d.tipo,
                'configuracion': d.configuracion
            }
            for d in dashboards
        ]
        return jsonify(resultado)
    except Exception as e:
        print("Error al cargar dashboards para gerente:", e)
        return jsonify([]), 500

# ======================
# Reportes
# ======================
@gerente_bp.route('/reportes')
def reportes():
    # Predicciones
    predicciones = db.session.execute(text("""
        SELECT pd.id_prediccion, p.nombre AS producto, s.nombre AS sucursal,
               pd.fechaprediccion, pd.cantidad_prevista, pd.confianza
        FROM predicciondemanda pd
        JOIN producto p ON pd.id_producto = p.id_producto
        JOIN sucursal s ON pd.id_sucursal = s.id_sucursal
        ORDER BY pd.fechaprediccion DESC
    """)).fetchall()

    # Comentarios
    comentarios = db.session.execute(text("""
        SELECT c.id_prediccion, c.descripcion, c.fecha
        FROM comentarioprediccion c
        ORDER BY c.fecha DESC
    """)).fetchall()

    # Ventas
    ventas = db.session.execute(text("""
        SELECT v.id_venta, v.fecha, s.nombre AS sucursal, v.total
        FROM venta v
        JOIN sucursal s ON v.id_sucursal = s.id_sucursal
        ORDER BY v.fecha DESC
    """)).fetchall()

    # Stock
    stock = db.session.execute(text("""
        SELECT s.nombre AS sucursal, p.nombre AS producto, i.stock_disponible
        FROM inventario i
        JOIN producto p ON i.id_producto = p.id_producto
        JOIN sucursal s ON i.id_sucursal = s.id_sucursal
        ORDER BY s.nombre
    """)).fetchall()

    return render_template('gerente/reportes.html',
                           predicciones=predicciones,
                           comentarios=comentarios,
                           ventas=ventas,
                           stock=stock)

# ======================
# Exportaciones CSV
# ======================
@gerente_bp.route('/descargar_predicciones')
def descargar_predicciones():
    try:
        data = db.session.execute(text("""
            SELECT pd.id_prediccion, p.nombre AS producto, s.nombre AS sucursal,
                   pd.fechaprediccion, pd.cantidad_prevista, pd.confianza
            FROM predicciondemanda pd
            JOIN producto p ON pd.id_producto = p.id_producto
            JOIN sucursal s ON pd.id_sucursal = s.id_sucursal
        """)).fetchall()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Producto', 'Sucursal', 'FechaPrediccion', 'Cantidad_Prevista', 'Confianza'])
        for row in data:
            writer.writerow(row)
        output.seek(0)

        return send_file(io.BytesIO(output.read().encode()),
                         mimetype='text/csv',
                         as_attachment=True,
                         download_name='predicciones.csv')
    except Exception as e:
        print("Error al exportar predicciones:", e)
        return jsonify({'error': 'No se pudo exportar'}), 500


@gerente_bp.route('/descargar_ventas')
def descargar_ventas():
    try:
        ventas = db.session.execute(text("""
            SELECT v.id_venta, v.fecha, s.nombre AS sucursal, v.total
            FROM venta v
            JOIN sucursal s ON v.id_sucursal = s.id_sucursal
            ORDER BY v.fecha DESC
        """)).fetchall()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID_Venta', 'Fecha', 'Sucursal', 'Total'])
        for v in ventas:
            writer.writerow(v)
        output.seek(0)

        return send_file(io.BytesIO(output.read().encode()),
                         mimetype='text/csv',
                         as_attachment=True,
                         download_name='ventas.csv')
    except Exception as e:
        print("Error al exportar ventas:", e)
        return jsonify({'error': 'No se pudo exportar'}), 500


@gerente_bp.route('/descargar_stock')
def descargar_stock():
    try:
        stock = db.session.execute(text("""
            SELECT s.nombre AS sucursal, p.nombre AS producto, i.stock_disponible
            FROM inventario i
            JOIN producto p ON i.id_producto = p.id_producto
            JOIN sucursal s ON i.id_sucursal = s.id_sucursal
            ORDER BY s.nombre
        """)).fetchall()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Sucursal', 'Producto', 'Stock_Disponible'])
        for row in stock:
            writer.writerow(row)
        output.seek(0)

        return send_file(io.BytesIO(output.read().encode()),
                         mimetype='text/csv',
                         as_attachment=True,
                         download_name='stock.csv')
    except Exception as e:
        print("Error al exportar stock:", e)
        return jsonify({'error': 'No se pudo exportar'}), 500
