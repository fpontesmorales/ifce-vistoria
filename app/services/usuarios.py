from app.extensions import db
from app.models.usuario import Usuario
from app.models.colaborador import Colaborador
from sqlalchemy import inspect


def ensure_usuario_operacional_columns():
    """Adiciona colunas operacionais em usuario quando banco antigo ainda não possui."""
    engine = db.engine
    insp = inspect(engine)
    tabelas = set(insp.get_table_names())
    if "usuario" not in tabelas:
        return

    colunas = {col["name"] for col in insp.get_columns("usuario")}

    with engine.begin() as conn:
        if "nome_exibicao" not in colunas:
            conn.exec_driver_sql("ALTER TABLE usuario ADD COLUMN nome_exibicao VARCHAR(120)")
        if "funcao" not in colunas:
            conn.exec_driver_sql("ALTER TABLE usuario ADD COLUMN funcao VARCHAR(80)")

        if "colaborador" in tabelas:
            # Migra dados já existentes de colaborador para usuario.
            conn.exec_driver_sql(
                """
                UPDATE usuario
                   SET nome_exibicao = (
                       SELECT c.nome_exibicao
                         FROM colaborador c
                        WHERE c.usuario_id = usuario.id
                   )
                 WHERE (nome_exibicao IS NULL OR TRIM(nome_exibicao) = '')
                   AND EXISTS (SELECT 1 FROM colaborador c WHERE c.usuario_id = usuario.id)
                """
            )
            conn.exec_driver_sql(
                """
                UPDATE usuario
                   SET funcao = (
                       SELECT c.funcao
                         FROM colaborador c
                        WHERE c.usuario_id = usuario.id
                   )
                 WHERE (funcao IS NULL OR TRIM(funcao) = '')
                   AND EXISTS (SELECT 1 FROM colaborador c WHERE c.usuario_id = usuario.id)
                """
            )


def sync_colaborador_projection(usuario: Usuario):
    """
    Mantém tabela colaborador sincronizada com usuario por compatibilidade
    com o schema atual de atividades/vistorias.
    """
    colaborador = db.session.scalar(
        db.select(Colaborador).where(Colaborador.usuario_id == usuario.id)
    )

    if usuario.perfil != "colaborador":
        if colaborador:
            colaborador.ativo = False
        return

    nome_exibicao = (usuario.nome_exibicao or usuario.nome or "").strip()
    if not nome_exibicao:
        nome_exibicao = usuario.username
    usuario.nome_exibicao = nome_exibicao

    if colaborador is None:
        colaborador = Colaborador(
            usuario_id=usuario.id,
            nome_exibicao=nome_exibicao,
            funcao=(usuario.funcao or "").strip() or None,
            ativo=usuario.ativo,
        )
        db.session.add(colaborador)
        return

    colaborador.nome_exibicao = nome_exibicao
    colaborador.funcao = (usuario.funcao or "").strip() or None
    colaborador.ativo = usuario.ativo


def sync_all_colaborador_projection():
    usuarios = db.session.scalars(db.select(Usuario)).all()
    for usuario in usuarios:
        sync_colaborador_projection(usuario)
