from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    username = StringField(
        "Usuário",
        validators=[DataRequired(message="Informe o usuário."), Length(min=3, max=64)],
    )
    senha = PasswordField(
        "Senha",
        validators=[DataRequired(message="Informe a senha.")],
    )
    lembrar = BooleanField("Manter conectado")
    submit = SubmitField("Entrar")
