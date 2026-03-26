from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required
from app.extensions import db
from app.models.bloco import Bloco
from app.models.ambiente import Ambiente
from app.models.vistoria import Vistoria
from app.forms.vistoria import VistoriaForm
from app.utils import requer_colaborador, get_colaborador_ou_404

bp = Blueprint("vistorias", __name__, url_prefix="/vistorias")


# ─── Nova vistoria ─────────────────────────────────────────────────────────────

@bp.route("/nova/<int:ambiente_id>", methods=["GET", "POST"])
@login_required
@requer_colaborador
def nova(ambiente_id):
    colaborador = get_colaborador_ou_404()

    ambiente = db.session.get(Ambiente, ambiente_id)
    if ambiente is None or not ambiente.ativo:
        abort(404)

    bloco = db.session.get(Bloco, ambiente.bloco_id)
    if bloco is None or not bloco.ativo:
        abort(404)

    form = VistoriaForm()

    if form.validate_on_submit():
        vistoria = Vistoria(
            colaborador_id=colaborador.id,
            bloco_id=bloco.id,
            ambiente_id=ambiente.id,
            data_vistoria=form.data_vistoria.data,
            situacao_geral=form.situacao_geral.data,
            observacoes=form.observacoes.data or None,
            status="registrada",
        )
        db.session.add(vistoria)
        db.session.commit()

        flash(
            f"Vistoria em «{ambiente.nome}» registrada com sucesso.",
            "success",
        )
        return redirect(url_for("vistorias.detalhe", vistoria_id=vistoria.id))

    # Histórico de vistorias neste ambiente (mais recentes primeiro)
    historico = db.session.scalars(
        db.select(Vistoria)
        .where(Vistoria.ambiente_id == ambiente_id)
        .order_by(Vistoria.data_vistoria.desc())
        .limit(5)
    ).all()

    return render_template(
        "vistorias/nova.html",
        form=form,
        ambiente=ambiente,
        bloco=bloco,
        colaborador=colaborador,
        historico=historico,
    )


# ─── Detalhe de uma vistoria ──────────────────────────────────────────────────

@bp.route("/<int:vistoria_id>")
@login_required
@requer_colaborador
def detalhe(vistoria_id):
    colaborador = get_colaborador_ou_404()

    vistoria = db.session.scalar(
        db.select(Vistoria).where(
            Vistoria.id == vistoria_id,
            Vistoria.colaborador_id == colaborador.id,
        )
    )
    if vistoria is None:
        abort(404)

    return render_template(
        "vistorias/detalhe.html",
        vistoria=vistoria,
        colaborador=colaborador,
    )
