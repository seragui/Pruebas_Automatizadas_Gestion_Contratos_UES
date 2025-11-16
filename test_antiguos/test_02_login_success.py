import pytest
from pages.login_page import LoginPage

@pytest.mark.smoke
def test_login_success(driver, base_url, qa_creds):
    login = LoginPage(driver, base_url)
    login.open_login()
    login.login_as(qa_creds["email"], qa_creds["password"])
    assert login.is_logged_in(), "El usuario no quedó autenticado tras login válido."

@pytest.mark.parametrize("email,password,reason", [
    ("", "", "vacíos"),
    ("qa.user@tu-app.com", "mala", "password incorrecta"),
    ("inexistente@tu-app.com", "SuperSecreta123!", "usuario inexistente"),
    ("formato-malo", "SuperSecreta123!", "email inválido"),
])
def test_login_fail_cases(driver, base_url, email, password, reason):
    login = LoginPage(driver, base_url)
    login.open_login()
    login.login_as(email, password)
    assert not login.is_logged_in(), f"Login no debería funcionar ({reason})."
