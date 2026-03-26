from app.extensions import db


class Colaborador(db.Model):
    __tablename__ = "colaborador"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False, unique=True)
    nome_exibicao = db.Column(db.String(120), nullable=False)
    funcao = db.Column(db.String(80), nullable=True)
    ativo = db.Column(db.Boolean, default=True, nullable=False)

    # Relacionamentos
    usuario = db.relationship("Usuario", back_populates="colaborador")
    atividades = db.relationship("Atividade", foreign_keys="Atividade.colaborador_id", back_populates="colaborador")
    vistorias = db.relationship("Vistoria", back_populates="colaborador")

    def __repr__(self):
        return f"<Colaborador {self.nome_exibicao}>"
