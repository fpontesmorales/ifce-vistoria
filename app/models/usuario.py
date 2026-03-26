from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, login_manager


class Usuario(UserMixin, db.Model):
    __tablename__ = "usuario"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    senha_hash = db.Column(db.String(256), nullable=False)
    perfil = db.Column(db.String(20), nullable=False, default="colaborador")
    # perfil: colaborador | coordenacao | admin
    ativo = db.Column(db.Boolean, default=True, nullable=False)
    criado_em = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relacionamentos
    colaborador = db.relationship("Colaborador", back_populates="usuario", uselist=False)
    atividades_validadas = db.relationship(
        "Atividade", foreign_keys="Atividade.validado_por_id", back_populates="validado_por_usuario"
    )

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def check_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)

    @property
    def is_admin(self):
        return self.perfil == "admin"

    @property
    def is_coordenacao(self):
        return self.perfil in ("coordenacao", "admin")

    @property
    def is_colaborador(self):
        return self.perfil == "colaborador"

    def __repr__(self):
        return f"<Usuario {self.username} [{self.perfil}]>"


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Usuario, int(user_id))
