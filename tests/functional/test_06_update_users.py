# tests/functional/test_users_search.py
import pytest
from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.users_page import UsersPage
from pages.users_edit_page import UserEditPage
import time

@pytest.mark.smoke
def test_buscar_usuario_por_nombre_y_abrir_edicion(driver, base_url, qa_creds, evidencia):
    # 1) Login
    login = LoginPage(driver, base_url)
    login.open_login()
    evidencia("users_search__login_form")

    login.login_as(qa_creds["email"], qa_creds["password"])
    assert login.is_logged_in(), "No se pudo iniciar sesión."
    evidencia("users_search__login_ok")

    # 2) Ir a Usuarios
    home = HomePage(driver, base_url)
    home.go_to_users()

    users = UsersPage(driver, base_url)
    users.wait_loaded()
    evidencia("users_search__usuarios_listado_inicial")

    users.reset_to_first_page()  # opcional

    time.sleep(3)
    # 3) Buscar por nombre y hacer CLIC en el botón de búsqueda
    nombre = "Pearline Kihn"   # <-- cambia el nombre si lo necesitás
    time.sleep(3)
    users.search_by_name(nombre)  # este método ya escribe y hace click en el botón

    # 4) Tomar evidencia del resultado tal cual se ve en la tabla (filtrada o no)
    evidencia("users_search__resultado_busqueda")

    # 5) Si el usuario existe, localizarlo (paginando si hace falta) y abrir 'Editar'
    #assert users.find_or_paginate_to_name(nombre, exact=True, max_pages=12), \
    #    f"No se encontró el usuario '{nombre}' tras buscar/paginar."

    assert users.open_edit_by_name(nombre, exact=True), \
        f"No fue posible abrir 'Editar' para '{nombre}'."

    time.sleep(3)
    # 6) Evidencia de la pantalla de edición (opcional)
    evidencia("buscar_usuario__editar_abierto")

    edit = UserEditPage(driver)
    edit.wait_loaded(expected_name=nombre)  # espera que el nombre esté cargado en el formulario

    evidencia("editar_usuario_form_cargado")

def test_buscar_usuario_editar_y_actualizar_email(driver, base_url, qa_creds, evidencia):
    # 1) Login
    login = LoginPage(driver, base_url)
    login.open_login()
    evidencia("users_update_email__login_form")
    login.login_as(qa_creds["email"], qa_creds["password"])
    assert login.is_logged_in(), "No se pudo iniciar sesión."
    evidencia("users_update_email__login_ok")

    # 2) Ir a Usuarios
    home = HomePage(driver, base_url)
    home.go_to_users()

    users = UsersPage(driver, base_url)
    users.wait_loaded()
    users.reset_to_first_page()  # opcional

    time.sleep(3)
    # 3) Buscar por nombre y hacer CLIC en el botón de búsqueda
    nombre = "Pearline Kihn"   # <-- cambia el nombre si lo necesitás
    time.sleep(3)
    users.search_by_name(nombre)  # este método ya escribe y hace click en el botón

    # 4) Tomar evidencia del resultado tal cual se ve en la tabla (filtrada o no)
    evidencia("buscar_usuario__resultado")

    # 5) Si el usuario existe, localizarlo (paginando si hace falta) y abrir 'Editar'
    #assert users.find_or_paginate_to_name(nombre, exact=True, max_pages=12), \
    #    f"No se encontró el usuario '{nombre}' tras buscar/paginar."

    assert users.open_edit_by_name(nombre, exact=True), \
        f"No fue posible abrir 'Editar' para '{nombre}'."

    time.sleep(3)
    # 6) Evidencia de la pantalla de edición (opcional)
    evidencia("buscar_usuario__editar_abierto")


    # 4) Editar correo y confirmar
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
    from selenium.webdriver.common.by import By
    email_val = driver.find_element(By.ID, "editUser_email").get_attribute("value")
    assert email_val == nuevo_email, f"El email visible no coincide. Esperado: {nuevo_email} / Actual: {email_val}"

def test_nombre_vacio_no_permite_actualizar(driver, base_url, qa_creds, evidencia):
    # 1) Login
    login = LoginPage(driver, base_url)
    login.open_login()
    login.login_as(qa_creds["email"], qa_creds["password"])
    assert login.is_logged_in(), "No se pudo iniciar sesión."

    # 2) Ir a Usuarios
    home = HomePage(driver, base_url)
    home.go_to_users()

    users = UsersPage(driver, base_url)
    users.wait_loaded()
    users.reset_to_first_page()  # opcional

    time.sleep(3)
    # 3) Buscar por nombre y hacer CLIC en el botón de búsqueda
    nombre = "Pearline Kihn"   # <-- cambia el nombre si lo necesitás
    time.sleep(3)
    users.search_by_name(nombre)  # este método ya escribe y hace click en el botón

    # 4) Tomar evidencia del resultado tal cual se ve en la tabla (filtrada o no)
    evidencia("buscar_usuario__resultado")

    # 5) Si el usuario existe, localizarlo (paginando si hace falta) y abrir 'Editar'
    #assert users.find_or_paginate_to_name(nombre, exact=True, max_pages=12), \
    #    f"No se encontró el usuario '{nombre}' tras buscar/paginar."

    assert users.open_edit_by_name(nombre, exact=True), \
        f"No fue posible abrir 'Editar' para '{nombre}'."

    time.sleep(3)
    # 6) Evidencia de la pantalla de edición (opcional)
    evidencia("buscar_usuario__editar_abierto")

    # Edit: borrar nombre y validar bloqueo aunque confirmemos el popconfirm
    edit = UserEditPage(driver)
    edit.wait_loaded()
    edit.clear_name()
    evidencia("usuario_edit__nombre_vacio_pre_update")

    edit.update_and_confirm_expect_name_error()
    evidencia("usuario_edit__nombre_vacio_post_confirm")

def test_email_invalido_no_permite_actualizar(driver, base_url, qa_creds, evidencia):
    # 1) Login
    login = LoginPage(driver, base_url)
    login.open_login()
    login.login_as(qa_creds["email"], qa_creds["password"])
    assert login.is_logged_in(), "No se pudo iniciar sesión."

    # 2) Ir a Usuarios
    home = HomePage(driver, base_url)
    home.go_to_users()

    users = UsersPage(driver, base_url)
    users.wait_loaded()
    users.reset_to_first_page()  # opcional

    time.sleep(3)
    # 3) Buscar por nombre y hacer CLIC en el botón de búsqueda
    nombre = "Prof. Joesph Koepp"   # <-- cambia el nombre si lo necesitás
    time.sleep(3)
    users.search_by_name(nombre)  # este método ya escribe y hace click en el botón

    # 4) Tomar evidencia del resultado tal cual se ve en la tabla (filtrada o no)
    evidencia("buscar_usuario__resultado")

    # 5) Si el usuario existe, localizarlo (paginando si hace falta) y abrir 'Editar'
    #assert users.find_or_paginate_to_name(nombre, exact=True, max_pages=12), \
    #    f"No se encontró el usuario '{nombre}' tras buscar/paginar."

    assert users.open_edit_by_name(nombre, exact=True), \
        f"No fue posible abrir 'Editar' para '{nombre}'."

    time.sleep(3)
    # 6) Evidencia de la pantalla de edición (opcional)
    evidencia("buscar_usuario__editar_abierto")

    # 4) Abrir edición
    edit = UserEditPage(driver)
    edit.wait_loaded()
    evidencia("email_invalido__form_edicion_abierto")

    # 5) Form edicion
    edit = UserEditPage(driver)
    edit.wait_loaded()
    evidencia("email_invalido__form_abierto")

    # 6) Colocar email inválido y verificar error
    edit.set_email_raw("nellie.ritchieexample.net", blur=True)  # sin '@'
    edit.wait_email_error_visible()
    evidencia("email_invalido__error_visible")

    # 7) Click en Actualizar -> Confirmar -> Asegurar que NO guarda y sigue el error
    edit.click_update_expect_validation_blocked()
    evidencia("email_invalido__tras_confirmar_sigue_error")

@pytest.mark.xfail(strict=True, reason="Mejora pendiente: mostrar 'correo ya en uso' de forma explícita")
def test_email_duplicado_no_permite_actualizar(driver, base_url, qa_creds, evidencia):
    # 1) Login
    login = LoginPage(driver, base_url)
    login.open_login()
    login.login_as(qa_creds["email"], qa_creds["password"])
    assert login.is_logged_in(), "No se pudo iniciar sesión."

    # 2) Ir a Usuarios
    home = HomePage(driver, base_url)
    home.go_to_users()

    users = UsersPage(driver, base_url)
    users.wait_loaded()
    users.reset_to_first_page()

    # 3) Buscar y abrir edición de “Toy Wiegand”
    nombre = "Toy Wiegand"
    users.search_by_name(nombre)
    evidencia("dup_email__lista_filtrada")
    assert users.open_edit_by_name(nombre, exact=True), f"No se pudo abrir 'Editar' para {nombre}"

    # 4) Form edición
    edit = UserEditPage(driver)
    edit.wait_loaded()
    evidencia("dup_email__form_abierto")

    # 5) Colocar correo duplicado
    correo_duplicado = "yasmine21@example.com"
    edit.set_email_raw(correo_duplicado, blur=True)

    # 6) Intentar actualizar (UI puede permitir click pero backend debe rechazar)
    if edit.is_update_enabled():
        edit.click_update_and_confirm()
    else:
        try:
            edit.click_update_and_confirm()
        except Exception:
            pass

    evidencia("dup_email__tras_confirmar")

    # 7) No hubo éxito y sí hubo error genérico
    edit.assert_no_success_toast()
    edit.wait_generic_error_toast()
    evidencia("dup_email__toast_error_generico")

    # 8) **xfail**: hoy NO aparece el mensaje específico “correo ya en uso”
    #    Esperamos que falle ahora (AssertionError) -> xfail
    #    Cuando lo implementen, NO fallará -> XPASS (y con strict=True marcará FAIL para que lo actualices)
    with pytest.raises(AssertionError):
        edit.wait_duplicate_email_error(timeout=2)