# pages/subir_acuerdo_page.py
from __future__ import annotations
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys

class SubirAcuerdoPage:
    """
    Page Object del formulario: 'Solicitud ... - Subir acuerdo'
    Solo lógica de la pantalla (sin capturas).
    """

    # Encabezado tolerante
    TITLE = (
        By.XPATH,
        "//*[contains(@class,'ant-page-header') or contains(@class,'ant-typography')]"
        "//*[contains(.,'Subir acuerdo')]"
    )

    # Locators del formulario
    INPUT_CODIGO = (By.ID, "createEscalafon_code")
    INPUT_FECHA  = (By.ID, "createEscalafon_agreed_on")  # AntD DatePicker (input)
    INPUT_FILE   = (By.ID, "createEscalafon_file")
    RADIO_GROUP  = (By.ID, "createEscalafon_approved")
    RADIO_APRO   = (By.XPATH, "//div[@id='createEscalafon_approved']//label[.//span[normalize-space()='Aprobado']]//input")
    RADIO_NOAPR  = (By.XPATH, "//div[@id='createEscalafon_approved']//label[.//span[normalize-space()='No aprobado']]//input")
    BTN_GUARDAR  = (By.XPATH, "//button[.//span[normalize-space()='Guardar']]")

    # En recepción (listado)
    TABLE = (By.XPATH, "//div[contains(@class,'ant-table') and .//table]")
    ROW_BY_CODE = lambda self, code: (By.XPATH, f"//table//tbody/tr[.//td[normalize-space()='{code}']]")
    BTN_MARK_REC = (By.XPATH, ".//button[.//span[normalize-space()='Marcar como recibido']]")
    # OJO: ya no usaremos el botón relativo a la fila; dejamos este por compat
    BTN_SUBIR_AC = (By.XPATH, ".//button[.//span[normalize-space()='Subir acuerdo de junta']]")

    # Modal confirmación
    MODAL_OK = (By.XPATH, "//div[contains(@class,'ant-modal')]//button[.//span[normalize-space()='Confirmar']]")

    SUCCESS_TOAST = (
        By.XPATH,
        "//div[contains(@class,'ant-message') and contains(.,'Acuerdo de junta creado con éxito')]"
    )

    # Redirección post-guardar
    RECEPCION_URL_FRAGMENT = "/recepcion-solicitudes"
    RECEPCION_TABLE = (By.XPATH, "//div[contains(@class,'ant-table') and .//table]")

    # Buscador (Recepción)
    SEARCH_ANY = (
        By.XPATH, "//input[contains(@placeholder,'Buscar') or contains(@placeholder,'Código')]"
    )
    CLEAR_ICON = (
        By.XPATH, "//span[contains(@class,'ant-input-clear-icon') and not(contains(@class,'hidden'))]"
    )

    def __init__(self, driver, base_url=None, timeout=20):
        self.driver = driver
        self.base_url = (base_url or "").rstrip("/")
        self.wait = WebDriverWait(driver, timeout)

    # ---------- Navegación desde recepción ----------
    def _open_recepcion(self):
        if "/recepcion-solicitudes" not in self.driver.current_url:
            if not self.base_url:
                raise AssertionError("SubirAcuerdoPage: base_url no definido para abrir /recepcion-solicitudes.")
            self.driver.get(self.base_url + "/recepcion-solicitudes")
        self.wait.until(EC.presence_of_element_located(self.TABLE))

    def _clear_and_search_code(self, code: str) -> None:
        try:
            ipt = self.driver.find_element(*self.SEARCH_ANY)
            ipt.click()
            try:
                ipt.send_keys(Keys.CONTROL, "a")
            except Exception:
                ipt.send_keys(Keys.CONTROL)
                ipt.send_keys("a")
            ipt.send_keys(Keys.BACKSPACE)
            # limpiar con ícono si aparece
            try:
                clear_el = self.driver.find_element(*self.CLEAR_ICON)
                try:
                    clear_el.click()
                except Exception:
                    self.driver.execute_script("arguments[0].click();", clear_el)
            except Exception:
                pass
            ipt.send_keys(code)
            ipt.send_keys(Keys.ENTER)
        except Exception:
            # Si no hay buscador, no hacemos nada (queda paginación manual si existiera)
            pass

    def _ensure_row(self, code: str):
        """
        Garantiza que la fila del 'code' esté visible.
        Intenta búsqueda y espera aparición.
        """
        try:
            return WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located(self.ROW_BY_CODE(code))
            )
        except TimeoutException:
            # aplicar búsqueda y reintentar
            self._clear_and_search_code(code)
            return WebDriverWait(self.driver, 8).until(
                EC.presence_of_element_located(self.ROW_BY_CODE(code))
            )

    def _mark_received_if_needed(self, row) -> None:
        """
        Marca como recibido si el botón existe en la fila (algunos estados).
        """
        try:
            btn = row.find_element(*self.BTN_MARK_REC)
        except Exception:
            return  # ya está recibido o no aplica

        try:
            btn.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", btn)

        # Confirmar modal
        self.wait.until(EC.element_to_be_clickable(self.MODAL_OK)).click()

        # Esperar refresco (tabla lista de nuevo)
        self.wait.until(EC.presence_of_element_located(self.TABLE))

    # ---------- Click global en "Subir acuerdo de junta" por código ----------
    def _btn_subir_global_variants(self, code: str):
        """
        Variantes tolerantes del botón 'Subir acuerdo de junta' enlazado a la fila del código.
        """
        return [
            # match exacto del texto del botón
            (By.XPATH,
             "//div[contains(@class,'ant-table')]//table"
             f"//tr[.//td[normalize-space()='{code}']]"
             "//button[.//span[normalize-space()='Subir acuerdo de junta']]"),
            # match parcial (por si el copy cambia levemente)
            (By.XPATH,
             "//div[contains(@class,'ant-table')]//table"
             f"//tr[.//td[normalize-space()='{code}']]"
             "//button[.//span[contains(normalize-space(),'Subir acuerdo')]]"),
        ]

    def _open_subir_acuerdo_global(self, code: str) -> None:
        """
        Evita row.find_element (fuente de NoSuchElement/Stale).
        Busca el botón por XPath global (code + texto) y hace clic.
        """
        last_err = None
        for by in self._btn_subir_global_variants(code):
            try:
                btn = WebDriverWait(self.driver, 8).until(EC.element_to_be_clickable(by))
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
                except Exception:
                    pass
                try:
                    btn.click()
                except Exception:
                    self.driver.execute_script("arguments[0].click();", btn)
                # Formulario cargado
                self.wait.until(EC.presence_of_element_located(self.INPUT_CODIGO))
                self.wait.until(EC.presence_of_element_located(self.INPUT_FECHA))
                self.wait.until(EC.presence_of_element_located(self.BTN_GUARDAR))
                self.wait.until(EC.presence_of_element_located(self.TITLE))
                return
            except Exception as e:
                last_err = e
                continue
        raise NoSuchElementException(
            f"No encontré el botón 'Subir acuerdo' para el código '{code}'. Último error: {last_err}"
        )

    def open_from_recepcion_by_code(self, code: str) -> None:
        """
        Flujo recomendado:
        1) Abrir recepción (si no estás allí).
        2) Asegurar que la fila del código existe (buscar si hace falta).
        3) Marcar como recibido si aplica (modal + refresco).
        4) Click global en 'Subir acuerdo de junta' por código.
        """
        self._open_recepcion()
        row = self._ensure_row(code)
        self._mark_received_if_needed(row)
        # re-resolver visibilidad por si el DOM se re-montó tras marcar recibido
        self._ensure_row(code)
        self._open_subir_acuerdo_global(code)

    # ---------- Rellenar formulario ----------
    def set_codigo(self, value: str) -> None:
        ipt = self.driver.find_element(*self.INPUT_CODIGO)
        ipt.clear()
        ipt.send_keys(value)

    def _guardar_enabled(self) -> bool:
        try:
            btn = self.driver.find_element(*self.BTN_GUARDAR)
            # enabled + atributo disabled vacío/None/false
            return btn.is_enabled() and (btn.get_attribute("disabled") in (None, "", "false"))
        except Exception:
            return False

    def set_fecha_ddmmyyyy(self, fecha_str: str) -> None:
        """
        Escribe la fecha en formato dd/mm/yyyy.
        Estrategia:
          1) Quitar readonly por JS y enfocar.
          2) Ctrl+A, Backspace, nueva fecha, ENTER, TAB.
          3) Esperar valor o habilitación de 'Guardar'.
        """
        ipt = self.driver.find_element(*self.INPUT_FECHA)

        # 1) quitar readonly y enfocar
        self.driver.execute_script(
            "arguments[0].removeAttribute('readonly'); arguments[0].focus();",
            ipt
        )

        # 2) limpiar y escribir
        try:
            ipt.send_keys(Keys.CONTROL, "a")
        except Exception:
            ipt.send_keys(Keys.CONTROL)
            ipt.send_keys("a")
        ipt.send_keys(Keys.BACKSPACE)
        ipt.send_keys(fecha_str)
        ipt.send_keys(Keys.ENTER)   # confirma AntD DatePicker
        ipt.send_keys(Keys.TAB)     # cierra panel si quedó abierto

        # 3) esperar confirmación
        try:
            WebDriverWait(self.driver, 8).until(
                lambda d: (
                    (d.find_element(*self.INPUT_FECHA).get_attribute("value") or "").strip() != ""
                ) or self._guardar_enabled()
            )
        except TimeoutException:
            val = self.driver.find_element(*self.INPUT_FECHA).get_attribute("value") or ""
            if val.strip() == "":
                raise AssertionError("No se pudo establecer la fecha en el DatePicker.")

    def upload_pdf(self, absolute_path: str) -> None:
        file_input = self.driver.find_element(*self.INPUT_FILE)
        # Asegura que no esté oculto (por si el input está display:none)
        try:
            self.driver.execute_script("arguments[0].style.display='block';", file_input)
        except Exception:
            pass
        file_input.send_keys(absolute_path)

    def set_aprobado(self, aprobado: bool = True) -> None:
        locator = self.RADIO_APRO if aprobado else self.RADIO_NOAPR
        el = self.driver.find_element(*locator)
        try:
            el.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", el)

    def wait_success_redirect(self, timeout: int = 12) -> None:
        wait = WebDriverWait(self.driver, timeout)
        # 1) toast de éxito
        wait.until(EC.visibility_of_element_located(self.SUCCESS_TOAST))
        # 2) redirección a recepción
        wait.until(EC.url_contains(self.RECEPCION_URL_FRAGMENT))
        # 3) tabla montada
        wait.until(EC.presence_of_element_located(self.RECEPCION_TABLE))

    def guardar(self) -> None:
        btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.BTN_GUARDAR)
        )
        try:
            btn.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", btn)
        # Bloquear hasta toast + redirect + tabla lista
        self.wait_success_redirect()
