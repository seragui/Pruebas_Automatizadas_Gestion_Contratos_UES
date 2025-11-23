import pytest
import allure
from pages.login_page import LoginPage



@allure.epic("Gestión de Contratos")
@allure.feature("Autenticación y Sesiones")
@allure.story("Login exitoso con credenciales válidas")
@allure.severity(allure.severity_level.CRITICAL)
@allure.label("owner", "Ronald Aguilar")
@allure.link("https://mi-matriz-casos/LOGIN_EXITO_01", name="LOGIN_EXITO_01")
@pytest.mark.functional
@pytest.mark.e2e
@pytest.mark.smoke
@pytest.mark.regression
@pytest.mark.case("LOGIN_EXITO_01")
@pytest.mark.tester("Ronald")
@pytest.mark.smoke
def test_cp01_login_success(driver, base_url, qa_creds, evidencia):
    with allure.step("Abrir pantalla de login"):
        login = LoginPage(driver, base_url)
        login.open_login()
        evidencia("login_success__form_visible")

    with allure.step("Ingresar credenciales válidas y enviar formulario"):
        # Evidencia: después de enviar credenciales válidas
        login.login_as(qa_creds["email"], qa_creds["password"])
        evidencia("login_success__after_submit")
    
    with allure.step("Verificar que el usuario quedó autenticado"):
        assert login.is_logged_in(), "El usuario no quedó autenticado tras login válido."



@allure.epic("Gestión de Contratos")
@allure.feature("Autenticación y Sesiones")
@allure.story("Login inválido: credenciales incorrectas o incompletas")
@allure.severity(allure.severity_level.CRITICAL)
@allure.label("owner", "Ronald Aguilar")  # Ej: "Ronald Aguilar"
@allure.link("https://mi-matriz-casos/LOGIN_NEGATIVO_01", name="LOGIN_NEGATIVO_01")
@pytest.mark.functional
@pytest.mark.e2e
@pytest.mark.negative
@pytest.mark.ddt
@pytest.mark.regression
@pytest.mark.case("LOGIN_NEGATIVO_01")
@pytest.mark.tester("Ronald")  
@pytest.mark.parametrize("email,password,reason", [
    ("", "", "campos vacíos"),
    ("qa.user@tu-app.com", "incorrecta", "password incorrecta"),
    ("noexiste@tu-app.com", "SuperSecreta123!", "usuario inexistente"),
    ("correo-malo", "SuperSecreta123!", "email inválido"),
])
def test_login_fail_cases(driver, base_url, email, password, reason, evidencia):
    login = LoginPage(driver, base_url)

    with allure.step("Abrir la pantalla de login"):
        # Evidencia: formulario visible antes de probar el caso negativo
        login.open_login()
        evidencia(f"login_fail__{reason}__form_visible")
    with allure.step(f"Intentar login con credenciales inválidas ({reason})"):
        # Evidencia: después de intentar hacer login con credenciales inválidas
        login.login_as(email, password)
        evidencia(f"login_fail__{reason}__after_submit")
    with allure.step("Verificar que el usuario NO queda autenticado"):
        assert not login.is_logged_in(), f"No debería autenticar ({reason})."
