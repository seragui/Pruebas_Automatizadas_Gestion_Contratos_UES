import time
import pytest
from faker import Faker
from urllib.parse import urlparse
from selenium.webdriver.support.ui import WebDriverWait
from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.users_page import UsersPage
from pages.create_user_page import CreateUserPage

@pytest.mark.smoke
def test_crear_usuario_candidato_ok(driver, base_url, qa_creds):
    """Flujo feliz: crea Candidato y valida modal de éxito + redirección a /usuarios."""
    fake = Faker()

    # Login
    login = LoginPage(driver, base_url)
    login.open_login()
    login.login_as(qa_creds["email"], qa_creds["password"])
    assert login.is_logged_in()

    # Ir a Usuarios > Crear
    home = HomePage(driver, base_url)
    home.go_to_users()
    users = UsersPage(driver, base_url)
    users.wait_loaded()
    users.click_create()

    # Llenar y enviar
    create = CreateUserPage(driver, base_url)
    create.wait_loaded()

    nombre = f"Candidato QA {fake.first_name()}"
    correo = f"cand_qa_{int(time.time())}_{fake.random_number(digits=4)}@example.com"

    create.set_name(nombre)
    create.set_email(correo)
    create.select_role("Candidato")
    create.wait_school_enabled()
    create.select_school("Ingeniería de Sistemas Informáticos")
    create.submit()

    # Validar éxito: acepta modal, toast o redirect a /usuarios
    resultado = create.wait_success_feedback()
    assert resultado in ("redirect-success", "toast-success") or "Usuario creado con éxito" in resultado
    assert "/usuarios" in driver.current_url


@pytest.mark.smoke
def test_crear_usuario_asistente_rrhh_debe_fallar(driver, base_url, qa_creds):
    """Debe fallar: Asistente Recursos Humanos muestra toast de error y NO redirige (se queda en /usuarios/crear)."""
    fake = Faker()

    # Login
    login = LoginPage(driver, base_url)
    login.open_login()
    login.login_as(qa_creds["email"], qa_creds["password"])
    assert login.is_logged_in()

    # Ir a Usuarios > Crear
    home = HomePage(driver, base_url)
    home.go_to_users()
    users = UsersPage(driver, base_url)
    users.wait_loaded()
    users.click_create()

    # Llenar y enviar
    create = CreateUserPage(driver, base_url)
    create.wait_loaded()

    nombre = f"RRHH QA {fake.first_name()}"
    correo = f"rrhh_qa_{int(time.time())}_{fake.random_number(digits=4)}@example.com"

    create.set_name(nombre)
    create.set_email(correo)
    create.select_role("Asistente Recursos Humanos")
    create.submit()

    # 1) Debe aparecer toast de error
    msg = create.wait_error_toast()
    assert msg and "El rol que esta ingresando No Existe" in msg

    # 2) NO debe redirigir a /usuarios; debe permanecer en /usuarios/crear
    #    (Esperamos brevemente por si hay animación/latencia)
    WebDriverWait(driver, 5).until(
        lambda d: urlparse(d.current_url).path.rstrip("/") == "/usuarios/crear"
    )
    assert urlparse(driver.current_url).path.rstrip("/") == "/usuarios/crear"

@pytest.mark.smoke
@pytest.mark.xfail(reason="BUG: Backend retorna 400 al crear 'Asistente Financiero'. Debe ser exitoso.", strict=True)
def test_crear_usuario_asistente_financiero_deberia_ser_exitoso(driver, base_url, qa_creds):
    """
    Este test expresa el COMPORTAMIENTO ESPERADO:
    - Crear usuario con rol 'Asistente Financiero' debe mostrar modal de Éxito y redirigir a /usuarios.
    Está marcado xfail porque HOY falla (bug conocido). Cuando lo arreglen, se verá XPASS y
    con strict=True hará fallar la suite para que quitemos el xfail.
    """
    fake = Faker()

    # Login
    login = LoginPage(driver, base_url)
    login.open_login()
    login.login_as(qa_creds["email"], qa_creds["password"])
    assert login.is_logged_in()

    # Ir a Usuarios > Crear
    home = HomePage(driver, base_url)
    home.go_to_users()
    users = UsersPage(driver, base_url)
    users.wait_loaded()
    users.click_create()

    # Llenar formulario
    create = CreateUserPage(driver, base_url)
    create.wait_loaded()

    nombre = f"Asistente Financiero QA {fake.first_name()}"
    correo = f"afin_qa_{int(time.time())}_{fake.random_number(digits=4)}@example.com"

    create.set_name(nombre)
    create.set_email(correo)
    create.select_role("Asistente Financiero")  # Este rol no habilita Escuela
    create.submit()

    # Validación de ÉXITO (lo esperado cuando el bug se resuelva)
    contenido = create.wait_success_modal_and_accept(timeout=12)
    assert "Usuario creado con éxito" in contenido
    assert driver.current_url.rstrip("/").endswith("/usuarios")