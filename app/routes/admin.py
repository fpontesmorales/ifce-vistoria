import json
from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, Response
from flask_login import login_required, current_user
from sqlalchemy.orm import selectinload
from app.extensions import db
from app.models.bloco import Bloco
from app.models.ambiente import Ambiente
from app.models.usuario import Usuario
from app.models.colaborador import Colaborador
from app.models.atividade import Atividade, AtividadeColaborador
from app.models.ocorrencia import Ocorrencia
from app.models.vistoria import Vistoria
from app.forms.admin import (
    BlocoForm, AmbienteForm,
    UsuarioCriarForm, UsuarioEditForm,
    ColaboradorForm, AtividadeForm,
    OcorrenciaAdminForm,
)
from app.utils import requer_coordenacao

bp = Blueprint("admin", __name__, url_prefix="/admin")


def _popular_choices_atividade(form):
    colaboradores = db.session.scalars(
        db.select(Colaborador).join(Usuario)
        .where(Colaborador.ativo == True)  # noqa: E712
        .order_by(Colaborador.nome_exibicao)
    ).all()
    blocos = db.session.scalars(
        db.select(Bloco).where(Bloco.ativo == True).order_by(Bloco.ordem, Bloco.nome)  # noqa: E712
    ).all()
    ambientes = db.session.scalars(
        db.select(Ambiente).join(Bloco)
        .where(Ambiente.ativo == True)  # noqa: E712
        .order_by(Bloco.nome, Ambiente.nome)
    ).all()
    form.tipo.choices = Atividade.TIPOS
    form.colaborador_id.choices = [(c.id, c.nome_exibicao) for c in colaboradores]
    form.colaboradores_ids.choices = [(c.id, c.nome_exibicao) for c in colaboradores]
    form.bloco_id.choices = [(0, "— nenhum —")] + [(b.id, b.nome) for b in blocos]
    form.ambiente_id.choices = [(0, "— nenhum —")] + [
        (a.id, f"{a.bloco.nome} / {a.nome}") for a in ambientes
    ]
    return colaboradores, blocos, ambientes


def _normalizar_bloco_ambiente_atividade(form):
    """Valida consistência bloco/ambiente e normaliza IDs finais."""
    bloco_id = form.bloco_id.data or None
    ambiente_id = form.ambiente_id.data or None

    if ambiente_id is None:
        return True, bloco_id, None

    ambiente = db.session.get(Ambiente, ambiente_id)
    if ambiente is None:
        flash("Ambiente selecionado é inválido.", "danger")
        return False, bloco_id, ambiente_id

    # Se o usuário escolher só o ambiente, inferimos automaticamente o bloco.
    if bloco_id is None:
        return True, ambiente.bloco_id, ambiente_id

    if ambiente.bloco_id != bloco_id:
        flash("O ambiente selecionado não pertence ao bloco escolhido.", "danger")
        return False, bloco_id, ambiente_id

    return True, bloco_id, ambiente_id


def _normalizar_colaboradores_destino(colaborador_principal_id, colaboradores_adicionais_ids):
    destino = [colaborador_principal_id]
    for colaborador_id in colaboradores_adicionais_ids or []:
        if colaborador_id and colaborador_id not in destino:
            destino.append(colaborador_id)
    return destino


def _sincronizar_alocacoes_atividade(atividade, colaboradores_ids):
    """Mantém a lista de colaboradores vinculados à atividade (N:N)."""
    desejados = set(colaboradores_ids or [])
    if atividade.colaborador_id:
        desejados.add(atividade.colaborador_id)

    atuais = {aloc.colaborador_id: aloc for aloc in atividade.alocacoes}
    for colaborador_id, aloc in list(atuais.items()):
        if colaborador_id not in desejados:
            atividade.alocacoes.remove(aloc)

    for colaborador_id in desejados:
        if colaborador_id not in atuais:
            atividade.alocacoes.append(AtividadeColaborador(colaborador_id=colaborador_id))


def _filtro_atividade_por_colaborador(colaborador_id):
    alocado_no_time = db.select(AtividadeColaborador.id).where(
        AtividadeColaborador.atividade_id == Atividade.id,
        AtividadeColaborador.colaborador_id == colaborador_id,
    ).exists()
    return db.or_(
        Atividade.colaborador_id == colaborador_id,
        alocado_no_time,
    )


# ─── Painel ──────────────────────────────────────────────────────────────────

@bp.route("/painel")
@login_required
@requer_coordenacao
def painel():
    _STATUS_ABERTOS = ["registrada", "em_analise", "planejada"]

    total_blocos = db.session.scalar(
        db.select(db.func.count(Bloco.id)).where(Bloco.ativo == True)  # noqa: E712
    ) or 0
    total_ambientes = db.session.scalar(
        db.select(db.func.count(Ambiente.id)).where(Ambiente.ativo == True)  # noqa: E712
    ) or 0
    total_ambientes_vistoriados = db.session.scalar(
        db.select(db.func.count(db.func.distinct(Vistoria.ambiente_id)))
    ) or 0
    total_ambientes_pendentes = max(0, total_ambientes - total_ambientes_vistoriados)

    total_atividades_pendentes = db.session.scalar(
        db.select(db.func.count(Atividade.id)).where(
            Atividade.status.in_(["pendente", "em_andamento"])
        )
    ) or 0
    total_atividades_aguardando = db.session.scalar(
        db.select(db.func.count(Atividade.id)).where(Atividade.status == "concluida")
    ) or 0

    total_ocorrencias_abertas = db.session.scalar(
        db.select(db.func.count(Ocorrencia.id)).where(
            Ocorrencia.status.in_(_STATUS_ABERTOS)
        )
    ) or 0
    ocorrencias_alta = db.session.scalar(
        db.select(db.func.count(Ocorrencia.id)).where(
            Ocorrencia.status.in_(_STATUS_ABERTOS),
            Ocorrencia.prioridade == "alta",
        )
    ) or 0
    ocorrencias_media = db.session.scalar(
        db.select(db.func.count(Ocorrencia.id)).where(
            Ocorrencia.status.in_(_STATUS_ABERTOS),
            Ocorrencia.prioridade == "media",
        )
    ) or 0
    ocorrencias_baixa = db.session.scalar(
        db.select(db.func.count(Ocorrencia.id)).where(
            Ocorrencia.status.in_(_STATUS_ABERTOS),
            Ocorrencia.prioridade == "baixa",
        )
    ) or 0

    total_usuarios = db.session.scalar(
        db.select(db.func.count(Usuario.id)).where(Usuario.ativo == True)  # noqa: E712
    ) or 0

    ultimas_vistorias = db.session.scalars(
        db.select(Vistoria).order_by(Vistoria.data_vistoria.desc()).limit(10)
    ).all()
    ultimas_ocorrencias = db.session.scalars(
        db.select(Ocorrencia).order_by(Ocorrencia.criado_em.desc()).limit(10)
    ).all()

    return render_template(
        "admin/painel.html",
        total_blocos=total_blocos,
        total_ambientes=total_ambientes,
        total_ambientes_vistoriados=total_ambientes_vistoriados,
        total_ambientes_pendentes=total_ambientes_pendentes,
        total_atividades_pendentes=total_atividades_pendentes,
        total_atividades_aguardando=total_atividades_aguardando,
        total_ocorrencias_abertas=total_ocorrencias_abertas,
        ocorrencias_alta=ocorrencias_alta,
        ocorrencias_media=ocorrencias_media,
        ocorrencias_baixa=ocorrencias_baixa,
        total_usuarios=total_usuarios,
        ultimas_vistorias=ultimas_vistorias,
        ultimas_ocorrencias=ultimas_ocorrencias,
    )


# ─── Blocos ──────────────────────────────────────────────────────────────────

@bp.route("/blocos")
@login_required
@requer_coordenacao
def blocos_lista():
    blocos = db.session.scalars(db.select(Bloco).order_by(Bloco.ordem, Bloco.nome)).all()
    return render_template("admin/blocos/lista.html", blocos=blocos)


@bp.route("/blocos/novo", methods=["GET", "POST"])
@login_required
@requer_coordenacao
def blocos_novo():
    form = BlocoForm()
    if form.validate_on_submit():
        duplicado = db.session.scalar(
            db.select(Bloco).where(Bloco.nome == form.nome.data.strip())
        )
        if duplicado:
            flash("Já existe um bloco com este nome.", "danger")
        else:
            bloco = Bloco(
                nome=form.nome.data.strip(),
                descricao=form.descricao.data.strip() or None,
                ordem=form.ordem.data if form.ordem.data is not None else 0,
            )
            db.session.add(bloco)
            db.session.commit()
            flash(f"Bloco '{bloco.nome}' criado com sucesso.", "success")
            return redirect(url_for("admin.cadastros", aba="blocos"))
    return render_template("admin/blocos/form.html", form=form, titulo="Novo bloco", bloco=None)


@bp.route("/blocos/<int:id>/editar", methods=["GET", "POST"])
@login_required
@requer_coordenacao
def blocos_editar(id):
    bloco = db.get_or_404(Bloco, id)
    form = BlocoForm(obj=bloco)
    if form.validate_on_submit():
        duplicado = db.session.scalar(
            db.select(Bloco).where(Bloco.nome == form.nome.data.strip(), Bloco.id != id)
        )
        if duplicado:
            flash("Já existe um bloco com este nome.", "danger")
        else:
            bloco.nome = form.nome.data.strip()
            bloco.descricao = form.descricao.data.strip() or None
            bloco.ordem = form.ordem.data if form.ordem.data is not None else 0
            db.session.commit()
            flash(f"Bloco '{bloco.nome}' atualizado.", "success")
            return redirect(url_for("admin.cadastros", aba="blocos"))
    return render_template("admin/blocos/form.html", form=form, titulo="Editar bloco", bloco=bloco)


@bp.route("/blocos/<int:id>/toggle", methods=["POST"])
@login_required
@requer_coordenacao
def blocos_toggle(id):
    bloco = db.get_or_404(Bloco, id)
    bloco.ativo = not bloco.ativo
    db.session.commit()
    flash(f"Bloco '{bloco.nome}' {'ativado' if bloco.ativo else 'inativado'}.", "success")
    return redirect(url_for("admin.blocos_lista"))


# ─── Ambientes ───────────────────────────────────────────────────────────────

@bp.route("/ambientes")
@login_required
@requer_coordenacao
def ambientes_lista():
    blocos_ativos = db.session.scalars(
        db.select(Bloco).where(Bloco.ativo == True).order_by(Bloco.ordem, Bloco.nome)  # noqa: E712
    ).all()
    bloco_id_filtro = request.args.get("bloco_id", type=int)
    query = (
        db.select(Ambiente)
        .join(Bloco)
        .order_by(Bloco.ordem, Bloco.nome, Ambiente.ordem, Ambiente.nome)
    )
    if bloco_id_filtro:
        query = query.where(Ambiente.bloco_id == bloco_id_filtro)
    ambientes = db.session.scalars(query).all()
    return render_template(
        "admin/ambientes/lista.html",
        ambientes=ambientes,
        blocos=blocos_ativos,
        bloco_id_filtro=bloco_id_filtro,
    )


@bp.route("/ambientes/novo", methods=["GET", "POST"])
@login_required
@requer_coordenacao
def ambientes_novo():
    form = AmbienteForm()
    blocos = db.session.scalars(
        db.select(Bloco).where(Bloco.ativo == True).order_by(Bloco.ordem, Bloco.nome)  # noqa: E712
    ).all()
    form.bloco_id.choices = [(b.id, b.nome) for b in blocos]
    if form.validate_on_submit():
        duplicado = db.session.scalar(
            db.select(Ambiente).where(
                Ambiente.bloco_id == form.bloco_id.data,
                Ambiente.nome == form.nome.data.strip(),
            )
        )
        if duplicado:
            flash("Já existe um ambiente com este nome neste bloco.", "danger")
        else:
            ambiente = Ambiente(
                bloco_id=form.bloco_id.data,
                nome=form.nome.data.strip(),
                descricao=form.descricao.data.strip() or None,
                ordem=form.ordem.data if form.ordem.data is not None else 0,
            )
            db.session.add(ambiente)
            db.session.commit()
            flash(f"Ambiente '{ambiente.nome}' criado.", "success")
            return redirect(url_for("admin.cadastros", aba="ambientes"))
    elif request.method == "GET":
        bloco_id_pre = request.args.get("bloco_id", type=int)
        if bloco_id_pre:
            form.bloco_id.data = bloco_id_pre
    return render_template("admin/ambientes/form.html", form=form, titulo="Novo ambiente", ambiente=None)


@bp.route("/ambientes/<int:id>/editar", methods=["GET", "POST"])
@login_required
@requer_coordenacao
def ambientes_editar(id):
    ambiente = db.get_or_404(Ambiente, id)
    form = AmbienteForm(obj=ambiente)
    blocos = db.session.scalars(db.select(Bloco).order_by(Bloco.ordem, Bloco.nome)).all()
    form.bloco_id.choices = [(b.id, b.nome) for b in blocos]
    if form.validate_on_submit():
        duplicado = db.session.scalar(
            db.select(Ambiente).where(
                Ambiente.bloco_id == form.bloco_id.data,
                Ambiente.nome == form.nome.data.strip(),
                Ambiente.id != id,
            )
        )
        if duplicado:
            flash("Já existe um ambiente com este nome neste bloco.", "danger")
        else:
            ambiente.bloco_id = form.bloco_id.data
            ambiente.nome = form.nome.data.strip()
            ambiente.descricao = form.descricao.data.strip() or None
            ambiente.ordem = form.ordem.data if form.ordem.data is not None else 0
            db.session.commit()
            flash(f"Ambiente '{ambiente.nome}' atualizado.", "success")
            return redirect(url_for("admin.cadastros", aba="ambientes"))
    return render_template("admin/ambientes/form.html", form=form, titulo="Editar ambiente", ambiente=ambiente)


@bp.route("/ambientes/<int:id>/toggle", methods=["POST"])
@login_required
@requer_coordenacao
def ambientes_toggle(id):
    ambiente = db.get_or_404(Ambiente, id)
    ambiente.ativo = not ambiente.ativo
    db.session.commit()
    flash(f"Ambiente '{ambiente.nome}' {'ativado' if ambiente.ativo else 'inativado'}.", "success")
    return redirect(url_for("admin.ambientes_lista"))


# ─── Usuários ────────────────────────────────────────────────────────────────

@bp.route("/usuarios")
@login_required
@requer_coordenacao
def usuarios_lista():
    usuarios = db.session.scalars(db.select(Usuario).order_by(Usuario.nome)).all()
    return render_template("admin/usuarios/lista.html", usuarios=usuarios)


@bp.route("/usuarios/novo", methods=["GET", "POST"])
@login_required
@requer_coordenacao
def usuarios_novo():
    form = UsuarioCriarForm()
    if form.validate_on_submit():
        usuario = Usuario(
            nome=form.nome.data.strip(),
            username=form.username.data.strip(),
            perfil=form.perfil.data,
            ativo=True,
        )
        usuario.set_senha(form.senha.data)
        db.session.add(usuario)
        db.session.commit()
        flash(f"Usuário '{usuario.username}' criado.", "success")
        return redirect(url_for("admin.cadastros", aba="usuarios"))
    return render_template("admin/usuarios/form.html", form=form, titulo="Novo usuário", usuario=None)


@bp.route("/usuarios/<int:id>/editar", methods=["GET", "POST"])
@login_required
@requer_coordenacao
def usuarios_editar(id):
    usuario = db.get_or_404(Usuario, id)
    form = UsuarioEditForm(usuario_id=id, obj=usuario)
    if form.validate_on_submit():
        usuario.nome = form.nome.data.strip()
        usuario.username = form.username.data.strip()
        usuario.perfil = form.perfil.data
        if form.nova_senha.data:
            usuario.set_senha(form.nova_senha.data)
        db.session.commit()
        flash(f"Usuário '{usuario.username}' atualizado.", "success")
        return redirect(url_for("admin.cadastros", aba="usuarios"))
    return render_template("admin/usuarios/form.html", form=form, titulo="Editar usuário", usuario=usuario)


@bp.route("/usuarios/<int:id>/toggle", methods=["POST"])
@login_required
@requer_coordenacao
def usuarios_toggle(id):
    usuario = db.get_or_404(Usuario, id)
    if usuario.id == current_user.id:
        flash("Você não pode inativar sua própria conta.", "warning")
        return redirect(url_for("admin.cadastros", aba="usuarios"))
    usuario.ativo = not usuario.ativo
    db.session.commit()
    flash(f"Usuário '{usuario.username}' {'ativado' if usuario.ativo else 'inativado'}.", "success")
    return redirect(url_for("admin.usuarios_lista"))


# ─── Colaboradores ───────────────────────────────────────────────────────────

@bp.route("/colaboradores")
@login_required
@requer_coordenacao
def colaboradores_lista():
    colaboradores = db.session.scalars(
        db.select(Colaborador).join(Usuario).order_by(Colaborador.nome_exibicao)
    ).all()
    return render_template("admin/colaboradores/lista.html", colaboradores=colaboradores)


@bp.route("/colaboradores/novo", methods=["GET", "POST"])
@login_required
@requer_coordenacao
def colaboradores_novo():
    form = ColaboradorForm()
    subq = db.select(Colaborador.usuario_id)
    usuarios_disponiveis = db.session.scalars(
        db.select(Usuario)
        .where(Usuario.perfil == "colaborador")
        .where(Usuario.ativo == True)  # noqa: E712
        .where(~Usuario.id.in_(subq))
        .order_by(Usuario.nome)
    ).all()
    form.usuario_id.choices = [(u.id, f"{u.nome} ({u.username})") for u in usuarios_disponiveis]
    if not usuarios_disponiveis and request.method == "GET":
        flash("Todos os usuários colaboradores já estão vinculados.", "info")
    if form.validate_on_submit():
        colaborador = Colaborador(
            usuario_id=form.usuario_id.data,
            nome_exibicao=form.nome_exibicao.data.strip(),
            funcao=form.funcao.data.strip() or None,
            ativo=True,
        )
        db.session.add(colaborador)
        db.session.commit()
        flash(f"Colaborador '{colaborador.nome_exibicao}' cadastrado.", "success")
        return redirect(url_for("admin.cadastros", aba="colaboradores"))
    return render_template(
        "admin/colaboradores/form.html", form=form, titulo="Novo colaborador", colaborador=None
    )


@bp.route("/colaboradores/<int:id>/editar", methods=["GET", "POST"])
@login_required
@requer_coordenacao
def colaboradores_editar(id):
    colaborador = db.get_or_404(Colaborador, id)
    form = ColaboradorForm(obj=colaborador)
    form.usuario_id.choices = [
        (colaborador.usuario_id, f"{colaborador.usuario.nome} ({colaborador.usuario.username})")
    ]
    if form.validate_on_submit():
        colaborador.nome_exibicao = form.nome_exibicao.data.strip()
        colaborador.funcao = form.funcao.data.strip() or None
        db.session.commit()
        flash(f"Colaborador '{colaborador.nome_exibicao}' atualizado.", "success")
        return redirect(url_for("admin.cadastros", aba="colaboradores"))
    return render_template(
        "admin/colaboradores/form.html", form=form, titulo="Editar colaborador", colaborador=colaborador
    )


@bp.route("/colaboradores/<int:id>/toggle", methods=["POST"])
@login_required
@requer_coordenacao
def colaboradores_toggle(id):
    colaborador = db.get_or_404(Colaborador, id)
    colaborador.ativo = not colaborador.ativo
    db.session.commit()
    flash(
        f"Colaborador '{colaborador.nome_exibicao}' {'ativado' if colaborador.ativo else 'inativado'}.",
        "success",
    )
    return redirect(url_for("admin.colaboradores_lista"))


# ─── Cadastros (Blocos + Ambientes + Colaboradores + Usuários) ───────────────

@bp.route("/cadastros")
@login_required
@requer_coordenacao
def cadastros():
    aba = request.args.get("aba", "blocos")
    bloco_id_filtro = request.args.get("bloco_id", type=int)

    blocos = db.session.scalars(
        db.select(Bloco).order_by(Bloco.ordem, Bloco.nome)
    ).all()

    query_amb = (
        db.select(Ambiente).join(Bloco)
        .order_by(Bloco.ordem, Bloco.nome, Ambiente.ordem, Ambiente.nome)
    )
    if bloco_id_filtro:
        query_amb = query_amb.where(Ambiente.bloco_id == bloco_id_filtro)
    ambientes = db.session.scalars(query_amb).all()

    colaboradores = db.session.scalars(
        db.select(Colaborador).join(Usuario).order_by(Colaborador.nome_exibicao)
    ).all()

    usuarios = db.session.scalars(
        db.select(Usuario).order_by(Usuario.nome)
    ).all()

    return render_template(
        "admin/cadastros.html",
        aba=aba,
        blocos=blocos,
        ambientes=ambientes,
        colaboradores=colaboradores,
        usuarios=usuarios,
        bloco_id_filtro=bloco_id_filtro,
    )


# ─── Atividades ──────────────────────────────────────────────────────────────

@bp.route("/atividades")
@login_required
@requer_coordenacao
def atividades_lista():
    status_filtro = request.args.get("status", "")
    query = (
        db.select(Atividade)
        .options(
            selectinload(Atividade.colaborador),
            selectinload(Atividade.alocacoes).selectinload(AtividadeColaborador.colaborador),
        )
        .join(Colaborador)
        .order_by(Atividade.criado_em.desc())
    )
    if status_filtro:
        query = query.where(Atividade.status == status_filtro)
    atividades = db.session.scalars(query).all()
    counts_raw = db.session.execute(
        db.select(Atividade.status, db.func.count(Atividade.id).label("cnt"))
        .group_by(Atividade.status)
    ).all()
    contagens = {row.status: row.cnt for row in counts_raw}
    return render_template(
        "admin/atividades/lista.html",
        atividades=atividades,
        contagens=contagens,
        status_filtro=status_filtro,
    )


@bp.route("/atividades/novo", methods=["GET", "POST"])
@login_required
@requer_coordenacao
def atividades_novo():
    form = AtividadeForm()
    _, blocos, ambientes = _popular_choices_atividade(form)
    if form.validate_on_submit():
        ok_loc, bloco_id_final, ambiente_id_final = _normalizar_bloco_ambiente_atividade(form)
        if not ok_loc:
            return render_template(
                "admin/atividades/form.html",
                form=form,
                titulo="Nova atividade",
                atividade=None,
                blocos_atividade=blocos,
                ambientes_atividade=ambientes,
            )

        modo_lote = form.modo_lote.data or "unica"
        colaboradores_destino = _normalizar_colaboradores_destino(
            form.colaborador_id.data,
            form.colaboradores_ids.data,
        )

        if modo_lote in {"compartilhada", "replicar", "dividir"} and len(colaboradores_destino) < 2:
            flash(
                "Selecione ao menos 2 colaboradores (incluindo o principal) para este modo de criação.",
                "warning",
            )
            return render_template(
                "admin/atividades/form.html",
                form=form,
                titulo="Nova atividade",
                atividade=None,
                blocos_atividade=blocos,
                ambientes_atividade=ambientes,
            )

        titulo_base = form.titulo.data.strip()
        descricao_base = form.descricao.data.strip() or None
        observacoes_base = form.observacoes.data.strip() or None
        atividades_criadas = []

        if modo_lote in {"replicar", "dividir"}:
            total = len(colaboradores_destino)
            for idx, colaborador_id in enumerate(colaboradores_destino, start=1):
                titulo_item = titulo_base
                observacoes_item = observacoes_base

                if modo_lote == "dividir" and total > 1:
                    titulo_item = f"{titulo_base} — Parte {idx}/{total}"
                    prefixo = f"[Divisão automática {idx}/{total}]"
                    observacoes_item = (
                        f"{prefixo} {observacoes_base}" if observacoes_base else prefixo
                    )

                atividade = Atividade(
                    titulo=titulo_item,
                    descricao=descricao_base,
                    tipo=form.tipo.data,
                    colaborador_id=colaborador_id,
                    bloco_id=bloco_id_final,
                    ambiente_id=ambiente_id_final,
                    observacoes=observacoes_item,
                )
                _sincronizar_alocacoes_atividade(atividade, [colaborador_id])
                db.session.add(atividade)
                atividades_criadas.append(atividade)
        else:
            # Atividade única (individual) ou compartilhada (dupla/trio/etc)
            colaboradores_vinculados = (
                colaboradores_destino if modo_lote == "compartilhada" else [form.colaborador_id.data]
            )
            atividade = Atividade(
                titulo=titulo_base,
                descricao=descricao_base,
                tipo=form.tipo.data,
                colaborador_id=form.colaborador_id.data,
                bloco_id=bloco_id_final,
                ambiente_id=ambiente_id_final,
                observacoes=observacoes_base,
            )
            _sincronizar_alocacoes_atividade(atividade, colaboradores_vinculados)
            db.session.add(atividade)
            atividades_criadas.append(atividade)

        db.session.commit()
        if modo_lote == "compartilhada":
            flash(
                f"Atividade compartilhada criada para {len(colaboradores_destino)} colaboradores.",
                "success",
            )
        elif len(atividades_criadas) == 1:
            flash(f"Atividade '{atividades_criadas[0].titulo}' criada.", "success")
        elif modo_lote == "dividir":
            flash(
                f"{len(atividades_criadas)} atividades criadas com divisão automática.",
                "success",
            )
        else:
            flash(
                f"{len(atividades_criadas)} atividades criadas em lote para os colaboradores selecionados.",
                "success",
            )
        return redirect(url_for("admin.atividades_lista"))
    return render_template(
        "admin/atividades/form.html",
        form=form,
        titulo="Nova atividade",
        atividade=None,
        blocos_atividade=blocos,
        ambientes_atividade=ambientes,
    )


@bp.route("/atividades/<int:id>/editar", methods=["GET", "POST"])
@login_required
@requer_coordenacao
def atividades_editar(id):
    atividade = db.get_or_404(Atividade, id)
    form = AtividadeForm(obj=atividade)
    _, blocos, ambientes = _popular_choices_atividade(form)
    if request.method == "GET":
        form.colaboradores_ids.data = [
            c.id for c in atividade.colaboradores_designados if c.id != atividade.colaborador_id
        ]

    if form.validate_on_submit():
        ok_loc, bloco_id_final, ambiente_id_final = _normalizar_bloco_ambiente_atividade(form)
        if not ok_loc:
            return render_template(
                "admin/atividades/form.html",
                form=form,
                titulo="Editar atividade",
                atividade=atividade,
                blocos_atividade=blocos,
                ambientes_atividade=ambientes,
            )

        atividade.titulo = form.titulo.data.strip()
        atividade.descricao = form.descricao.data.strip() or None
        atividade.tipo = form.tipo.data
        atividade.colaborador_id = form.colaborador_id.data
        atividade.bloco_id = bloco_id_final
        atividade.ambiente_id = ambiente_id_final
        atividade.observacoes = form.observacoes.data.strip() or None
        colaboradores_destino = _normalizar_colaboradores_destino(
            form.colaborador_id.data,
            form.colaboradores_ids.data,
        )
        _sincronizar_alocacoes_atividade(atividade, colaboradores_destino)
        db.session.commit()
        flash(f"Atividade '{atividade.titulo}' atualizada.", "success")
        return redirect(url_for("admin.atividades_lista"))
    return render_template(
        "admin/atividades/form.html",
        form=form,
        titulo="Editar atividade",
        atividade=atividade,
        blocos_atividade=blocos,
        ambientes_atividade=ambientes,
    )


@bp.route("/atividades/validacao")
@login_required
@requer_coordenacao
def atividades_validacao():
    colaborador_id_filtro = request.args.get("colaborador_id", type=int)
    query = (
        db.select(Atividade)
        .options(
            selectinload(Atividade.colaborador),
            selectinload(Atividade.alocacoes).selectinload(AtividadeColaborador.colaborador),
        )
        .join(Colaborador)
        .where(Atividade.status == "concluida")
        .order_by(Atividade.concluido_em.asc())
    )
    if colaborador_id_filtro:
        query = query.where(_filtro_atividade_por_colaborador(colaborador_id_filtro))
    atividades = db.session.scalars(query).all()
    colaboradores = db.session.scalars(
        db.select(Colaborador).where(Colaborador.ativo == True)  # noqa: E712
        .order_by(Colaborador.nome_exibicao)
    ).all()
    return render_template(
        "admin/atividades/validacao.html",
        atividades=atividades,
        colaboradores=colaboradores,
        colaborador_id_filtro=colaborador_id_filtro,
    )


@bp.route("/atividades/<int:id>/validar", methods=["POST"])
@login_required
@requer_coordenacao
def atividades_validar(id):
    atividade = db.get_or_404(Atividade, id)
    if atividade.status != "concluida":
        flash("Apenas atividades concluídas podem ser validadas.", "warning")
    else:
        atividade.validar(current_user)
        db.session.commit()
        flash(f"Atividade '{atividade.titulo}' validada com sucesso.", "success")
    return redirect(request.referrer or url_for("admin.atividades_validacao"))


@bp.route("/atividades/<int:id>/reabrir", methods=["POST"])
@login_required
@requer_coordenacao
def atividades_reabrir(id):
    atividade = db.get_or_404(Atividade, id)
    if atividade.status != "validada":
        flash("Apenas atividades validadas podem ser reabertas.", "warning")
    else:
        atividade.reabrir()
        db.session.commit()
        flash(f"Atividade '{atividade.titulo}' reaberta para revisão.", "info")
    return redirect(request.referrer or url_for("admin.atividades_lista"))


# ─── Export / Import JSON ────────────────────────────────────────────────────

@bp.route("/dados")
@login_required
@requer_coordenacao
def dados():
    return render_template("admin/dados.html")


@bp.route("/dados/exportar")
@login_required
@requer_coordenacao
def dados_exportar():
    blocos = db.session.scalars(db.select(Bloco).order_by(Bloco.ordem, Bloco.nome)).all()
    ambientes = db.session.scalars(
        db.select(Ambiente).join(Bloco).order_by(Bloco.ordem, Bloco.nome, Ambiente.ordem, Ambiente.nome)
    ).all()
    usuarios = db.session.scalars(db.select(Usuario).order_by(Usuario.nome)).all()

    payload = {
        "exportado_em": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "versao": "1",
        "blocos": [
            {"id": b.id, "nome": b.nome, "descricao": b.descricao,
             "ativo": b.ativo, "ordem": b.ordem}
            for b in blocos
        ],
        "ambientes": [
            {"id": a.id, "bloco_id": a.bloco_id, "nome": a.nome,
             "descricao": a.descricao, "ativo": a.ativo, "ordem": a.ordem}
            for a in ambientes
        ],
        "usuarios": [
            {"id": u.id, "nome": u.nome, "username": u.username,
             "perfil": u.perfil, "ativo": u.ativo}
            for u in usuarios
        ],
    }

    nome_arquivo = f"ifce_vistorias_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    return Response(
        json.dumps(payload, ensure_ascii=False, indent=2),
        mimetype="application/json",
        headers={"Content-Disposition": f"attachment; filename={nome_arquivo}"},
    )


@bp.route("/dados/importar", methods=["POST"])
@login_required
@requer_coordenacao
def dados_importar():
    arquivo = request.files.get("arquivo_json")
    if not arquivo or not arquivo.filename.endswith(".json"):
        flash("Selecione um arquivo .json válido.", "danger")
        return redirect(url_for("admin.dados"))

    try:
        payload = json.loads(arquivo.read().decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        flash("Arquivo inválido: não é um JSON legível.", "danger")
        return redirect(url_for("admin.dados"))

    if payload.get("versao") != "1":
        flash("Versão de arquivo não suportada.", "danger")
        return redirect(url_for("admin.dados"))

    criados_blocos = criados_amb = criados_usr = 0
    ignorados = []

    # ── Blocos ──
    bloco_id_map: dict = {}   # id_original → objeto Bloco
    for item in payload.get("blocos", []):
        existente = db.session.scalar(
            db.select(Bloco).where(Bloco.nome == item["nome"])
        )
        if existente:
            bloco_id_map[item["id"]] = existente
            ignorados.append(f"Bloco '{item['nome']}' (já existe)")
        else:
            b = Bloco(
                nome=item["nome"],
                descricao=item.get("descricao"),
                ativo=item.get("ativo", True),
                ordem=item.get("ordem", 0),
            )
            db.session.add(b)
            db.session.flush()   # obtém o id gerado
            bloco_id_map[item["id"]] = b
            criados_blocos += 1

    # ── Ambientes ──
    for item in payload.get("ambientes", []):
        bloco = bloco_id_map.get(item["bloco_id"])
        if not bloco:
            ignorados.append(f"Ambiente '{item['nome']}' (bloco de origem não encontrado)")
            continue
        existente = db.session.scalar(
            db.select(Ambiente).where(
                Ambiente.bloco_id == bloco.id,
                Ambiente.nome == item["nome"],
            )
        )
        if existente:
            ignorados.append(f"Ambiente '{item['nome']}' em '{bloco.nome}' (já existe)")
        else:
            db.session.add(Ambiente(
                bloco_id=bloco.id,
                nome=item["nome"],
                descricao=item.get("descricao"),
                ativo=item.get("ativo", True),
                ordem=item.get("ordem", 0),
            ))
            criados_amb += 1

    # ── Usuários ──
    for item in payload.get("usuarios", []):
        existente = db.session.scalar(
            db.select(Usuario).where(Usuario.username == item["username"])
        )
        if existente:
            ignorados.append(f"Usuário '{item['username']}' (já existe)")
        else:
            u = Usuario(
                nome=item["nome"],
                username=item["username"],
                perfil=item.get("perfil", "colaborador"),
                ativo=item.get("ativo", True),
            )
            # Senha temporária = username — coordenação deve redefinir
            u.set_senha(item["username"])
            db.session.add(u)
            criados_usr += 1

    db.session.commit()

    partes = []
    if criados_blocos:  partes.append(f"{criados_blocos} bloco(s)")
    if criados_amb:     partes.append(f"{criados_amb} ambiente(s)")
    if criados_usr:     partes.append(f"{criados_usr} usuário(s) (senha = username)")
    if partes:
        flash(f"Importação concluída: {', '.join(partes)} criado(s).", "success")
    else:
        flash("Nenhum registro novo encontrado no arquivo.", "info")

    if ignorados:
        flash(f"Ignorados ({len(ignorados)}): " + "; ".join(ignorados[:5])
              + ("…" if len(ignorados) > 5 else ""), "warning")

    return redirect(url_for("admin.dados"))


# ─── Vistorias (admin) ───────────────────────────────────────────────────────

@bp.route("/vistorias/<int:id>")
@login_required
@requer_coordenacao
def vistorias_detalhe(id):
    vistoria = db.get_or_404(Vistoria, id)
    return render_template("admin/vistorias/detalhe.html", vistoria=vistoria)


# ─── Ocorrências (admin) ──────────────────────────────────────────────────────

@bp.route("/ocorrencias")
@login_required
@requer_coordenacao
def ocorrencias_lista():
    status_filtro = request.args.get("status", "")
    prioridade_filtro = request.args.get("prioridade", "")
    categoria_filtro = request.args.get("categoria", "")
    bloco_id_filtro = request.args.get("bloco_id", type=int)
    ambiente_id_filtro = request.args.get("ambiente_id", type=int)
    colaborador_id_filtro = request.args.get("colaborador_id", type=int)
    data_inicio_filtro = request.args.get("data_inicio", "")
    data_fim_filtro = request.args.get("data_fim", "")

    query = (
        db.select(Ocorrencia)
        .join(Vistoria, Ocorrencia.vistoria_id == Vistoria.id)
        .order_by(Ocorrencia.criado_em.desc())
    )
    if status_filtro:
        query = query.where(Ocorrencia.status == status_filtro)
    if prioridade_filtro:
        query = query.where(Ocorrencia.prioridade == prioridade_filtro)
    if categoria_filtro:
        query = query.where(Ocorrencia.categoria == categoria_filtro)
    if bloco_id_filtro:
        query = query.where(Vistoria.bloco_id == bloco_id_filtro)
    if ambiente_id_filtro:
        query = query.where(Vistoria.ambiente_id == ambiente_id_filtro)
    if colaborador_id_filtro:
        query = query.where(Vistoria.colaborador_id == colaborador_id_filtro)
    if data_inicio_filtro:
        try:
            dt = datetime.strptime(data_inicio_filtro, "%Y-%m-%d")
            query = query.where(Ocorrencia.criado_em >= dt)
        except ValueError:
            data_inicio_filtro = ""
    if data_fim_filtro:
        try:
            dt_fim = datetime.strptime(data_fim_filtro, "%Y-%m-%d") + timedelta(days=1)
            query = query.where(Ocorrencia.criado_em < dt_fim)
        except ValueError:
            data_fim_filtro = ""

    page = request.args.get('page', 1, type=int)
    pagination = db.paginate(query, page=page, per_page=25, error_out=False)
    ocorrencias = pagination.items

    blocos = db.session.scalars(
        db.select(Bloco).where(Bloco.ativo == True).order_by(Bloco.nome)  # noqa: E712
    ).all()
    ambientes = db.session.scalars(
        db.select(Ambiente)
        .join(Bloco)
        .where(Ambiente.ativo == True)  # noqa: E712
        .order_by(Bloco.nome, Ambiente.nome)
    ).all()
    colaboradores = db.session.scalars(
        db.select(Colaborador)
        .where(Colaborador.ativo == True)  # noqa: E712
        .order_by(Colaborador.nome_exibicao)
    ).all()

    # Contagem global por status (totais sem filtros ativos)
    status_counts_raw = db.session.execute(
        db.select(Ocorrencia.status, db.func.count(Ocorrencia.id).label("cnt"))
        .group_by(Ocorrencia.status)
    ).all()
    stats_status = {row.status: row.cnt for row in status_counts_raw}

    return render_template(
        "admin/ocorrencias/lista.html",
        ocorrencias=ocorrencias,
        blocos=blocos,
        ambientes=ambientes,
        colaboradores=colaboradores,
        stats_status=stats_status,
        status_filtro=status_filtro,
        prioridade_filtro=prioridade_filtro,
        categoria_filtro=categoria_filtro,
        bloco_id_filtro=bloco_id_filtro,
        ambiente_id_filtro=ambiente_id_filtro,
        colaborador_id_filtro=colaborador_id_filtro,
        data_inicio_filtro=data_inicio_filtro,
        data_fim_filtro=data_fim_filtro,
        pagination=pagination,
        STATUS_CHOICES=Ocorrencia.STATUS,
        PRIORIDADE_CHOICES=Ocorrencia.PRIORIDADES,
        CATEGORIA_CHOICES=Ocorrencia.CATEGORIAS,
    )


@bp.route("/ocorrencias/<int:id>", methods=["GET", "POST"])
@login_required
@requer_coordenacao
def ocorrencias_detalhe(id):
    ocorrencia = db.get_or_404(Ocorrencia, id)
    form = OcorrenciaAdminForm(obj=ocorrencia)
    form.status.choices = Ocorrencia.STATUS
    form.prioridade.choices = Ocorrencia.PRIORIDADES

    if form.validate_on_submit():
        ocorrencia.status = form.status.data
        ocorrencia.prioridade = form.prioridade.data
        if form.observacoes_coordenacao.data and form.observacoes_coordenacao.data.strip():
            ocorrencia.observacoes_coordenacao = form.observacoes_coordenacao.data.strip()
        db.session.commit()
        flash("Ocorrência atualizada.", "success")
        return redirect(url_for("admin.ocorrencias_detalhe", id=id))

    return render_template(
        "admin/ocorrencias/detalhe.html",
        ocorrencia=ocorrencia,
        form=form,
    )
