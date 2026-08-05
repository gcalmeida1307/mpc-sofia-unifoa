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
