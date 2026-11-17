import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from .database import get_db
from .models import Usuario
from .security import ler_token

esquema = HTTPBearer(auto_error=False)


def usuario_logado(
    credenciais: HTTPAuthorizationCredentials = Depends(esquema),
    db: Session = Depends(get_db),
) -> Usuario:
    """Exige token válido e confere no banco se o usuário continua ativo."""
    if credenciais is None:
        raise HTTPException(status_code=401, detail="Acesso não autorizado.")
    try:
        dados = ler_token(credenciais.credentials)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Acesso não autorizado.")
    usuario = db.get(Usuario, int(dados["sub"]))
    if usuario is None or not usuario.ativo:
        raise HTTPException(status_code=401, detail="Acesso não autorizado.")
    return usuario


def apenas_coordenador(usuario: Usuario = Depends(usuario_logado)) -> Usuario:
    if usuario.perfil != "coordenador":
        raise HTTPException(status_code=403, detail="Permissão insuficiente.")
    return usuario
