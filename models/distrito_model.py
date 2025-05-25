from config import db

class Distrito(db.Model):
    __tablename__ = 'distrito'

    id_distrito = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    id_provincia = db.Column(db.Integer, db.ForeignKey('provincia.id_provincia'), nullable=False)

    def __repr__(self):
        return f'<Distrito {self.nombre}>'
