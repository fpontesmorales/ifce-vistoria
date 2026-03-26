from flask_wtf import FlaskForm
from wtforms import SelectField, TextAreaField, StringField, SubmitField
from wtforms.validators import DataRequired, Optional, Length
from app.models.ocorrencia import Ocorrencia


class OcorrenciaForm(FlaskForm):
    categoria = SelectField(
        "Categoria",
        choices=Ocorrencia.CATEGORIAS,
        validators=[DataRequired(message="Selecione uma categoria.")],
    )
    descricao = TextAreaField(
        "Descrição",
        validators=[
            DataRequired(message="A descrição é obrigatória."),
            Length(max=2000),
        ],
        render_kw={"rows": 4, "placeholder": "Descreva detalhadamente o problema encontrado…"},
    )
    prioridade = SelectField(
        "Prioridade",
        choices=Ocorrencia.PRIORIDADES,
        default="media",
        validators=[DataRequired()],
    )
    risco = SelectField(
        "Risco",
        choices=Ocorrencia.RISCOS,
        default="medio",
        validators=[DataRequired()],
    )
    material_sugerido = StringField(
        "Material sugerido",
        validators=[Optional(), Length(max=255)],
        render_kw={"placeholder": "Ex: tinta acrílica, disjuntor 20A, silicone…"},
    )
    observacoes = TextAreaField(
        "Observações",
        validators=[Optional()],
        render_kw={"rows": 3, "placeholder": "Informações complementares, contexto ou urgência…"},
    )
    submit = SubmitField("Registrar ocorrência")
