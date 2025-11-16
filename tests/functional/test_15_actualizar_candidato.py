import pytest
import random
from faker import Faker
from datetime import date
from urllib.parse import urljoin
import time
from urllib.parse import unquote

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from pages.login_page import LoginPage
from pages.candidate_home_page import CandidateHomePage
from pages.candidate_profile_page import CandidateProfilePage


@pytest.mark.functional
@pytest.mark.e2e
@pytest.mark.case("CANDIDATO_DATOS_PERSONALES_01")
def test_candidato_ingresa_datos_personales(driver, base_url, candidate_creds, evidencia, candidate_name_cache):
    """
    Escenario:
    1. El candidato inicia sesión en el sistema.
    2. Desde el dashboard, abre el menú del avatar y selecciona 'Mi perfil'.
    3. Actualiza el teléfono y el correo alterno en su perfil.
    4. Guarda los cambios y verifica que se muestre un mensaje de éxito.
    """

    # 1) Login como candidato
    login_page = LoginPage(driver, base_url)
    login_page.open_login()
    evidencia("candidato_login__form_visible")

    login_page.login_as(candidate_creds["email"], candidate_creds["password"])
    assert login_page.is_logged_in(), "El candidato no quedó autenticado tras el login válido."
    evidencia("candidato_login__ok")

    # 2) Home del candidato: validar que cargó y dar clic en 'Ingresar datos personales'
    candidate_home = CandidateHomePage(driver, base_url)
    candidate_home.wait_home_loaded()
    evidencia("candidato_home__visible")

    # Abrir menú del avatar y luego 'Mi perfil'
    candidate_home.open_profile()
    evidencia("perfil_candidato__perfil_desde_menu")

    # 3) Página de perfil: vista resumen
    perfil_page = CandidateProfilePage(driver, base_url)
    perfil_page.wait_loaded()
    evidencia("perfil_edit__perfil_visible")

    # Hacer clic en 'Editar mi perfil'
    perfil_page.click_editar_perfil()
    evidencia("perfil_edit__click_editar_perfil")

    # 4) Cerrar modal Información Laboral si aparece
    perfil_page.close_info_modal_if_present()
    evidencia("perfil_edit__modal_info_laboral_cerrado")

    

    current_url = driver.current_url
    decoded_url = unquote(current_url)  # decodifica %C3%B3 -> ó

    assert decoded_url.rstrip("/").endswith("/información-personal/editar"), (
        "Se esperaba estar en la ruta de edición de información personal "
        f"('/información-personal/editar'), pero la URL actual es: {decoded_url}"
    )

    time.sleep(2)  # pequeña espera para evitar issues de renderizado lento

    # 5) Actualizar Teléfono con un valor aleatorio válido
    nuevo_telefono = perfil_page.update_phone_with_random()
    evidencia("perfil_edit__telefono_actualizado")

    # 6) Hacer clic en 'Actualizar mis datos'
    perfil_page.click_actualizar_datos()
    evidencia("perfil_edit__click_actualizar_datos")

    # 7) Confirmar en el modal dando clic en 'Sí'
    perfil_page.confirm_update()
    evidencia("perfil_edit__confirmacion_si")

    # 8) Esperar mensaje de éxito 'Información actualizada con éxito'
    perfil_page.wait_for_success_message()
    evidencia("perfil_edit__mensaje_exito")

    # (Opcional) Verificar que nos llevó de regreso al perfil
    decoded_after = unquote(driver.current_url)
    assert "/perfil" in decoded_after, (
        "Luego de actualizar los datos se esperaba volver a '/perfil', "
        f"pero la URL actual es: {decoded_after}"
    )

@pytest.mark.functional
@pytest.mark.e2e
@pytest.mark.case("CANDIDATO_DATOS_PERSONALES_02")
def test_candidato_no_actualiza_con_campos_obligatorios_vacios(
    driver,
    base_url,
    candidate_creds,
    evidencia,
    candidate_name_cache,
):
    """
    Escenario negativo:
    1. El candidato inicia sesión en el sistema.
    2. Desde el dashboard, abre el menú del avatar y selecciona 'Mi perfil'.
    3. En la pantalla de edición, borra campos obligatorios (teléfono y correo alterno).
    4. Intenta guardar los cambios y confirma si aparece el popconfirm.
    5. Verifica que NO se redirija al perfil y que NO aparezca el mensaje de éxito.
    """

    # 1) Login como candidato
    login_page = LoginPage(driver, base_url)
    login_page.open_login()
    evidencia("candidato_login__form_visible_neg")

    login_page.login_as(candidate_creds["email"], candidate_creds["password"])
    assert login_page.is_logged_in(), "El candidato no quedó autenticado tras el login válido."
    evidencia("candidato_login__ok_neg")

    # 2) Home del candidato: validar que cargó y dar clic en 'Mi perfil'
    candidate_home = CandidateHomePage(driver, base_url)
    candidate_home.wait_home_loaded()
    evidencia("candidato_home__visible_neg")

    candidate_home.open_profile()
    evidencia("perfil_candidato__perfil_desde_menu_neg")

    # 3) Página de perfil: vista resumen
    perfil_page = CandidateProfilePage(driver, base_url)
    perfil_page.wait_loaded()
    evidencia("perfil_edit__perfil_visible_neg")

    # Clic en 'Editar mi perfil'
    perfil_page.click_editar_perfil()
    evidencia("perfil_edit__click_editar_perfil_neg")

    # Cerrar modal Información Laboral si aparece
    perfil_page.close_info_modal_if_present()
    evidencia("perfil_edit__modal_info_laboral_cerrado_neg")

    # Verificar que estamos en la ruta de edición
    decoded_url = unquote(driver.current_url)
    assert decoded_url.rstrip("/").endswith("/información-personal/editar"), (
        f"Se esperaba estar en '/información-personal/editar', pero la URL actual es: {decoded_url}"
    )

    time.sleep(2)  # pequeña espera por renderizado

    # 4) Dejar campos obligatorios vacíos
    perfil_page.clear_required_fields_for_negative_test()
    evidencia("perfil_edit__campos_obligatorios_vacios")

    # 5) Clic en 'Actualizar mis datos'
    perfil_page.click_actualizar_datos()
    evidencia("perfil_edit__click_actualizar_datos_campos_vacios")

    # Confirmar solo si aparece el popconfirm
    perfil_page.confirm_update()
    evidencia("perfil_edit__confirmacion_si_campos_vacios")

    # 6) Validaciones:
    #   - No debe redirigir al perfil
    assert perfil_page.is_on_edit_page(), (
        "No debió redirigir a la vista de perfil con campos obligatorios vacíos."
    )

    #   - No debe aparecer mensaje de éxito
    assert not perfil_page.has_success_message(), (
        "No debería mostrarse 'Información actualizada con éxito' con datos incompletos."
    )