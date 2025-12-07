import pytest
import allure
from pathlib import Path
from pages.login_page import LoginPage
from pages.candidate_upload_documents import CandidateUploadDocumentsPage


@allure.epic("Portal de Candidatos")
@allure.feature("Gestión de documentos")
@allure.story("Candidato sube la documentación requerida")
@allure.severity(allure.severity_level.CRITICAL)
@allure.label("owner", "Jose Lucero")
@allure.link(
    "https://mi-matriz-casos/CANDIDATO_DOCUMENTOS_01",
    name="CANDIDATO_DOCUMENTOS_01",
)
@pytest.mark.functional
@pytest.mark.e2e
@pytest.mark.regression
@pytest.mark.case("CANDIDATO_DOCUMENTOS_01")
@pytest.mark.tester("Jose")
def test_cp15_candidato_ve_modal_subir_documentos(
    driver,
    base_url,
    candidate_creds,
    evidencia,
):
    """
    Escenario:
    1. El candidato inicia sesión en el sistema.
    2. Desde el menú lateral, da clic en 'Subir documentos'.
    3. Se muestra el modal 'Información de subida de documentos'.
    4. El candidato da clic en 'Aceptar' en el modal.
    5. Se mantiene en la pantalla 'Subir documentos'.
    6. Sube los documentos: DUI, Curriculum, Cuenta bancaria, Título, Declaración jurada.
    """
    allure.dynamic.title("Candidato - Subir documentos con modal de información")

    # ===============================
    # 0) Rutas de archivos de prueba
    # ===============================
    with allure.step("Preparar rutas de archivos PDF de prueba"):
        tests_dir = Path(__file__).resolve().parents[1]   # ...\tests

        dui_pdf = tests_dir / "resources" / "docs" / "dui_prueba.pdf"
        cv_pdf = tests_dir / "resources" / "docs" / "cv_prueba.pdf"
        cuenta_pdf = tests_dir / "resources" / "docs" / "cuenta_bancaria_prueba.pdf"
        titulo_pdf = tests_dir / "resources" / "docs" / "titulo_prueba.pdf"
        declaracion_pdf = tests_dir / "resources" / "docs" / "declaracion_jurada_prueba.pdf"

        for p in [dui_pdf, cv_pdf, cuenta_pdf, titulo_pdf, declaracion_pdf]:
            assert p.is_file(), f"Falta el archivo de prueba: {p}"
    # ===============================
    # 1) Login como candidato
    # ===============================
    with allure.step("Login como candidato"):
        login_page = LoginPage(driver, base_url)
        login_page.open_login()
        evidencia("candidato_documentos__login_form_visible")

        login_page.login_as(candidate_creds["email"], candidate_creds["password"])
        assert login_page.is_logged_in(), "El candidato no quedó autenticado tras el login válido."
        evidencia("candidato_documentos__login_ok")

    with allure.step("Navegar a la pantalla 'Subir documentos' desde el menú lateral"):
        # ===============================
        # 2) Ir a 'Subir documentos' desde el menú lateral
        # ===============================
        upload_page = CandidateUploadDocumentsPage(driver)

        # este método debe:
        #  - esperar que aparezca el item de menú "Subir documentos"
        #  - hacer clic
        upload_page.open_from_sidebar()
        evidencia("candidato_documentos__pagina_subir_documentos")

    # ===============================
    # 3) Ver modal de información
    # ===============================
    with allure.step("Ver y validar el modal de información de subida de documentos"):
        upload_page.wait_upload_info_modal()
        evidencia("candidato_documentos__modal_subida_visible")

    # ===============================
    # 4) Aceptar el modal
    # ===============================
    with allure.step("Aceptar el modal de información de subida de documentos"):
        upload_page.accept_upload_info_modal()
        evidencia("candidato_documentos__modal_subida_aceptado")

    # ===============================
    # 5) Seguimos en 'Subir documentos'
    # ===============================
    with allure.step("Verificar que se mantiene la pantalla 'Subir documentos'"):
        assert upload_page.is_on_upload_page(), (
            "Después de cerrar el modal de información de subida de documentos, "
            "no se muestra la pantalla 'Subir documentos'."
        )

        evidencia("candidato_documentos__pantalla_subir_documentos")

    # ===============================
    # 4) Subir DUI
    # ===============================
    with allure.step("Subir documento: DUI"):
        upload_page.upload_dui(str(dui_pdf))
        evidencia("candidato_documentos__subir_dui_ok")

    # ===============================
    # 5) Subir Curriculum
    # ===============================
    with allure.step("Subir documento: Curriculum"):
        upload_page.upload_cv(str(cv_pdf))
        evidencia("candidato_documentos__subir_cv_ok")

    # ===============================
    # 6) Subir Cuenta bancaria
    # ===============================
    with allure.step("Subir documento: Cuenta bancaria"):
        upload_page.upload_bank_account(str(cuenta_pdf))
        evidencia("candidato_documentos__subir_cuenta_bancaria_ok")

    # ===============================
    # 7) Subir Título
    # ===============================
    with allure.step("Subir documento: Título"):
        upload_page.upload_title(str(titulo_pdf))
        evidencia("candidato_documentos__subir_titulo_ok")

    # ===============================
    # 8) Subir Declaración jurada
    # ===============================
    with allure.step("Subir documento: Declaración jurada"):
        upload_page.upload_statement(str(declaracion_pdf))
        evidencia("candidato_documentos__subir_declaracion_ok")
