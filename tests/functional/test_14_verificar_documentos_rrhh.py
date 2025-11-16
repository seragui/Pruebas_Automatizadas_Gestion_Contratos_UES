import pytest
import time

from pages.login_page import LoginPage
from pages.rrhh_candidates_registered_page import RRHHCandidatesRegisteredPage
from pages.rrhh_candidate_documents_page import (
    RRHHCandidateDocumentsPage,
    RRHHDuiValidationPage, RRHHBankValidationPage,
    RRHHCVValidationPage, RRHHStatementValidationPage,
    RRHHTituloNValidationPage
    
)


def assert_nombre_en_header(candidate_name: str, header_text: str):
    """
    Verifica que al menos 2 palabras del nombre del candidato
    aparezcan en el header de documentos (ignorando mayúsculas).
    """
    header_norm = header_text.lower()
    tokens = [t.lower() for t in candidate_name.split() if len(t) > 2]

    matches = sum(1 for t in tokens if t in header_norm)

    assert matches >= 2, (
        "El header de documentos no parece corresponder al candidato esperado. "
        f"Header: {header_text!r}, nombre esperado: {candidate_name!r}, "
        f"coincidencias de palabras: {matches}"
    )


@pytest.mark.functional
@pytest.mark.e2e
@pytest.mark.case("RRHH_CONTROL_DATOS_01")
def test_rrhh_busca_candidato_y_abre_control_datos(
    driver,
    base_url,
    rrhh_creds,
    evidencia,
    candidate_name_cache
):
    # 1) Nombre desde cache
    candidate_name = candidate_name_cache["get"]()
    assert candidate_name, "No se encontró nombre de candidato en cache (gc/candidate_full_name)."

    print(f"[TEST RRHH] Buscando candidato con nombre: {candidate_name!r}")

    # 2) Login RRHH
    login_page = LoginPage(driver, base_url)
    login_page.open_login()
    evidencia("rrhh_control_datos__login_form_visible")

    login_page.login_as(rrhh_creds["email"], rrhh_creds["password"])
    assert login_page.is_logged_in()
    evidencia("rrhh_control_datos__login_ok")

    time.sleep(1)

    # 3) Ir a Candidatos registrados
    page = RRHHCandidatesRegisteredPage(driver)
    page.open_from_sidebar()
    evidencia("rrhh_control_datos__lista_candidatos")
    assert page.is_on_page()

    time.sleep(3)

    # 4) Buscar candidato por nombre
    page.search_candidate(candidate_name)
    evidencia("rrhh_control_datos__candidato_filtrado")

    # 5) Abrir Control de datos
    page.open_control_datos_for_name(candidate_name)
    evidencia("rrhh_control_datos__detalle_candidato")

    time.sleep(2)

    # 6) Página de documentos
    docs_page = RRHHCandidateDocumentsPage(driver)
    docs_page.wait_loaded()
    evidencia("rrhh_control_datos__documentos_listado")

    header_text = docs_page.get_header_text()
    print(f"[TEST RRHH] Header documentos: {header_text!r}")
    assert_nombre_en_header(candidate_name, header_text)


    # ==========================
    # 7) Validar DUI (todas "Si")
    # ==========================
    docs_page.click_verificar_dui()
    evidencia("rrhh_control_datos__dui_pantalla")

    dui_page = RRHHDuiValidationPage(driver)
    dui_page.wait_loaded()
    evidencia("rrhh_control_datos__dui_validaciones_visible")

    dui_page.mark_all_yes()
    evidencia("rrhh_control_datos__dui_validaciones_todas_si")

    dui_page.submit()
    evidencia("rrhh_control_datos__dui_validaciones_enviadas")

    # Modal de éxito y regreso a documentos
    docs_page.wait_loaded()
    docs_page.wait_success_modal_and_accept()
    evidencia("rrhh_control_datos__dui_modal_aceptado")

    # ==================================
    # 8) Validar Cuenta de Banco (todas "Si")
    # ==================================
    docs_page.click_verificar_banco()
    evidencia("rrhh_control_datos__banco_pantalla")

    banco_page = RRHHBankValidationPage(driver)   # <- CAMBIAR AQUÍ
    banco_page.wait_loaded()
    evidencia("rrhh_control_datos__banco_validaciones_visible")

    banco_page.mark_all_yes()
    evidencia("rrhh_control_datos__banco_validaciones_todas_si")

    banco_page.submit()
    evidencia("rrhh_control_datos__banco_validaciones_enviadas")

    docs_page.wait_success_modal_and_accept()
    evidencia("rrhh_control_datos__banco_modal_aceptado")

    # ==================================
    # 9) Validar CV (todas "Si")
    # ==================================
    docs_page.click_verificar_cv()
    cv_page = RRHHCVValidationPage(driver)
    cv_page.wait_loaded()
    cv_page.mark_all_yes()
    cv_page.submit()
    docs_page.wait_success_modal_and_accept()

    # ==================================
    # 10) Validar Statement (todas "Si")
    # ==================================
    docs_page.click_verificar_statement()
    st_page = RRHHStatementValidationPage(driver)
    st_page.wait_loaded()
    st_page.mark_all_yes()
    st_page.submit()
    docs_page.wait_success_modal_and_accept()

    # ==================================
    # 11) Validar Título (todas "Si")
    # ==================================
    docs_page.click_verificar_title()
    title_page = RRHHTituloNValidationPage(driver)
    title_page.wait_loaded()
    title_page.mark_all_yes()
    title_page.submit()
    docs_page.wait_success_modal_and_accept()

    