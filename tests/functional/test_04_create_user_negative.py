import time
import pytest
from faker import Faker
from urllib.parse import urlparse
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.users_page import UsersPage
from pages.create_user_page import CreateUserPage

DUP_EMAIL = "rocio_lara@ues.edu.sv"

def _login_y_abrir_crear(driver, base_url, qa_creds, evidencia, prefix: str):
    """Login y navegación hasta ruta /usuaruios/crear, devolvemos el PageObject del form."""
    login = LoginPage(driver, base_url)
    login.open_login()
    evidencia(f"{prefix}__login_form")
    login.login_as(qa_creds["email"], qa_creds["password"])
    assert login.is_logged_in()
    evidencia(f"{prefix}__login_ok")

    home = HomePage(driver, base_url)
    home.go_to_users()
    users = UsersPage(driver, base_url)
    users.wait_loaded()
    evidencia(f"{prefix}__usuarios_listado")
    users.click_create()    

    create = CreateUserPage(driver, base_url)
    create.wait_loaded()
    evidencia(f"{prefix}__form_crear_visible")
    return create

def _assert_se_queda_en_crear(driver, path_before=None):
    """Verifica que la URL actual es /usuarios/crear (no hubo redirección)."""
    path_after = urlparse(driver.current_url).path.lower()
    assert "/usuarios" in path_after and "/crear" in path_after, f"Debe quedarse en /usuarios/crear, quedó en {path_after}"

    if path_before:
        # opcional: comprobar que no cambió de ruta
        assert path_after == path_before.lower(), f"No debía cambiar de ruta (antes {path_before}, ahora {path_after})"

# ======================================================================
# CASO 1: Nombre vacío
# ======================================================================  
@pytest.mark.smoke
def test_crear_usuario_nombre_vacio(driver, base_url, qa_creds, evidencia):
    fake = Faker()
    prefix = "nombre_vacio"
    create = _login_y_abrir_crear(driver, base_url, qa_creds,evidencia, prefix)

    # No seteamos Nombre
    correo = f"neg_nombre_vacio_{int(time.time())}_{fake.random_number(digits=4)}@example.com"
    create.set_email(correo)
    create.select_role("Candidato")
    create.wait_school_enabled()
    create.select_school("Ingeniería de Sistemas Informáticos")

    # Evidencia antes de enviar
    evidencia(f"{prefix}__antes_de_submit")

    path_before = urlparse(driver.current_url).path
    create.submit()

    # Debe quedarse en /usuarios/crear
    _assert_se_queda_en_crear(driver, path_before)

    # Validación visual del campo
    assert create.form_item_has_error("createUser_name"), "Se esperaba error visual en el campo Nombre."

    # Evidencia después de enviar (se ve el mensaje/estilo de error)
    evidencia(f"{prefix}__despues_de_submit")

    # (Opcional) si querés una tercera captura sólo si detectó el error:
    if create.form_item_has_error("createUser_name"):
        evidencia(f"{prefix}__resaltado_error")

# ======================================================================
# CASO 2: Email vacío
# ======================================================================
@pytest.mark.smoke
def test_crear_usuario_email_vacio(driver, base_url, qa_creds, evidencia):
    fake = Faker()
    prefix = "email_vacio"
    create = _login_y_abrir_crear(driver, base_url, qa_creds,evidencia, prefix)

    evidencia("email_vacio__comienzo")

    # No seteamos Email
    nombre = f"Neg_EmailVacio {fake.first_name()}"
    create.set_name(nombre)
    create.select_role("Candidato")
    create.wait_school_enabled()
    create.select_school("Ingeniería de Sistemas Informáticos")

    # Evidencia antes de enviar
    evidencia(f"{prefix}__antes_de_submit")

    # Enviar
    from urllib.parse import urlparse
    path_before = urlparse(driver.current_url).path
    create.submit()

    # Debe quedarse en /usuarios/crear (no hay redirección)
    _assert_se_queda_en_crear(driver, path_before)

    # Validación visual del campo Email
    assert create.form_item_has_error("createUser_email"), "Se esperaba error visual en el campo Email."

    # Evidencia después del submit (se ve el mensaje/estilo de error)
    evidencia(f"{prefix}__despues_de_submit")

# ======================================================================
# CASO 3: Email inválido
# ======================================================================
@pytest.mark.smoke
def test_crear_usuario_email_invalido(driver, base_url, qa_creds, evidencia):
    """
    Camino negativo: el email tiene formato inválido, no debe permitir crear
    y debe marcar error visual en el campo Email.
    """
    fake = Faker()
    prefix = "email_invalido"

    create = _login_y_abrir_crear(driver, base_url, qa_creds, evidencia, prefix)

    nombre = f"Neg_EmailInvalido {fake.first_name()}"
    email_invalido = "correo-invalido"  # sin @ ni dominio; puedes probar "user@dominio" también

    create.set_name(nombre)
    create.set_email(email_invalido)
    create.select_role("Candidato")
    create.wait_school_enabled()
    create.select_school("Ingeniería de Sistemas Informáticos")

    # Evidencia antes de enviar
    evidencia(f"{prefix}__antes_de_submit")

    # Enviar
    path_before = urlparse(driver.current_url).path
    create.submit()

    # Debe quedarse en /usuarios/crear
    _assert_se_queda_en_crear(driver, path_before)

    # Debe marcar error en el campo Email
    assert create.form_item_has_error("createUser_email"), "Se esperaba error visual en el campo Email por formato inválido."

    # Evidencia después (mensaje/borde de error visible)
    evidencia(f"{prefix}__despues_de_submit")

# ======================================================================
# CASO 4: Sin rol
# ======================================================================
@pytest.mark.smoke
def test_crear_usuario_sin_rol(driver, base_url, qa_creds, evidencia):
    """
    Camino negativo: no seleccionar Rol.
    Debe bloquear el envío, quedarse en /usuarios/crear
    y marcar error visual en el campo Rol.
    """

    fake = Faker()
    prefix = "sin_rol"

    create = _login_y_abrir_crear(driver, base_url, qa_creds, evidencia, prefix)
    time.sleep(1.0)
    

    # Datos válidos en nombre y email
    nombre = f"Neg_SinRol {fake.first_name()}"
    correo = f"neg_sinrol_{int(time.time())}_{fake.random_number(digits=4)}@example.com"

    create.set_name(nombre)
    create.set_email(correo)
    # IMPORTANTE: NO seleccionar rol

    # Si tu flujo requiere escuela solo cuando hay rol Candidato/Director, como no elegimos rol, tampoco tocamos escuela.

    evidencia(f"{prefix}__antes_de_submit")

    path_before = urlparse(driver.current_url).path
    create.submit()

    # Debe quedarse en la misma ruta (no redirige a /usuarios)
    _assert_se_queda_en_crear(driver, path_before)

    # Validar error visual en el campo Rol
    assert create.form_item_has_error("createUser_role"), "Se esperaba error visual en el campo Rol (rol no seleccionado)."

    time.sleep(1.0)

    evidencia(f"{prefix}__despues_de_submit")

# ======================================================================
# CASO 5: Candidato sin escuela
# ======================================================================
@pytest.mark.smoke
def test_candidato_sin_escuela_muestra_error(driver, base_url, qa_creds, evidencia):
    fake = Faker()
    prefix = "candidato_sin_escuela"

    create = _login_y_abrir_crear(driver, base_url, qa_creds, evidencia, prefix)

    # Datos válidos, pero NO seleccionaremos escuela
    nombre = f"Candidato Neg {fake.first_name()}"
    correo = f"cand_neg_sin_esc_{int(time.time())}_{fake.random_number(digits=4)}@example.com"

    create.set_name(nombre)
    create.set_email(correo)
    create.select_role("Candidato")
    create.wait_school_enabled()   # se habilita, pero no la seleccionamos

    evidencia(f"{prefix}__antes_de_submit")

    path_before = urlparse(driver.current_url).path
    create.submit()

    # Localizador del texto de error bajo "Escuela"
    school_error = (
        By.XPATH,
        "//label[@for='createUser_school_id']"
        "/ancestor::div[contains(@class,'ant-form-item')]"
        "//div[contains(@class,'ant-form-item-explain-error')]"
    )

    # Espera robusta: hasta 6s a que salga el error o (fallback) a que el form marque error
    end = time.time() + 6
    error_visible = False
    while time.time() < end and not error_visible:
        try:
            WebDriverWait(driver, 0.8).until(EC.visibility_of_element_located(school_error))
            error_visible = True
            break
        except Exception:
            # Alternativa: la clase de error en el form-item
            if create.form_item_has_error("createUser_school_id"):
                error_visible = True
                break

    # Evidencia cuando ya hay señal de error
    evidencia(f"{prefix}__error_visible")

    # Aserciones finales
    _assert_se_queda_en_crear(driver, path_before)
    assert error_visible, "Se esperaba error visual en el campo Escuela y no apareció."

# ======================================================================
# CASO 6: Email duplicado
# ======================================================================
def test_crear_usuario_email_duplicado(driver, base_url, qa_creds, evidencia):
    """
    Camino negativo: el email ya existe en el sistema.
    Debe mostrarse un toast de error y NO debe redirigir a /usuarios.
    """
    fake = Faker()
    prefix = "email_duplicado"

    create = _login_y_abrir_crear(driver, base_url, qa_creds, evidencia, prefix)

    nombre = f"Neg_EmailDuplicado {fake.first_name()}"
    correo = DUP_EMAIL  # correo existente que nos vas a proporcionar

    create.set_name(nombre)
    create.set_email(correo)
    create.select_role("Candidato")
    create.wait_school_enabled()
    create.select_school("Ingeniería de Sistemas Informáticos")

    # evidencia antes de enviar
    evidencia(f"{prefix}__antes_de_submit")

    path_before = urlparse(driver.current_url).path
    create.submit()

    # esperamos el toast de error (y capturamos evidencia cuando aparezca)
    msg = create.wait_error_toast(timeout=8)  # usa tu helper del PageObject
    evidencia(f"{prefix}__toast_error")

    # NO debe redirigir
    _assert_se_queda_en_crear(driver, path_before)

    # El mensaje puede variar; validación laxa por si el texto cambia
    assert msg is not None and len(msg) > 0, "Se esperaba algún mensaje de error (toast) por email duplicado."
    norm = " ".join((msg or "").lower().split())  # normaliza espacios y saltos de línea
    assert any(pat in norm for pat in [
        "ya está en uso",   # texto real del toast
        "ya esta en uso",   # sin tilde por si acaso
        "duplic",           # fallback genérico
        "existe"            # fallback genérico
    ]), f"El toast no parece indicar duplicado. Mensaje obtenido: {msg}"

    # (opcional) si tu formulario también marca el campo como inválido
    # evidencia adicional si hay marca visual en el input email
    if create.form_item_has_error("createUser_email"):
        evidencia(f"{prefix}__input_email_en_error")
