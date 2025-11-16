# pages/user_edit_page.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
import time

class UserEditPage:
    # Encabezado “Editar usuario”
    HEADER = (By.XPATH, "//span[contains(@class,'ant-page-header-heading-title') and normalize-space()='Editar usuario']"
                        " | //h1[starts-with(normalize-space(),'Editando usuario')]")

    # Inputs
    NAME_INPUT  = (By.ID, "editUser_name")
    EMAIL_INPUT = (By.ID, "editUser_email")
    EMAIL_ERROR = (By.XPATH, "//div[contains(@class,'ant-form-item-explain-error')"
                             " and contains(., 'email')]")  # “Email no es un email válido”
    NAME_ERROR  = (By.XPATH,
        "//div[contains(@class,'ant-form-item')][.//label[@for='editUser_name']]"
        "//div[contains(@class,'ant-form-item-explain-error')"
        " and (contains(.,'Por favor ingresar Nombre') or contains(.,'Por favor ingresar'))]"
    )

    DUPLICATE_INLINE = (
    By.XPATH,
    # AntD error bajo el input que contenga “existe”, “en uso”, “ya está”, “ya se encuentra”, “already”
    "//div[contains(@class,'ant-form-item-explain-error')]"
    "[contains(translate(., 'ÁÉÍÓÚáéíóú', 'AEIOUaeiou'), 'existe') or "
    " contains(translate(., 'ÁÉÍÓÚáéíóú', 'AEIOUaeiou'), 'en uso') or "
    " contains(translate(., 'ÁÉÍÓÚáéíóú', 'AEIOUaeiou'), 'ya esta') or "
    " contains(., 'already') or contains(., 'exists')]"
    )

    DUPLICATE_GLOBAL = (
        By.XPATH,
        # Ant message / alert global que mencione lo mismo
        "//div[contains(@class,'ant-message') or contains(@class,'ant-alert')]["
        " .//span[contains(translate(., 'ÁÉÍÓÚáéíóú', 'AEIOUaeiou'), 'existe') or "
        "        contains(translate(., 'ÁÉÍÓÚáéíóú', 'AEIOUaeiou'), 'en uso') or "
        "        contains(translate(., 'ÁÉÍÓÚáéíóú', 'AEIOUaeiou'), 'ya esta') or "
        "        contains(., 'already') or contains(., 'exists')]]"
    )

    GENERIC_ERROR_TOAST = (
    By.XPATH,
    "//div[contains(@class,'ant-message') or contains(@class,'ant-alert')]"
    "[contains(translate(., 'ÁÉÍÓÚáéíóú', 'AEIOUaeiou'), 'error') or "
    " contains(translate(., 'ÁÉÍÓÚáéíóú', 'AEIOUaeiou'), 'hubo un error') or "
    " contains(., 'Hubo un error')]"
    )

    # Botones
    UPDATE_BTN  = (By.XPATH, "//button[normalize-space()='Actualizar' or .//span[normalize-space()='Actualizar']]")
    POPCONFIRM  = (By.CSS_SELECTOR, ".ant-popover")  # contenedor
    CONFIRM_YES = (By.XPATH, "//div[contains(@class,'ant-popover')]//button[.//span[normalize-space()='Sí'] or normalize-space()='Sí' or normalize-space()='Si']")

    # Toast de éxito
    SUCCESS_TOAST = (By.XPATH, "//div[contains(@class,'ant-message')]//span[contains(normalize-space(),'Usuario actualizado con éxito')]")

    def __init__(self, driver, timeout=15):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def wait_loaded(self,expected_name: str | None = None, timeout: int = 10):
        self.wait.until(EC.visibility_of_element_located(self.HEADER))
        self.wait.until(EC.visibility_of_element_located(self.EMAIL_INPUT))
        if expected_name:
            name_val = self.driver.find_element(*self.NAME_INPUT).get_attribute("value") or ""
            assert expected_name in name_val, (
                f"Se esperaba que el nombre en el formulario contuviera "
                f"'{expected_name}', pero tiene: '{name_val}'"
            )

    def set_email(self, new_email: str):
        """Limpia con fuerza, escribe el nuevo email y valida que sea aceptado."""
        inp = self.wait.until(EC.element_to_be_clickable(self.EMAIL_INPUT))
        self._force_clear(inp)
        inp.send_keys(new_email)
        # Blur para que AntD revalide
        inp.send_keys(Keys.TAB)
        self._wait_email_valid()
        # sanity check: el valor visible es el nuevo
        val = inp.get_attribute("value") or ""
        assert val.strip() == new_email, f"El email en el input no coincide: '{val}' != '{new_email}'"

    def click_update_and_confirm(self):
        self.wait.until(EC.element_to_be_clickable(self.UPDATE_BTN)).click()
        # espera popconfirm y confirma
        self.wait.until(EC.visibility_of_element_located(self.POPCONFIRM))
        self.wait.until(EC.element_to_be_clickable(self.CONFIRM_YES)).click()

    def wait_success(self):
        self.wait.until(EC.visibility_of_element_located(self.SUCCESS_TOAST))

    # -------------------------
    # NUEVO: helpers para Nombre
    # -------------------------
    def clear_name(self):
        """Deja vacío el Nombre y dispara la validación del formulario."""
        name = self.wait.until(EC.element_to_be_clickable(self.NAME_INPUT))
        self._force_clear(name)
        name.send_keys(Keys.TAB)  # dispara validación
        return name
    
    def assert_cannot_update_due_to_name(self, wait_error_timeout=3):
        """
        Asegura que con el nombre vacío NO se permite actualizar:
        - Aparece el mensaje rojo de 'Por favor ingresar Nombre'
        - No aparece el pop-confirm de confirmación
        """
        # mensaje rojo requerido
        WebDriverWait(self.driver, wait_error_timeout).until(
            EC.visibility_of_element_located(self.NAME_ERROR)
        )

        # intentar click (algunos UIs deshabilitan el botón y no hace nada)
        try:
            self.wait.until(EC.element_to_be_clickable(self.UPDATE_BTN)).click()
        except Exception:
            pass

        # confirmar que NO se abrió el popconfirm
        try:
            WebDriverWait(self.driver, 1.2).until(EC.visibility_of_element_located(self.POPCONFIRM))
            raise AssertionError("Se mostró la confirmación aunque el nombre está vacío.")
        except TimeoutException:
            # correcto: no se abrió
            return
    def update_and_confirm_expect_name_error(self):
        """
        Click en Actualizar -> aparece popconfirm -> confirmamos 'Sí'
        y verificamos que NO se guarde:
        - NO aparece toast de éxito
        - Permanece visible el error rojo del nombre requerido
        """
        # aseguramos que el error esté visible antes de intentar guardar
        self.wait.until(EC.visibility_of_element_located(self.NAME_ERROR))

        # click en Actualizar y confirma en el popconfirm
        self.wait.until(EC.element_to_be_clickable(self.UPDATE_BTN)).click()
        self.wait.until(EC.visibility_of_element_located(self.POPCONFIRM))
        self.wait.until(EC.element_to_be_clickable(self.CONFIRM_YES)).click()

        # 1) NO debe salir el toast de éxito
        from selenium.common.exceptions import TimeoutException
        try:
            WebDriverWait(self.driver, 2).until(EC.visibility_of_element_located(self.SUCCESS_TOAST))
            raise AssertionError("Se mostró 'Usuario actualizado con éxito' a pesar del nombre vacío.")
        except TimeoutException:
            pass  # correcto: no hubo éxito

        # 2) Debe seguir el error rojo del nombre requerido
        self.wait.until(EC.visibility_of_element_located(self.NAME_ERROR))

    def _force_clear(self, el):
        """Borra de forma robusta inputs controlados (AntD/React)."""
        try:
            el.click()
            el.send_keys(Keys.CONTROL, "a")
            el.send_keys(Keys.DELETE)
        except Exception:
            pass
        # Fallback JS por si el valor sigue “controlado”
        try:
            self.driver.execute_script(
                "arguments[0].value='';"
                "arguments[0].dispatchEvent(new Event('input', {bubbles:true}));"
                "arguments[0].dispatchEvent(new Event('change', {bubbles:true}));",
                el
            )
        except Exception:
            pass

    def _wait_email_valid(self):
        """Espera a que no haya error de validación en el campo email."""
        # Si aparece el mensaje de error, espera a que desaparezca; si no aparece, continúa.
        try:
            # pequeño grace-period por si el error aparece primero
            WebDriverWait(self.driver, 0.8).until(EC.visibility_of_element_located(self.EMAIL_ERROR))
        except TimeoutException:
            pass
        try:
            WebDriverWait(self.driver, 5).until(EC.invisibility_of_element_located(self.EMAIL_ERROR))
        except TimeoutException:
            # Si no desaparece, igual devolvemos el control (el test asertará luego)
            pass

# ---------- Email inválido: helpers ----------

    def is_update_enabled(self) -> bool:
        try:
            btn = self.wait.until(EC.presence_of_element_located(self.UPDATE_BTN))
            dis = btn.get_attribute("disabled")
            return not (dis and dis.strip().lower() in ("true", "disabled"))
        except Exception:
            return False
        
    def set_email_raw(self, text: str, blur: bool = True):
        el = self.wait.until(EC.element_to_be_clickable(self.EMAIL_INPUT))
        # clear robusto
        el.click()
        el.send_keys(Keys.CONTROL, "a")
        el.send_keys(Keys.DELETE)
        try:
            self.driver.execute_script(
                "arguments[0].value=''; arguments[0].dispatchEvent(new Event('input', {bubbles:true}));",
                el
            )
        except Exception:
            pass
        el.send_keys(text)
        if blur:
            el.send_keys(Keys.TAB)

    def wait_email_error_visible(self, timeout: int = 5):
        WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(self.EMAIL_ERROR))

    def click_update_expect_validation_blocked(self):
        # 1) Click al botón
        self.wait.until(EC.element_to_be_clickable(self.UPDATE_BTN)).click()

        # 2) Si aparece el popconfirm, darle “Sí”
        try:
            WebDriverWait(self.driver, 3).until(EC.visibility_of_element_located(self.POPCONFIRM))
            self.wait.until(EC.element_to_be_clickable(self.CONFIRM_YES)).click()
        except TimeoutException:
            # No apareció confirmación (ok también)
            pass

        # 3) Asegurar: NO toast de éxito
        self.assert_no_success_toast()

        # 4) Asegurar: sigue el error de email visible
        self.wait_email_error_visible()

    def email_error_text(self) -> str:
        try:
            el = self.driver.find_element(*self.EMAIL_ERROR)
            return (el.text or "").strip()
        except Exception:
            return ""

    def is_update_enabled(self) -> bool:
        """Chequea si el botón Actualizar está habilitado (no disabled y sin clase disabled)."""
        btn = self.driver.find_element(*self.UPDATE_BTN)
        disabled_attr = btn.get_attribute("disabled")
        classes = btn.get_attribute("class") or ""
        style = btn.get_attribute("style") or ""
        return not (disabled_attr or "ant-btn-disabled" in classes or "pointer-events: none" in style)

    def assert_no_popconfirm(self):
        """Verifica que NO haya popconfirm visible (cuando el form es inválido)."""
        pops = self.driver.find_elements(*self.POPCONFIRM)
        assert all(not p.is_displayed() for p in pops), "No debería mostrarse confirmación con email inválido."
    
    # Utilidad para negar el toast
    def assert_no_success_toast(self, timeout: int = 2):
        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(self.SUCCESS_TOAST))
            raise AssertionError("Apareció el toast de éxito, pero no debía guardarse.")
        except TimeoutException:
            # correcto: no se vio
            return
        
    def wait_duplicate_email_error(self, timeout: int = 6):
        """Espera a un mensaje de 'email duplicado' (inline o global)."""
        end = time.time() + timeout
        while time.time() < end:
            try:
                if self.driver.find_elements(*self.DUPLICATE_INLINE):
                    return
                if self.driver.find_elements(*self.DUPLICATE_GLOBAL):
                    return
            except Exception:
                pass
            time.sleep(0.2)
        raise AssertionError("No apareció el mensaje de 'email duplicado' (inline ni global).")

    def wait_generic_error_toast(self, timeout: int = 6):
        WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(self.GENERIC_ERROR_TOAST)
        )