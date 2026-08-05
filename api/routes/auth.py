from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from pydantic import BaseModel, Field
from services.auth import auth_service
from services.notifications import email_notifier

router = APIRouter(prefix='/auth', tags=['Authentication'])

class LoginIn(BaseModel):
    username: str; password: str; otp: str
class FirstAccessStartIn(BaseModel):
    username: str
    invite_token: str = Field(min_length=16, max_length=200)
class FirstAccessIn(BaseModel):
    username: str; password: str; otp: str
class ProfileIn(BaseModel):
    display_name: str = Field(min_length=2, max_length=120)
    email: str = Field(min_length=5, max_length=200)
class PasswordResetIn(BaseModel):
    username: str = Field(min_length=3, max_length=80)
    reset_token: str = Field(min_length=20, max_length=200)
    password: str
    otp: str
class AccessIn(BaseModel):
    username: str = Field(min_length=3, max_length=80)
    display_name: str = Field(min_length=2, max_length=120)
    email: str = Field(min_length=5, max_length=200)
    reason: str = Field(default='', max_length=1000)

def bearer(request: Request) -> str:
    value=request.headers.get('authorization','')
    return value[7:].strip() if value.lower().startswith('bearer ') else ''

@router.post('/first-access/start')
def first_access_start(payload: FirstAccessStartIn):
    result=auth_service.enrollment(payload.username, payload.invite_token)
    if not result: raise HTTPException(400, 'Usuário não está disponível para primeiro acesso')
    return result

@router.post('/first-access/complete')
def first_access_complete(payload: FirstAccessIn, request: Request):
    try: ok=auth_service.complete_first_access(payload.username,payload.password,payload.otp,request.client.host if request.client else None)
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

@router.patch('/me')
def update_me(payload: ProfileIn, request: Request):
    user=auth_service.authenticate(bearer(request))
    if not user: raise HTTPException(401,'Sessao invalida ou expirada')
    try: result=auth_service.update_profile(user['id'],payload.display_name,payload.email)
    except ValueError as exc: raise HTTPException(422,str(exc))
    auth_service.audit(user['username'],'update_profile',True,user_id=user['id'])
    return result

@router.post('/password-reset/complete')
def password_reset(payload: PasswordResetIn, request: Request):
    try: ok=auth_service.complete_password_reset(payload.username,payload.reset_token,payload.password,payload.otp,request.client.host if request.client else None)
    except ValueError as exc: raise HTTPException(422,str(exc))
    if not ok: raise HTTPException(401,'Token, TOTP ou solicitacao invalidos')
    return {'status':'password_updated'}

@router.post('/access-requests', status_code=201)
def access_request(payload: AccessIn, background_tasks: BackgroundTasks):
    try: request_id=auth_service.request_access(payload.username,payload.display_name,payload.email,payload.reason)
    except ValueError as exc: raise HTTPException(422,str(exc))
    except Exception: raise HTTPException(409,'Já existe uma solicitação pendente')
    recipients=auth_service.admin_notification_emails()
    background_tasks.add_task(email_notifier.notify_access_request,recipients,payload.username,payload.display_name,payload.email,payload.reason)
    return {'id':request_id,'status':'pending','notification_scheduled':bool(recipients and email_notifier.configured())}


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
    result=auth_service.approve_request(request_id,admin['id'])
    if not result: raise HTTPException(404,'Solicitação pendente não encontrada')
    auth_service.audit(admin['username'],'approve_access',True,user_id=admin['id'])
    return {'status':'approved', 'setup_token':result['setup_token']}

@router.get('/admin/users')
def users(request: Request):
    require_admin(request); return {'users':auth_service.list_users()}

@router.post('/admin/users/{user_id}/require-password-reset')
def require_password_reset(user_id: int, request: Request, background_tasks: BackgroundTasks):
    admin=require_admin(request)
    result=auth_service.require_password_reset(user_id)
    if not result: raise HTTPException(404,'Usuario ativo nao encontrado')
    email_sent=bool(result['email'] and email_notifier.configured())
    if email_sent: background_tasks.add_task(email_notifier.notify_password_reset,result['email'],result['username'],result['reset_token'])
    auth_service.audit(admin['username'],'require_password_reset',True,user_id=admin['id'])
    return {'status':'reset_required','reset_token':result['reset_token'],'email_sent':email_sent}

@router.post('/admin/users/{user_id}/revoke-sessions')
def revoke_sessions(user_id: int, request: Request):
    require_admin(request); return {'revoked':auth_service.revoke_user_sessions(user_id)}

@router.get('/admin/audit')
def audit(request: Request):
    require_admin(request); return {'entries':auth_service.audit_entries()}
