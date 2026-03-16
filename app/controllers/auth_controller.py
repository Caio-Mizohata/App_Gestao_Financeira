from flask import session
from app.models import db
from app.models.usuario import Usuario
from app.models.categoria import Categoria
from app.models.caixa_config import CaixaConfig
from app.config.settings import CATEGORIAS_PADRAO

def process_login(email, password):
    """Autentica usuário e salva migração de hash caso tenha ocorrido."""
    if not email or not password:
        return False, {"error": "Email e senha são obrigatórios"}

    user = Usuario.query.filter_by(email=email).first()
    
    if user and user.check_password(password):
        # Verifica se a senha foi atualizada para Bcrypt durante o check_password
        if db.session.is_modified(user):
            db.session.commit()
            
        session["user_id"] = user.id
        session["username"] = user.email
        return True, {}

    return False, {"error": "Email ou senha inválidos"}


def process_register(email, password):
    """Cria conta com proteção contra Enumeração de Usuários."""
    if not email or not password:
        return False, {"reg_error": "Email e senha são obrigatórios", "show_register": True}
    if len(email) > 254:
        return False, {"reg_error": "Email muito longo (máx. 254 caracteres)", "show_register": True}
    if len(password) < 8:
        return False, {"reg_error": "A senha deve ter ao menos 8 caracteres", "show_register": True}

    existing = Usuario.query.filter_by(email=email).first()
    
    success_msg = "Processamento concluído! Se o email for válido e inédito, sua conta foi criada. Faça login."

    if existing:
        return True, {"success": success_msg}

    user = Usuario(email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    for nome, cor in CATEGORIAS_PADRAO:
        db.session.add(Categoria(nome=nome, cor=cor, usuario_id=user.id))

    db.session.add(CaixaConfig(saldo_inicial=0, usuario_id=user.id))
    db.session.commit()

    return True, {"success": success_msg}