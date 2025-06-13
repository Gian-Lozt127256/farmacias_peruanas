from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import all models
from .sistema import *
from .comercial import *
from .monitoreo import *
from .reportes import *