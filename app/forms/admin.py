from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SelectField,
    TextAreaField, IntegerField, SubmitField,
)
from wtforms.validators import DataRequired, Optional, Length, EqualTo, ValidationError, NumberRange
from app.extensions import db
from app.models.usuario import Usuario


PERFIS = [
    ("colaborador", "Colaborador"),
    ("coordenacao", "Coordenação"),
    ("admin", "Admin"),
]


# ─── Bloco ───────────────────────────────────────────────────────────────────

class BlocoForm(FlaskForm):
    nome = StringField("Nome", validators=[DataRequired(message="Informe o nome."), Length(max=100)])
    descricao = StringField("Descrição", validators=[Optional(), Length(max=255)])
    ordem = IntegerField(
        "Ordem de exibição",
        default=0,
        validators=[Optional(), NumberRange(min=0, message="Deve ser um número positivo.")],
    )
    submit = SubmitField("Salvar")


# ─── Ambiente ────────────────────────────────────────────────────────────────

class AmbienteForm(FlaskForm):
    bloco_id = SelectField("Bloco", coerce=int, validators=[DataRequired(message="Selecione o bloco.")])
    nome = StringField("Nome", validators=[DataRequired(message="Informe o nome."), Length(max=100)])
    descricao = StringField("Descrição", validators=[Optional(), Length(max=255)])
    ordem = IntegerField(
        "Ordem de exibição",
        default=0,
        validators=[Optional(), NumberRange(min=0, message="Deve ser um número positivo.")],
    )
    submit = SubmitField("Salvar")


# ─── Usuário ─────────────────────────────────────────────────────────────────

class UsuarioCriarForm(FlaskForm):
    nome = StringField("Nome completo", validators=[DataRequired(), Length(max=120)])
    username = StringField(
        "Usuário (login)",
        validators=[DataRequired(), Length(min=3, max=64, message="Entre 3 e 64 caracteres.")],
    )
    perfil = SelectField("Perfil", choices=PERFIS, validators=[DataRequired()])
    senha = PasswordField(
        "Senha",
        validators=[DataRequired(), Length(min=6, message="Mínimo 6 caracteres.")],
    )
    senha_confirmacao = PasswordField(
        "Confirmar senha",
        validators=[DataRequired(), EqualTo("senha", message="As senhas não conferem.")],
    )
    submit = SubmitField("Salvar")

    def validate_username(self, field):
        existe = db.session.scalar(
            db.select(Usuario).where(Usuario.username == field.data.strip())
        )
        if existe:
            raise ValidationError("Este nome de usuário já está em uso.")


class UsuarioEditForm(FlaskForm):
    nome = StringField("Nome completo", validators=[DataRequired(), Length(max=120)])
    username = StringField(
        "Usuário (login)",
        validators=[DataRequired(), Length(min=3, max=64, message="Entre 3 e 64 caracteres.")],
    )
    perfil = SelectField("Perfil", choices=PERFIS, validators=[DataRequired()])
    nova_senha = PasswordField(
        "Nova senha",
        validators=[Optional(), Length(min=6, message="Mínimo 6 caracteres.")],
    )
    nova_senha_confirmacao = PasswordField(
        "Confirmar nova senha",
        validators=[EqualTo("nova_senha", message="As senhas não conferem.")],
    )
    submit = SubmitField("Salvar")

    def __init__(self, usuario_id, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._usuario_id = usuario_id

    def validate_username(self, field):
        existe = db.session.scalar(
            db.select(Usuario).where(
                Usuario.username == field.data.strip(),
                Usuario.id != self._usuario_id,
            )
        )
        if existe:
            raise ValidationError("Este nome de usuário já está em uso.")


# ─── Colaborador ─────────────────────────────────────────────────────────────

class ColaboradorForm(FlaskForm):
    usuario_id = SelectField(
        "Usuário vinculado",
        coerce=int,
        validators=[DataRequired(message="Selecione o usuário.")],
    )
    nome_exibicao = StringField(
        "Nome de exibição",
        validators=[DataRequired(), Length(max=120)],
    )
    funcao = StringField("Função", validators=[Optional(), Length(max=80)])
    submit = SubmitField("Salvar")


# ─── Atividade ───────────────────────────────────────────────────────────────

class AtividadeForm(FlaskForm):
    titulo = StringField("Título", validators=[DataRequired(), Length(max=150)])
    descricao = TextAreaField("Descrição", validators=[Optional()])
    tipo = SelectField("Tipo", validators=[DataRequired()])
    colaborador_id = SelectField(
        "Colaborador",
        coerce=int,
        validators=[DataRequired(message="Selecione o colaborador.")],
    )
    bloco_id = SelectField("Bloco (opcional)", coerce=int)
    ambiente_id = SelectField("Ambiente (opcional)", coerce=int)
    observacoes = TextAreaField("Observações", validators=[Optional()])
    submit = SubmitField("Salvar")


# ─── Ocorrência (admin) ───────────────────────────────────────────────────────

class OcorrenciaAdminForm(FlaskForm):
    status = SelectField("Status", validators=[DataRequired()])
    prioridade = SelectField("Prioridade", validators=[DataRequired()])
    observacoes_coordenacao = TextAreaField("Observações da coordenação", validators=[Optional()])
    submit = SubmitField("Atualizar")
