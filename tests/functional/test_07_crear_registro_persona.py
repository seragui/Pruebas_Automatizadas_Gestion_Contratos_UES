import pytest
import random
import allure
from faker import Faker
from datetime import date
from urllib.parse import urljoin

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from pages.login_page import LoginPage
from pages.candidate_home_page import CandidateHomePage
from pages.candidate_personal_info import (CandidatePersonalInfoStep1Page, 
                                           CandidatePersonalInfoStep2Page,
                                           CandidatePersonalInfoStep3Page,
                                           CandidatePersonalInfoStep4Page,
                                           CandidatePersonalInfoReviewPage)
from utils.shared_state import set_candidate_full_name

fake = Faker("es_MX")

# ==========================
# DUI helpers
# ==========================

def dui_dv(base8: str) -> int:
    if not (base8.isdigit() and len(base8) == 8):
        raise ValueError("Base debe tener 8 dígitos")
    pesos = [9, 8, 7, 6, 5, 4, 3, 2]
    s = sum(int(d) * p for d, p in zip(base8, pesos))
    return (10 - (s % 10)) % 10

def dui_valido(base8: str) -> str:
    return f"{base8}-{dui_dv(base8)}"

def generar_duis(n=1):
    vistos = set()
    res = []
    while len(res) < n:
        base = f"{random.randint(0, 99999999):08d}"
        if base in vistos:
            continue
        vistos.add(base)
        res.append(dui_valido(base))
    return res

def generar_dui_unico() -> str:
    """Retorna un único DUI válido."""
    return generar_duis(1)[0]

# ==========================
# Otros helpers
# ==========================

def random_numeric(length: int) -> str:
    return "".join(random.choice("0123456789") for _ in range(length))

def random_email() -> str:
    return fake.email()

def random_phone_sv_formateado() -> str:
    """
    Teléfono SV 8 dígitos, con guion, ej: 7789-1056
    Debe iniciar con 6 o 7.
    """
    first = random.choice(["6", "7"])
    bloque1 = first + random_numeric(3)   # 4 dígitos
    bloque2 = random_numeric(4)           # 4 dígitos
    return f"{bloque1}-{bloque2}"



@allure.epic("Portal de Candidatos")
@allure.feature("Gestión de datos personales")
@allure.story("Candidato registra su información personal completa (wizard)")
@allure.severity(allure.severity_level.CRITICAL)
@allure.label("owner", "Jose Lucero")
@allure.link(
    "https://mi-matriz-casos/CANDIDATO_DATOS_PERSONALES_01",
    name="CANDIDATO_DATOS_PERSONALES_01",
)
@pytest.mark.functional
@pytest.mark.e2e
@pytest.mark.regression
@pytest.mark.case("CANDIDATO_DATOS_PERSONALES_01")
@pytest.mark.tester("Jose")
def test_cp12_candidato_ingresa_datos_personales(driver, base_url, candidate_creds, evidencia, candidate_name_cache):
    """
    Escenario:
    1. El candidato inicia sesión en el sistema.
    2. Desde el home de candidato, da clic en el botón 'Ingresar datos personales'.
    3. Se verifica que se navegue a la pantalla de información personal.
    4. Se capturan evidencias en los puntos clave.
    """
    allure.dynamic.title("Candidato ingresa y registra sus datos personales (wizard completo)")

    # 1) Login como candidato
    with allure.step("Login como candidato"):
        login_page = LoginPage(driver, base_url)
        login_page.open_login()
        evidencia("candidato_login__form_visible")

        login_page.login_as(candidate_creds["email"], candidate_creds["password"])
        assert login_page.is_logged_in(), "El candidato no quedó autenticado tras el login válido."
        evidencia("candidato_login__ok")

    # 2) Home del candidato: validar que cargó y dar clic en 'Ingresar datos personales'
    with allure.step("Ir al home del candidato y entrar a 'Ingresar datos personales'"):
        candidate_home = CandidateHomePage(driver, base_url)
        candidate_home.wait_home_loaded()
        evidencia("candidato_home__visible")

        candidate_home.click_ingresar_datos_personales()
        evidencia("candidato_home__click_ingresar_datos_personales")

    # 3) Verificar navegación hacia la pantalla de datos personales
    with allure.step("Paso 1 - Nacionalidad: seleccionar 'Salvadoreño' y avanzar"):
        assert candidate_home.is_on_personal_info_page(), (
            "No se redirigió a la pantalla de información personal del candidato "
            "después de hacer clic en 'Ingresar datos personales'."
        )
        evidencia("candidato_datos_personales__pantalla_informacion")

        # 3) Verificar que estamos en la pantalla de información personal
        assert candidate_home.is_on_personal_info_page(), (
            "No se redirigió a la pantalla de información personal del candidato "
            "después de hacer clic en 'Ingresar datos personales'."
        )

        # 4) Paso 1 del wizard: Nacionalidad
        personal_info_step1 = CandidatePersonalInfoStep1Page(driver)
        personal_info_step1.wait_loaded()
        evidencia("candidato_datos_personales__step1_nacionalidad_visible")

        # Seleccionar 'Salvadoreño'
        personal_info_step1.seleccionar_salvadoreno()
        evidencia("candidato_datos_personales__step1_nacionalidad_salvadoreno_seleccionado")

        # 5) Clic en 'Siguiente'
        personal_info_step1.click_siguiente()
        evidencia("candidato_datos_personales__step1_despues_de_siguiente")

    # ===============================
    # 4) Paso 2: Datos generales
    # ===============================
    with allure.step("Paso 2 - Datos generales: completar nombres, estado civil, género, etc."):
        step2_page = CandidatePersonalInfoStep2Page(driver)
        step2_page.wait_loaded()
        evidencia("candidato_datos_personales__step2_datos_generales_visible")

        # --- Definimos los datos con Faker / reglas que acordamos ---
        genero = random.choice(["Masculino", "Femenino"])
        estado_civil = random.choice(["Soltero", "Casado/a"])

        if genero == "Masculino":
            primer_nombre = fake.first_name_male()
            segundo_nombre = fake.first_name_male()
        else:
            primer_nombre = fake.first_name_female()
            segundo_nombre = fake.first_name_female()

        # Dos apellidos
        apellido1 = fake.last_name()
        apellido2 = fake.last_name()
        apellidos = f"{apellido1} {apellido2}"

        #Fecha de nacimiento: adulto (por ejemplo entre 25 y 45 años)
        birth_date = fake.date_of_birth(minimum_age=25, maximum_age=45)
        birth_date_str = birth_date.strftime("%d/%m/%Y")

        profesion = "Empleado"
        direccion = fake.address().replace("\n", " ")
        distrito = "San Salvador"

        # --- Llenamos el formulario ---
        # Nombres y apellidos
        step2_page.fill_names(primer_nombre, segundo_nombre, apellidos)
        evidencia("candidato_datos_personales__step2_nombres_apellidos")

        # Estado civil
        step2_page.select_civil_status(estado_civil)
        evidencia("candidato_datos_personales__step2_estado_civil")

        # Género
        step2_page.select_gender(genero)
        evidencia("candidato_datos_personales__step2_genero")

        # Conocido por -> lo dejamos vacío (opcional), no tocamos el campo

        # Fecha de nacimiento
        step2_page.fill_birth_date(birth_date_str)
        evidencia("candidato_datos_personales__step2_fecha_nacimiento")

        # Profesión / oficio (siempre Empleado)
        step2_page.set_profession_title(profesion)
        evidencia("candidato_datos_personales__step2_profesion")

        # ¿Posee otro título? -> No
        step2_page.set_other_title(has_other=False)
        evidencia("candidato_datos_personales__step2_otro_titulo")

        # Dirección de residencia
        step2_page.set_address(direccion)
        evidencia("candidato_datos_personales__step2_direccion")

        # Distrito -> siempre San Salvador
        step2_page.select_distrito(distrito)
        evidencia("candidato_datos_personales__step2_distrito")

        # ==============================
        # 5) Avanzar al siguiente paso
        # ==============================
        step2_page.click_siguiente()
        evidencia("candidato_datos_personales__step2_despues_de_siguiente")

    with allure.step("Paso 3 - Documentos e información adicional: DUI, NUP, ISSS, banco, contacto"):
        # 5) Paso 3: Documentos e info adicional
        # ===============================
        step3_page = CandidatePersonalInfoStep3Page(driver)
        step3_page.wait_loaded()
        evidencia("candidato_datos_personales__step3_visible")

        dui = generar_dui_unico()
        dui_vencimiento = fake.date_between(
            start_date="+1y", end_date="+9y"
        ).strftime("%Y-%m-%d")  # formato YYYY-MM-DD

        nup = random_numeric(9)
        isss = random_numeric(9)
        correo_alt = random_email()
        cuenta_bancaria = random_numeric(9)
        telefono = random_phone_sv_formateado()

        # DUI
        step3_page.fill_dui(dui)
        evidencia("candidato_datos_personales__step3_dui")

        # Fecha vencimiento DUI (YYYY-MM-DD)
        step3_page.fill_dui_expiration_date(dui_vencimiento)
        evidencia("candidato_datos_personales__step3_dui_vencimiento")

        # AFP/NUP
        step3_page.fill_nup(nup)
        evidencia("candidato_datos_personales__step3_nup")

        # ISSS
        step3_page.fill_isss(isss)
        evidencia("candidato_datos_personales__step3_isss")

        # Correo alterno
        step3_page.fill_alternate_email(correo_alt)
        evidencia("candidato_datos_personales__step3_correo_alterno")

        # Nombre del banco (uno al azar)
        step3_page.select_random_bank()
        evidencia("candidato_datos_personales__step3_banco")

        # Tipo de cuenta: siempre "Cuenta de ahorro"
        step3_page.select_account_type_ahorro()
        evidencia("candidato_datos_personales__step3_tipo_cuenta")

        # Número de cuenta bancaria (9 dígitos)
        step3_page.fill_bank_account_number(cuenta_bancaria)
        evidencia("candidato_datos_personales__step3_numero_cuenta")

        # Teléfono principal (7xxx-xxxx o 6xxx-xxxx)
        step3_page.fill_telephone(telefono)
        evidencia("candidato_datos_personales__step3_telefono")

        # Teléfono adicional lo podemos dejar vacío o llenar si querés:
        # step3_page.fill_alt_telephone(random_phone_sv_formateado())
        # evidencia("candidato_datos_personales__step3_telefono_adicional")

        # Siguiente
        step3_page.click_siguiente()
        evidencia("candidato_datos_personales__step3_despues_de_siguiente")

    # ===============================
    # 6) Paso 4: Información laboral
    # ===============================
    with allure.step("Paso 4 - Información laboral: marcar que NO es empleado UES y pasar a revisión"):
        step4_page = CandidatePersonalInfoStep4Page(driver)
        step4_page.wait_loaded()

        # Modal de Información Laboral -> Aceptar
        evidencia("candidato_datos_personales__step4_modal_visible")
        step4_page.close_info_modal_if_present()
        evidencia("candidato_datos_personales__step4_modal_aceptado")

        # Es empleado de la universidad -> No
        step4_page.set_is_employee(False)
        evidencia("candidato_datos_personales__step4_is_employee_no")

        # Click en 'Revisar información' (paso 5: Revisión)
        step4_page.click_revisar_informacion()
        evidencia("candidato_datos_personales__step4_revisar_informacion")

    # ===============================
    # ===============================
    # 7) Paso 5: Revisión
    # ===============================
    with allure.step("Paso 5 - Revisar resumen y registrar información"):
        review_page = CandidatePersonalInfoReviewPage(driver)
        review_page.wait_loaded()
        evidencia("candidato_datos_personales__step5_revision_visible")

        # Nombre completo en minúsculas y lo guardamos en “cache”
        full_name_for_search = f"{primer_nombre} {segundo_nombre}".strip()
        set_candidate_full_name(full_name_for_search)
        candidate_name_cache["set"](full_name_for_search)
        print(f"[TEST CANDIDATO] Nombre guardado para RRHH: {full_name_for_search!r}")
        evidencia("candidato_datos_personales__step5_full_name")

        # Click en 'Registrar mi información'
        review_page.click_registrar_informacion()
        evidencia("candidato_datos_personales__step5_despues_registrar")

@allure.epic("Portal de Candidatos")
@allure.feature("Seguridad y RBAC")
@allure.story("Bloqueo de acceso a flujo de información personal para roles no autorizados")
@allure.severity(allure.severity_level.CRITICAL)
@allure.label("owner", "Jose Lucero")
@allure.link(
    "https://mi-matriz-casos/CANDIDATO_ACCESO_NO_AUTORIZADO",
    name="CANDIDATO_ACCESO_NO_AUTORIZADO",
)
@pytest.mark.functional
@pytest.mark.e2e
@pytest.mark.security
@pytest.mark.negative
@pytest.mark.regression
@pytest.mark.case("CANDIDATO_ACCESO_NO_AUTORIZADO")
@pytest.mark.tester("Jose")
@pytest.mark.xfail(
    reason=(
        "Defecto conocido de seguridad/RBAC: el Asistente Administrativo puede acceder "
        "al flujo de información personal del candidato mediante acceso directo a "
        "la ruta /información-personal o no es redirigido al home."
    ),
    strict=False,  # Cuando se corrija, XPASS pero sin romper la suite
)
def test_cp12_acceso_no_autorizado_crear_informacion(driver, base_url, candidate_creds, evidencia, candidate_name_cache):
    allure.dynamic.title(
        "RBAC candidato - Asistente Administrativo NO debe acceder a /información-personal (xfail por defecto conocido)"
    )

    # Login
    with allure.step("Iniciar sesión como Asistente Administrativo"):
        login = LoginPage(driver, base_url)
        login.open_login()
        login.login_as("asistente@ues.edu.sv", "Password.1")
        assert login.is_logged_in(), "No se pudo iniciar sesión."
        evidencia("acceso_no_autorizado__login_ok")

    # 2) Intentar acceder directo a la ruta protegida
    with allure.step("Intentar acceder directamente a la ruta protegida /información-personal"):
        restricted_url = urljoin(base_url.rstrip("/"), "/información-personal")
        driver.get(restricted_url)
        evidencia("acceso_no_autorizado__navegar_a_informacion_personal")

        # 3) Esperar redirección hacia base_url (home)
        wait = WebDriverWait(driver, 10)

        def redirected_to_home(d):
            current = d.current_url
            # Normalizamos slashes al final para comparar correctamente
            return current.rstrip("/") == base_url.rstrip("/")

    with allure.step("Verificar que el sistema redirige al home (o documentar el defecto)"):
        try:
            wait.until(redirected_to_home)
        except TimeoutException:
            # Aquí documentamos claramente el defecto
            evidencia("acceso_no_autorizado__flujo_prohibido_visible")
            current_url = driver.current_url
            assert False, (
                "Defecto de seguridad / RBAC: el Asistente Administrativo puede acceder "
                "al flujo de información personal del candidato o no es redirigido a la "
                f"página de inicio. URL actual: {current_url}"
            )

        # Si en algún momento el sistema se corrige y SÍ redirige,
        # este assert pasará y el caso se considerará exitoso.
        current_url = driver.current_url
        evidencia("acceso_no_autorizado__redireccion_home")

        assert current_url.rstrip("/") == base_url.rstrip("/"), (
            "Se esperaba redirección a la página de inicio (base_url) al intentar acceder "
            f"a /información-personal. URL final: {current_url}"
        )