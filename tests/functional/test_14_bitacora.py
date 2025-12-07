import pytest
from urllib.parse import urlparse
import time
import allure

from pages.login_page import LoginPage
from pages.bitacora_page import BitacoraPage


@allure.epic("Gestión de Contratos")
@allure.feature("Bitácora de acciones")
@allure.story("Listado muestra registros de actividades")
@allure.severity(allure.severity_level.NORMAL)
@allure.label("owner", "Griselda Fernandez")
@allure.link(
    "https://mi-matriz-casos/BITACORA_LISTADO_01",
    name="BITACORA_LISTADO_01",
)
@pytest.mark.functional
@pytest.mark.e2e
@pytest.mark.regression
@pytest.mark.case("BITACORA_LISTADO_01")
@pytest.mark.tester("Griselda")
def test_cp19_bitacora_listado_muestra_registros(
    driver,
    base_url,
    admin_creds,
    evidencia,
):
    """
    Escenario:
    1. Admin inicia sesión.
    2. Navega a /bitacora.
    3. Verifica que la tabla cargue y tenga al menos un registro.
    """

    allure.dynamic.title("Bitácora - Listado muestra al menos un registro")
    
    # 1) Login admin
    with allure.step("Iniciar sesión como admin"):
        login_page = LoginPage(driver, base_url)
        login_page.open_login()
        evidencia("bitacora_listado__login_form")

        login_page.login_as(admin_creds["email"], admin_creds["password"])
        assert login_page.is_logged_in(), "El admin no quedó autenticado."
        evidencia("bitacora_listado__login_ok")

        time.sleep(3)

    # 2) Ir a bitácora
    with allure.step("Navegar a la pantalla de bitácora"):
        bitacora_page = BitacoraPage(driver)
        bitacora_page.open_direct(base_url)
        evidencia("bitacora_listado__navegacion_directa")

        # Esperar a que la vista cargue (título + tabla con filas o mensaje vacío)
        bitacora_page.wait_loaded()
        evidencia("bitacora_listado__vista_bitacora")

    # 3) Validar URL y que haya filas
    with allure.step("Verificar que la URL es /bitacora y que hay registros en la tabla"):
        current_url = driver.current_url
        path = urlparse(current_url).path
        assert path.endswith("/bitacora"), f"Se esperaba /bitacora, quedó: {current_url}"

        assert bitacora_page.has_rows(), (
            "La bitácora no muestra registros en la tabla, "
            "se esperaba al menos una fila."
        )


@allure.epic("Gestión de Contratos")
@allure.feature("Bitácora de acciones")
@allure.story("Filtrado de bitácora por término existente")
@allure.severity(allure.severity_level.NORMAL)
@allure.label("owner", "Griselda Fernandez")
@allure.link(
    "https://mi-matriz-casos/BITACORA_FILTRO_01",
    name="BITACORA_FILTRO_01",
)
@pytest.mark.functional
@pytest.mark.e2e
@pytest.mark.regression
@pytest.mark.case("BITACORA_FILTRO_01")
@pytest.mark.tester("Griselda")
def test_cp20_bitacora_filtrar_por_termino_existente(
    driver,
    base_url,
    admin_creds,
    evidencia,
):
    """
    Escenario:
    1. Admin inicia sesión.
    2. En bitácora, usa 'Buscar por usuario' con un término que exista.
    3. Verifica que existan resultados y que las filas contengan el texto.
    """

    # Usa un nombre que *sabemos* existe en las filas, por ejemplo "Admin"
    SEARCH_TERM = "Oscar Quintana"
    allure.dynamic.title(
        f"Bitácora - Filtrar por término existente ('{SEARCH_TERM}') muestra resultados coherentes"
    )

    # 1) Login admin
    with allure.step("Iniciar sesión como admin"):
        login_page = LoginPage(driver, base_url)
        login_page.open_login()
        evidencia("bitacora_filtro_ok__login_form")

        login_page.login_as(admin_creds["email"], admin_creds["password"])
        assert login_page.is_logged_in(), "El admin no quedó autenticado."
        evidencia("bitacora_filtro_ok__login_ok")


    # 2) Ir a bitácora
    with allure.step("Navegar a la pantalla de bitácora"):
        bitacora_page = BitacoraPage(driver)
        bitacora_page.open_direct(base_url)
        bitacora_page.wait_loaded()
        time.sleep(3)
        evidencia("bitacora_filtro_ok__vista_bitacora")

    # 3) Aplicar filtro (usuario existente)
    with allure.step(f"Aplicar filtro por usuario con término existente: '{SEARCH_TERM}'"):
        bitacora_page.search_by_text(SEARCH_TERM)
        evidencia("bitacora_filtro_ok__despues_filtrar")

        time.sleep(2)

    # 4) Validar que haya filas y que el texto esté en alguna
    with allure.step("Verificar que las filas filtradas contienen el término buscado"):
        rows_text = bitacora_page.get_rows_text()
        assert rows_text, "Después de filtrar se esperaban filas en la bitácora."

        assert any(SEARCH_TERM.lower() in row.lower() for row in rows_text), (
            f"Se esperaban filas que contuvieran '{SEARCH_TERM}' tras filtrar, "
            f"pero se obtuvieron filas: {rows_text}"
        )



@allure.epic("Gestión de Contratos")
@allure.feature("Bitácora de acciones")
@allure.story("Filtrado de bitácora sin resultados muestra 'No hay datos'")
@allure.severity(allure.severity_level.MINOR)
@allure.label("owner", "Griselda Fernandez")
@allure.link(
    "https://mi-matriz-casos/BITACORA_FILTRO_02",
    name="BITACORA_FILTRO_02",
)
@pytest.mark.functional
@pytest.mark.e2e
@pytest.mark.negative
@pytest.mark.regression
@pytest.mark.case("BITACORA_FILTRO_02")
@pytest.mark.tester("Griselda")
def test_cp20_bitacora_filtrar_por_termino_inexistente_muestra_sin_datos(
    driver,
    base_url,
    admin_creds,
    evidencia,
):
    """
    Escenario:
    1. Admin inicia sesión.
    2. En bitácora, busca por un usuario inexistente.
    3. Verifica que el combo 'Buscar por usuario' muestre 'No hay datos'.
    """

    SEARCH_TERM = "usuario_que_no_existe_12345"

    allure.dynamic.title(
        "Bitácora - Filtrar por término inexistente muestra 'No hay datos' en el combo"
    )

    # 1) Login admin
    with allure.step("Iniciar sesión como admin"):
        login_page = LoginPage(driver, base_url)
        login_page.open_login()
        evidencia("bitacora_filtro_no_results__login_form")

        login_page.login_as(admin_creds["email"], admin_creds["password"])
        assert login_page.is_logged_in(), "El admin no quedó autenticado."
        evidencia("bitacora_filtro_no_results__login_ok")

    # 2) Ir a bitácora
    with allure.step("Navegar a la pantalla de bitácora"):
        bitacora_page = BitacoraPage(driver)
        bitacora_page.open_direct(base_url)
        bitacora_page.wait_loaded()
        evidencia("bitacora_filtro_no_results__vista_bitacora")

    # 3) Buscar usuario inexistente y validar "No hay datos" en dropdown
    with allure.step(
        f"Buscar un usuario inexistente ('{SEARCH_TERM}') y verificar que el combo muestre 'No hay datos'"
    ):
        assert bitacora_page.search_no_results_in_dropdown(SEARCH_TERM), (
            "Se esperaba que el combo de 'Buscar por usuario' mostrara 'No hay datos' "
            "al buscar un usuario inexistente, pero no apareció ese mensaje."
        )
        evidencia("bitacora_filtro_no_results__dropdown_no_hay_datos")


@allure.epic("Gestión de Contratos")
@allure.feature("Bitácora de acciones")
@allure.story("Paginación de registros en el listado de bitácora")
@allure.severity(allure.severity_level.NORMAL)
@allure.label("owner", "Griselda Fernandez")
@allure.link(
    "https://mi-matriz-casos/BITACORA_PAGINACION_01",
    name="BITACORA_PAGINACION_01",
)
@pytest.mark.functional
@pytest.mark.e2e
@pytest.mark.regression
@pytest.mark.case("BITACORA_PAGINACION_01")
@pytest.mark.tester("Griselda")
def test_cp21_bitacora_paginacion_siguiente_pagina_cambia_registros(
    driver,
    base_url,
    admin_creds,
    evidencia,
):
    """
    Escenario:
    1. Admin inicia sesión.
    2. Navega a /bitacora.
    3. Verifica que haya varias páginas.
    4. Pasa a la página siguiente.
    5. Verifica que cambie el número de página activo y los registros.
    """

    allure.dynamic.title(
        "Bitácora - Paginación a la siguiente página cambia número activo y registros"
    )
    # 1) Login admin
    with allure.step("Iniciar sesión como admin"):
        login_page = LoginPage(driver, base_url)
        login_page.open_login()
        evidencia("bitacora_paginacion__login_form")

        login_page.login_as(admin_creds["email"], admin_creds["password"])
        assert login_page.is_logged_in(), "El admin no quedó autenticado."
        evidencia("bitacora_paginacion__login_ok")

    # 2) Ir a bitácora
    with allure.step("Navegar a la pantalla de bitácora"):
        bitacora_page = BitacoraPage(driver)
        bitacora_page.open_direct(base_url)
        bitacora_page.wait_loaded()
        evidencia("bitacora_paginacion__vista_bitacora")

        time.sleep(3)

    # 3) Verificar que exista más de una página
    with allure.step("Verificar que el componente de paginación tenga varias páginas"):
        assert bitacora_page.has_multiple_pages(), (
            "Se esperaba que la bitácora tuviera varias páginas para probar la paginación, "
            "pero solo se detectó una."
        )

        pagina_inicial = bitacora_page.get_active_page_number()
        filas_iniciales = bitacora_page.get_rows_text()
        first_row_before = filas_iniciales[0] if filas_iniciales else None

    

    # 4) Ir a la página siguiente
    with allure.step("Ir a la página siguiente de la bitácora"):
        bitacora_page.go_to_next_page()
        evidencia("bitacora_paginacion__pagina_siguiente")

        time.sleep(2)

        pagina_nueva = bitacora_page.get_active_page_number()
        filas_nuevas = bitacora_page.get_rows_text()

        time.sleep(2)
    
    # 5) Asserts
    with allure.step("Validar que la página activa y los registros cambian"):
        assert pagina_nueva != pagina_inicial, (
            f"Se esperaba cambiar de página (de {pagina_inicial}) pero la página activa "
            f"sigue siendo {pagina_nueva}."
        )

        assert filas_nuevas, "La bitácora no muestra registros en la página siguiente."

        if first_row_before is not None:
            assert filas_nuevas[0] != first_row_before, (
                "El primer registro de la siguiente página es igual al de la página inicial; "
                "parece que la paginación no cambió los registros."
            )