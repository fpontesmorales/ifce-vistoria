# Estrutura preparada para uso futuro — tabela NÃO criada no MVP.
# Descomente e rode db.create_all() quando o upload de fotos for implementado.
#
# from datetime import datetime, timezone
# from app.extensions import db
#
# class AnexoFoto(db.Model):
#     __tablename__ = "anexo_foto"
#
#     id            = db.Column(db.Integer, primary_key=True)
#     ocorrencia_id = db.Column(db.Integer, db.ForeignKey("ocorrencia.id"), nullable=False)
#     arquivo       = db.Column(db.String(255), nullable=False)   # caminho no servidor
#     nome_original = db.Column(db.String(255), nullable=False)   # nome enviado pelo usuário
#     criado_em     = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
#
#     ocorrencia = db.relationship("Ocorrencia", back_populates="fotos")
