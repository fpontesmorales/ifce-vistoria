from datetime import datetime, timezone
from app.extensions import db


class Ocorrencia(db.Model):
    __tablename__ = "ocorrencia"

    id = db.Column(db.Integer, primary_key=True)
    vistoria_id = db.Column(db.Integer, db.ForeignKey("vistoria.id"), nullable=False)
    categoria = db.Column(db.String(30), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    prioridade = db.Column(db.String(10), nullable=False, default="media")
    # prioridade: baixa | media | alta
    risco = db.Column(db.String(10), nullable=False, default="medio")
    # risco: baixo | medio | alto
    material_sugerido = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), nullable=False, default="registrada")
    # status: registrada | em_analise | planejada | executada | nao_procede
    observacoes = db.Column(db.Text, nullable=True)
    observacoes_coordenacao = db.Column(db.Text, nullable=True)
    criado_em = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    atualizado_em = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relacionamentos
    vistoria = db.relationship("Vistoria", back_populates="ocorrencias")

    CATEGORIAS = [
        ("eletrica", "Elétrica"),
        ("hidraulica", "Hidráulica"),
        ("civil", "Civil"),
        ("pintura", "Pintura"),
        ("esquadrias", "Esquadrias"),
        ("cobertura", "Cobertura"),
        ("mobiliario", "Mobiliário"),
        ("limpeza_conservacao", "Limpeza / Conservação"),
        ("seguranca", "Segurança"),
        ("outros", "Outros"),
    ]

    PRIORIDADES = [
        ("baixa", "Baixa"),
        ("media", "Média"),
        ("alta", "Alta"),
    ]

    RISCOS = [
        ("baixo", "Baixo"),
        ("medio", "Médio"),
        ("alto", "Alto"),
    ]

    STATUS = [
        ("registrada", "Registrada"),
        ("em_analise", "Em análise"),
        ("planejada", "Planejada"),
        ("executada", "Executada"),
        ("nao_procede", "Não procede"),
    ]

    def __repr__(self):
        return f"<Ocorrencia #{self.id} [{self.categoria}] [{self.status}]>"
