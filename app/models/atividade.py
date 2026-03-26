from datetime import datetime, timezone
from app.extensions import db


class AtividadeColaborador(db.Model):
    __tablename__ = "atividade_colaborador"
    __table_args__ = (
        db.UniqueConstraint("atividade_id", "colaborador_id", name="uq_atividade_colaborador"),
    )

    id = db.Column(db.Integer, primary_key=True)
    atividade_id = db.Column(db.Integer, db.ForeignKey("atividade.id"), nullable=False)
    colaborador_id = db.Column(db.Integer, db.ForeignKey("colaborador.id"), nullable=False)
    criado_em = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    atividade = db.relationship("Atividade", back_populates="alocacoes")
    colaborador = db.relationship("Colaborador", back_populates="alocacoes_atividade")

    def __repr__(self):
        return f"<AtividadeColaborador atividade={self.atividade_id} colaborador={self.colaborador_id}>"


class Atividade(db.Model):
    __tablename__ = "atividade"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(150), nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    tipo = db.Column(db.String(30), nullable=False, default="reconhecimento")
    # tipo: integracao | reconhecimento | vistoria | apoio
    status = db.Column(db.String(20), nullable=False, default="pendente")
    # status: pendente | em_andamento | concluida | validada

    colaborador_id = db.Column(db.Integer, db.ForeignKey("colaborador.id"), nullable=False)
    bloco_id = db.Column(db.Integer, db.ForeignKey("bloco.id"), nullable=True)
    ambiente_id = db.Column(db.Integer, db.ForeignKey("ambiente.id"), nullable=True)

    criado_em = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    iniciado_em = db.Column(db.DateTime, nullable=True)
    concluido_em = db.Column(db.DateTime, nullable=True)
    validado_em = db.Column(db.DateTime, nullable=True)
    validado_por_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=True)

    observacoes = db.Column(db.Text, nullable=True)

    # Relacionamentos
    colaborador = db.relationship("Colaborador", foreign_keys=[colaborador_id], back_populates="atividades")
    alocacoes = db.relationship(
        "AtividadeColaborador",
        back_populates="atividade",
        cascade="all, delete-orphan",
    )
    bloco = db.relationship("Bloco", back_populates="atividades")
    ambiente = db.relationship("Ambiente", back_populates="atividades")
    validado_por_usuario = db.relationship(
        "Usuario", foreign_keys=[validado_por_id], back_populates="atividades_validadas"
    )

    TIPOS = [
        ("integracao", "Integração"),
        ("reconhecimento", "Reconhecimento"),
        ("vistoria", "Vistoria"),
        ("apoio", "Apoio"),
    ]

    STATUS = [
        ("pendente", "Pendente"),
        ("em_andamento", "Em andamento"),
        ("concluida", "Concluída"),
        ("validada", "Validada"),
    ]

    def avancar_status(self, usuario):
        now = datetime.now(timezone.utc)
        if self.status == "pendente":
            self.status = "em_andamento"
            self.iniciado_em = now
        elif self.status == "em_andamento":
            self.status = "concluida"
            self.concluido_em = now

    def validar(self, usuario):
        if self.status == "concluida":
            self.status = "validada"
            self.validado_em = datetime.now(timezone.utc)
            self.validado_por_id = usuario.id

    def reabrir(self):
        """Coordenação reabre atividade validada → volta para concluida."""
        if self.status == "validada":
            self.status = "concluida"
            self.validado_em = None
            self.validado_por_id = None

    @property
    def colaboradores_designados(self):
        """Lista de colaboradores atribuídos (com fallback para legado)."""
        if self.alocacoes:
            vinculados = [aloc.colaborador for aloc in self.alocacoes if aloc.colaborador]
            vinculados.sort(key=lambda c: (c.id != self.colaborador_id, c.nome_exibicao.lower()))
            return vinculados
        return [self.colaborador] if self.colaborador else []

    @property
    def colaboradores_nomes(self):
        nomes = [c.nome_exibicao for c in self.colaboradores_designados]
        return ", ".join(nomes)

    @property
    def total_colaboradores(self):
        return len(self.colaboradores_designados)

    def __repr__(self):
        return f"<Atividade {self.titulo} [{self.status}]>"
