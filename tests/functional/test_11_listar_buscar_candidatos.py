import pytest
import time
import allure

from pages.login_page import LoginPage
from pages.rrhh_candidates_registered_page import RRHHCandidatesRegisteredPage

@allure.epic("Gestión de Contratos")
@allure.feature("RRHH - Candidatos registrados")
@allure.story("RRHH visualiza candidato registrado en la tabla")
@allure.severity(allure.severity_level.NORMAL)
@allure.label("owner", "Ronald Aguilar")
@allure.link(
    "https://mi-matriz-casos/RRHH_CANDIDATO_REGISTRADO_01",
    name="RRHH_CANDIDATO_REGISTRADO_01",
)
@pytest.mark.functional
@pytest.mark.e2e
@pytest.mark.regression
@pytest.mark.case("RRHH_CANDIDATO_REGISTRADO_01")
@pytest.mark.tester("Ronald")
def test_cp14_rrhh_ve_candidato_en_candidatos_registrados(
    driver,
    base_url,
    rrhh_creds,
    evidencia,
    candidate_name_cache,
):
    """
    Escenario:
    1. RRHH inicia sesión en el sistema.
    2. Abre el menú 'Candidatos registrados'.
    3. Busca por el nombre del candidato previamente registrado.
    4. Verifica que el candidato aparezca en los resultados de la tabla.
    """

    allure.dynamic.title(
        "RRHH - Ver candidato previamente registrado en 'Candidatos registrados'"
    )

    with allure.step("Obtener nombre del candidato desde cache"):
        # Nombre del candidato guardado en cache en el flujo anterior
        candidate_name = candidate_name_cache["get"]()
        assert candidate_name, "No hay nombre de candidato guardado en cache para buscar."

    # 1) Login como RRHH
    with allure.step("Login como usuario de RRHH"):
        login_page = LoginPage(driver, base_url)
        login_page.open_login()
        evidencia("rrhh_login__form_visible")

        login_page.login_as(rrhh_creds["email"], rrhh_creds["password"])
        assert login_page.is_logged_in(), "RRHH no quedó autenticado tras el login válido."
        evidencia("rrhh_login__ok")

    # 2) Abrir 'Candidatos registrados' desde el sidebar
    with allure.step("Abrir página 'Candidatos registrados' desde el menú lateral"):
        rrhh_page = RRHHCandidatesRegisteredPage(driver)
        rrhh_page.open_from_sidebar()
        evidencia("rrhh_candidatos__pagina_visible")

        time.sleep(3)


    # 3) Buscar por el nombre de candidato
    with allure.step(f"Buscar candidato por nombre: {candidate_name}"):
        rrhh_page.search_candidate(candidate_name)
        evidencia("rrhh_candidatos__busqueda_realizada")

    # 4) Verificar que el candidato esté en la tabla
    with allure.step("Verificar que el candidato aparezca en la tabla de resultados"):
        assert rrhh_page.has_candidate_in_table(candidate_name), (
            f"El candidato {candidate_name!r} no aparece en la tabla de 'Candidatos registrados'."
        )
        evidencia("rrhh_candidatos__candidato_en_tabla")

@allure.epic("Gestión de Contratos")
@allure.feature("RRHH - Candidatos registrados")
@allure.story("Búsqueda de candidatos: manejo de resultados vacíos")
@allure.severity(allure.severity_level.MINOR)
@allure.label("owner", "Ronald Aguilar")
@allure.link(
    "https://mi-matriz-casos/RRHH_CANDIDATOS_NO_DATOS_01",
    name="RRHH_CANDIDATOS_NO_DATOS_01",
)
@pytest.mark.functional
@pytest.mark.e2e
@pytest.mark.negative
@pytest.mark.regression
@pytest.mark.case("RRHH_CANDIDATOS_NO_DATOS_01")
@pytest.mark.tester("Ronald")
def test_cp14_rrhh_busca_candidato_inexistente_y_ve_no_hay_datos(
    driver,
    base_url,
    rrhh_creds,
    evidencia,
):
    """
    Escenario:
    1. RRHH inicia sesión.
    2. Abre el menú 'Candidatos registrados'.
    3. Busca un nombre de candidato inexistente.
    4. La tabla muestra el mensaje 'No hay datos'.
    """

    allure.dynamic.title(
        "RRHH - Búsqueda de candidato inexistente muestra 'No hay datos'"
    )

    # 1) Login como RRHH
    with allure.step("Login como usuario de RRHH"):
        login_page = LoginPage(driver, base_url)
        login_page.open_login()
        evidencia("rrhh_login__form_visible")

        login_page.login_as(rrhh_creds["email"], rrhh_creds["password"])
        assert login_page.is_logged_in(), "RRHH no quedó autenticado."
        evidencia("rrhh_login__ok")

    # 2) Ir a 'Candidatos registrados'
    with allure.step("Abrir página 'Candidatos registrados' desde el menú lateral"):
        rrhh_page = RRHHCandidatesRegisteredPage(driver)
        rrhh_page.open_from_sidebar()
        evidencia("rrhh_candidatos__pantalla_listado")

    # 3) Buscar un nombre que seguro no exista
    with allure.step("Buscar candidato inexistente y observar el resultado"):
        nombre_inexistente = "CANDIDATO_INEXISTENTE_XYZ_999"
        rrhh_page.search_any_name(nombre_inexistente)
        evidencia("rrhh_candidatos__busqueda_inexistente")

    # 4) Verificar mensaje 'No hay datos'
    with allure.step("Verificar que la tabla muestra el mensaje 'No hay datos'"):
        assert rrhh_page.shows_no_data_message(), (
            "Al buscar un candidato inexistente, se esperaba ver el mensaje "
            "'No hay datos' en la tabla, pero no apareció."
        )