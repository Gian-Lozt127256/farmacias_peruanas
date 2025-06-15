from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from models.sistema import Usuario, Rol
from config import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            usuario = db.session.query(Usuario).join(Rol).filter(
                Usuario.email == email,
                Usuario.password == password
            ).first()

            print("usuario:", usuario)
            if usuario:
                print("usuario.rol:", usuario.rol)
                print("usuario.rol.nombre:", usuario.rol.nombre)

                session['usuario_id'] = usuario.id_usuario
                session['rol'] = usuario.rol.nombre

                if usuario.rol.nombre == 'Farmaceutico':
                    return redirect(url_for('farmaceutico.menu'))
                elif usuario.rol.nombre == 'Analista':
                    return redirect(url_for('analista.menu'))
                elif usuario.rol.nombre == 'Gerente':
                    return redirect(url_for('gerente.dashboard'))
            else:
                flash('Credenciales inválidas.')
        except Exception as e:
            import traceback
            traceback.print_exc()
            flash("Error interno al procesar la solicitud.")
        
        return redirect(url_for('auth.login'))

    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
