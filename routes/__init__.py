from .auth_routes import auth_bp
from .analista_routes import analista_bp
from .farmaceutico_routes import farmaceutico_bp
from .gerente_routes import gerente_bp

__all__ = [
    "auth_bp",
    "analista_bp",
    "farmaceutico_bp",
    "gerente_bp"
]
