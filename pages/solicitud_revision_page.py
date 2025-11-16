from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class SolicitudRevisionPage:
    """
    Vista de detalle de la solicitud donde aparecen los pasos y el botón:
    [Enviar a secretaría]
    NO modifica clases existentes. Es un Page Object nuevo y autocontenido.
    """

    # --- Señales de que la vista cargó ---
    # Cualquiera de estas dos debería estar:
    HEADER_SOLICITUD = (
        By.XPATH,
        "//span[contains(@class,'ant-page-header-heading-title') and contains(.,'Solicitud de Contratación')]"
    )

    STEP_RRHH = (By.XPATH, "//div[contains(@class,'ant-steps-item')]"
                           "[.//div[contains(@class,'ant-steps-item-title')][normalize-space()='Revision de solicitud de contratación por Recursos Humanos']]")
    
    STEP_RRHH_ACTIVO = (
        By.XPATH,
        "//div[contains(@class,'ant-steps')]"
        "//*[contains(@class,'ant-steps-item-active') or contains(@class,'ant-steps-item-process')]"
        "//*[contains(@class,'ant-steps-item-title') and contains(normalize-space(),'Revision de solicitud de contratación')]"
    )

    BTN_ENVIAR_SECRETARIA = (By.XPATH, "//button[.//span[normalize-space()='Enviar a secretaría']]")

    # --- Éxito: toast (si existe Ant Message) ---
    ANY_TOAST = (By.CSS_SELECTOR, ".ant-message .ant-message-notice")
    SUCCESS_TOAST_TEXT = (By.XPATH, "//div[contains(@class,'ant-message')]"
                                    "//span[contains(translate(., 'ÉEXITO', 'éexito'), 'exito') or "
                                    "contains(translate(., 'ÉVALIDÓ', 'évalidó'), 'valid') or "
                                    "contains(., 'envi')]")

    # --- Éxito alterno: cambio en el step “Enviado a Secretaría de Facultad” ---
    STEP_SECRETARIA_TITLE = (By.XPATH, "//div[contains(@class,'ant-steps-item')]"
                                       "[.//div[contains(@class,'ant-steps-item-title')][normalize-space()='Enviado a Secretaría de Facultad']]")
    # El mismo step, pero en estado process/finish
    STEP_SECRETARIA_ACTIVA_O_FINISH = (By.XPATH, "//div[contains(@class,'ant-steps-item') "
                                                 "and (contains(@class,'ant-steps-item-process') or contains(@class,'ant-steps-item-finish'))]"
                                                 "[.//div[contains(@class,'ant-steps-item-title')][normalize-space()='Enviado a Secretaría de Facultad']]")
    
    MODAL_EXITO = (
            By.XPATH,
            "//*[contains(@class,'ant-modal') or contains(@class,'swal2-popup') or @role='dialog']"
            "//*[contains(.,'Solicitud de contratación') and contains(.,'enviada con éxito')]")
    
    MODAL_ACEPTAR = (
            By.XPATH,
            "//*[contains(@class,'ant-modal') or contains(@class,'swal2-popup') or @role='dialog']"
            "//button[.//span[normalize-space()='Aceptar'] or normalize-space()='Aceptar']")
    
    HEADER_DETALLE_FLEX = (
        By.XPATH,
        "//*[contains(@class,'ant-page-header') and "
        "("
        "contains(.,'Solicitud de Contratación') or "
        "contains(.,'Docentes requeridos en la solicitud') or "
        "contains(.,'Validación') or "
        "contains(.,'Detalle')"
        ")]"
    )

    def __init__(self, driver, timeout=20):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def wait_loaded(self, evidencia=None):
        # Cualquiera de los dos confirma la vista correcta
        self.wait.until(
            EC.any_of(
                EC.visibility_of_element_located(self.HEADER_SOLICITUD),
                EC.visibility_of_element_located(self.STEP_RRHH_ACTIVO),
            )
        )
        # Y nos aseguramos que el botón objetivo esté clickable
        self.wait.until(EC.element_to_be_clickable(self.BTN_ENVIAR_SECRETARIA))
        if evidencia:
            evidencia("revision_page_loaded")
        return self


    def enviar_a_secretaria(self, evidencia=None):
        # click al botón (ya existente)
        btn = self.wait.until(EC.element_to_be_clickable(self.BTN_ENVIAR_SECRETARIA))
        try:
            btn.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", btn)
        if evidencia:
            evidencia("click_enviar_a_secretaria")

        # 1) Modal de éxito → click Aceptar → esperar redirección
        try:
            self.wait.until(EC.visibility_of_element_located(self.MODAL_EXITO))
            if evidencia:
                evidencia("modal_enviado_secretaria_visible")

            aceptar = self.wait.until(EC.element_to_be_clickable(self.MODAL_ACEPTAR))
            try:
                aceptar.click()
            except Exception:
                self.driver.execute_script("arguments[0].click();", aceptar)
            if evidencia:
                evidencia("modal_enviado_secretaria_aceptar")

            # Redirección a /contratos
            self.wait.until(EC.url_contains("/contratos"))
            if evidencia:
                evidencia("redirect_contratos_ok")
            return
        except TimeoutException:
            # 2) Fallback: si no se vio modal, mantenemos los chequeos previos (toast/step) o URL
            pass

        # Fallbacks existentes (por si tu UI muestra toast o step sin modal)
        try:
            self.wait.until(EC.url_contains("/contratos"))
            if evidencia:
                evidencia("redirect_contratos_ok")
            return
        except TimeoutException:
            pass

        # Si no hubo ni modal ni redirect, fallamos con contexto
        raise AssertionError("No se mostró el modal de éxito ni se detectó redirección a /contratos tras enviar a secretaría.")
    
    def _soft_wait_detalle(self, evidencia=None, timeout=10):
        """Intenta detectar que abrimos el detalle, pero NO lanza excepción."""
        w = WebDriverWait(self.driver, timeout)
        ok = False
        try:
            w.until(
                lambda d: (
                    "/contratos/solicitud/" in d.current_url
                    or "/recepcion-solicitudes/" in d.current_url
                    or "/solicitudes/" in d.current_url
                )
            )
            ok = True
        except TimeoutException:
            pass

        if not ok:
            try:
                w.until(EC.presence_of_element_located(self.HEADER_DETALLE_FLEX))
                ok = True
            except TimeoutException:
                ok = False

        if evidencia:
            evidencia("asist_pos_click_ver")  # captura post-click
        return ok

    def click_ver_by_code(self, code, evidencia=None, require_detalle=False):
        # localizar fila por código y dar clic al botón "Ver información"
        row = self._find_row_by_code(code)  # tu helper actual
        if evidencia:
            evidencia(f"asist_row_encontrada__{code}")

        btn = row.find_element(By.XPATH, ".//button[.//span[normalize-space()='Ver información']]")
        btn.click()
        if evidencia:
            evidencia(f"asist_click_ver__{code}")

        # Espera suave del detalle
        ok = self._soft_wait_detalle(evidencia=evidencia)

        # Si la prueba exige el detalle, entonces sí fallamos si no se detecta
        if require_detalle and not ok:
            raise AssertionError("No se detectó la vista de detalle tras hacer clic en 'Ver'.")

        # Devolvemos si se logró (True) o no (False), por si lo querés loguear
        return ok