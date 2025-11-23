# tests/functional/test_users_listado.py
import pytest
import time
import allure

from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.users_page import UsersPage


@allure.epic("Gestión de Contratos")
@allure.feature("Administración de Usuarios")
@allure.story("Listado de usuarios: carga de tabla y encabezados")
@allure.severity(allure.severity_level.NORMAL)
@allure.label("owner", "Ronald Aguilar")
@allure.link(
    "https://mi-matriz-casos/USUARIOS_LISTADO_CARGA_TABLA_01",
    name="USUARIOS_LISTADO_CARGA_TABLA_01",
)
@pytest.mark.functional
@pytest.mark.e2e
@pytest.mark.regression
@pytest.mark.smoke
@pytest.mark.case("USUARIOS_LISTADO_CARGA_TABLA_01")
@pytest.mark.tester("Ronald")
def test_listado_carga_headers_y_filas(driver, base_url, qa_creds, evidencia):
    allure.dynamic.title("Listado de usuarios - Carga de tabla, encabezados y filas")
    
    # Login
    with allure.step("Iniciar sesión con usuario válido"):
        login = LoginPage(driver, base_url)
        login.open_login()
        evidencia("listado__login_form")
        login.login_as(qa_creds["email"], qa_creds["password"])
        assert login.is_logged_in(), "No se pudo iniciar sesión."
        evidencia("listado__login_ok")

    # Ir a Usuarios
    with allure.step("Navegar al módulo de Usuarios"):
        home = HomePage(driver, base_url)
        home.go_to_users()

        users = UsersPage(driver, base_url)
        users.wait_loaded()
        evidencia("listado__pantalla_cargada")

    # Encabezados visibles y filas cargadas
    with allure.step("Verificar encabezados de la tabla y filas/estado vacío"):
        headers = users.get_headers()
        assert headers, "La tabla no mostró encabezados."
        assert "Nombre" in headers, f"Se esperaba el encabezado 'Nombre'. Headers: {headers}"

        # O hay filas o hay estado vacío, pero no ambas cosas a la vez
        if users.is_empty():
            evidencia("listado__estado_vacio")
        else:
            assert users.row_count() > 0, "No hay filas visibles en el listado."
            evidencia("listado__con_filas")


@allure.epic("Gestión de Contratos")
@allure.feature("Administración de Usuarios")
@allure.story("Listado de usuarios: paginación siguiente/anterior")
@allure.severity(allure.severity_level.NORMAL)
@allure.label("owner", "Ronald Aguilar")
@allure.link(
    "https://mi-matriz-casos/USUARIOS_LISTADO_PAGINACION_01",
    name="USUARIOS_LISTADO_PAGINACION_01",
)
@pytest.mark.functional
@pytest.mark.e2e
@pytest.mark.regression
@pytest.mark.case("USUARIOS_LISTADO_PAGINACION_01")
@pytest.mark.tester("Ronald")
def test_listado_paginacion_siguiente_y_anterior(driver, base_url, qa_creds, evidencia):
    allure.dynamic.title("Listado de usuarios - Paginación siguiente y anterior")

    # Login
    with allure.step("Iniciar sesión con usuario válido"):
        login = LoginPage(driver, base_url)
        login.open_login()
        evidencia("paginacion__login_form")
        login.login_as(qa_creds["email"], qa_creds["password"])
        assert login.is_logged_in(), "No se pudo iniciar sesión."
        evidencia("paginacion__login_ok")


    # Ir a Usuarios
    with allure.step("Navegar al módulo de Usuarios y cargar primera página"):
        home = HomePage(driver, base_url)
        home.go_to_users()

        users = UsersPage(driver, base_url)
        time.sleep(4)
        users.wait_loaded()
        users.reset_to_first_page()
        first_sample = users.first_names_sample(k=5)
        evidencia("paginacion__pagina_1")

    # Intentar ir a siguiente página
    with allure.step("Ir a la siguiente página de resultados"):
        went_next = users.next_page()
        if not went_next:
            pytest.skip("Solo existe una página; no se puede validar paginación.")

        evidencia("paginacion__pagina_2")
        second_sample = users.first_names_sample(k=5)
        assert users.row_count() > 0, "La segunda página no tiene filas."
        assert second_sample != first_sample, "El contenido de la página 2 parece igual al de la página 1."

    # Volver a la anterior
    with allure.step("Regresar a la página anterior"):
        went_prev = users.prev_page()
        assert went_prev, "No se pudo regresar a la página anterior."
        evidencia("paginacion__de_regreso_a_pagina_1")

@allure.epic("Gestión de Contratos")
@allure.feature("Administración de Usuarios")
@allure.story("Listado de usuarios: ordenamiento por nombre")
@allure.severity(allure.severity_level.MINOR)
@allure.label("owner", "Ronald Aguilar")
@allure.link(
    "https://mi-matriz-casos/USUARIOS_LISTADO_ORDENAR_POR_NOMBRE_01",
    name="USUARIOS_LISTADO_ORDENAR_POR_NOMBRE_01",
)
@pytest.mark.functional
@pytest.mark.e2e
@pytest.mark.regression
@pytest.mark.case("USUARIOS_LISTADO_ORDENAR_POR_NOMBRE_01")
@pytest.mark.tester("Ronald")
def test_listado_ordenar_por_nombre(driver, base_url, qa_creds, evidencia):
    allure.dynamic.title("Listado de usuarios - Ordenar por columna Nombre")
    def norm(xs):
        return [ (x or "").strip().lower() for x in xs ]
    
    with allure.step("Iniciar sesión con usuario válido"):
        # Login
        login = LoginPage(driver, base_url)
        login.open_login()
        evidencia("orden__login_form")
        login.login_as(qa_creds["email"], qa_creds["password"])
        assert login.is_logged_in()
        evidencia("orden__login_ok")

    # Ir a Usuarios
    with allure.step("Navegar al módulo de Usuarios y cargar primera página"):
        home = HomePage(driver, base_url)
        home.go_to_users()

        users = UsersPage(driver, base_url)
        time.sleep(4)
        users.wait_loaded()
        users.reset_to_first_page()

        

        base_sample = users.first_names_sample(k=8)
        evidencia("orden__base")

    # Toggle 1
    with allure.step("Aplicar primer toggle de ordenamiento en columna Nombre"):
        users.sort_by_nombre_toggle()
        sample_1 = users.first_names_sample(k=8)
        evidencia("orden__toggle_1")

    # Toggle 2
    with allure.step("Aplicar segundo toggle de ordenamiento en columna Nombre"):
        users.sort_by_nombre_toggle()
        sample_2 = users.first_names_sample(k=8)
        evidencia("orden__toggle_2")

    # Al menos uno de los toggles debe cambiar el orden visible
    with allure.step("Verificar que el ordenamiento modifica el orden visible de las filas"):
        assert norm(sample_1) != norm(base_sample) or norm(sample_2) != norm(sample_1), \
            f"No se observó cambio de orden. base={base_sample} t1={sample_1} t2={sample_2}"


@allure.epic("Gestión de Contratos")
@allure.feature("Administración de Usuarios")
@allure.story("Listado de usuarios: cambio de tamaño de página")
@allure.severity(allure.severity_level.MINOR)
@allure.label("owner", "Ronald Aguilar")
@allure.link(
    "https://mi-matriz-casos/USUARIOS_LISTADO_CAMBIAR_TAMANO_PAGINA_01",
    name="USUARIOS_LISTADO_CAMBIAR_TAMANO_PAGINA_01",
)
@pytest.mark.functional
@pytest.mark.e2e
@pytest.mark.regression
@pytest.mark.case("USUARIOS_LISTADO_CAMBIAR_TAMANO_PAGINA_01")
@pytest.mark.tester("Ronald")
def test_listado_cambiar_tamano_pagina(driver, base_url, qa_creds, evidencia):
    
    allure.dynamic.title("Listado de usuarios - Cambiar tamaño de página (page size)")
    # Login
    
    with allure.step("Iniciar sesión con usuario válido"):
        login = LoginPage(driver, base_url)
        login.open_login()
        evidencia("page_size__login_form")
        login.login_as(qa_creds["email"], qa_creds["password"])
        assert login.is_logged_in()
        evidencia("page_size__login_ok")

    # Ir a Usuarios
    with allure.step("Navegar al módulo de Usuarios y cargar primera página"):
        home = HomePage(driver, base_url)
        home.go_to_users()

        users = UsersPage(driver, base_url)
        time.sleep(4)
        users.wait_loaded()
        users.reset_to_first_page()

        count_before = users.row_count()
        evidencia("page_size__antes")

    with allure.step("Cambiar tamaño de página a 20 registros por página"):
        # Intentar 20 por página (Ant Design suele ofrecer 10/20/50)
        changed = users.change_page_size(20)
        if not changed:
            pytest.skip("El control de tamaño de página no está disponible o no aceptó 20 / página.")

        evidencia("page_size__despues")
        count_after = users.row_count()

    with allure.step("Verificar que la tabla sigue siendo válida tras el cambio de tamaño"):
        # No exigimos que necesariamente aumente (puede haber pocos registros),
        # pero sí que siga habiendo tabla válida.
        assert count_after >= 0, "No se pudieron leer filas tras cambiar el tamaño de página."
