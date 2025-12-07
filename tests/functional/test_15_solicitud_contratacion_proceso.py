# tests/functional/test_contratos_new_request.py
import time
import random
import pytest
import allure 
import os
from datetime import datetime
from pages.login_page import LoginPage
from pages.contracts_list_page import ContractsListPage, ContractCreateWizard
from pages.contract_detail_page import ContractDetailPage
from pages.director_home_page import DirectorHomePage  
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


@allure.epic("Gestión de Contratos")
@allure.feature("Módulo de Contratos")
@allure.story("Director genera solicitud de contratación desde el wizard")
@allure.severity(allure.severity_level.CRITICAL)
@allure.label("owner", "Ronald Aguilar")
@allure.link(
    "https://mi-matriz-casos/CONTRATO_CREAR_SOLICITUD_01",
    name="CONTRATO_CREAR_SOLICITUD_01",
)
@pytest.mark.functional
@pytest.mark.e2e
@pytest.mark.case("CONTRATO_CREAR_SOLICITUD_01")
@pytest.mark.tester("Ronald")
def test_cp30_crear_solicitud_contrato(driver, base_url, evidencia, cod_cache ):
    """
    Escenario:
    1. Director inicia sesión.
    2. Desde el home, navega a 'Contratos'.
    3. Abre el wizard 'Generar nueva solicitud de contrato'.
    4. Completa los pasos del wizard.
    5. Registra la solicitud y se muestra modal de éxito.
    6. Se captura el código de la solicitud creada y se guarda en cache
       para ser usado en pruebas posteriores.
    """
    allure.dynamic.title("Director - Crear nueva solicitud de contrato y capturar código")
    
    # Login
    with allure.step("Iniciar sesión como Director"):
        login = LoginPage(driver, base_url)
        login.open_login()
        evidencia("contrato_crear__login_form")
        login.login_as("director@ues.edu.sv", "Password.1")
        assert login.is_logged_in(), "No se pudo iniciar sesión."
        evidencia("contrato_crear__login_ok")

    # Ir a contratos
    with allure.step("Navegar al módulo de 'Contratos' desde el home de Director"):
        home = DirectorHomePage(driver, base_url)
        home.wait_loaded()
        home.go_to_contratos()

        contratos = ContractsListPage(driver, base_url)
        contratos.wait_loaded()
        evidencia("contratos__listado_cargado")

    # Crear nueva solicitud
    with allure.step("Abrir wizard de 'Generar nueva solicitud de contrato'"):
        contratos.click_new_request()
        evidencia("contratos__click_generar_nueva")
        time.sleep(1)

    # Wizard
    with allure.step("Completar Step 1 del wizard: tipo y modalidad"):
        wizard = ContractCreateWizard(driver)
        wizard.wait_step1_loaded()
        evidencia("wizard_step1__loaded")

        wizard.select_type_and_modality()
        evidencia("wizard_step1__seleccionado")

        wizard.click_next()
        evidencia("wizard_step1__next_click")

    # 5) Paso 2 del wizard: cuerpo de la solicitud
    with allure.step("Completar Step 2 del wizard: cuerpo de la solicitud"):
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

    # 6) Paso 3 del wizard: confirmación y registro
    with allure.step("Completar Step 3 del wizard y registrar la solicitud"):
        wizard.wait_step3_loaded()
        evidencia("wizard_step3__loaded")

        wizard.click_register()
        evidencia("wizard_step3__register_click")

    # Cerrar modal y volver a lista
    # 7) Confirmar modal de éxito y regresar al listado
    with allure.step("Confirmar modal de éxito y volver al listado de contratos"):
        contratos.confirm_success_modal()
        evidencia("contratos__modal_cerrado")

    # Capturar el código recién creado
    # 8) Capturar código de solicitud creada y guardarlo en cache
    with allure.step("Capturar el código de la solicitud recién creada y guardarlo en cache"):
        nuevo_codigo = contratos.get_last_created_code()
        print(f"[QA] Código capturado: {nuevo_codigo}")
        assert nuevo_codigo, "No se pudo capturar el código creado."
        evidencia(f"codigo_guardado__{nuevo_codigo}")

        # Guardarlo para el siguiente test
        cod_cache["set"](nuevo_codigo)

@allure.epic("Gestión de Contratos")
@allure.feature("Módulo de Contratos")
@allure.story("Director agrega candidato a una solicitud existente")
@allure.severity(allure.severity_level.CRITICAL)
@allure.label("owner", "Ronald Aguilar")
@allure.link(
    "https://mi-matriz-casos/CONTRATO_AGREGAR_CANDIDATO_01",
    name="CONTRATO_AGREGAR_CANDIDATO_01",
)
@pytest.mark.functional
@pytest.mark.e2e
@pytest.mark.case("CONTRATO_AGREGAR_CANDIDATO_01")
@pytest.mark.tester("Ronald")
def test_cp_31_agregar_candidato_a_solicitud_contrato(driver, base_url, evidencia, cod_cache, candidate_name_cache, materia_grupo_label):
    """
    Escenario:
    1. Recuperar el código de solicitud creado previamente (cache).
    2. Recuperar el nombre del candidato ya registrado y validado (cache).
    3. Director inicia sesión.
    4. Busca la solicitud por código y abre el detalle.
    5. Agrega un candidato, su cargo, periodo, materia/grupo y compensación.
    6. Guarda los cambios y verifica mensaje de éxito.
    """

    allure.dynamic.title(
        "Director - Agregar candidato, carga y compensación a una solicitud de contrato"
    )
    
    # 1) Leemos el código almacenado por la prueba anterior
    with allure.step("Recuperar código de solicitud desde cache"):
        codigo = cod_cache["get"](None)
        if not codigo:
            pytest.skip("No hay código cacheado desde la prueba anterior (crear_solicitud).")

    # 2) Recuperar el nombre del candidato desde cache
    with allure.step("Recuperar nombre de candidato desde cache"):
        nombre_cache = candidate_name_cache["get"](None) 
        assert nombre_cache, (
            "No hay nombre de candidato cacheado. "
            "Asegúrate de que el flujo de candidato (datos personales / docs / validación RRHH) "
            "se ejecutó antes y guardó el nombre."
        )

    # 3) Login (nueva sesión = nuevo login)
    with allure.step("Iniciar sesión como Director"):
        login = LoginPage(driver, base_url)
        login.open_login()
        login.login_as("director@ues.edu.sv", "Password.1")
        assert login.is_logged_in(), "No se pudo iniciar sesión."
        evidencia("login_ok")

    # 4) Ir al listado de contratos
    with allure.step("Navegar al listado de contratos y buscar por código"):
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
        contratos.ensure_code_visible(codigo)   
        evidencia(f"resultado_en_tabla__{codigo}")

    # 5) Abrir detalle de la solicitud
    with allure.step("Abrir el detalle de la solicitud de contrato"):
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

    # 6) Ir a flujo de agregar candidato
    with allure.step("Abrir pantalla 'Agregar Candidato'"):
        detail.click_add_candidate()
        evidencia("click_agregar_candidato")

        WebDriverWait(driver, 10).until(EC.url_contains("/contratos/solicitud/"))
        evidencia(f"detalle_cargado__{codigo}")
        assert "/contratos/solicitud/" in driver.current_url, "No navegó al detalle de la solicitud."

        detail.wait_add_candidate_loaded()
        evidencia("pantalla_agregar_candidato_cargada")

    # 7) Seleccionar candidato, cargo y funciones
    with allure.step("Seleccionar candidato, cargo y funciones para la solicitud"):
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

    # 8) Periodo, materia/grupo y compensación
    with allure.step("Configurar periodo, materia/grupo y compensación"):
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

    # 9) Guardar y validar éxito
    with allure.step("Guardar cambios en la solicitud y verificar mensaje de éxito"):
        detail.click_guardar()
        evidencia("click_guardar")

        detail.wait_redirect_to_detail()
        evidencia("detalle_post_guardar")

        detail.wait_success_message()
        evidencia("toast_exito_visible")


@allure.epic("Gestión de Contratos")
@allure.feature("Módulo de Contratos")
@allure.story("Director envía solicitud de contratación a RRHH")
@allure.severity(allure.severity_level.CRITICAL)
@allure.label("owner", "Ronald Aguilar")
@allure.link(
    "https://mi-matriz-casos/CONTRATO_ENVIAR_RRHH_01",
    name="CONTRATO_ENVIAR_RRHH_01",
)
@pytest.mark.functional
@pytest.mark.e2e
@pytest.mark.case("CONTRATO_ENVIAR_RRHH_01")
@pytest.mark.tester("Ronald")
def test_cp33_enviar_solicitud_a_rrhh(driver, base_url, evidencia, cod_cache):
    """
    Escenario:
    1. Recuperar código de solicitud en curso (cache).
    2. Director inicia sesión.
    3. Busca la solicitud por código y entra al detalle.
    4. Envía la solicitud a RRHH.
    5. Cierra sesión del Director.
    6. Inicia sesión RRHH y navega a Validación de Solicitudes.
    7. Abre el detalle de la solicitud enviada.
    """

    allure.dynamic.title("Director - Enviar solicitud de contrato a RRHH y validarla en bandeja RRHH")

    # 1) Código cacheado
    with allure.step("Recuperar código de solicitud desde cache"):
        codigo = cod_cache["get"](None)
        if not codigo:
            pytest.skip("No hay código cacheado de solicitud previa.")

    # 2) Login Director
    with allure.step("Iniciar sesión como Director"):
        login = LoginPage(driver, base_url)
        login.open_login()
        login.login_as("director@ues.edu.sv", "Password.1")
        assert login.is_logged_in(), "No se pudo iniciar sesión como Director."
        evidencia("login_director_ok")

     # 3) Ir a Solicitudes y buscar por código
    with allure.step("Navegar al listado de contratos y buscar la solicitud por código"):
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
    with allure.step("Abrir detalle de la solicitud antes de enviar a RRHH"):
        contratos.click_view_for_code(codigo)
        WebDriverWait(driver, 12).until(EC.url_contains("/contratos/solicitud/"))
        evidencia(f"detalle_solicitud__{codigo}")

    # 5) Enviar a RRHH (reutilizando helper existente)
    with allure.step("Enviar la solicitud a RRHH desde el detalle"):
        enviar_a_rrhh(driver, evidencia)

    # 6) Logout Director e inicio de sesión RRHH
    with allure.step("Cerrar sesión como Director e iniciar sesión como RRHH"):
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

    # 7) Ir a Validación de Solicitudes y abrir la solicitud
    with allure.step("Navegar a 'Validación de Solicitudes' y abrir la solicitud enviada"):
        rrhh_home = RRHHHomePage(driver, base_url)
        rrhh_home.wait_loaded()
        rrhh_home.go_to_validacion(evidencia)

        # 8) (Opcional) confirmar carga de la página
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

@allure.epic("Gestión de Contratos")
@allure.feature("Flujo de Solicitudes")
@allure.story("RRHH valida solicitud sin observaciones")
@allure.severity(allure.severity_level.CRITICAL)
@allure.label("owner", "Ronald Aguilar")
@allure.link(
    "https://mi-matriz-casos/RRHH_VALIDAR_SOLICITUD_01",
    name="RRHH_VALIDAR_SOLICITUD_01",
)
@pytest.mark.functional
@pytest.mark.e2e
@pytest.mark.case("RRHH_VALIDAR_SOLICITUD_01")
@pytest.mark.tester("Ronald")
def test_cp34_validar_solicitud_rrhh(driver, base_url, evidencia, cod_cache):
    """
    Escenario:
    1. Recuperar el código de la solicitud desde cache.
    2. RRHH inicia sesión.
    3. Navega a 'Validación de solicitudes'.
    4. Abre el detalle de la solicitud por código.
    5. Selecciona 'Validar sin observaciones'.
    6. Guarda y confirma.
    7. Verifica mensaje/estado de éxito.
    """

    allure.dynamic.title("RRHH - Validar solicitud de contrato sin observaciones")

    with allure.step("Recuperar código de solicitud desde cache"):
        codigo = cod_cache["get"](None)
        if not codigo:
            pytest.skip("No hay código cacheado (gc/ultimo_codigo). Ejecutá antes el flujo que guarda el código.")

    # 1) Login RRHH
    with allure.step("Iniciar sesión como RRHH"):
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

     # 2) Ir a Validación de solicitudes
    with allure.step("Navegar a 'Validación de solicitudes'"):
        rrhh_home = RRHHHomePage(driver, base_url)
        rrhh_home.wait_loaded()
        rrhh_home.go_to_validacion(evidencia)
        evidencia("validacion_solicitudes_nav")

    # 3) Abrir detalle por código
    with allure.step(f"Abrir el detalle de la solicitud con código: {codigo}"):
        listado = ValidacionSolicitudesPage(driver)
        listado.wait_loaded()
        evidencia("validacion_solicitudes_visible")
        listado.click_ver_solicitud(codigo, evidencia)
        evidencia(f"rrhh_detalle_abierto__{codigo}")

    # 4) Seleccionar 'Validar sin observaciones'
    with allure.step("Seleccionar la opción 'Validar sin observaciones' en el detalle"):
        detalle = SolicitudDetallePage(driver)
        detalle.wait_loaded()
        detalle.seleccionar_validar_sin_observaciones(evidencia=evidencia)
        evidencia("rrhh_detalle_radio_validar_sin_obs")

    # 5) Guardar + Confirmar
    with allure.step("Guardar la validación y confirmar la acción"):
        detalle.guardar(evidencia=evidencia)

    # 6) Verificar éxito (toast o redirección)
    with allure.step("Verificar mensaje o estado de éxito tras la validación"):
        detalle.esperar_exito(evidencia=evidencia)
        evidencia("rrhh_validacion_sin_obs_exito")
        time.sleep(1)

@allure.epic("Gestión de Contratos")
@allure.feature("Flujo de Solicitudes")
@allure.story("Director envía solicitud validada a Secretaría")
@allure.severity(allure.severity_level.CRITICAL)
@allure.label("owner", "Ronald Aguilar")
@allure.link(
    "https://mi-matriz-casos/CONTRATO_ENVIAR_SECRETARIA_01",
    name="CONTRATO_ENVIAR_SECRETARIA_01",
)
@pytest.mark.functional
@pytest.mark.e2e
@pytest.mark.case("CONTRATO_ENVIAR_SECRETARIA_01")
@pytest.mark.tester("Ronald")
def test_cp35_enviar_solicitud_a_secretaria(driver, base_url, evidencia, cod_cache):
    """
    Escenario:
    1. Recuperar código de la solicitud desde cache.
    2. Director inicia sesión.
    3. Navega al listado de contratos y busca la solicitud por código.
    4. Abre el detalle de la solicitud.
    5. Envía la solicitud a Secretaría desde la pantalla de revisión.
    """

    allure.dynamic.title("Director - Enviar solicitud de contrato a Secretaría Académica")

    # 1) Recuperar código
    with allure.step("Recuperar código de solicitud desde cache"):
        codigo = cod_cache["get"](None)
        if not codigo:
            pytest.skip("No hay código cacheado desde la prueba anterior.")

    # 2) Login Director
    with allure.step("Iniciar sesión como Director"):
        login = LoginPage(driver, base_url)
        login.open_login()
        login.login_as("director@ues.edu.sv", "Password.1")
        assert login.is_logged_in(), "No se pudo iniciar sesión como Director."
        evidencia("login_director_ok_sec")

    # 3) Ir a Solicitudes y buscar por código
    with allure.step("Navegar al listado de contratos y buscar la solicitud por código"):
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
    with allure.step("Abrir detalle de la solicitud para enviarla a Secretaría"):
        contratos.click_view_for_code(codigo)
        time.sleep(2)  # breve espera por animaciones
        WebDriverWait(driver, 12).until(EC.url_contains("/contratos/solicitud/"))
        evidencia(f"detalle_solicitud__{codigo}_sec")

    # 5) Pantalla de revisión y envío a Secretaría
    with allure.step("Usar la pantalla de revisión para enviar la solicitud a Secretaría"):
        pagina = SolicitudRevisionPage(driver)
        time.sleep(2)  # espera breve por animaciones   
        pagina.wait_loaded(evidencia=evidencia)
        pagina.enviar_a_secretaria(evidencia=evidencia)  # listo

@allure.epic("Gestión de Contratos")
@allure.feature("Bandeja de Recepción - Asistente")
@allure.story("Asistente Administrativo navega a la bandeja de recepción de solicitudes")
@allure.severity(allure.severity_level.NORMAL)
@allure.label("owner", "Ronald Aguilar")
@allure.link(
    "https://mi-matriz-casos/CP_ASISTENTE_Recepcion_Navegar",
    name="CP_ASISTENTE_Recepcion_Navegar",
)
@pytest.mark.functional
@pytest.mark.e2e
@pytest.mark.case("CP_ASISTENTE_Recepcion_Navegar")
@pytest.mark.tester("Ronald")
def test_cp40_asistente_navega_a_recepcion(driver, base_url, evidencia, cod_cache):
    """
    Escenario:
    1. Asistente inicia sesión.
    2. Navega a la bandeja de 'Recepción de solicitudes'.
    3. Verifica que la vista cargue.
    4. Da clic en 'Ver' (por código cacheado si existe, o primera fila).
       Solo se toma evidencia post-click, sin assert duro.
    """

    allure.dynamic.title("Asistente - Navegar a Recepción de solicitudes y abrir un detalle suave")

    # 1) Login Asistente
    with allure.step("Iniciar sesión como Asistente Administrativo"):
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
    with allure.step("Navegar a la pantalla de Recepción de solicitudes"):
        home = AsistenteHomePage(driver, base_url)
        home.wait_loaded()
        home.go_to_recepcion_solicitudes(evidencia=evidencia)

        recep = RecepcionSolicitudesPage(driver)
        recep.wait_loaded(evidencia=evidencia)

        time.sleep(1)  # Pequeña espera para evitar capturas muy tempranas
    
    # 3) Click en 'Ver' (suave: sin assert duro)
    with allure.step("Hacer clic en 'Ver' para alguna solicitud (por código o primera fila disponible)"):
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


@allure.epic("Gestión de Contratos")
@allure.feature("Flujo Asistente - Recepción y acuerdos")
@allure.story("Asistente sube acuerdo de Junta a una solicitud recibida")
@allure.severity(allure.severity_level.CRITICAL)
@allure.label("owner", "Ronald Aguilar")
@allure.link(
    "https://mi-matriz-casos/CP_ASISTENTE_Subir_Acuerdo_Junta",
    name="CP_ASISTENTE_Subir_Acuerdo_Junta",
)
@pytest.mark.functional
@pytest.mark.e2e
@pytest.mark.case("CP_ASISTENTE_Subir_Acuerdo_Junta")
@pytest.mark.tester("Ronald")
def test_cp41_asistente_subir_acuerdo(driver, base_url, evidencia, cod_cache):
    """
    Escenario:
    1. Recuperar código de la solicitud desde cache.
    2. Asistente inicia sesión.
    3. Navega a 'Recepción de solicitudes'.
    4. Abre el formulario 'Subir acuerdo' para la solicitud.
    5. Completa fecha, código JP y adjunta PDF del acuerdo.
    6. Marca como aprobado y guarda.
    7. Verifica que regresa a la pantalla de Recepción.
    """

    allure.dynamic.title("Asistente - Subir acuerdo de Junta a una solicitud")

    with allure.step("Recuperar código de la solicitud desde cache"):
        codigo = cod_cache["get"](None)
        if not codigo:
            pytest.skip("No hay código cacheado desde la prueba anterior.")

    # 1) Login Asistente
    with allure.step("Iniciar sesión como Asistente Administrativo"):
        login = LoginPage(driver, base_url)
        login.open_login()
        login.login_as("asistente@ues.edu.sv", "Password.1")

        WebDriverWait(driver, 15).until(EC.visibility_of_element_located((
            By.XPATH,
            "//header//span[contains(.,'Sesión iniciada como') and "
            "(contains(.,'Asistente') or contains(.,'Asistente Administrativo'))]"
        )))
        evidencia("asistente_login_ok_subir")

    # 2) Ir a Recepción de solicitudes
    with allure.step("Navegar a la bandeja de Recepción de solicitudes"):
        home = AsistenteHomePage(driver, base_url)
        home.wait_loaded()
        home.go_to_recepcion_solicitudes(evidencia=evidencia)

        recep = RecepcionSolicitudesPage(driver)
        recep.wait_loaded(evidencia=evidencia)
        recep.wait_loaded_table()
        evidencia("asistente_recepcion_visible_subir")


     # 3) Abrir formulario 'Subir acuerdo' para la solicitud
    with allure.step("Abrir formulario 'Subir acuerdo' para el código cacheado"):
        subir = SubirAcuerdoPage(driver, base_url)
        subir.open_from_recepcion_by_code(codigo)
        evidencia("asistente_form_subir_visible")

    # 4) Completar con fecha dd/mm/yyyy y PDF
    with allure.step("Completar datos del acuerdo (fecha, código y PDF) y marcar aprobado"):
        fecha_hoy = datetime.now().strftime("%d/%m/%Y")
        pdf_path = _ensure_min_pdf(os.path.join("fixtures", "acuerdo_demo.pdf"))

        codigo = generar_codigo_jp()
        subir.set_codigo(codigo)
        subir.set_fecha_ddmmyyyy(fecha_hoy)
        subir.upload_pdf(pdf_path)
        subir.set_aprobado(True)
        evidencia("asistente_form_subir_completado")

    # 5) Guardar (el PageObject espera toast + redirección)
    with allure.step("Guardar acuerdo y esperar redirección a Recepción"):
        time.sleep(0.5)  # leve respiro visual en evidencias
        subir.guardar()
        evidencia("asistente_subir_guardado_ok")

        # 6) Afirmación final: estamos de vuelta en recepción
        WebDriverWait(driver, 8).until(EC.url_contains("/recepcion-solicitudes"))

@allure.epic("Gestión de Contratos")
@allure.feature("Módulo RRHH - Generar contratos")
@allure.story("RRHH genera contrato de candidato y completa flujo hasta solicitudes finalizadas")
@allure.severity(allure.severity_level.CRITICAL)
@allure.label("owner", "Ronald Aguilar")
@allure.link(
    "https://mi-matriz-casos/CP_RRHH_Generar_Contratos",
    name="CP_RRHH_Generar_Contratos",
)
@pytest.mark.functional
@pytest.mark.e2e
@pytest.mark.case("CP_RRHH_Generar_Contratos")
@pytest.mark.tester("Ronald")
def test_cp42_generar_contratos_rrhh(driver, base_url, evidencia, cod_cache):
    """
    Escenario:
    1. Recuperar código de solicitud desde cache.
    2. RRHH inicia sesión y entra a 'Generar contratos'.
    3. Abre el detalle de la solicitud por código.
    4. Abre el contrato del candidato y genera nueva versión.
    5. Completa el flujo de estados del contrato (hasta fecha de firma).
    6. Regresa a 'Generar contratos', marca la solicitud como finalizada.
    7. Navega a 'Solicitudes finalizadas' y verifica que el código esté listado.
    """

    allure.dynamic.title("RRHH - Generar contrato, completar flujo y marcar solicitud como finalizada")

    with allure.step("Recuperar código de solicitud desde cache"):
        codigo = cod_cache["get"](None)
        if not codigo:
            pytest.skip("No hay código cacheado desde la prueba anterior.")

    # 1) Login RRHH
    with allure.step("Iniciar sesión como RRHH"):
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

    # 2) Ir al módulo Generar contratos
    with allure.step("Navegar al módulo 'Generar contratos'"):
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
    
    # 3) Abrir detalle de la solicitud por código
    with allure.step(f"Abrir detalle de generación de contratos para la solicitud {codigo}"):
        gen.click_ver(codigo, evidencia=evidencia)
        gc_detalle = GenerarContratosDetallePage(driver)
        gc_detalle.wait_loaded(evidencia=evidencia)

    # 4) Abrir contrato del candidato
    with allure.step("Abrir contrato del candidato desde el detalle de generación de contratos"):
        gc_detalle.click_contrato_by_name("Veronica Camila Campos Vega", evidencia=evidencia)

        # Ahora sí, estamos en "Contrato - ..."
        contrato = ContratoCandidatoPage(driver)
        contrato.wait_loaded(evidencia=evidencia)


    # 5) Generar versión y completar flujo de estados
    with allure.step("Generar nueva versión de contrato y completar flujo de estados"):
        contrato.generar_nueva_version(evidencia=evidencia)

        # 2) Avanzar estados (toma evidencias por estado)
        contrato.completar_flujo_estados("09/11/2025", evidencia=evidencia)

        contrato.volver_a_generar_contratos(evidencia=evidencia)

        gc_detalle = GenerarContratosDetallePage(driver)
        gc_detalle.wait_loaded(evidencia=evidencia)

    # 6) Marcar como finalizada y navegar a solicitudes finalizadas
    with allure.step("Marcar la solicitud como finalizada y navegar a 'Solicitudes finalizadas'"):
        # Marcar como finalizada
        gc_detalle.marcar_como_finalizada(evidencia=evidencia)

        # Ir a Solicitudes finalizadas
        gc_detalle.ir_a_solicitudes_finalizadas(evidencia=evidencia)

        # Verificar que aparece el código
        sol_fin = SolicitudesFinalizadasPage(driver)
        sol_fin.assert_code_present(codigo, evidencia=evidencia)
                        
                   