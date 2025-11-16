import pytest
import time

from pages.login_page import LoginPage
from pages.rrhh_candidates_registered_page import RRHHCandidatesRegisteredPage

@pytest.mark.functional
@pytest.mark.e2e
@pytest.mark.case("RRHH_CANDIDATO_REGISTRADO_01")
def test_rrhh_ve_candidato_en_candidatos_registrados(
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

    # Nombre del candidato guardado en cache en el flujo anterior
    candidate_name = candidate_name_cache["get"]()
    assert candidate_name, "No hay nombre de candidato guardado en cache para buscar."

    # 1) Login como RRHH
    login_page = LoginPage(driver, base_url)
    login_page.open_login()
    evidencia("rrhh_login__form_visible")

    login_page.login_as(rrhh_creds["email"], rrhh_creds["password"])
    assert login_page.is_logged_in(), "RRHH no quedó autenticado tras el login válido."
    evidencia("rrhh_login__ok")

    # 2) Abrir 'Candidatos registrados' desde el sidebar
    rrhh_page = RRHHCandidatesRegisteredPage(driver)
    rrhh_page.open_from_sidebar()
    evidencia("rrhh_candidatos__pagina_visible")

    time.sleep(3)


    # 3) Buscar por el nombre de candidato
    rrhh_page.search_candidate(candidate_name)
    evidencia("rrhh_candidatos__busqueda_realizada")

    # 4) Verificar que el candidato esté en la tabla
    assert rrhh_page.has_candidate_in_table(candidate_name), (
        f"El candidato {candidate_name!r} no aparece en la tabla de 'Candidatos registrados'."
    )
    evidencia("rrhh_candidatos__candidato_en_tabla")

@pytest.mark.functional
@pytest.mark.e2e
@pytest.mark.case("RRHH_CANDIDATOS_NO_DATOS_01")
def test_rrhh_busca_candidato_inexistente_y_ve_no_hay_datos(
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

    # 1) Login como RRHH
    login_page = LoginPage(driver, base_url)
    login_page.open_login()
    evidencia("rrhh_login__form_visible")

    login_page.login_as(rrhh_creds["email"], rrhh_creds["password"])
    assert login_page.is_logged_in(), "RRHH no quedó autenticado."
    evidencia("rrhh_login__ok")

    # 2) Ir a 'Candidatos registrados'
    rrhh_page = RRHHCandidatesRegisteredPage(driver)
    rrhh_page.open_from_sidebar()
    evidencia("rrhh_candidatos__pantalla_listado")

    # 3) Buscar un nombre que seguro no exista
    nombre_inexistente = "CANDIDATO_INEXISTENTE_XYZ_999"
    rrhh_page.search_any_name(nombre_inexistente)
    evidencia("rrhh_candidatos__busqueda_inexistente")

    # 4) Verificar mensaje 'No hay datos'
    assert rrhh_page.shows_no_data_message(), (
        "Al buscar un candidato inexistente, se esperaba ver el mensaje "
        "'No hay datos' en la tabla, pero no apareció."
    )