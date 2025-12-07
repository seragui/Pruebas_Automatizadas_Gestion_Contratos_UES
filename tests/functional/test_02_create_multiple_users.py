# tests/functional/test_create_users.py
import time
import pytest
import allure
from faker import Faker
from urllib.parse import urlparse

from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.users_page import UsersPage
from pages.create_user_page import CreateUserPage


# (rol, needs_school, expected_ok)
ROLES = [
    pytest.param("Administrador",False, True, id="Administrador"),
    pytest.param("Candidato",True,  True, id="Candidato"),
    pytest.param("Director Escuela",True,  True, id="Director Escuela"),
    pytest.param("Asistente Administrativo",False, True, id="Asistente Administrativo"),
    pytest.param("Asistente Financiero",False, True, id="Asistente Financiero"),
    pytest.param("Recursos Humanos",False, True, id="Recursos Humanos"),

    # ← Este es el “malo”: lo marcamos como XFAIL pero lo dejamos expected_ok=True
    #    (porque en el futuro debería pasar) y strict=True para que un XPASS rompa la suite,
    #    avisándote que ya se arregló y debes quitar el xfail.
    pytest.param(
        "Asistente Recursos Humanos",
        False,
        True,  # debería pasar cuando el bug se arregle
        id="Asistente RRHH (bug conocido)",
        marks=pytest.mark.xfail(reason="BUG: backend devuelve 400 al crear Asistente RRHH", strict=True),
    ),

    pytest.param("Decano",False, True, id="Decano"),
]

@allure.epic("Gestión de Contratos")
@allure.feature("Administración de Usuarios")
@allure.story("Creación de usuarios por rol desde el panel de administración")
@allure.severity(allure.severity_level.CRITICAL)
@allure.label("owner", "Ronald Aguilar")
@allure.link(
    "https://mi-matriz-casos/USUARIOS_CREAR_POR_ROL_01",
    name="USUARIOS_CREAR_POR_ROL_01",
)
@pytest.mark.functional
@pytest.mark.e2e
@pytest.mark.regression
@pytest.mark.ddt
@pytest.mark.smoke
@pytest.mark.case("USUARIOS_CREAR_POR_ROL_01")
@pytest.mark.tester("Ronald")  
@pytest.mark.parametrize("role,needs_school,expected_ok", ROLES)
def test_cp03_crear_usuario_por_rol_con_resultado(driver, base_url, qa_creds, role, needs_school, expected_ok, evidencia):
    fake = Faker()

    # ===== (Opcional) Habilitar captura de red vía CDP para ver el status HTTP =====
    # Esto no rompe si no está disponible; simplemente no valida status si falla la suscripción.
    captured_status = {"code": None, "url": None}
    try:
        devtools = driver.devtools
        devtools.create_session()
        from selenium.webdriver.common.devtools.v129 import network as devtools_network
        devtools.send(devtools_network.enable())

        def _on_response(resp):
            try:
                # Filtra endpoints que contengan "users" y probablemente sea POST del create.
                # Puedes ajustar el filtro si tu endpoint es, por ejemplo, "/api/users"
                url = resp.response.url
                if "user" in url.lower():
                    captured_status["code"] = resp.response.status
                    captured_status["url"] = url
            except Exception:
                pass

        devtools.add_listener(devtools_network.ResponseReceived, _on_response)
    except Exception:
        # Si no se puede, seguimos con aserciones de UI.
        pass

    # pequeño sufijo para diferenciar evidencias por rol en el reporte
    role_slug = role.lower().replace(" ", "_")

    with allure.step("Autenticarse como Administrador QA"):
        # ===== 1) Login =====
        login = LoginPage(driver, base_url)
        login.open_login()
        evidencia(f"crear_usuario__{role_slug}__login_form")
        login.login_as(qa_creds["email"], qa_creds["password"])
        assert login.is_logged_in()
        evidencia(f"crear_usuario__{role_slug}__login_ok")

    with allure.step(f"Ir al módulo Usuarios y abrir la pantalla de creación ({role})"):
        # ===== 2) Ir a Usuarios y abrir Crear =====
        home = HomePage(driver, base_url)
        home.go_to_users()

        users = UsersPage(driver, base_url)
        users.wait_loaded()
        evidencia(f"crear_usuario__{role_slug}__listado_usuarios")
        users.click_create()

        # ===== 3) Llenar formulario =====
        create = CreateUserPage(driver, base_url)
        create.wait_loaded()
        evidencia(f"crear_usuario__{role_slug}__form_crear_visible")

    with allure.step(f"Llenar formulario de creación para el rol {role}"):
        nombre = f"{role} QA {fake.first_name()}"
        correo = f"{role.lower().replace(' ', '_')}_{int(time.time())}_{fake.random_number(digits=4)}@example.com"

        create.set_name(nombre)
        create.set_email(correo)
        create.select_role(role)

        if needs_school:
            create.wait_school_enabled()
            create.select_school("Ingeniería de Sistemas Informáticos")

        evidencia(f"crear_usuario__{role_slug}__form_completo")

    with allure.step("Enviar formulario y validar resultado esperado"):
        # ===== 4) Enviar =====
        current_path = urlparse(driver.current_url).path
        create.submit()
        evidencia(f"crear_usuario__{role_slug}__despues_submit")

        # ===== 5) Validaciones diferenciadas =====
        if expected_ok:
            # Debe redirigir a /usuarios (ajusta si tu ruta exacta difiere)
            users.wait_loaded()  # espera la tabla de usuarios
            new_path = urlparse(driver.current_url).path
            evidencia(f"crear_usuario__{role_slug}__ok_redirigido")
            assert "/usuarios" in new_path, f"Se esperaba redirección a /usuarios, quedó en {new_path}"

            # Si capturamos HTTP status, esperamos 200/201
            if captured_status["code"] is not None:
                assert captured_status["code"] in (200, 201), f"Se esperaba 200/201, se obtuvo {captured_status}"
        else:
            # FALLA ESPERADA: no debería salir del form
            #  - sigue en la misma página (o vuelve a /usuarios/crear)
            #  - debería aparecer algún mensaje/validación/alert de error
            # Intentamos una heurística de error de AntD: mensajes o no redirección
            time.sleep(0.5)  # micro-pausing por animaciones
            new_path = urlparse(driver.current_url).path
            evidencia(f"crear_usuario__{role_slug}__fallo_esperado")
            assert new_path == current_path or "crear" in new_path.lower(), \
                f"Se esperaba NO redirigir (fallo), pero cambió a {new_path}"

            # Puedes agregar validación de toast si tu UI lo muestra:
            # users.assert_error_toast_visible()  # si implementas ese método

            # Si capturamos HTTP status, esperamos 400/422
            if captured_status["code"] is not None:
                assert captured_status["code"] in (400, 422), f"Se esperaba 400/422, se obtuvo {captured_status}"
