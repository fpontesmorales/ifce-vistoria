import os
from flask import Flask
from config import Config
from app.extensions import db, login_manager, csrf
from app.services.usuarios import ensure_usuario_operacional_columns, sync_all_colaborador_projection


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    # Garante que a pasta instance existe
    os.makedirs(app.instance_path, exist_ok=True)

    # Inicializa extensões
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Registra blueprints
    from app.routes.auth import bp as auth_bp
    from app.routes.colaborador import bp as colaborador_bp
    from app.routes.admin import bp as admin_bp
    from app.routes.vistorias import bp as vistorias_bp
    from app.routes.ocorrencias import bp as ocorrencias_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(colaborador_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(vistorias_bp)
    app.register_blueprint(ocorrencias_bp)

    # Cria as tabelas se não existirem
    with app.app_context():
        from app.models import usuario, colaborador, bloco, ambiente, atividade, vistoria, ocorrencia  # noqa: F401
        db.create_all()
        ensure_usuario_operacional_columns()
        sync_all_colaborador_projection()
        db.session.commit()

    return app
