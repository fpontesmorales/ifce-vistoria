from app.extensions import db


class Ambiente(db.Model):
    __tablename__ = "ambiente"
    __table_args__ = (
        db.UniqueConstraint("bloco_id", "nome", name="uq_ambiente_nome_bloco"),
    )

    id = db.Column(db.Integer, primary_key=True)
    bloco_id = db.Column(db.Integer, db.ForeignKey("bloco.id"), nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(255), nullable=True)
    ativo = db.Column(db.Boolean, default=True, nullable=False)
    ordem = db.Column(db.Integer, default=0, nullable=False)

    # Relacionamentos
    bloco = db.relationship("Bloco", back_populates="ambientes")
    atividades = db.relationship("Atividade", back_populates="ambiente")
    vistorias = db.relationship("Vistoria", back_populates="ambiente")

    def __repr__(self):
        return f"<Ambiente {self.nome} / Bloco {self.bloco_id}>"
