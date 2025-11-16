# tests/functional/test_asistente_subir_acuerdo.py
import os
import pytest
import time
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pages.login_page import LoginPage
from pages.asistente_home_page import AsistenteHomePage, RecepcionSolicitudesPage
from pages.subir_acuerdo_page import SubirAcuerdoPage


def _ensure_min_pdf(path: str) -> str:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        minimal_pdf = (
            b"%PDF-1.4\n"
            b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
            b"2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj\n"
            b"3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>endobj\n"
            b"xref\n0 4\n0000000000 65535 f \n"
            b"0000000010 00000 n \n0000000061 00000 n \n0000000112 00000 n \n"
            b"trailer<</Size 4/Root 1 0 R>>\nstartxref\n164\n%%EOF\n"
        )
        with open(path, "wb") as f:
            f.write(minimal_pdf)
    return os.path.abspath(path)


@pytest.mark.functional
@pytest.mark.case("CP_ASISTENTE_Subir_Acuerdo_Junta")
def test_asistente_subir_acuerdo(driver, base_url, evidencia, cod_cache):
    codigo = cod_cache["get"](None)
    if not codigo:
        pytest.skip("No hay código cacheado desde la prueba anterior.")

    # 1) Login
    login = LoginPage(driver, base_url)
    login.open_login()
    login.login_as("asistente@ues.edu.sv", "Password.1")

    WebDriverWait(driver, 15).until(EC.visibility_of_element_located((
        By.XPATH,
        "//header//span[contains(.,'Sesión iniciada como') and "
        "(contains(.,'Asistente') or contains(.,'Asistente Administrativo'))]"
    )))
    evidencia("asistente_login_ok_subir")

    # 2) Recepción
    home = AsistenteHomePage(driver, base_url)
    home.wait_loaded()
    home.go_to_recepcion_solicitudes(evidencia=evidencia)

    recep = RecepcionSolicitudesPage(driver)
    recep.wait_loaded(evidencia=evidencia)
    recep.wait_loaded_table()
    evidencia("asistente_recepcion_visible_subir")

    # 3) Abrir "Subir acuerdo" para el código (marcando recibido si hace falta)
    subir = SubirAcuerdoPage(driver, base_url)
    subir.open_from_recepcion_by_code(codigo)
    evidencia("asistente_form_subir_visible")

    # 4) Completar con fecha dd/mm/yyyy y PDF
    fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    pdf_path = _ensure_min_pdf(os.path.join("fixtures", "acuerdo_demo.pdf"))

    subir.set_codigo("JP-999/2099")
    subir.set_fecha_ddmmyyyy(fecha_hoy)  # <-- ahora sí escribimos y disparamos eventos
    subir.upload_pdf(pdf_path)
    subir.set_aprobado(True)
    evidencia("asistente_form_subir_completado")

    time.sleep(5)  # breve espera para evitar capturas muy tempranas

    # 5) Guardar y verificar éxito (flexible)
    subir.guardar(wait_success=True)
    evidencia("asistente_subir_guardado_ok")

    # Afirmación final adicional (blanda): o vuelve al listado o hay un toast visible
    ok = False
    try:
        WebDriverWait(driver, 3).until(EC.url_contains("/recepcion-solicitudes"))
        ok = True
    except Exception:
        try:
            WebDriverWait(driver, 3).until(EC.presence_of_element_located((
                By.XPATH,
                "//*[contains(@class,'ant-message') or contains(@class,'ant-notification')]"
                "//*[contains(translate(normalize-space(.),'ÁÉÍÓÚáéíóú','AEIOUaeiou'),'exito')"
                " or contains(.,'Guardado') or contains(.,'guardado') or contains(.,'correctamente')]"
            )))
            ok = True
        except Exception:
            ok = False

    assert ok, "No se pudo confirmar el éxito al guardar el Acuerdo."
