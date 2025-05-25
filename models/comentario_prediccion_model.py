from config import db

class ComentarioPrediccion(db.Model):
    __tablename__ = 'comentarioprediccion'

    id_comentario = db.Column(db.Integer, primary_key=True)
    id_prediccion = db.Column(db.Integer, db.ForeignKey('predicciondemanda.id_prediccion'), nullable=False)
    descripcion = db.Column(db.String(255), nullable=False)
    fecha = db.Column(db.DateTime, nullable=False)

    prediccion = db.relationship('PrediccionDemanda', backref='comentarios')
