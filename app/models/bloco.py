from app.extensions import db


class Bloco(db.Model):
    __tablename__ = "bloco"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    descricao = db.Column(db.String(255), nullable=True)
    ativo = db.Column(db.Boolean, default=True, nullable=False)
    ordem = db.Column(db.Integer, default=0, nullable=False)

    # Relacionamentos
    ambientes = db.relationship("Ambiente", back_populates="bloco", order_by="Ambiente.ordem")
    atividades = db.relationship("Atividade", back_populates="bloco")
    vistorias = db.relationship("Vistoria", back_populates="bloco")

    def __repr__(self):
        return f"<Bloco {self.nome}>"
