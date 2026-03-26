"""
Script de carga inicial de blocos e ambientes — IFCE Campus Caucaia.

Uso:
    python scripts/seed_campus.py

Comportamento:
    - Lê a estrutura de D:/DEV/SISTEMA/ifce-vistorias/scripts/data/campus_caucaia.json
    - Insere blocos e ambientes que ainda não existem (idempotente).
    - Nunca duplica: usa o nome do bloco e (bloco_id + nome do ambiente) como chave.
    - Itens com "ativo": false no JSON são inseridos como inativos.
    - Pode ser executado múltiplas vezes com segurança.

Para alterar a estrutura do campus, edite apenas:
    scripts/data/campus_caucaia.json
"""

import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.extensions import db
from app.models.bloco import Bloco
from app.models.ambiente import Ambiente

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "campus_caucaia.json")


def carregar_dados():
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


def seed_bloco(dados_bloco):
    """Insere ou ignora um bloco. Retorna a instância (nova ou existente)."""
    nome = dados_bloco["nome"]
    bloco = db.session.scalar(db.select(Bloco).where(Bloco.nome == nome))

    if bloco:
        print(f"  [JÁ EXISTE] Bloco: {nome}")
        return bloco

    bloco = Bloco(
        nome=nome,
        descricao=dados_bloco.get("descricao", ""),
        ordem=dados_bloco.get("ordem", 0),
        ativo=dados_bloco.get("ativo", True),
    )
    db.session.add(bloco)
    db.session.flush()  # garante bloco.id antes de criar os ambientes
    print(f"  [CRIADO]    Bloco: {nome} (id={bloco.id})")
    return bloco


def seed_ambiente(bloco, dados_amb):
    """Insere ou ignora um ambiente dentro de um bloco."""
    nome = dados_amb["nome"]
    existe = db.session.scalar(
        db.select(Ambiente).where(
            Ambiente.bloco_id == bloco.id,
            Ambiente.nome == nome,
        )
    )

    if existe:
        print(f"      [JÁ EXISTE] Ambiente: {nome}")
        return

    amb = Ambiente(
        bloco_id=bloco.id,
        nome=nome,
        descricao=dados_amb.get("descricao", ""),
        ordem=dados_amb.get("ordem", 0),
        ativo=dados_amb.get("ativo", True),
    )
    db.session.add(amb)
    print(f"      [CRIADO]    Ambiente: {nome}")


def seed_campus():
    dados = carregar_dados()
    blocos = dados.get("blocos", [])

    print(f"\nCarregando {len(blocos)} bloco(s) de '{DATA_FILE}'...\n")

    for dados_bloco in blocos:
        bloco = seed_bloco(dados_bloco)
        ambientes = dados_bloco.get("ambientes", [])
        for dados_amb in ambientes:
            seed_ambiente(bloco, dados_amb)

    db.session.commit()
    print("\n[OK] Carga concluída e persistida.\n")


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        print("=== Carga de Blocos e Ambientes — IFCE Campus Caucaia ===")
        seed_campus()
        print("=== Concluído ===")
