import pytest
from pages.login_page import LoginPage

@pytest.mark.smoke
def test_login_success(driver, base_url, qa_creds, evidencia):
    login = LoginPage(driver, base_url)
    login.open_login()
    evidencia("login_success__form_visible")

    # Evidencia: después de enviar credenciales válidas
    login.login_as(qa_creds["email"], qa_creds["password"])
    evidencia("login_success__after_submit")
    assert login.is_logged_in(), "El usuario no quedó autenticado tras login válido."

@pytest.mark.parametrize("email,password,reason", [
    ("", "", "campos vacíos"),
    ("qa.user@tu-app.com", "incorrecta", "password incorrecta"),
    ("noexiste@tu-app.com", "SuperSecreta123!", "usuario inexistente"),
    ("correo-malo", "SuperSecreta123!", "email inválido"),
])
def test_login_fail_cases(driver, base_url, email, password, reason, evidencia):
    login = LoginPage(driver, base_url)

     # Evidencia: formulario visible antes de probar el caso negativo
    login.open_login()
    evidencia(f"login_fail__{reason}__form_visible")

    # Evidencia: después de intentar hacer login con credenciales inválidas
    login.login_as(email, password)
    evidencia(f"login_fail__{reason}__after_submit")
    assert not login.is_logged_in(), f"No debería autenticar ({reason})."
