from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_file
from config import db
#from models.producto_model import Producto, ImagenProducto
#from models.venta_model import Venta, DetalleVenta
#from models.devolucion_model import Devolucion
#from models.usuario_model import Usuario
from models.sistema import Producto, ImagenProducto, Usuario
from models.comercial import Venta, DetalleVenta, Devolucion, Inventario
from datetime import datetime, date
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

farmaceutico_bp = Blueprint('farmaceutico', __name__, template_folder='../templates/farmaceutico')

def query(id_sucursal):
    query = db.session.query(Producto, Inventario).join(Inventario, Producto.id_producto == Inventario.id_producto)
    query = query.filter(Inventario.id_sucursal == id_sucursal).order_by(Producto.id_producto)
    return query

@farmaceutico_bp.route('/dashboard')
def dashboard():
    return render_template('farmaceutico/home.html')

@farmaceutico_bp.route('/ventas')
def ventas():
    resultados = query(id_sucursal=1).all()  # Cambiar según la sucursal actual
    imagenes = {img.id_producto: img.url_imagen for img in db.session.query(ImagenProducto).all()}
    return render_template('farmaceutico/ventas.html', resultados=resultados, imagenes=imagenes)

@farmaceutico_bp.route('/procesar_venta', methods=['POST'])
def procesar_venta():
    cantidades = {
        int(k.split('[')[1].split(']')[0]): int(v or 0)
        for k, v in request.form.items() if k.startswith("cantidades[")
    }
    id_usuario = session.get('usuario_id') or 1
    resultado = query(id_sucursal=1)
    productos = resultado.filter(Producto.id_producto.in_(cantidades.keys())).all()

    total = 0.0
    detalles = []

    for producto, inventario in productos:
        cantidad = cantidades.get(producto.id_producto, 0)
        if cantidad > 0:
            if inventario.stock_disponible < cantidad:
                flash(f"Stock insuficiente para {producto.nombre}", "danger")
                return redirect(url_for('farmaceutico.ventas'))
            # Calcular subtotal y actualizar total
            subtotal = float(producto.precio) * cantidad
            total += subtotal
            # Agregar detalle de venta
            detalles.append((producto, cantidad, subtotal))
            # Actualizar stock disponible
            inventario.stock_disponible -= cantidad
            inventario.fecha = date.today()  # Actualizar fecha de inventario

    if total == 0:
        flash("No se seleccionaron productos.", "warning")
        return redirect(url_for('farmaceutico.ventas'))

    venta = Venta(fecha=datetime.now(), id_sucursal=1, id_usuario=id_usuario, total=total)
    db.session.add(venta)
    db.session.flush()

    for producto, cantidad, subtotal in detalles:
        db.session.add(DetalleVenta(
            id_venta=venta.id_venta,
            id_producto=producto.id_producto,
            cantidad=cantidad,
            precio_unitario=producto.precio,
            subtotal=subtotal
        ))
    
    db.session.commit()
    return redirect(url_for('farmaceutico.generar_boleta', id_venta=venta.id_venta))

@farmaceutico_bp.route('/boleta/<int:id_venta>')
def generar_boleta(id_venta):
    venta = db.session.query(Venta).get(id_venta)
    detalles = db.session.query(DetalleVenta).filter_by(id_venta=id_venta).all()
    productos = {p.id_producto: p.nombre for p in db.session.query(Producto).all()}

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle(f"Boleta de Venta Nº {id_venta}")
    width, height = letter

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawCentredString(width / 2, height - 50, "FARMACIAS PERUANAS S.A.C")
    pdf.setFont("Helvetica", 10)
    pdf.drawCentredString(width / 2, height - 65, "RUC: 20512345678")
    pdf.drawCentredString(width / 2, height - 78, "Av. Salud N° 123 - Lima, Perú")
    pdf.drawCentredString(width / 2, height - 91, "Teléfono: (01) 345-6789")
    pdf.line(40, height - 100, width - 40, height - 100)

    y = height - 120
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y, f"Boleta de Venta Nº {venta.id_venta}")
    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, y - 20, f"Fecha: {venta.fecha.strftime('%Y-%m-%d %H:%M:%S')}")
    pdf.drawString(50, y - 35, "Detalle de productos:")

    y -= 55
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(50, y, "Producto")
    pdf.drawString(250, y, "Cantidad")
    pdf.drawString(320, y, "P. Unitario")
    pdf.drawString(420, y, "Subtotal")
    y -= 15
    pdf.line(40, y, width - 40, y)
    y -= 15

    pdf.setFont("Helvetica", 10)
    for d in detalles:
        nombre = productos.get(d.id_producto, "Desconocido")
        pdf.drawString(50, y, nombre)
        pdf.drawString(260, y, str(d.cantidad))
        pdf.drawString(330, y, f"S/ {float(d.precio_unitario):.2f}")
        pdf.drawString(430, y, f"S/ {float(d.subtotal):.2f}")
        y -= 18
        if y < 80:
            pdf.showPage()
            y = height - 80

    y -= 10
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawRightString(width - 50, y, f"TOTAL: S/ {float(venta.total):.2f}")
    pdf.line(400, y - 2, width - 40, y - 2)

    pdf.showPage()
    pdf.save()

    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"boleta_venta_{id_venta}.pdf", mimetype='application/pdf')

@farmaceutico_bp.route('/historial_ventas')
def historial_ventas():
    ventas = db.session.query(Venta).order_by(Venta.fecha.desc()).all()
    detalles = db.session.query(DetalleVenta).all()
    productos = {p.id_producto: p.nombre for p in db.session.query(Producto).all()}
    usuarios = {u.id_usuario: u.nombre for u in db.session.query(Usuario).all()}
    return render_template('farmaceutico/historial_ventas.html',
                           ventas=ventas, detalles=detalles,
                           productos=productos, usuarios=usuarios)

@farmaceutico_bp.route('/devoluciones')
def devoluciones():
    productos = db.session.query(Producto).all()
    ventas = db.session.query(Venta).all()
    return render_template('farmaceutico/devoluciones.html', productos=productos, ventas=ventas)

@farmaceutico_bp.route('/registrar_devolucion', methods=['POST'])
def registrar_devolucion():
    id_producto = int(request.form['id_producto'])
    id_venta = int(request.form['id_venta'])
    cantidad = int(request.form['cantidad'])
    motivo = request.form['motivo']

    producto = db.session.query(Producto).get(id_producto)
    venta = db.session.query(Venta).get(id_venta)

    if not producto or not venta:
        flash("Producto o venta no encontrada.")
        return redirect(url_for('farmaceutico.devoluciones'))

    devolucion = Devolucion(id_venta=id_venta, id_producto=id_producto,
                            cantidad=cantidad, fecha=datetime.now(), motivo=motivo)
    db.session.add(devolucion)
    producto.stock_actual += cantidad
    db.session.commit()

    flash("Devolución registrada y stock actualizado.")
    return redirect(url_for('farmaceutico.devoluciones'))

@farmaceutico_bp.route('/historial_devoluciones')
def historial_devoluciones():
    devoluciones = db.session.query(Devolucion).order_by(Devolucion.fecha.desc()).all()
    productos = {p.id_producto: p.nombre for p in db.session.query(Producto).all()}
    ventas = {v.id_venta: v.fecha for v in db.session.query(Venta).all()}
    return render_template('farmaceutico/historial_devoluciones.html',
                           devoluciones=devoluciones,
                           productos=productos,
                           ventas=ventas)
@farmaceutico_bp.route('/farmaceutico/home')
def home():
    return render_template('farmaceutico/home.html')