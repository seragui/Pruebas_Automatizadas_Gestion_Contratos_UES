from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
import time


class ContratoCandidatoPage:
    # ====== Anchors / spinners / mensajes ======
    HEADER_TITLE = (
        By.XPATH,
        "//*[contains(@class,'ant-page-header') and .//span[contains(.,'Contrato - ')]]",
    )
    SPINNER = (By.CSS_SELECTOR, ".ant-spin-spinning")
    TOAST_ANY = (By.CSS_SELECTOR, ".ant-message .ant-message-notice")
    MODAL_ANY = (By.CSS_SELECTOR, ".ant-modal-content")
    MODAL_OK = (
        By.XPATH,
        "//div[contains(@class,'ant-modal-content')]//button[.//span[normalize-space()='Aceptar'] or .//span[normalize-space()='OK']]",
    )

    # ====== Acciones principales ======
    BTN_GENERAR_NUEVA_VERSION = (
        By.XPATH,
        "//button[.//span[normalize-space()='Generar nueva versión a partir de los datos de la solicitud']]",
    )

    # ====== Navegación ======
    BTN_BACK = (By.XPATH, "//div[contains(@class,'ant-page-header-back-button')]")

    # ====== Estados en orden (para flujo completo) ======
    STATES_ORDER = [
        "Revisión Fiscalía",
        "Firma Rectoría",
        "Firma Contratante",
        "Elaboración Planilla",
        "Finalizado",
    ]

    def __init__(self, driver, timeout=20):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    # ---------- utils básicos ----------
    def _wait_spinner_out(self, extra=0):
        try:
            WebDriverWait(self.driver, 10 + extra).until(
                EC.invisibility_of_element_located(self.SPINNER)
            )
        except TimeoutException:
            pass

    def _wait_modal(self):
        return WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located(self.MODAL_ANY)
        )

    def _take(self, evidencia, name):
        if evidencia:
            evidencia(name)

    # ---------- pantalla ----------
    def wait_loaded(self, evidencia=None):
        self.wait.until(EC.presence_of_element_located(self.HEADER_TITLE))
        self._wait_spinner_out()
        self._take(evidencia, "contrato_pantalla_lista")

    # ---------- generar nueva versión ----------
    def generar_nueva_version(self, evidencia=None):
        self.wait_loaded()
        self.wait.until(EC.element_to_be_clickable(self.BTN_GENERAR_NUEVA_VERSION)).click()

        # Modal visible
        self._wait_modal()
        self._take(evidencia, "modal_generacion_visible")

        # Aceptar (OK/Aceptar)
        self.wait.until(EC.element_to_be_clickable(self.MODAL_OK)).click()

        self._wait_spinner_out()

        # Toast de confirmación (opcional)
        try:
            WebDriverWait(self.driver, 6).until(
                EC.visibility_of_element_located(self.TOAST_ANY)
            )
        except TimeoutException:
            pass
        self._take(evidencia, "generacion_ok_toast")

    # ---------- helpers para el MODAL de fecha ----------
    def _visible_modal_root(self):
        # Modal AntD visible
        return self.wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//div[contains(@class,'ant-modal') and not(contains(@class,'ant-modal-hidden'))]",
                )
            )
        )

    def _modal_date_input(self):
        """
        Devuelve el input donde escribimos la fecha.
        1) Intenta el input de texto del DatePicker (ant-input).
        2) Fallback: cualquier input visible dentro del modal (no hidden).
        """
        try:
            return self.wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//div[contains(@class,'ant-modal') and not(contains(@class,'ant-modal-hidden'))]"
                        "//input[@type='text' and contains(@class,'ant-input')]",
                    )
                )
            )
        except TimeoutException:
            pass

        return self.wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//div[contains(@class,'ant-modal') and not(contains(@class,'ant-modal-hidden'))]"
                    "//input[not(@type='hidden')]",
                )
            )
        )

    def _modal_primary_ok(self):
        # Botón primario "Aceptar/OK" del modal
        return self.wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//div[contains(@class,'ant-modal') and not(contains(@class,'ant-modal-hidden'))]"
                    "//button[contains(@class,'ant-btn-primary')]",
                )
            )
        )

    def _set_modal_date_and_confirm(self, fecha_ddmmyyyy: str, evidencia=None, etiqueta=""):
        # 1) Modal visible
        self._visible_modal_root()
        time.sleep(0.15)  # pequeño yield

        # 2) Input de fecha
        date_input = self._modal_date_input()
        try:
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});", date_input
            )
            self.driver.execute_script("arguments[0].focus();", date_input)
        except Exception:
            pass

        # 3) Ctrl+A, escribir fecha, ENTER (cierra el datepicker si está abierto)
        try:
            date_input.send_keys(Keys.CONTROL, "a")
        except Exception:
            # Windows vs Mac: CONTROL o COMMAND; pero normalmente CONTROL funciona en Windows
            pass

        date_input.clear()
        date_input.send_keys(fecha_ddmmyyyy)
        date_input.send_keys(Keys.ENTER)

        if evidencia:
            evidencia(f"{etiqueta}fecha_ingresada")

        # 4) Clic en "Aceptar"/OK
        btn_ok = self._modal_primary_ok()
        try:
            btn_ok.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", btn_ok)

        # 5) Esperar toast de éxito (dos variantes de mensaje)
        self.wait.until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//*[contains(@class,'ant-message') and "
                    "(contains(.,'actualizado correctamente') or contains(.,'éxito') or contains(.,'exito'))]",
                )
            )
        )
        if evidencia:
            evidencia(f"{etiqueta}estado_actualizado")
        time.sleep(0.4)  # evitar que el siguiente (+) choque con tooltips

    # ---------- Helpers para localizar el (+) de cada paso ----------
    def _step_plus_btn_xpath_by_title(self, titulo: str):
        """
        Busca el botón (+) dentro del step cuyo título contenga el texto,
        tolerando acentos y espacios con translate/normalize-space.
        """
        safe = (titulo or "").strip()
        return (
            By.XPATH,
            "("
            "//div[contains(@class,'ant-steps-item')]"
            "[.//div[contains(@class,'ant-steps-item-title')]["
            "contains(translate(normalize-space(.),"
            "'ÁÉÍÓÚÜáéíóúü','AEIOUUAEIOUU'), "
            f"translate('{safe}','ÁÉÍÓÚÜáéíóúü','AEIOUUAEIOUU'))"
            "]]"
            "//button[.//span[contains(@class,'anticon-plus')]]"
            ")[1]",
        )

    def _step_plus_btn_xpath_by_index(self, index_1_based: int):
        # Fallback: toma el ítem N (1-based) y busca su botón (+)
        return (
            By.XPATH,
            "("
            "//div[contains(@class,'ant-steps') and contains(@class,'ant-steps-horizontal')]"
            "//div[contains(@class,'ant-steps-item')]"
            f")[{index_1_based}]//button[.//span[contains(@class,'anticon-plus')]]",
        )

    def _click_step_plus(self, by_tuple, evidencia=None, etiqueta=""):
        # localiza, hace scroll, espera clickeable y clic (con JS de respaldo)
        btn = self.wait.until(EC.presence_of_element_located(by_tuple))
        try:
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});", btn
            )
        except Exception:
            pass
        btn = self.wait.until(EC.element_to_be_clickable(by_tuple))
        try:
            btn.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", btn)

        if evidencia and etiqueta:
            evidencia(f"estado_click_plus__{etiqueta}")

        time.sleep(0.15)

    # ---------- cambiar estado con fecha ----------
    def cambiar_estado(self, titulo_estado: str, fecha_ddmmyyyy: str, evidencia=None):
        # 1) Intentar localizar el (+) por TÍTULO (accent-insensitive)
        try:
            self._click_step_plus(
                self._step_plus_btn_xpath_by_title(titulo_estado),
                evidencia=evidencia,
                etiqueta=f"{titulo_estado}__by_title",
            )
        except TimeoutException:
            # 2) Fallback: localizar por ÍNDICE del paso
            orden = {
                "Elaborado": 1,
                "Revisión Fiscalía": 2,
                "Firma Rectoría": 3,
                "Firma Contratante": 4,
                "Elaboración Planilla": 5,
                "Finalizado": 6,
            }
            idx = orden.get((titulo_estado or "").strip(), None)
            if idx is None:
                raise
            self._click_step_plus(
                self._step_plus_btn_xpath_by_index(idx),
                evidencia=evidencia,
                etiqueta=f"{titulo_estado}__by_index_{idx}",
            )

        # 3) Setear fecha en el modal y confirmar (Aceptar) + esperar toast
        self._set_modal_date_and_confirm(
            fecha_ddmmyyyy,
            evidencia=evidencia,
            etiqueta=f"estado_{titulo_estado.lower().replace(' ', '_')}_",
        )

    # ---------- flujo completo de estados ----------
    def completar_flujo_estados(self, fecha_ddmmyyyy: str, evidencia=None):
        for titulo in self.STATES_ORDER:
            self.cambiar_estado(titulo, fecha_ddmmyyyy, evidencia=evidencia)

    # ---------- volver ----------
    def volver_a_generar_contratos(self, evidencia=None):
        self.wait.until(EC.element_to_be_clickable(self.BTN_BACK)).click()
        self._wait_spinner_out()
        self._take(evidencia, "volver_generar_contratos")

