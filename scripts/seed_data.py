"""
Script de carga inicial de dados — usuários e colaboradores demo.
Uso: python scripts/seed_data.py

Cria usuários padrão para primeiro acesso.
Não duplica registros se já existirem.

Para carregar blocos e ambientes do campus, execute em seguida:
    python scripts/seed_campus.py
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.extensions import db
from app.models.usuario import Usuario
from app.services.usuarios import sync_colaborador_projection


def seed_usuario_admin():
    existe = db.session.scalar(db.select(Usuario).where(Usuario.username == "admin"))
    if existe:
        print("[OK] Usuário admin já existe.")
        return

    admin = Usuario(nome="Administrador", username="admin", perfil="admin", ativo=True)
    admin.set_senha("admin123")
    db.session.add(admin)
    db.session.commit()
    print(f"[CRIADO] Usuário admin (id={admin.id}) — senha: admin123")


def seed_usuario_coordenacao():
    existe = db.session.scalar(db.select(Usuario).where(Usuario.username == "coordenacao"))
    if existe:
        print("[OK] Usuário coordenacao já existe.")
        return

    coord = Usuario(nome="Coordenação Infra", username="coordenacao", perfil="coordenacao", ativo=True)
    coord.set_senha("coord123")
    db.session.add(coord)
    db.session.commit()
    print(f"[CRIADO] Usuário coordenacao (id={coord.id}) — senha: coord123")


def seed_colaborador_demo():
    existe = db.session.scalar(db.select(Usuario).where(Usuario.username == "colaborador1"))
    if existe:
        print("[OK] Colaborador demo já existe.")
        return

    usuario = Usuario(
        nome="João da Silva",
        nome_exibicao="João Silva",
        funcao="Servente de Limpeza",
        username="colaborador1",
        perfil="colaborador",
        ativo=True,
    )
    usuario.set_senha("colab123")
    db.session.add(usuario)
    db.session.flush()
    sync_colaborador_projection(usuario)
    db.session.commit()
    print(f"[CRIADO] Colaborador demo '{usuario.username}' (id={usuario.id}) — senha: colab123")


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        print("=== Carga inicial de dados ===")
        seed_usuario_admin()
        seed_usuario_coordenacao()
        seed_colaborador_demo()
        print("=== Concluído ===")
