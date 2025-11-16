# pages/create_user_page.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.common.exceptions import TimeoutException
import time


class CreateUserPage:
    def __init__(self, driver, base_url, timeout=20):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(driver, timeout)

    # -------- Locators base --------
    NAME = (By.ID, "createUser_name")
    EMAIL = (By.ID, "createUser_email")

    # Select (Rol)
    ROLE_SELECTOR = (By.XPATH, "//label[@for='createUser_role']/following::div[contains(@class,'ant-select')][1]")

    # Select (Escuela) — aparece/habilita cuando Rol = Candidato o Director Escuela
    SCHOOL_SELECTOR = (By.XPATH, "//label[@for='createUser_school_id']/following::div[contains(@class,'ant-select')][1]")

    # Cualquier dropdown visible de Ant Design (el overlay)
    DROPDOWN_VISIBLE = (By.XPATH, "//div[contains(@class,'ant-select-dropdown') and not(contains(@class,'ant-select-dropdown-hidden'))]")

    # Opción visible por texto (para usar tanto en Rol como en Escuela)
    def _OPTION_BY_TEXT(self, text):
        return (By.XPATH,
            "//div[contains(@class,'ant-select-dropdown') and not(contains(@class,'ant-select-dropdown-hidden'))]"
            "//div[contains(@class,'ant-select-item-option')][.//div[contains(@class,'ant-select-item-option-content')][normalize-space(text())="
            f"'{text}']]"
        )

    # Botón Crear
    CREATE_BUTTON = (By.XPATH, "//button[@type='submit' and contains(@class,'ant-btn-primary')]")

    # -------- Utilidades --------
    def wait_loaded(self):
        self.wait.until(EC.visibility_of_element_located(self.NAME))
        self.wait.until(EC.visibility_of_element_located(self.EMAIL))
        self.wait.until(EC.visibility_of_element_located(self.ROLE_SELECTOR))

    def set_name(self, text):
        el = self.wait.until(EC.element_to_be_clickable(self.NAME))
        el.clear()
        el.send_keys(text)

    def set_email(self, text):
        el = self.wait.until(EC.element_to_be_clickable(self.EMAIL))
        el.clear()
        el.send_keys(text)

    def _open_select(self, selector_locator):
        box = self.wait.until(EC.element_to_be_clickable(selector_locator))
        box.click()
        self.wait.until(EC.visibility_of_element_located(self.DROPDOWN_VISIBLE))

    def _move_and_click(self, element):
        actions = ActionChains(self.driver)
        actions.move_to_element(element).pause(0.15).click().perform()

    def _scroll_into_view(self, element):
        try:
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block:'center', inline:'nearest'});", element
            )
        except Exception:
            pass

    def _pick_from_dropdown(self, visible_text):
        # Asegurar overlay visible
        panel = self.wait.until(EC.visibility_of_element_located(self.DROPDOWN_VISIBLE))
        self._scroll_into_view(panel)

        # Localizar opción por texto
        opt_locator = self._OPTION_BY_TEXT(visible_text)
        option = self.wait.until(EC.visibility_of_element_located(opt_locator))
        self._scroll_into_view(option)

        # Click con movimiento real de mouse (el dropdown no responde a teclas/tap)
        self._move_and_click(option)

        # Esperar que cierre (confirmación de selección)
        self.wait.until(EC.invisibility_of_element_located(self.DROPDOWN_VISIBLE))

    # -------- Acciones de alto nivel --------
    def select_role(self, role_text: str):
        """
        Abre el dropdown de Rol y selecciona usando mouse movement (sin TAP/teclas).
        """
        self._open_select(self.ROLE_SELECTOR)
        self._pick_from_dropdown(role_text)

    def wait_school_enabled(self):
        """
        Cuando el rol es Candidato o Director Escuela, espera que el selector de Escuela
        esté visible y clickeable.
        """
        self.wait.until(EC.visibility_of_element_located(self.SCHOOL_SELECTOR))
        self.wait.until(EC.element_to_be_clickable(self.SCHOOL_SELECTOR))

    def select_school(self, school_text: str):
        """
        Abre el dropdown de Escuela y selecciona usando mouse movement.
        """
        self._open_select(self.SCHOOL_SELECTOR)
        self._pick_from_dropdown(school_text)

    def submit(self):
        btn = self.wait.until(EC.element_to_be_clickable(self.CREATE_BUTTON))
        self._move_and_click(btn)

# ... arriba quedan tus imports y clase ...

    # ====== Selectores de feedback (modal / toast) ======
    SUCCESS_TITLE = (By.XPATH, "//div[contains(@class,'ant-modal-confirm')]//div[contains(@class,'ant-modal-confirm-title') and contains(., 'Éxito')]")
    SUCCESS_CONTENT = (By.XPATH, "//div[contains(@class,'ant-modal-confirm')]//div[contains(@class,'ant-modal-confirm-content')]")
    SUCCESS_OK = (By.XPATH, "//div[contains(@class,'ant-modal-confirm')]//button[.//span[normalize-space()='Aceptar']]")

    TOAST_SUCCESS = (By.XPATH, "//div[contains(@class,'ant-message')]//div[contains(@class,'ant-message-success')]")
    TOAST_ERROR = (By.XPATH, "//div[contains(@class,'ant-message')]//div[contains(@class,'ant-message-error')]")

    # ...

    def wait_success_modal_and_accept(self, timeout: int = 8) -> str:
        """
        Espera el modal de éxito y da clic en 'Aceptar'. Devuelve el texto del contenido.
        Si no aparece en 'timeout', lanza TimeoutException.
        """
        WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(self.SUCCESS_TITLE))
        content_el = self.wait.until(EC.visibility_of_element_located(self.SUCCESS_CONTENT))
        ok_btn = self.wait.until(EC.element_to_be_clickable(self.SUCCESS_OK))
        self._move_and_click(ok_btn)
        return content_el.text.strip()

    def wait_success_feedback(self, timeout_total: int = 12) -> str:
        """
        Robusto: acepta 3 caminos de éxito.
        1) Modal 'Éxito' (clic en Aceptar) -> retorna contenido del modal.
        2) Toast de éxito -> retorna 'toast-success'.
        3) Redirección a /usuarios -> retorna 'redirect-success'.
        Si no detecta ninguno, levanta TimeoutException.
        """
        end = time.time() + timeout_total

        # 1) Intentar modal ~5s
        try:
            return self.wait_success_modal_and_accept(timeout=5)
        except Exception:
            pass

        # 2) Intentar toast éxito ~3s
        try:
            WebDriverWait(self.driver, 3).until(EC.visibility_of_element_located(self.TOAST_SUCCESS))
            return "toast-success"
        except Exception:
            pass

        # 3) Intentar redirección a /usuarios hasta agotar el tiempo
        while time.time() < end:
            if "/usuarios" in self.driver.current_url:
                return "redirect-success"
            time.sleep(0.25)

        # Si llegamos aquí no hubo señal de éxito
        raise TimeoutError("No se detectó modal, toast ni redirección exitosa.")

    def wait_error_toast(self, timeout: int = 6) -> str | None:
        """
        Espera un toast de error y retorna su texto (si el DOM lo expone). Si no, retorna 'error-toast'.
        """
        el = WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(self.TOAST_ERROR))
        try:
            return el.text.strip() or "error-toast"
        except Exception:
            return "error-toast"
    
    def form_item_has_error(self, field_for_id: str) -> bool:
        try:
            item = self.wait.until(EC.visibility_of_element_located((
                By.XPATH,
                f"//label[@for='{field_for_id}']/ancestor::div[contains(@class,'ant-form-item')]"
            )))
            cls = item.get_attribute("class") or ""
            return "ant-form-item-has-error" in cls
        except TimeoutException:
            return False
    
    def wait_error_toast(self, timeout: int = 6) -> str | None:
        try:
            toast = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((
                    By.XPATH, "//div[contains(@class,'ant-message') and .//div[contains(@class,'ant-message-notice')]]"
                ))
            )
            # Texto dentro del toast
            try:
                inner = toast.find_element(By.XPATH, ".//div[contains(@class,'ant-message-custom-content')]")
                return (inner.text or "").strip()
            except Exception:
                return (toast.text or "").strip()
        except TimeoutException:
            return None
