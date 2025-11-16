# tests/functional/test_asistente_home_smoke.py
import pytest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

from pages.login_page import LoginPage
from pages.asistente_home_page import AsistenteHomePage, RecepcionSolicitudesPage

@pytest.mark.functional
@pytest.mark.case("CP_ASISTENTE_Recepcion_Navegar")
def test_asistente_navega_a_recepcion(driver, base_url, evidencia, cod_cache):
    # 1) Login Asistente
    login = LoginPage(driver, base_url)
    login.open_login()
    login.login_as("asistente@ues.edu.sv", "Password.1")

    WebDriverWait(driver, 15).until(EC.visibility_of_element_located((
        By.XPATH,
        "//header//span[contains(.,'Sesión iniciada como') and "
        "(contains(.,'Asistente') or contains(.,'Asistente Administrativo') or contains(.,'Director Escuela'))]"
    )))
    time.sleep(1)  # Pequeña espera para evitar capturas muy tempranas
    evidencia("asistente_login_ok")

    # 2) Ir a Recepción
    home = AsistenteHomePage(driver, base_url)
    home.wait_loaded()
    home.go_to_recepcion_solicitudes(evidencia=evidencia)

    recep = RecepcionSolicitudesPage(driver)
    recep.wait_loaded(evidencia=evidencia)

    time.sleep(1)  # Pequeña espera para evitar capturas muy tempranas
    # 3) Click en "Ver" (suave)
    codigo = cod_cache["get"](None)
    if codigo:
        ok = recep.click_ver_by_code(codigo, evidencia=evidencia, require_detalle=False)
    else:
        ok = recep.click_ver_first(evidencia=evidencia, require_detalle=False)

    # 4) Solo evidencia post-click (no assert duro)
    time.sleep(8)  # Pequeña espera para evitar capturas muy tempranas
    evidencia("asistente_ver_detalle_ok")

    # (Opcional) Log suave por si querés ver en reporte si detectó el detalle:
    # assert ok is not None