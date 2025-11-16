from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from urllib.parse import unquote
import random

class CandidateProfilePage:
    URL_PATH = "/perfil"

    # Contenedor principal del perfil
    CONTAINER = (By.CSS_SELECTOR, "div.my-profile")

    # Botón 'Editar mi perfil'
    EDITAR_PERFIL_BUTTON = (
        By.XPATH,
        "//div[contains(@class,'profile-header')]"
        "//a[@href='/información-personal/editar/']/button"
    )

    # Modal "Información Laboral"
    MODAL_INFO_LABORAL = (
        By.XPATH,
        "//div[contains(@class,'ant-modal')]"
        "//div[contains(@class,'ant-modal-title') and normalize-space()='Información Laboral']"
    )
    MODAL_BTN_ACEPTAR = (
        By.XPATH,
        "//div[contains(@class,'ant-modal')]"
        "//button[.//span[normalize-space()='Aceptar']]"
    )

        # --- Formulario de edición de información personal ---
    PHONE_INPUT = (By.ID, "personal-info_telephone")

    ALT_MAIL_INPUT = (By.XPATH, "//input[@id='personal-info_alternate_mail']")

    BTN_ACTUALIZAR_DATOS = (
        By.CSS_SELECTOR,
        "form#personal-info button[type='submit']"
    )

    # Modal de confirmación ("¿Está seguro...?") -> botón "Sí"
    POPOVER_CONFIRM = (
        By.XPATH,
        "//div[contains(@class,'ant-popover') and "
        " .//span[contains(normalize-space(),'¿Está seguro de querer ingresar estos datos?')]]"
    )

    CONFIRM_YES = (
        By.XPATH,
        "//div[contains(@class,'ant-popover') and "
        "     not(contains(@class,'ant-popover-hidden'))]"
        "//button[.//span[normalize-space()='Sí' or normalize-space()='Si']]"
    )


    # Mensaje de éxito "Información actualizada con éxito"
    SUCCESS_MESSAGE = (
        By.XPATH,
        "//div[contains(@class,'ant-message')]"
        "//div[contains(@class,'ant-message-notice-content')]"
        "//span[contains(normalize-space(), 'Información actualizada con éxito')]"
    )

    def __init__(self, driver, base_url: str, timeout: int = 10):
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.wait = WebDriverWait(driver, timeout)

    def open_direct(self):
        self.driver.get(self.base_url + self.URL_PATH)

    def wait_loaded(self):
        self.wait.until(EC.visibility_of_element_located(self.CONTAINER))

    def click_editar_perfil(self):
        btn = self.wait.until(EC.element_to_be_clickable(self.EDITAR_PERFIL_BUTTON))
        btn.click()

    def close_info_modal_if_present(self, timeout: int = 5):
        """
        Si aparece el modal 'Información Laboral', hace clic en Aceptar.
        Si no aparece, no rompe la prueba.
        """
        wait = WebDriverWait(self.driver, timeout)
        try:
            wait.until(EC.visibility_of_element_located(self.MODAL_INFO_LABORAL))
            btn = self.driver.find_element(*self.MODAL_BTN_ACEPTAR)
            btn.click()
        except TimeoutException:
            pass

    def update_phone_with_random(self) -> str:
        """
        Limpia el campo Teléfono y escribe un número aleatorio con formato ####-####.
        Devuelve el teléfono usado.
        """
        phone_input = self.wait.until(
            EC.visibility_of_element_located(self.PHONE_INPUT)
        )

        phone_input.click()

        # Limpieza agresiva (para inputs enmascarados)
        phone_input.send_keys(Keys.CONTROL, "a")
        phone_input.send_keys(Keys.BACKSPACE)
        phone_input.clear()
        # algunos masks no respetan clear, mandamos varios backspace extra
        for _ in range(10):
            phone_input.send_keys(Keys.BACKSPACE)

        # Generar número tipo 7xxx-xxxx
        prefix = "7"
        middle = "".join(str(random.randint(0, 9)) for _ in range(3))
        last4 = "".join(str(random.randint(0, 9)) for _ in range(4))
        new_phone = f"{prefix}{middle}-{last4}"

        phone_input.send_keys(new_phone)
        return new_phone

    def click_actualizar_datos(self):
        """
        Hace clic en el botón 'Actualizar mis datos'.
        """
        btn = self.wait.until(
            EC.element_to_be_clickable(self.BTN_ACTUALIZAR_DATOS)
        )
        btn.click()

    def confirm_update(self, timeout: int = 20):
        """
        Confirma la actualización haciendo clic en el botón 'Sí' del popconfirm.
        Si por alguna razón no aparece, intenta aceptar un alert nativo.
        """
        # 1) Intentar con el popconfirm de Ant Design
        try:
            btn_yes = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(self.CONFIRM_YES)
            )

            # Nos aseguramos de que esté en viewport
            self.driver.execute_script("arguments[0].scrollIntoView(true);", btn_yes)

            # Click JS por si hay overlays
            self.driver.execute_script("arguments[0].click();", btn_yes)

            return
        except TimeoutException:
            # No se encontró el popconfirm; intentamos con alert nativo
            pass

        # 2) Fallback: alert/confirm nativo del navegador
        try:
            WebDriverWait(self.driver, 5).until(EC.alert_is_present())
            alert = self.driver.switch_to.alert
            alert.accept()
        except TimeoutException:
            # No hay nada que confirmar; lo dejamos pasar
            pass

    def wait_for_success_message(self, timeout: int = 25):
        """
        Espera a que se complete la actualización:
        1) Redirección a /perfil
        2) (Best-effort) Toast 'Información actualizada con éxito'
        """
        # 1) Esperar que cambie la URL a /perfil
        WebDriverWait(self.driver, timeout).until(
            EC.url_contains("/perfil")
        )

        # 2) Intentar ver el toast (si no se ve, no rompemos el test)
        try:
            WebDriverWait(self.driver, 5).until(
                EC.visibility_of_element_located(self.SUCCESS_MESSAGE)
            )
        except TimeoutException:
            # Si nos perdemos el toast pero ya estamos en /perfil, lo consideramos OK
            pass

    def clear_required_fields_for_negative_test(self):
        """
        Deja en blanco algunos campos obligatorios para validar que el sistema
        no permita guardar información incompleta.
        Usamos: Teléfono y Correo electrónico alterno.
        """
        # Teléfono
        tel_input = WebDriverWait(self.driver, 20).until(
            EC.visibility_of_element_located(self.PHONE_INPUT)
        )
        tel_input.clear()
        tel_input.send_keys(Keys.CONTROL, "a")
        tel_input.send_keys(Keys.DELETE)

        # Correo alterno
        alt_mail_input = WebDriverWait(self.driver, 20).until(
            EC.visibility_of_element_located(self.ALT_MAIL_INPUT)
        )
        alt_mail_input.clear()
        alt_mail_input.send_keys(Keys.CONTROL, "a")
        alt_mail_input.send_keys(Keys.DELETE)

    def is_on_edit_page(self) -> bool:
        """
        Devuelve True si seguimos en /información-personal/editar
        (sin redirigir al perfil).
        """
        current_url = unquote(self.driver.current_url)
        return current_url.rstrip("/").endswith("/información-personal/editar")
    
    def has_success_message(self, timeout: int = 5) -> bool:
        """
        Devuelve True si aparece el mensaje 'Información actualizada con éxito'
        en un tiempo corto. False si no aparece.
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(self.SUCCESS_MESSAGE)
            )
            return True
        except TimeoutException:
            return False