from datetime import datetime, timezone
from app.extensions import db


class Vistoria(db.Model):
    __tablename__ = "vistoria"

    id = db.Column(db.Integer, primary_key=True)
    data_vistoria = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    colaborador_id = db.Column(db.Integer, db.ForeignKey("colaborador.id"), nullable=False)
    bloco_id = db.Column(db.Integer, db.ForeignKey("bloco.id"), nullable=False)
    ambiente_id = db.Column(db.Integer, db.ForeignKey("ambiente.id"), nullable=False)
    situacao_geral = db.Column(db.String(20), nullable=False, default="ok")
    # situacao_geral: ok | com_pendencia
    observacoes = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default="registrada")
    # status: registrada | finalizada

    # Relacionamentos
    colaborador = db.relationship("Colaborador", back_populates="vistorias")
    bloco = db.relationship("Bloco", back_populates="vistorias")
    ambiente = db.relationship("Ambiente", back_populates="vistorias")
    # passive_deletes=True preserva ocorrências no histórico se a vistoria for deletada via SQL direto.
    # delete-orphan mantido apenas para remoção via ORM (que não exposta em nenhuma rota do MVP).
    ocorrencias = db.relationship("Ocorrencia", back_populates="vistoria",
                                  cascade="save-update, merge, delete, delete-orphan",
                                  passive_deletes=True)

    SITUACOES = [
        ("ok", "OK — sem pendências"),
        ("com_pendencia", "Com pendência"),
    ]

    STATUS = [
        ("registrada", "Registrada"),
        ("finalizada", "Finalizada"),
    ]

    def finalizar(self):
        """Colaborador finaliza a vistoria após registrar todas as ocorrências."""
        if self.status == "registrada":
            self.status = "finalizada"

    def __repr__(self):
        return f"<Vistoria #{self.id} Ambiente {self.ambiente_id} [{self.situacao_geral}]>"
