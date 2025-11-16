import pytest
from urllib.parse import urljoin
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from pages.login_page import LoginPage
from pages.director_carga_academica_page import DirectorCargaAcademicaPage

@pytest.mark.functional
@pytest.mark.e2e
@pytest.mark.case("RRHH_NO_ACCESO_CARGA_ACADEMICA_01")
def test_rrhh_no_puede_acceder_a_carga_academica(
    driver,
    base_url,
    rrhh_creds,
    evidencia,
):
    """
    Escenario:
    1. El usuario de RRHH inicia sesión en el sistema.
    2. Intenta acceder directamente a /carga-academica.
    3. Se espera que el sistema NO le permita ver esa pantalla
       y lo redireccione al inicio (base_url).
    """

    # 1) Login como RRHH
    login_page = LoginPage(driver, base_url)
    login_page.open_login()
    evidencia("rrhh_login__form_visible")

    login_page.login_as(rrhh_creds["email"], rrhh_creds["password"])
    assert login_page.is_logged_in(), "El usuario RRHH no quedó autenticado tras el login válido."
    evidencia("rrhh_login__ok")

    # 2) Navegar directamente a /carga-academica
    carga_academica_url = f"{base_url.rstrip('/')}/carga-academica"
    driver.get(carga_academica_url)
    evidencia("rrhh_carga_academica__intento_acceso")

    # 3) Esperar que lo redireccione a la pantalla principal (base_url)
    wait = WebDriverWait(driver, 15)

    def _redirected_to_home(drv):
        current = drv.current_url.rstrip("/")
        expected = base_url.rstrip("/")
        # Puedes imprimir para debug si quieres:
        print(f"[DEBUG] current_url={current} | expected={expected}")
        return current == expected

    wait.until(_redirected_to_home)

    current_url = driver.current_url.rstrip("/")
    expected_url = base_url.rstrip("/")

    assert current_url == expected_url, (
        "Se esperaba que el usuario RRHH fuera redirigido a la pantalla principal "
        f"({expected_url}) al intentar acceder a /carga-academica, pero quedó en: {current_url}"
    )

    # (Opcional) Validar que no se ve nada propio de la pantalla de carga académica
    body_text = driver.find_element(By.TAG_NAME, "body").text
    assert "Carga académica" not in body_text, (
        "El texto 'Carga académica' apareció en la pantalla, indicando que el usuario RRHH "
        "podría estar viendo la sección restringida."
    )

    evidencia("rrhh_carga_academica__redireccion_home_ok")
@pytest.mark.functional
@pytest.mark.e2e
@pytest.mark.case("DIRECTOR_ACCESO_CARGA_ACADEMICA_01")
def test_director_puede_acceder_a_carga_academica(
    driver,
    base_url,
    director_creds,
    evidencia,
):
    """
    Escenario:
    1. El usuario Director inicia sesión en el sistema.
    2. Navega directamente a /carga-academica.
    3. Se espera que pueda ver la pantalla de Carga Académica
       (no sea redirigido al inicio ni a login).
    """

    # 1) Login como Director
    login_page = LoginPage(driver, base_url)
    login_page.open_login()
    evidencia("director_login__form_visible")

    login_page.login_as(director_creds["email"], director_creds["password"])
    assert login_page.is_logged_in(), "El usuario Director no quedó autenticado tras el login válido."
    evidencia("director_login__ok")

    # 2) Navegar directamente a /carga-academica
    carga_academica_url = f"{base_url.rstrip('/')}/carga-academica"
    driver.get(carga_academica_url)
    evidencia("director_carga_academica__navegacion_directa")

    # 3) Esperar que realmente estemos en la pantalla de Carga Académica
    wait = WebDriverWait(driver, 20)

    def _carga_academica_cargada(drv):
        current = drv.current_url.rstrip("/")
        body_text = drv.find_element(By.TAG_NAME, "body").text.lower()

        url_ok = current.endswith("/carga-academica")
        # Si en tu pantalla sale otro texto clave, cámbialo aquí
        texto_ok = ("carga académica" in body_text) or ("carga academica" in body_text)

        # Esto ayuda cuando algo falla, para debug
        print(f"[DEBUG] current_url={current} | texto_ok={texto_ok}")
        return url_ok and texto_ok

    wait.until(_carga_academica_cargada)

    current_url = driver.current_url.rstrip("/")
    assert current_url.endswith("/carga-academica"), (
        "Se esperaba que el Director permaneciera en la ruta '/carga-academica', "
        f"pero quedó en: {current_url}"
    )

    evidencia("director_carga_academica__acceso_ok")

@pytest.mark.functional
@pytest.mark.e2e
@pytest.mark.case("DIRECTOR_CARGA_ACADEMICA_01")
def test_director_no_puede_generar_carga_academica_duplicada(
    driver,
    base_url,
    director_creds,
    evidencia,
):
    # 1) Login como Director
    login_page = LoginPage(driver, base_url)
    login_page.open_login()
    evidencia("director_login__form_visible")

    login_page.login_as(director_creds["email"], director_creds["password"])
    assert login_page.is_logged_in(), "El director no quedó autenticado tras el login."
    evidencia("director_login__ok")

    # 2) Navegar directamente a /carga-academica
    carga_url = f"{base_url.rstrip('/')}/carga-academica"
    driver.get(carga_url)
    evidencia("director_carga_academica__navegacion_directa")

    # Aquí creamos el Page Object
    carga_page = DirectorCargaAcademicaPage(driver)
    
    time.sleep(2)

    # (opcional) validar que estamos en la página
    carga_page = DirectorCargaAcademicaPage(driver)

    assert carga_page.is_on_page(), "No se cargó correctamente /carga-academica"

    time.sleep(2)

    carga_page.click_generar_nueva_carga()
    evidencia("director_carga__click_generar")

    carga_page.confirmar_generar_carga()
    evidencia("director_carga__confirmar_generar")

    assert carga_page.esperar_error_carga_ya_existente(), (
        "No apareció el modal de error indicando que ya existe una carga académica."
    )
    evidencia("director_carga__error_carga_existente")

    carga_page.cerrar_modal_error()
    evidencia("director_carga__cerrar_error")

    assert "/carga-academica" in driver.current_url

@pytest.mark.functional
@pytest.mark.e2e
@pytest.mark.case("DIRECTOR_CARGA_ACADEMICA_LISTAR")
def test_director_puede_listar_cargas_academicas(
    driver,
    base_url,
    director_creds,
    evidencia,
):
    """
    Escenario:
    1. Director inicia sesión.
    2. Navega a /carga-academica.
    3. Se muestra la tabla de cargas académicas.
    4. Se valida que exista al menos una carga listada.
    """

    # 1) Login como Director
    login_page = LoginPage(driver, base_url)
    login_page.open_login()
    evidencia("director_login__form_visible_listar_carga")

    login_page.login_as(director_creds["email"], director_creds["password"])
    assert login_page.is_logged_in(), "El director no quedó autenticado tras el login."
    evidencia("director_login__ok_listar_carga")

    # 2) Navegar directamente a /carga-academica
    carga_url = f"{base_url.rstrip('/')}/carga-academica"
    driver.get(carga_url)
    evidencia("director_carga_academica__navegacion_directa_listar")

    carga_page = DirectorCargaAcademicaPage(driver)
    assert carga_page.is_on_page(), "No se cargó correctamente /carga-academica"

    # 3) Esperar que la tabla esté visible y con filas
    carga_page.wait_list_loaded()
    evidencia("director_carga_academica__tabla_visible")

    # 4) Validar que hay al menos una carga académica listada
    num_cargas = carga_page.count_cargas()
    print(f"[DEBUG] Cantidad de cargas académicas listadas: {num_cargas}")
    assert num_cargas > 0, "Se esperaba al menos una carga académica listada en la tabla."

@pytest.mark.functional
@pytest.mark.e2e
@pytest.mark.case("DIRECTOR_CARGA_ACADEMICA_BUSQUEDA_OK")
def test_director_busca_carga_academica_existente(
    driver,
    base_url,
    director_creds,
    evidencia,
):
    """
    Escenario:
    1. Director inicia sesión.
    2. Navega a /carga-academica.
    3. Escribe un texto que corresponde a una carga existente.
    4. Da clic en la lupa.
    5. Se muestra al menos una fila que contenga ese texto.
    """

    # 1) Login como Director
    login_page = LoginPage(driver, base_url)
    login_page.open_login()
    evidencia("director_carga_busqueda_ok__login_form")

    login_page.login_as(director_creds["email"], director_creds["password"])
    assert login_page.is_logged_in(), "El director no quedó autenticado tras el login."
    evidencia("director_carga_busqueda_ok__login_ok")

    # 2) Ir a /carga-academica
    carga_url = f"{base_url.rstrip('/')}/carga-academica"
    driver.get(carga_url)
    evidencia("director_carga_busqueda_ok__navegacion_directa")

    carga_page = DirectorCargaAcademicaPage(driver)
    assert carga_page.is_on_page(), "No se cargó correctamente /carga-academica"

    carga_page.wait_list_loaded()
    evidencia("director_carga_busqueda_ok__tabla_visible")

    # 3) Buscar una carga que sabemos que existe (por texto parcial)
    texto_busqueda = "Ciclo 1-2025"  # aparece en varias filas según la pantalla
    carga_page.search_carga(texto_busqueda)
    evidencia("director_carga_busqueda_ok__search_enviado")

    # 4) Validar que hay al menos una fila que contenga ese texto
    assert carga_page.wait_row_with_text(texto_busqueda), (
        f"No se encontró ninguna fila que contenga el texto: {texto_busqueda!r}"
    )
    evidencia("director_carga_busqueda_ok__resultado_en_tabla")

@pytest.mark.functional
@pytest.mark.e2e
@pytest.mark.case("DIRECTOR_CARGA_ACADEMICA_BUSQUEDA_SIN_RESULTADOS")
def test_director_busca_carga_academica_inexistente(
    driver,
    base_url,
    director_creds,
    evidencia,
):
    """
    Escenario:
    1. Director inicia sesión.
    2. Navega a /carga-academica.
    3. Escribe un texto que NO corresponde a ninguna carga.
    4. Da clic en la lupa.
    5. Se muestra el placeholder de 'No hay datos'.
    """

    # 1) Login como Director
    login_page = LoginPage(driver, base_url)
    login_page.open_login()
    evidencia("director_carga_busqueda_empty__login_form")

    login_page.login_as(director_creds["email"], director_creds["password"])
    assert login_page.is_logged_in(), "El director no quedó autenticado tras el login."
    evidencia("director_carga_busqueda_empty__login_ok")

    # 2) Ir a /carga-academica
    carga_url = f"{base_url.rstrip('/')}/carga-academica"
    driver.get(carga_url)
    evidencia("director_carga_busqueda_empty__navegacion_directa")

    carga_page = DirectorCargaAcademicaPage(driver)
    assert carga_page.is_on_page(), "No se cargó correctamente /carga-academica"

    carga_page.wait_list_loaded()
    evidencia("director_carga_busqueda_empty__tabla_visible")

    # 3) Buscar algo que claramente no exista
    texto_inexistente = "Carga academica fantasma 2099 XYZ"
    carga_page.search_carga(texto_inexistente)
    evidencia("director_carga_busqueda_empty__search_enviado")

    # 4) Esperar el mensaje de No hay datos
    assert carga_page.wait_no_data_message(), (
        "Se esperaba ver el mensaje de 'No hay datos' al no encontrar cargas académicas."
    )
    evidencia("director_carga_busqueda_empty__no_hay_datos")