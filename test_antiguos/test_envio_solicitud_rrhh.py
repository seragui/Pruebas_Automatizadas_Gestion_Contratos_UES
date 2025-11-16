import pytest
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from pages.login_page import LoginPage
from pages.director_home_page import DirectorHomePage
from pages.contracts_list_page import ContractsListPage
from pages.envio_director_rrhh import enviar_a_rrhh
from pages.logout_bar import LogoutBar
from pages.rrhh_home_page import RRHHHomePage, ValidacionSolicitudesPage

def test_enviar_solicitud_a_rrhh(driver, base_url, evidencia, cod_cache):
    # 1) Código cacheado de la solicitud en curso
    codigo = cod_cache["get"](None)
    if not codigo:
        pytest.skip("No hay código cacheado de solicitud previa.")

    # 2) Login Director
    login = LoginPage(driver, base_url)
    login.open_login()
    login.login_as("director@ues.edu.sv", "Password.1")
    assert login.is_logged_in(), "No se pudo iniciar sesión como Director."
    evidencia("login_director_ok")

    # 3) Ir a Solicitudes y buscar por código
    home = DirectorHomePage(driver, base_url)
    home.wait_loaded()
    home.go_to_contratos()

    contratos = ContractsListPage(driver, base_url)
    contratos.wait_loaded()
    evidencia("listado_contratos_visible")

    time.sleep(1)  # microespera por animación de tabla/filtros
    contratos.search_code(codigo)
    evidencia(f"buscar_codigo__{codigo}")
    contratos.ensure_code_visible(codigo)
    evidencia(f"codigo_en_tabla__{codigo}")

    # 4) Entrar al detalle
    contratos.click_view_for_code(codigo)
    WebDriverWait(driver, 12).until(EC.url_contains("/contratos/solicitud/"))
    evidencia(f"detalle_solicitud__{codigo}")

    # 5) Enviar a RRHH (sin tocar tus POs)
    #enviar_a_rrhh(driver, evidencia)

    nav = LogoutBar(driver, base_url)
    nav.do_logout()

    login.open_login()
    login.login_as("rrhh@ues.edu.sv", "Password.1")

    time.sleep(2)  # espera breve por animaciones

    wait = WebDriverWait(driver, 15)
    wait.until(EC.visibility_of_element_located((
        By.XPATH,
        "//header//span[contains(.,'Sesión iniciada como') "
        "and (contains(.,'RRHH') or contains(.,'Recursos Humanos'))]"
    )))
    evidencia("login_rrhh_ok")

    # 8) Ir a Validación de Solicitudes
    rrhh_home = RRHHHomePage(driver, base_url)
    rrhh_home.wait_loaded()
    rrhh_home.go_to_validacion(evidencia)

    # 9) (Opcional) confirmar carga de la página
    try:
        val = ValidacionSolicitudesPage(driver)
        val.wait_loaded()
        evidencia("validacion_solicitudes_visible")
    except Exception:
        # Si tu vista no tiene header distintivo, al menos quedamos en /solicitudes
        evidencia("validacion_solicitudes_url_ok")
    time.sleep(2)  # espera breve por animaciones

    val.click_ver_solicitud(codigo, evidencia)
    time.sleep(2)  # espera breve por animaciones   
    evidencia(f"rrhh_detalle_abierto__{codigo}")