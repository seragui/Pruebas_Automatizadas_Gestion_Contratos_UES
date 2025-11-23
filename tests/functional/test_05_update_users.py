# tests/functional/test_users_search.py
import pytest
import allure
from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.users_page import UsersPage
from pages.users_edit_page import UserEditPage
import time
from selenium.webdriver.common.by import By

@allure.epic("Gestión de Contratos")
@allure.feature("Administración de Usuarios")
@allure.story("Búsqueda de usuario y acceso a edición")
@allure.severity(allure.severity_level.NORMAL)
@allure.label("owner", "Ronald Aguilar")
@allure.link(
    "https://mi-matriz-casos/USUARIOS_BUSCAR_Y_ABRIR_EDICION_01",
    name="USUARIOS_BUSCAR_Y_ABRIR_EDICION_01",
)
@pytest.mark.functional
@pytest.mark.e2e
@pytest.mark.regression
@pytest.mark.smoke
@pytest.mark.case("USUARIOS_BUSCAR_Y_ABRIR_EDICION_01")
@pytest.mark.tester("Ronald")
def test_buscar_usuario_por_nombre_y_abrir_edicion(driver, base_url, qa_creds, evidencia):
    nombre = "Pearline Kihn"   # <-- cambia el nombre si lo necesitás
    allure.dynamic.title(f"Buscar usuario '{nombre}' y abrir pantalla de edición")
    
    with allure.step("Iniciar sesión con usuario válido"):
        # 1) Login
        login = LoginPage(driver, base_url)
        login.open_login()
        evidencia("users_search__login_form")

        login.login_as(qa_creds["email"], qa_creds["password"])
        assert login.is_logged_in(), "No se pudo iniciar sesión."
        evidencia("users_search__login_ok")

    # 2) Ir a Usuarios
    with allure.step("Navegar al módulo de Usuarios"):
        home = HomePage(driver, base_url)
        home.go_to_users()

        users = UsersPage(driver, base_url)
        users.wait_loaded()
        evidencia("users_search__usuarios_listado_inicial")

        users.reset_to_first_page()  # opcional

    time.sleep(3)
    # 3) Buscar por nombre y hacer CLIC en el botón de búsqueda
    with allure.step(f"Buscar usuario por nombre: {nombre}"):
        time.sleep(3)
        users.search_by_name(nombre)  # este método ya escribe y hace click en el botón

        # 4) Tomar evidencia del resultado tal cual se ve en la tabla (filtrada o no)
        evidencia("users_search__resultado_busqueda")

    # 5) Si el usuario existe, localizarlo (paginando si hace falta) y abrir 'Editar'
    #assert users.find_or_paginate_to_name(nombre, exact=True, max_pages=12), \
    #    f"No se encontró el usuario '{nombre}' tras buscar/paginar."

    with allure.step(f"Abrir pantalla de edición para '{nombre}'"):
        assert users.open_edit_by_name(nombre, exact=True), \
            f"No fue posible abrir 'Editar' para '{nombre}'."

        time.sleep(3)
        # 6) Evidencia de la pantalla de edición (opcional)
        evidencia("buscar_usuario__editar_abierto")

    with allure.step("Verificar que el formulario de edición cargó los datos del usuario"):
        edit = UserEditPage(driver)
        edit.wait_loaded(expected_name=nombre)  # espera que el nombre esté cargado en el formulario

        evidencia("editar_usuario_form_cargado")

@allure.epic("Gestión de Contratos")
@allure.feature("Administración de Usuarios")
@allure.story("Edición de usuario y actualización de email")
@allure.severity(allure.severity_level.NORMAL)
@allure.label("owner", "Ronald Aguilar")
@allure.link(
    "https://mi-matriz-casos/USUARIOS_EDITAR_ACTUALIZAR_EMAIL_01",
    name="USUARIOS_EDITAR_ACTUALIZAR_EMAIL_01",
)
@pytest.mark.functional
@pytest.mark.e2e
@pytest.mark.regression
@pytest.mark.smoke
@pytest.mark.case("USUARIOS_EDITAR_ACTUALIZAR_EMAIL_01")
@pytest.mark.tester("Ronald")
def test_buscar_usuario_editar_y_actualizar_email(driver, base_url, qa_creds, evidencia):
    nombre = "Pearline Kihn"   # <-- cambia el nombre si lo necesitás
    allure.dynamic.title(f"Buscar usuario '{nombre}' y actualizar su email")
    
    # 1) Login
    with allure.step("Iniciar sesión con usuario válido"):
        login = LoginPage(driver, base_url)
        login.open_login()
        evidencia("users_update_email__login_form")
        login.login_as(qa_creds["email"], qa_creds["password"])
        assert login.is_logged_in(), "No se pudo iniciar sesión."
        evidencia("users_update_email__login_ok")
    
    with allure.step("Navegar al módulo de Usuarios"):
        # 2) Ir a Usuarios
        home = HomePage(driver, base_url)
        home.go_to_users()

        users = UsersPage(driver, base_url)
        users.wait_loaded()
        users.reset_to_first_page()  # opcional
        time.sleep(3)
    
    # 3) Buscar por nombre y hacer CLIC en el botón de búsqueda
    with allure.step(f"Buscar usuario por nombre: {nombre}"):
        time.sleep(3)
        users.search_by_name(nombre)  # este método ya escribe y hace click en el botón

        # 4) Tomar evidencia del resultado tal cual se ve en la tabla (filtrada o no)
        evidencia("buscar_usuario__resultado")

    # 5) Si el usuario existe, localizarlo (paginando si hace falta) y abrir 'Editar'
    #assert users.find_or_paginate_to_name(nombre, exact=True, max_pages=12), \
    #    f"No se encontró el usuario '{nombre}' tras buscar/paginar."
    with allure.step(f"Abrir pantalla de edición para '{nombre}'"):
        assert users.open_edit_by_name(nombre, exact=True), \
            f"No fue posible abrir 'Editar' para '{nombre}'."

        time.sleep(3)
        # 6) Evidencia de la pantalla de edición (opcional)
        evidencia("buscar_usuario__editar_abierto")


    # 4) Editar correo y confirmar
    with allure.step("Modificar email del usuario y confirmar actualización"):
        edit = UserEditPage(driver)
        edit.wait_loaded()
        evidencia("usuario_editar_form_abierto")

        nuevo_email = f"auto+{int(time.time())}@example.com"
        edit.set_email(nuevo_email)
        evidencia("usuario_editar_email_modificado")

        edit.click_update_and_confirm()
        evidencia("usuario_editar_popconfirm_si")  # (hará la captura justo después del click)

        time.sleep(2)
        # 5) Verificar toast de éxito
        edit.wait_success()
        evidencia("usuario_actualizado_con_exito")

    # Validación rápida: el input muestra el nuevo correo
    # (evita flakes si el botón queda deshabilitado después del guardado)
    with allure.step("Verificar que el formulario muestra el nuevo email guardado"):
        email_val = driver.find_element(By.ID, "editUser_email").get_attribute("value")
        assert email_val == nuevo_email, f"El email visible no coincide. Esperado: {nuevo_email} / Actual: {email_val}"

@allure.epic("Gestión de Contratos")
@allure.feature("Administración de Usuarios")
@allure.story("Validaciones de edición de usuario")
@allure.severity(allure.severity_level.NORMAL)
@allure.label("owner", "Ronald Aguilar")
@allure.link(
    "https://mi-matriz-casos/USUARIOS_EDITAR_VALIDACION_NOMBRE_VACIO",
    name="USUARIOS_EDITAR_VALIDACION_NOMBRE_VACIO",
)
@pytest.mark.functional
@pytest.mark.e2e
@pytest.mark.negative
@pytest.mark.regression
@pytest.mark.case("USUARIOS_EDITAR_VALIDACION_NOMBRE_VACIO")
@pytest.mark.tester("Ronald")
def test_nombre_vacio_no_permite_actualizar(driver, base_url, qa_creds, evidencia):

    nombre = "Pearline Kihn"   # <-- cambia el nombre si lo necesitás
    allure.dynamic.title(
        f"Editar usuario '{nombre}' - nombre vacío no permite actualizar"
    )
    # 1) Login
    with allure.step("Iniciar sesión con usuario válido"):
        login = LoginPage(driver, base_url)
        login.open_login()
        evidencia("usuario_edit_nombre_vacio__login_form")
        login.login_as(qa_creds["email"], qa_creds["password"])
        assert login.is_logged_in(), "No se pudo iniciar sesión."
        evidencia("usuario_edit_nombre_vacio__login_ok")


    # 2) Ir a Usuarios
    with allure.step("Navegar al módulo de Usuarios"):
        home = HomePage(driver, base_url)
        home.go_to_users()

        users = UsersPage(driver, base_url)
        users.wait_loaded()
        users.reset_to_first_page()  # opcional
    with allure.step(f"Buscar usuario por nombre: {nombre}"):
        time.sleep(3)
        # 3) Buscar por nombre y hacer CLIC en el botón de búsqueda
        time.sleep(3)
        users.search_by_name(nombre)  # este método ya escribe y hace click en el botón

        # 4) Tomar evidencia del resultado tal cual se ve en la tabla (filtrada o no)
        evidencia("buscar_usuario__resultado")

    # 5) Si el usuario existe, localizarlo (paginando si hace falta) y abrir 'Editar'
    #assert users.find_or_paginate_to_name(nombre, exact=True, max_pages=12), \
    #    f"No se encontró el usuario '{nombre}' tras buscar/paginar."

    with allure.step(f"Abrir pantalla de edición para '{nombre}'"):
        assert users.open_edit_by_name(nombre, exact=True), \
            f"No fue posible abrir 'Editar' para '{nombre}'."

        time.sleep(3)
        # 6) Evidencia de la pantalla de edición (opcional)
        evidencia("buscar_usuario__editar_abierto")

    with allure.step("Borrar el nombre y confirmar que el sistema muestra error"):
        # Edit: borrar nombre y validar bloqueo aunque confirmemos el popconfirm
        edit = UserEditPage(driver)
        edit.wait_loaded()
        edit.clear_name()
        evidencia("usuario_edit__nombre_vacio_pre_update")    
        edit.update_and_confirm_expect_name_error()
        evidencia("usuario_edit__nombre_vacio_post_confirm")

@allure.epic("Gestión de Contratos")
@allure.feature("Administración de Usuarios")
@allure.story("Validaciones de edición de usuario")
@allure.severity(allure.severity_level.NORMAL)
@allure.label("owner", "Ronald Aguilar")
@allure.link(
    "https://mi-matriz-casos/USUARIOS_EDITAR_VALIDACION_EMAIL_INVALIDO",
    name="USUARIOS_EDITAR_VALIDACION_EMAIL_INVALIDO",
)
@pytest.mark.functional
@pytest.mark.e2e
@pytest.mark.negative
@pytest.mark.regression
@pytest.mark.case("USUARIOS_EDITAR_VALIDACION_EMAIL_INVALIDO")
@pytest.mark.tester("Ronald")
def test_email_invalido_no_permite_actualizar(driver, base_url, qa_creds, evidencia):
    nombre = "Prof. Joesph Koepp"   # <-- cambia el nombre si lo necesitás
    allure.dynamic.title(
        f"Editar usuario '{nombre}' - email inválido no permite actualizar"
    )

    # 1) Login
    with allure.step("Iniciar sesión con usuario válido"):
        login = LoginPage(driver, base_url)
        evidencia("email_invalido__login_form")
        login.open_login()
        login.login_as(qa_creds["email"], qa_creds["password"])
        assert login.is_logged_in(), "No se pudo iniciar sesión."
        evidencia("email_invalido__login_ok")

    # 2) Ir a Usuarios
    with allure.step("Navegar al módulo de Usuarios"):
        home = HomePage(driver, base_url)
        home.go_to_users()

        users = UsersPage(driver, base_url)
        users.wait_loaded()
        users.reset_to_first_page()  # opcional

    with allure.step(f"Buscar usuario por nombre: {nombre}"):
        time.sleep(3)
        # 3) Buscar por nombre y hacer CLIC en el botón de búsqueda
        time.sleep(3)
        users.search_by_name(nombre)  # este método ya escribe y hace click en el botón

        # 4) Tomar evidencia del resultado tal cual se ve en la tabla (filtrada o no)
        evidencia("buscar_usuario__resultado")

    # 5) Si el usuario existe, localizarlo (paginando si hace falta) y abrir 'Editar'
    #assert users.find_or_paginate_to_name(nombre, exact=True, max_pages=12), \
    #    f"No se encontró el usuario '{nombre}' tras buscar/paginar."
    with allure.step(f"Abrir pantalla de edición para '{nombre}'"):
        assert users.open_edit_by_name(nombre, exact=True), \
            f"No fue posible abrir 'Editar' para '{nombre}'."

        time.sleep(3)
        # 6) Evidencia de la pantalla de edición (opcional)
        evidencia("buscar_usuario__editar_abierto")

    # 4) Abrir edición
    with allure.step("Esperar a que el formulario de edición esté cargado"):
        edit = UserEditPage(driver)
        edit.wait_loaded()
        evidencia("email_invalido__form_edicion_abierto")

    # 5) Form edicion
    with allure.step("Ingresar email en formato inválido y verificar validación"):
        edit = UserEditPage(driver)
        edit.wait_loaded()
        evidencia("email_invalido__form_abierto")

        # 6) Colocar email inválido y verificar error
        edit.set_email_raw("nellie.ritchieexample.net", blur=True)  # sin '@'
        edit.wait_email_error_visible()
        evidencia("email_invalido__error_visible")

    # 7) Click en Actualizar -> Confirmar -> Asegurar que NO guarda y sigue el error
    with allure.step("Intentar actualizar con email inválido y confirmar que se bloquea"):
        edit.click_update_expect_validation_blocked()
        evidencia("email_invalido__tras_confirmar_sigue_error")

@allure.epic("Gestión de Contratos")
@allure.feature("Administración de Usuarios")
@allure.story("Validaciones de edición de usuario")
@allure.severity(allure.severity_level.NORMAL)
@allure.label("owner", "Ronald Aguilar")
@allure.link(
    "https://mi-matriz-casos/USUARIOS_EDITAR_VALIDACION_EMAIL_DUPLICADO",
    name="USUARIOS_EDITAR_VALIDACION_EMAIL_DUPLICADO",
)
@pytest.mark.functional
@pytest.mark.e2e
@pytest.mark.negative
@pytest.mark.regression
@pytest.mark.case("USUARIOS_EDITAR_VALIDACION_EMAIL_DUPLICADO")
@pytest.mark.tester("Ronald")
@pytest.mark.xfail(
    strict=True,
    reason="Mejora pendiente: mostrar 'correo ya en uso' de forma explícita",
)
def test_email_duplicado_no_permite_actualizar(driver, base_url, qa_creds, evidencia):

    nombre = "Toy Wiegand"
    correo_duplicado = "yasmine21@example.com"

    allure.dynamic.title(
        f"Editar usuario '{nombre}' - email duplicado no permite actualizar (xfail hasta mejora)"
    )

    # 1) Login
    with allure.step("Iniciar sesión con usuario válido"):
        login = LoginPage(driver, base_url)
        login.open_login()
        evidencia("dup_email__login_form")
        login.login_as(qa_creds["email"], qa_creds["password"])
        assert login.is_logged_in(), "No se pudo iniciar sesión."
        evidencia("dup_email__login_ok")

    # 2) Ir a Usuarios
    with allure.step("Navegar al módulo de Usuarios"):
        home = HomePage(driver, base_url)
        home.go_to_users()

        users = UsersPage(driver, base_url)
        users.wait_loaded()
        users.reset_to_first_page()

    # 3) Buscar y abrir edición de “Toy Wiegand”
    with allure.step(f"Buscar usuario por nombre: {nombre} y abrir Edición"):
        users.search_by_name(nombre)
        evidencia("dup_email__lista_filtrada")
        assert users.open_edit_by_name(nombre, exact=True), f"No se pudo abrir 'Editar' para {nombre}"

    # 4) Form edición
    with allure.step(f"Ingresar correo ya existente: {correo_duplicado}"):
        edit = UserEditPage(driver)
        edit.wait_loaded()
        evidencia("dup_email__form_abierto")

        # 5) Colocar correo duplicado
        edit.set_email_raw(correo_duplicado, blur=True)

    # 6) Intentar actualizar (UI puede permitir click pero backend debe rechazar)
    with allure.step("Intentar actualizar y esperar rechazo del backend"):
        if edit.is_update_enabled():
            edit.click_update_and_confirm()
        else:
            try:
                edit.click_update_and_confirm()
            except Exception:
                pass

        evidencia("dup_email__tras_confirmar")

    # 7) No hubo éxito y sí hubo error genérico
    with allure.step("Verificar que NO hay toast de éxito y SÍ hay toast genérico de error"):
        edit.assert_no_success_toast()
        edit.wait_generic_error_toast()
        evidencia("dup_email__toast_error_generico")

    # 8) **xfail**: hoy NO aparece el mensaje específico “correo ya en uso”
    #    Esperamos que falle ahora (AssertionError) -> xfail
    #    Cuando lo implementen, NO fallará -> XPASS (y con strict=True marcará FAIL para que lo actualices)
    with allure.step(
        "Esperar (fallando adrede) la validación específica de correo duplicado (xfail controlado)"
    ):
        with pytest.raises(AssertionError):
            edit.wait_duplicate_email_error(timeout=2)