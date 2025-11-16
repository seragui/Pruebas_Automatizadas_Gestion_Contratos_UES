# tests/functional/test_logout_invalidates_session.py
import os
import pytest
from pages.login_page import LoginPage
from pages.logout_bar import LogoutBar  # asegúrate de tener este Page Object

@pytest.mark.e2e
@pytest.mark.regression
@pytest.mark.security
def test_logout_invalidates_session(driver, base_url, qa_creds, evidencia):
    """
    CP_02 – Logout invalida sesión
    1) Login con usuario válido
    2) Acceder a ruta protegida (debe permitir)
    3) Logout
    4) Intentar ruta protegida (debe bloquear/redirigir a login)
    5) Back/refresh no debe reabrir sesión
    """
    protected_path = os.getenv("PROTECTED_PATH", "/usuarios")  # ajusta en .env

    # 1) Login
    login = LoginPage(driver, base_url)
    login.open_login()
    evidencia("logout_invalidates__login_form")

    login.login_as(qa_creds["email"], qa_creds["password"])
    assert login.is_logged_in(), "No se autenticó el usuario válido."
    evidencia("logout_invalidates__login_ok")

    # 2) Estando logueado, una ruta protegida NO debe mostrar el login
    login.open(protected_path)
    evidencia("logout_invalidates__protected_path")
    assert not login.is_login_screen(), "Se ve el login pese a estar autenticado."

    # 3) Logout
    nav = LogoutBar(driver, base_url)
    nav.do_logout()

    # 4) Espera explícita: tras logout debe verse el formulario de login
    try:
        # Usa el wait del BasePage (15s por defecto)
        login.wait_visible(LoginPage.EMAIL)
    except TimeoutException:
        # Fallback defensivo: refresca una vez y vuelve a esperar
        driver.refresh()
        login.wait_visible(LoginPage.EMAIL)

    assert login.is_login_screen(), "Tras logout debería mostrarse el formulario de login."
    evidencia("logout_invalidates__login_after_logout")

    # 5) Intentar ir a la ruta protegida vuelve a mostrar login (guard de la SPA)
    login.open(protected_path)
    # Esperamos explícitamente el input para no depender del timing
    login.wait_visible(LoginPage.EMAIL)
    assert login.is_login_screen(), "Tras logout, la ruta protegida no debe ser accesible."
    evidencia("logout_invalidates__protected_after_logout")

    # 6) Back/refresh no debe reabrir sesión
    driver.back()
    driver.refresh()
    login.wait_visible(LoginPage.EMAIL)
    assert login.is_login_screen(), "Back/refresh no debería reabrir la sesión."
    evidencia("logout_invalidates__back_refresh")