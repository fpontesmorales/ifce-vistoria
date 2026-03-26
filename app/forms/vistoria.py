from flask_wtf import FlaskForm
from wtforms import SelectField, TextAreaField, DateTimeLocalField, SubmitField
from wtforms.validators import DataRequired
from datetime import datetime


class VistoriaForm(FlaskForm):
    data_vistoria = DateTimeLocalField(
        "Data e hora",
        format="%Y-%m-%dT%H:%M",
        validators=[DataRequired(message="Informe a data e hora da vistoria.")],
        default=datetime.now,
    )
    situacao_geral = SelectField(
        "Situação geral",
        choices=[
            ("ok", "OK — sem pendências"),
            ("com_pendencia", "Com pendência"),
        ],
        validators=[DataRequired()],
    )
    observacoes = TextAreaField("Observações", render_kw={"rows": 4})
    submit = SubmitField("Registrar vistoria")
