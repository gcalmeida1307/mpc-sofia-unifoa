from __future__ import annotations

import time

import pytest

from api import auth


@pytest.fixture
def isolated_auth(tmp_path, monkeypatch):
    monkeypatch.setattr(auth, "DATABASE_PATH", tmp_path / "auth.sqlite3")
    for name in (
        "SOFIA_POSTGRES_URL",
        "DATABASE_URL",
        "SOFIA_ENCRYPTION_KEY",
        "SOFIA_DATA_ENCRYPTION_KEY",
    ):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("SOFIA_ADMIN_FIRST_PASSWORD", "Admin123")
    auth._rate_limits.clear()
    auth.initialize_user_store()
    yield
    auth._rate_limits.clear()


def _activation_user() -> tuple[str, str]:
    auth.create_access_request(
        "Pessoa de Teste",
        "activation@example.local",
        "infraestrutura",
        ["infraestrutura"],
    )
    request = auth.list_access_requests("pending")[0]
    result = auth.decide_access_request(
        int(request["id"]), True, ["infraestrutura"], auth.ADMIN_CODE
    )
    return str(result["user_code"]), str(result["activation_token"])


def test_activation_is_resumable_and_token_is_single_use(isolated_auth) -> None:
    user_code, activation_token = _activation_user()

    first = auth.activate_account(user_code.lower(), activation_token, "SenhaNova1!")
    resumed = auth.activate_account(user_code, activation_token, "OutraSenha2!")
    assert first["secret"] == resumed["secret"]

    with pytest.raises(ValueError, match="Código 2FA inválido"):
        auth.enable_activation_two_factor(user_code, activation_token, "000000")

    code = auth._totp_code(first["secret"])
    auth.enable_activation_two_factor(user_code.lower(), activation_token, code)
    logged = auth.authenticate(user_code, "SenhaNova1!", code)
    assert logged is not None
    assert logged["user_code"] == user_code
    assert logged["two_factor_enabled"] is True

    with pytest.raises(ValueError, match="já foi ativada"):
        auth.enable_activation_two_factor(user_code, activation_token, code)
    with pytest.raises(ValueError, match="já foi ativada"):
        auth.resume_account_activation(user_code, activation_token)


def test_used_activation_token_explains_normal_login(isolated_auth) -> None:
    user_code, activation_token = _activation_user()
    artifact = auth.activate_account(user_code, activation_token, "SenhaNova1!")
    auth.enable_activation_two_factor(
        user_code, activation_token, auth._totp_code(artifact["secret"])
    )

    with pytest.raises(ValueError, match="Esta conta já foi ativada"):
        auth.activate_account(user_code, activation_token, "OutraSenha2!")
    with pytest.raises(ValueError, match="Esta conta já foi ativada"):
        auth.resume_account_activation(user_code, activation_token)


def test_admin_can_reissue_incomplete_activation(isolated_auth) -> None:
    user_code, original_token = _activation_user()
    replacement = auth.create_activation_token(user_code.lower(), auth.ADMIN_CODE)

    with pytest.raises(ValueError, match="já foi utilizado"):
        auth.activate_account(user_code, original_token, "SenhaNova1!")
    artifact = auth.activate_account(
        user_code, replacement["activation_token"], "SenhaNova1!"
    )
    auth.enable_activation_two_factor(
        user_code,
        replacement["activation_token"],
        auth._totp_code(artifact["secret"]),
    )

    with pytest.raises(ValueError, match="já foi ativada"):
        auth.create_activation_token(user_code, auth.ADMIN_CODE)


def test_pending_activation_cannot_bypass_two_factor(isolated_auth) -> None:
    user_code, activation_token = _activation_user()
    artifact = auth.activate_account(user_code, activation_token, "SenhaNova1!")

    login = auth.authenticate(
        user_code, "SenhaNova1!", auth._totp_code(artifact["secret"])
    )
    assert login == {"requires_activation": True}

    auth.enable_activation_two_factor(
        user_code, activation_token, auth._totp_code(artifact["secret"])
    )
    login = auth.authenticate(
        user_code, "SenhaNova1!", auth._totp_code(artifact["secret"])
    )
    assert login is not None
    assert login["user_code"] == user_code


def test_password_reset_does_not_destroy_password_before_token_redeemed(
    isolated_auth,
) -> None:
    user = auth.create_user(
        "reset@example.local",
        "Reset Teste",
        "SenhaAtual1!",
        scopes=["infraestrutura"],
        primary_module="infraestrutura",
    )
    user_code = str(user["user_code"])
    artifact = auth.create_password_reset_token(user_code.lower(), auth.ADMIN_CODE)

    pending = auth.authenticate(user_code, "SenhaAtual1!")
    assert pending == {"requires_password_reset": True}

    with pytest.raises(ValueError, match="inválido, expirado ou já utilizado"):
        auth.reset_password_with_token(user_code, "token-invalido", "SenhaNova2!")
    assert auth.authenticate(user_code, "SenhaAtual1!") == {
        "requires_password_reset": True
    }

    auth.reset_password_with_token(
        user_code.lower(), artifact["reset_token"], "SenhaNova2!"
    )
    assert auth.authenticate(user_code, "SenhaNova2!") is not None
    assert auth.authenticate(user_code, "SenhaAtual1!") is None

    with pytest.raises(ValueError, match="inválido, expirado ou já utilizado"):
        auth.reset_password_with_token(
            user_code, artifact["reset_token"], "SenhaNova3!"
        )


def test_expired_reset_token_does_not_lock_out_existing_credential(isolated_auth) -> None:
    user = auth.create_user(
        "expired@example.local",
        "Expirado Teste",
        "SenhaAtual1!",
        scopes=["infraestrutura"],
        primary_module="infraestrutura",
    )
    user_code = str(user["user_code"])
    auth.create_password_reset_token(user_code, auth.ADMIN_CODE)
    with auth._connection() as connection:
        connection.execute(
            "UPDATE password_reset_tokens SET expires_at = ? WHERE user_code = ?",
            (int(time.time()) - 1, user_code),
        )
        connection.commit()

    logged = auth.authenticate(user_code, "SenhaAtual1!")
    assert logged is not None
    assert logged["user_code"] == user_code


def test_invalid_recovery_codes_are_rejected_before_database_lookup(isolated_auth) -> None:
    with pytest.raises(ValueError, match="Matrícula inválida"):
        auth.reset_password_with_token("IN123", "x" * 32, "SenhaNova1!")
    with pytest.raises(ValueError, match="Matrícula inválida"):
        auth.resume_account_activation("não-é-matrícula", "x" * 32)
