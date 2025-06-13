
from flask import Flask
from config import init_app
from routes.auth_routes import auth_bp
from routes.farmaceutico_routes import farmaceutico_bp
from routes.analista_routes import analista_bp
from routes.gerente_routes import gerente_bp
from flask import redirect, url_for

app = Flask(__name__)
init_app(app)

# Registrar Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(farmaceutico_bp, url_prefix='/farmaceutico')
app.register_blueprint(analista_bp, url_prefix='/analista')
app.register_blueprint(gerente_bp, url_prefix='/gerente')

@app.route('/')
def index():
    return redirect(url_for('auth.login'))

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")