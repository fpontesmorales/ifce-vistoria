from datetime import datetime, timedelta, timezone
from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from sqlalchemy.orm import selectinload
from app.extensions import db
from app.models.colaborador import Colaborador
from app.models.atividade import Atividade, AtividadeColaborador
from app.models.vistoria import Vistoria
from app.models.ocorrencia import Ocorrencia
from app.models.bloco import Bloco
from app.models.ambiente import Ambiente
from app.utils import requer_colaborador, get_colaborador_ou_404

bp = Blueprint("colaborador", __name__, url_prefix="/painel")

# Transições de status permitidas ao colaborador (não pode validar)
_PROXIMOS_STATUS = {
    "pendente": "em_andamento",
    "em_andamento": "concluida",
}

_LABEL_PROXIMO = {
    "pendente": "Iniciar",
    "em_andamento": "Concluir",
}


def _filtro_atividade_para_colaborador(colaborador_id):
    alocado_no_time = db.select(AtividadeColaborador.id).where(
        AtividadeColaborador.atividade_id == Atividade.id,
        AtividadeColaborador.colaborador_id == colaborador_id,
    ).exists()
    return db.or_(
        Atividade.colaborador_id == colaborador_id,
        alocado_no_time,
    )


# ─── Painel ───────────────────────────────────────────────────────────────────

@bp.route("/")
@login_required
@requer_colaborador
def painel():
    colaborador = get_colaborador_ou_404()

    pendentes = db.session.scalar(
        db.select(db.func.count(Atividade.id)).where(
            _filtro_atividade_para_colaborador(colaborador.id),
            Atividade.status == "pendente",
        )
    ) or 0

    em_andamento = db.session.scalar(
        db.select(db.func.count(Atividade.id)).where(
            _filtro_atividade_para_colaborador(colaborador.id),
            Atividade.status == "em_andamento",
        )
    ) or 0

    total_vistorias = db.session.scalar(
        db.select(db.func.count(Vistoria.id)).where(
            Vistoria.colaborador_id == colaborador.id
        )
    ) or 0

    total_ocorrencias = db.session.scalar(
        db.select(db.func.count(Ocorrencia.id))
        .join(Vistoria, Ocorrencia.vistoria_id == Vistoria.id)
        .where(Vistoria.colaborador_id == colaborador.id)
    ) or 0

    # Atividades ativas (pendente + em_andamento), mais recentes primeiro
    atividades_ativas = db.session.scalars(
        db.select(Atividade)
        .options(
            selectinload(Atividade.colaborador),
            selectinload(Atividade.alocacoes).selectinload(AtividadeColaborador.colaborador),
        )
        .where(
            _filtro_atividade_para_colaborador(colaborador.id),
            Atividade.status.in_(["pendente", "em_andamento"]),
        )
        .order_by(Atividade.criado_em.desc())
        .limit(5)
    ).all()

    # Últimas vistorias
    ultimas_vistorias = db.session.scalars(
        db.select(Vistoria)
        .where(Vistoria.colaborador_id == colaborador.id)
        .order_by(Vistoria.data_vistoria.desc())
        .limit(3)
    ).all()

    # Ocorrências recentes registradas pelo colaborador
    ultimas_ocorrencias = db.session.scalars(
        db.select(Ocorrencia)
        .join(Vistoria, Ocorrencia.vistoria_id == Vistoria.id)
        .where(Vistoria.colaborador_id == colaborador.id)
        .order_by(Ocorrencia.criado_em.desc())
        .limit(3)
    ).all()

    # Vistorias realizadas hoje (UTC — consistente com os timestamps dos models)
    hoje_inicio = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    amanha_inicio = hoje_inicio + timedelta(days=1)
    vistorias_hoje = db.session.scalar(
        db.select(db.func.count(Vistoria.id)).where(
            Vistoria.colaborador_id == colaborador.id,
            Vistoria.data_vistoria >= hoje_inicio,
            Vistoria.data_vistoria < amanha_inicio,
        )
    ) or 0

    return render_template(
        "colaborador/painel.html",
        colaborador=colaborador,
        pendentes=pendentes,
        em_andamento=em_andamento,
        total_vistorias=total_vistorias,
        total_ocorrencias=total_ocorrencias,
        atividades_ativas=atividades_ativas,
        ultimas_vistorias=ultimas_vistorias,
        ultimas_ocorrencias=ultimas_ocorrencias,
        vistorias_hoje=vistorias_hoje,
        proximos_status=_PROXIMOS_STATUS,
        label_proximo=_LABEL_PROXIMO,
    )


# ─── Atividades ───────────────────────────────────────────────────────────────

@bp.route("/atividades")
@login_required
@requer_colaborador
def atividades():
    colaborador = get_colaborador_ou_404()

    filtro = (
        db.select(Atividade)
        .options(
            selectinload(Atividade.colaborador),
            selectinload(Atividade.alocacoes).selectinload(AtividadeColaborador.colaborador),
        )
        .where(_filtro_atividade_para_colaborador(colaborador.id))
        .order_by(Atividade.criado_em.desc())
    )

    todas = db.session.scalars(filtro).all()

    # Agrupamentos para os cards de resumo
    contagens = {s: 0 for s, _ in Atividade.STATUS}
    for a in todas:
        if a.status in contagens:
            contagens[a.status] += 1

    return render_template(
        "colaborador/atividades.html",
        colaborador=colaborador,
        atividades=todas,
        contagens=contagens,
        proximos_status=_PROXIMOS_STATUS,
        label_proximo=_LABEL_PROXIMO,
    )


@bp.route("/atividades/<int:id>/status", methods=["POST"])
@login_required
@requer_colaborador
def atividade_status(id):
    colaborador = get_colaborador_ou_404()

    atividade = db.session.scalar(
        db.select(Atividade).where(
            Atividade.id == id,
            _filtro_atividade_para_colaborador(colaborador.id),
        )
    )

    if atividade is None:
        abort(404)

    # Valida transição — colaborador não pode validar
    if atividade.status not in _PROXIMOS_STATUS:
        flash("Esta atividade não pode ser avançada.", "warning")
        return redirect(url_for("colaborador.atividades"))

    atividade.avancar_status(current_user)
    db.session.commit()

    flash(
        f"Atividade «{atividade.titulo}» atualizada para "
        f"«{dict(Atividade.STATUS).get(atividade.status, atividade.status)}».",
        "success",
    )
    return redirect(url_for("colaborador.atividades"))


# ─── Finalizar vistoria ───────────────────────────────────────────────────────

@bp.route("/vistorias/<int:vistoria_id>/finalizar", methods=["POST"])
@login_required
@requer_colaborador
def vistoria_finalizar(vistoria_id):
    colaborador = get_colaborador_ou_404()

    vistoria = db.session.scalar(
        db.select(Vistoria).where(
            Vistoria.id == vistoria_id,
            Vistoria.colaborador_id == colaborador.id,
        )
    )
    if vistoria is None:
        abort(404)

    if vistoria.status != "registrada":
        flash("Esta vistoria já foi finalizada.", "info")
    else:
        vistoria.finalizar()
        db.session.commit()
        flash(f"Vistoria em «{vistoria.ambiente.nome}» finalizada.", "success")

    return redirect(url_for("vistorias.detalhe", vistoria_id=vistoria_id))


# ─── Blocos ───────────────────────────────────────────────────────────────────

@bp.route("/blocos")
@login_required
@requer_colaborador
def blocos():
    colaborador = get_colaborador_ou_404()

    blocos_ativos = db.session.scalars(
        db.select(Bloco)
        .where(Bloco.ativo == True)  # noqa: E712
        .order_by(Bloco.ordem, Bloco.nome)
    ).all()

    ambientes_ativos = db.session.scalars(
        db.select(Ambiente)
        .where(
            Ambiente.bloco_id.in_([b.id for b in blocos_ativos]),
            Ambiente.ativo == True,  # noqa: E712
        )
    ).all() if blocos_ativos else []

    # Agrupa IDs de ambientes por bloco
    amb_por_bloco: dict = {b.id: [] for b in blocos_ativos}
    for a in ambientes_ativos:
        amb_por_bloco[a.bloco_id].append(a.id)

    # Última vistoria por ambiente (uma query só)
    ultima_por_ambiente: dict = {}
    if ambientes_ativos:
        ultima_sq = (
            db.select(
                Vistoria.ambiente_id,
                db.func.max(Vistoria.data_vistoria).label("ultima_data"),
            )
            .group_by(Vistoria.ambiente_id)
            .subquery()
        )
        ultimas = db.session.scalars(
            db.select(Vistoria).join(
                ultima_sq,
                db.and_(
                    Vistoria.ambiente_id == ultima_sq.c.ambiente_id,
                    Vistoria.data_vistoria == ultima_sq.c.ultima_data,
                ),
            ).where(Vistoria.ambiente_id.in_([a.id for a in ambientes_ativos]))
        ).all()
        ultima_por_ambiente = {v.ambiente_id: v for v in ultimas}

    # Estatísticas por bloco
    stats: dict = {}
    for b in blocos_ativos:
        ids = amb_por_bloco[b.id]
        total = len(ids)
        vistoriados = sum(1 for aid in ids if aid in ultima_por_ambiente)
        com_pendencia = sum(
            1 for aid in ids
            if aid in ultima_por_ambiente
            and ultima_por_ambiente[aid].situacao_geral == "com_pendencia"
        )
        stats[b.id] = {
            "total": total,
            "vistoriados": vistoriados,
            "nao_vistoriados": total - vistoriados,
            "com_pendencia": com_pendencia,
        }

    return render_template(
        "colaborador/blocos.html",
        colaborador=colaborador,
        blocos=blocos_ativos,
        stats=stats,
    )


# ─── Ambientes de um bloco ─────────────────────────────────────────────────────

@bp.route("/blocos/<int:bloco_id>/ambientes")
@login_required
@requer_colaborador
def ambientes_do_bloco(bloco_id):
    colaborador = get_colaborador_ou_404()

    bloco = db.session.get(Bloco, bloco_id)
    if bloco is None or not bloco.ativo:
        abort(404)

    ambientes = db.session.scalars(
        db.select(Ambiente)
        .where(Ambiente.bloco_id == bloco_id, Ambiente.ativo == True)  # noqa: E712
        .order_by(Ambiente.ordem, Ambiente.nome)
    ).all()

    ultima_por_ambiente: dict = {}
    if ambientes:
        ultima_sq = (
            db.select(
                Vistoria.ambiente_id,
                db.func.max(Vistoria.data_vistoria).label("ultima_data"),
            )
            .group_by(Vistoria.ambiente_id)
            .subquery()
        )
        ultimas = db.session.scalars(
            db.select(Vistoria).join(
                ultima_sq,
                db.and_(
                    Vistoria.ambiente_id == ultima_sq.c.ambiente_id,
                    Vistoria.data_vistoria == ultima_sq.c.ultima_data,
                ),
            ).where(Vistoria.ambiente_id.in_([a.id for a in ambientes]))
        ).all()
        ultima_por_ambiente = {v.ambiente_id: v for v in ultimas}

    nao_vistoriados = sum(1 for a in ambientes if a.id not in ultima_por_ambiente)
    com_pendencia = sum(
        1 for a in ambientes
        if a.id in ultima_por_ambiente
        and ultima_por_ambiente[a.id].situacao_geral == "com_pendencia"
    )

    return render_template(
        "colaborador/ambientes.html",
        colaborador=colaborador,
        bloco=bloco,
        ambientes=ambientes,
        ultima_por_ambiente=ultima_por_ambiente,
        nao_vistoriados=nao_vistoriados,
        com_pendencia=com_pendencia,
    )


# ─── Histórico ────────────────────────────────────────────────────────────────

@bp.route("/historico")
@login_required
@requer_colaborador
def historico():
    colaborador = get_colaborador_ou_404()

    atividades_hist = db.session.scalars(
        db.select(Atividade)
        .options(
            selectinload(Atividade.colaborador),
            selectinload(Atividade.alocacoes).selectinload(AtividadeColaborador.colaborador),
        )
        .where(_filtro_atividade_para_colaborador(colaborador.id))
        .order_by(Atividade.criado_em.desc())
    ).all()

    vistorias_hist = db.session.scalars(
        db.select(Vistoria)
        .where(Vistoria.colaborador_id == colaborador.id)
        .order_by(Vistoria.data_vistoria.desc())
    ).all()

    ocorrencias_hist = db.session.scalars(
        db.select(Ocorrencia)
        .join(Vistoria, Ocorrencia.vistoria_id == Vistoria.id)
        .where(Vistoria.colaborador_id == colaborador.id)
        .order_by(Ocorrencia.criado_em.desc())
    ).all()

    return render_template(
        "colaborador/historico.html",
        colaborador=colaborador,
        atividades=atividades_hist,
        vistorias=vistorias_hist,
        ocorrencias=ocorrencias_hist,
    )
