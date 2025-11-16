# tests/functional/test_contratos_new_request.py
import time
import random
import pytest
import os
from datetime import datetime
from pages.login_page import LoginPage
from pages.contracts_list_page import ContractsListPage, ContractCreateWizard
from pages.contract_detail_page import ContractDetailPage
from pages.director_home_page import DirectorHomePage  # si ya lo tenés
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pages.envio_director_rrhh import enviar_a_rrhh
from pages.logout_bar import LogoutBar
from pages.rrhh_home_page import RRHHHomePage, ValidacionSolicitudesPage, SolicitudDetallePage
from pages.solicitud_revision_page import SolicitudRevisionPage
from pages.asistente_home_page import AsistenteHomePage, RecepcionSolicitudesPage
from pages.asistente_home_page import AsistenteHomePage, RecepcionSolicitudesPage
from pages.subir_acuerdo_page import SubirAcuerdoPage
from pages.generar_contratos_page import GenerarContratosPage, GenerarContratosDetallePage
from pages.contrato_candidato_page import ContratoCandidatoPage
from pages.solicitudes_finalizadas_page import SolicitudesFinalizadasPage


def generar_codigo_jp():
    """
    Genera un código con formato JP-XXX/YYYY
    donde X e Y son dígitos (con ceros a la izquierda).
    Ej: JP-037/5821
    """
    parte1 = random.randint(0, 999)    # 0–999  -> 3 dígitos
    parte2 = random.randint(0, 9999)   # 0–9999 -> 4 dígitos
    return f"JP-{parte1:03d}/{parte2:04d}"


def test_crear_solicitud_contrato(driver, base_url, evidencia, cod_cache ):
    # Login
    login = LoginPage(driver, base_url)
    login.open_login()
    login.login_as("director@ues.edu.sv", "Password.1")
    assert login.is_logged_in(), "No se pudo iniciar sesión."

    # Ir a contratos
    home = DirectorHomePage(driver, base_url)
    home.wait_loaded()
    home.go_to_contratos()

    contratos = ContractsListPage(driver, base_url)
    contratos.wait_loaded()
    evidencia("contratos__listado_cargado")

    # Crear nueva solicitud
    contratos.click_new_request()
    evidencia("contratos__click_generar_nueva")
    time.sleep(1)

    # Wizard
    wizard = ContractCreateWizard(driver)
    wizard.wait_step1_loaded()
    evidencia("wizard_step1__loaded")

    wizard.select_type_and_modality()
    evidencia("wizard_step1__seleccionado")

    wizard.click_next()
    evidencia("wizard_step1__next_click")

    wizard.wait_step2_loaded()
    wizard.wait_step2_active()
    evidencia("wizard_step2__loaded")

    cuerpo = (
        "Estimados/as,\n"
        "Por este medio solicito el ingreso del requerimiento de contratación de un/a docente para la asignatura "
        "Programación I (INF-101) del Departamento de Informática, a impartirse en el Ciclo I-2026.\n"
        "Datos generales:\n"
        "• Carga: 4 horas/semana, 1 sección, modalidad presencial\n"
        "• Horario tentativo: Lunes y miércoles, 8:00–10:00\n"
        "• Periodo: 15/01/2026 – 30/06/2026\n"
        "• Perfil referencial: Ingeniero en Informática o afín, experiencia docente básica\n"
        "• Justificación: Cobertura de sección por demanda estudiantil\n"
    )

    wizard.fill_body(cuerpo)
    evidencia("wizard_step2__body_filled")

    wizard.click_next_step2()
    evidencia("wizard_step2__next_click")

    wizard.wait_step3_loaded()
    evidencia("wizard_step3__loaded")

    wizard.click_register()
    evidencia("wizard_step3__register_click")

    # Cerrar modal y volver a lista
    contratos.confirm_success_modal()
    evidencia("contratos__modal_cerrado")

    # Capturar el código recién creado
    nuevo_codigo = contratos.get_last_created_code()
    print(f"[QA] Código capturado: {nuevo_codigo}")
    assert nuevo_codigo, "No se pudo capturar el código creado."
    evidencia(f"codigo_guardado__{nuevo_codigo}")

    # Guardarlo para el siguiente test
    cod_cache["set"](nuevo_codigo)

def test_agregar_candidato_a_solicitud_contrato(driver, base_url, evidencia, cod_cache, candidate_name_cache, materia_grupo_label):
    # 1) Leemos el código almacenado por la prueba anterior
    codigo = cod_cache["get"](None)
    if not codigo:
        pytest.skip("No hay código cacheado desde la prueba anterior (crear_solicitud).")

    # 2) Recuperar el nombre del candidato desde cache
    nombre_cache = candidate_name_cache["get"](None) 
    assert nombre_cache, (
        "No hay nombre de candidato cacheado. "
        "Asegúrate de que el flujo de candidato (datos personales / docs / validación RRHH) "
        "se ejecutó antes y guardó el nombre."
    )

    # 2) Login (nueva sesión = nuevo login)
    login = LoginPage(driver, base_url)
    login.open_login()
    login.login_as("director@ues.edu.sv", "Password.1")
    assert login.is_logged_in(), "No se pudo iniciar sesión."
    evidencia("login_ok")

    # 3) Ir al listado de contratos
    home = DirectorHomePage(driver, base_url)
    home.wait_loaded()
    home.go_to_contratos()

    contratos = ContractsListPage(driver, base_url)
    contratos.wait_loaded()
    evidencia("contratos_listado_cargado")

    time.sleep(2)  # breve espera por animaciones
    # 4) Buscar por el código cacheado y validar resultado
    contratos.search_code(codigo)
    evidencia(f"busqueda_codigo__{codigo}")
    contratos.ensure_code_visible(codigo)   # <-- usa el helper nuevo
    evidencia(f"resultado_en_tabla__{codigo}")

    # 5) Clic en "Ver" de esa fila
    contratos.click_view_for_code(codigo)
    evidencia(f"click_ver__{codigo}")
    time.sleep(2)  # breve espera por animaciones

    # 6) Asegurar navegación al detalle
    WebDriverWait(driver, 10).until(EC.url_contains("/contratos/solicitud/"))
    evidencia(f"detalle_cargado__{codigo}")

    # 7) Ya en el detalle, NO volver a usar 'contratos'. Usa el page object del detalle
    from pages.contract_detail_page import ContractDetailPage
    detail = ContractDetailPage(driver)
    detail.wait_loaded()
    evidencia("detalle_ready")

    # 8) Click en "Agregar Candidato"
    detail.click_add_candidate()
    evidencia("click_agregar_candidato")

    WebDriverWait(driver, 10).until(EC.url_contains("/contratos/solicitud/"))
    evidencia(f"detalle_cargado__{codigo}")
    assert "/contratos/solicitud/" in driver.current_url, "No navegó al detalle de la solicitud."

    detail.wait_add_candidate_loaded()
    evidencia("pantalla_agregar_candidato_cargada")

    # Escribimos y seleccionamos
    detail.select_candidate_by_typing_and_pick(
    nombre_cache.lower(),
    exact=nombre_cache)
    evidencia(f"candidato_{nombre_cache}_seleccionado")

    detail.select_cargo("Profesor")
    evidencia("cargo_profesor_seleccionado")

    time.sleep(3)  # breve espera por animaciones

    detail.select_all_functions()
    evidencia("funciones_todas_seleccionadas")

    detail.click_agregar_cargo()
    evidencia("agregar_cargo_click")

    detail.ensure_cargo_visible("Profesor")
    evidencia("cargo_profesor_agregado")

    detail.set_period_dates("01/06/2025", "09/11/2025")
    evidencia("periodo_contratacion_lleno")

    detail.select_materia_grupo(materia_grupo_label)
    evidencia(f"materia_grupo__{materia_grupo_label}__seleccionado")

    detail.fill_compensation(hourly_usd=15, weeks=16, weekly_hours=4)
    evidencia("compensacion_15usd_16sem_4hsem_ok")

    detail.click_agregar_materia()
    evidencia("materia_agregada")

    # Valida la fila recién agregada (ajusta si cambiaste los números)
    detail.assert_ultima_fila(valor_hora=15.00, horas_sem=4, semanas=16)
    evidencia("materia_valores_ok")

    detail.click_guardar()
    evidencia("click_guardar")

    detail.wait_redirect_to_detail()
    evidencia("detalle_post_guardar")

    detail.wait_success_message()
    evidencia("toast_exito_visible")

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
    enviar_a_rrhh(driver, evidencia)

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

def test_validar_solicitud_rrhh(driver, base_url, evidencia, cod_cache):
    codigo = cod_cache["get"](None)
    if not codigo:
        pytest.skip("No hay código cacheado (gc/ultimo_codigo). Ejecutá antes el flujo que guarda el código.")

    # 1) Login RRHH
    login = LoginPage(driver, base_url)
    login.open_login()
    login.login_as("rrhh@ues.edu.sv", "Password.1")
    wait = WebDriverWait(driver, 15)
    wait.until(EC.visibility_of_element_located((
        By.XPATH,
        "//header//span[contains(.,'Sesión iniciada como') "
        "and (contains(.,'RRHH') or contains(.,'Recursos Humanos'))]"
    )))
    evidencia("login_rrhh_ok")

    # 2) Validación de solicitudes
    rrhh_home = RRHHHomePage(driver, base_url)
    rrhh_home.wait_loaded()
    rrhh_home.go_to_validacion(evidencia)
    evidencia("validacion_solicitudes_nav")

    # 3) Abrir detalle por código
    listado = ValidacionSolicitudesPage(driver)
    listado.wait_loaded()
    evidencia("validacion_solicitudes_visible")
    listado.click_ver_solicitud(codigo, evidencia)
    evidencia(f"rrhh_detalle_abierto__{codigo}")

    # 4) Seleccionar 'Validar sin observaciones'
    detalle = SolicitudDetallePage(driver)
    detalle.wait_loaded()
    detalle.seleccionar_validar_sin_observaciones(evidencia=evidencia)
    evidencia("rrhh_detalle_radio_validar_sin_obs")

    # 5) Guardar + Confirmar
    detalle.guardar(evidencia=evidencia)

    # 6) Éxito (toast o redirección /solicitudes)
    detalle.esperar_exito(evidencia=evidencia)
    evidencia("rrhh_validacion_sin_obs_exito")
    time.sleep(1)

def test_enviar_solicitud_a_secretaria(driver, base_url, evidencia, cod_cache):
    codigo = cod_cache["get"](None)
    if not codigo:
        pytest.skip("No hay código cacheado desde la prueba anterior.")

    # 2) Login Director
    login = LoginPage(driver, base_url)
    login.open_login()
    login.login_as("director@ues.edu.sv", "Password.1")
    assert login.is_logged_in(), "No se pudo iniciar sesión como Director."
    evidencia("login_director_ok_sec")

    # 3) Ir a Solicitudes y buscar por código
    home = DirectorHomePage(driver, base_url)
    home.wait_loaded()
    home.go_to_contratos()

    contratos = ContractsListPage(driver, base_url)
    contratos.wait_loaded()
    evidencia("listado_contratos_visible_sec")

    time.sleep(1)  # microespera por animación de tabla/filtros
    contratos.search_code(codigo)
    evidencia(f"buscar_codigo__{codigo}_sec")
    contratos.ensure_code_visible(codigo)
    evidencia(f"codigo_en_tabla__{codigo}_sec")

    # 4) Entrar al detalle
    contratos.click_view_for_code(codigo)
    time.sleep(2)  # breve espera por animaciones
    WebDriverWait(driver, 12).until(EC.url_contains("/contratos/solicitud/"))
    evidencia(f"detalle_solicitud__{codigo}_sec")

    pagina = SolicitudRevisionPage(driver)
    time.sleep(2)  # espera breve por animaciones   
    pagina.wait_loaded(evidencia=evidencia)
    pagina.enviar_a_secretaria(evidencia=evidencia)  # listo

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

    # 3) Abrir “Subir acuerdo” (marcando recibido si hace falta)
    subir = SubirAcuerdoPage(driver, base_url)
    subir.open_from_recepcion_by_code(codigo)
    evidencia("asistente_form_subir_visible")

    # 4) Completar con fecha dd/mm/yyyy y PDF
    fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    pdf_path = _ensure_min_pdf(os.path.join("fixtures", "acuerdo_demo.pdf"))

    codigo = generar_codigo_jp()
    subir.set_codigo(codigo)
    subir.set_fecha_ddmmyyyy(fecha_hoy)
    subir.upload_pdf(pdf_path)
    subir.set_aprobado(True)
    evidencia("asistente_form_subir_completado")

    # 5) Guardar (el PageObject espera toast + redirección)
    time.sleep(0.5)  # leve respiro visual en evidencias
    subir.guardar()
    evidencia("asistente_subir_guardado_ok")

    # 6) Afirmación final: estamos de vuelta en recepción
    WebDriverWait(driver, 8).until(EC.url_contains("/recepcion-solicitudes"))

def test_generar_contratos_rrhh(driver, base_url, evidencia, cod_cache):
    codigo = cod_cache["get"](None)
    if not codigo:
        pytest.skip("No hay código cacheado desde la prueba anterior.")

    # 1) Login RRHH
    login = LoginPage(driver, base_url)
    login.open_login()
    login.login_as("rrhh@ues.edu.sv", "Password.1")
    wait = WebDriverWait(driver, 15)
    wait.until(EC.visibility_of_element_located((
        By.XPATH,
        "//header//span[contains(.,'Sesión iniciada como') and "
        "(contains(.,'RRHH') or contains(.,'Recursos Humanos'))]"
    )))
    evidencia("rrhh_login_ok")

    # 2) Ir al módulo: Generar contratos
    rrhh = RRHHHomePage(driver, base_url)
    rrhh.wait_loaded()
    rrhh.go_to_generar_contratos(evidencia=evidencia)

    # 3) Sanity-check de que la vista cargó
    wait.until(EC.url_contains("/generar-contratos"))
    wait.until(EC.visibility_of_element_located((
        By.XPATH,
        "//*[contains(@class,'ant-page-header') or contains(@class,'ant-typography')]"
        "//*[normalize-space()='Generar contratos']"
    )))
    wait.until(EC.presence_of_element_located((
        By.XPATH, "//div[contains(@class,'ant-table') and .//table]"
    )))
    evidencia("rrhh_generar_contratos_listo")

    time.sleep(2)  # breve espera por animaciones

    gen = GenerarContratosPage(driver)
    gen.wait_loaded(evidencia=evidencia)
    time.sleep(3)
    gen.click_ver(codigo, evidencia=evidencia)

    gc_detalle = GenerarContratosDetallePage(driver)
    gc_detalle.wait_loaded(evidencia=evidencia)
    gc_detalle.click_contrato_by_name("Veronica Camila Campos Vega", evidencia=evidencia)

    # Ahora sí, estamos en "Contrato - ..."
    contrato = ContratoCandidatoPage(driver)
    contrato.wait_loaded(evidencia=evidencia)

    # 1) Generar versión y aceptar
    contrato.generar_nueva_version(evidencia=evidencia)

    # 2) Avanzar estados (toma evidencias por estado)
    contrato.completar_flujo_estados("09/11/2025", evidencia=evidencia)

    contrato.volver_a_generar_contratos(evidencia=evidencia)

    gc_detalle = GenerarContratosDetallePage(driver)
    gc_detalle.wait_loaded(evidencia=evidencia)

    # Marcar como finalizada
    gc_detalle.marcar_como_finalizada(evidencia=evidencia)

    # Ir a Solicitudes finalizadas
    gc_detalle.ir_a_solicitudes_finalizadas(evidencia=evidencia)

    # Verificar que aparece el código
    sol_fin = SolicitudesFinalizadasPage(driver)
    sol_fin.assert_code_present(codigo, evidencia=evidencia)
                        
                   