from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from services.auth import auth_service

router = APIRouter(prefix='/auth', tags=['Authentication'])

class LoginIn(BaseModel):
    username: str; password: str; otp: str
class FirstAccessIn(BaseModel):
    username: str; password: str; totp_secret: str; otp: str
class AccessIn(BaseModel):
    username: str = Field(min_length=3, max_length=80)
    display_name: str = Field(min_length=2, max_length=120)
    email: str = Field(min_length=5, max_length=200)
    reason: str = Field(default='', max_length=1000)

def bearer(request: Request) -> str:
    value=request.headers.get('authorization','')
    return value[7:].strip() if value.lower().startswith('bearer ') else ''

@router.post('/first-access/start')
def first_access_start(payload: dict):
    result=auth_service.enrollment(str(payload.get('username','')))
    if not result: raise HTTPException(400, 'Usuário não está disponível para primeiro acesso')
    return result

@router.post('/first-access/complete')
def first_access_complete(payload: FirstAccessIn, request: Request):
    try: ok=auth_service.complete_first_access(payload.username,payload.password,payload.totp_secret,payload.otp,request.client.host if request.client else None)
    except ValueError as exc: raise HTTPException(422,str(exc))
    if not ok: raise HTTPException(401,'TOTP inválido ou cadastro indisponível')
    return {'status':'active'}

@router.post('/login')
def login(payload: LoginIn, request: Request):
    result=auth_service.login(payload.username,payload.password,payload.otp,request.client.host if request.client else None,request.headers.get('user-agent'))
    if not result: raise HTTPException(401,'Credenciais ou TOTP inválidos')
    return result

@router.post('/logout')
def logout(request: Request):
    if not auth_service.logout(bearer(request)): raise HTTPException(401,'Sessão inválida')
    return {'status':'revoked'}

@router.get('/me')
def me(request: Request):
    user=auth_service.authenticate(bearer(request))
    if not user: raise HTTPException(401,'Sessão inválida ou expirada')
    return user

@router.post('/access-requests', status_code=201)
def access_request(payload: AccessIn):
    try: request_id=auth_service.request_access(payload.username,payload.display_name,payload.email,payload.reason)
    except Exception: raise HTTPException(409,'Já existe uma solicitação pendente')
    return {'id':request_id,'status':'pending'}


def require_admin(request: Request):
    user=auth_service.authenticate(bearer(request))
    if not user or user['role']!='admin': raise HTTPException(403,'Perfil admin necessário')
    return user

@router.get('/admin/access-requests')
def access_requests(request: Request):
    require_admin(request); return {'requests':auth_service.list_requests()}

@router.post('/admin/access-requests/{request_id}/approve')
def approve(request_id: int, request: Request):
    admin=require_admin(request)
    if not auth_service.approve_request(request_id,admin['id']): raise HTTPException(404,'Solicitação pendente não encontrada')
    auth_service.audit(admin['username'],'approve_access',True,user_id=admin['id'])
    return {'status':'approved'}

@router.get('/admin/users')
def users(request: Request):
    require_admin(request); return {'users':auth_service.list_users()}

@router.post('/admin/users/{user_id}/revoke-sessions')
def revoke_sessions(user_id: int, request: Request):
    require_admin(request); return {'revoked':auth_service.revoke_user_sessions(user_id)}

@router.get('/admin/audit')
def audit(request: Request):
    require_admin(request); return {'entries':auth_service.audit_entries()}
