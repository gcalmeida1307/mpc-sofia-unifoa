import pytest
from services.auth import AuthService, IDLE_MINUTES

def test_password_policy():
    for password in ['Curta!','semsimboloA','SEMMINUSCULA!','semmaiuscula!']:
        with pytest.raises(ValueError): AuthService.validate_password(password)
    AuthService.validate_password('SenhaForte!')

def test_password_hash_is_salted_and_verifiable():
    first=AuthService.hash_password('SenhaForte!')
    second=AuthService.hash_password('SenhaForte!')
    assert first != second
    assert AuthService.verify_password('SenhaForte!',first)
    assert not AuthService.verify_password('errada',first)

def test_session_idle_timeout_is_fifteen_minutes():
    assert IDLE_MINUTES == 15


def test_recovery_email_validation():
    assert AuthService.validate_email(' Nome@Empresa.COM ') == 'nome@empresa.com'
    for email in ['sem-arroba', '@empresa.com', 'nome@', 'nome empresa@teste.com']:
        with pytest.raises(ValueError):
            AuthService.validate_email(email)


def test_only_valid_account_roles_are_accepted():
    service=AuthService()
    with pytest.raises(ValueError):
        service.change_user_role(2,'superadmin',1)
    with pytest.raises(ValueError):
        service.change_user_role(1,'user',1)


def test_administrator_cannot_reconfigure_own_access():
    service=AuthService()
    with pytest.raises(ValueError, match='próprio acesso'):
        service.recover_access(1,1)
