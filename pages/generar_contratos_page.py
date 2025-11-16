# pages/generar_contratos_page.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time

class GenerarContratosPage:
    # Encabezado
    TITLE = (
        By.XPATH,
        "//*[contains(@class,'ant-page-header') or contains(@class,'ant-typography')]"
        "//*[normalize-space()='Generar contratos']"
    )

    DEST_URL_FRAGMENT = "/generacion-contratos"
    DEST_HEADER_ANY = (By.XPATH, "//div[contains(@class,'ant-page-header')]")
    DEST_TABLE_ANY  = (By.XPATH, "//div[contains(@class,'ant-table') and .//table]")
    DEST_MAIN_BLOCK = (By.XPATH, "//main[contains(@class,'ant-layout-content')]//div[contains(@class,'background')]")

    BTN_VER_INFO_IN_ROW = (By.XPATH, ".//button[span[normalize-space()='Ver información']]")
    BTN_CONTRATO_IN_ROW = (By.XPATH, ".//button[span[normalize-space()='Contrato']]")
    DEST_URL_FRAGMENT_CONTRATO = "/contrato-candidato/"

    # (opcional) mantenemos un título “bonito” pero lo tratamos como opcional
    DEST_TITLE_NICE = (
        By.XPATH,
        "//*[contains(@class,'ant-page-header') or contains(@class,'ant-typography')]"
        "//*[contains(.,'Generación de contratos') or contains(.,'Generar contratos') or contains(.,'Contratos')]"
    )


    # Tabla
    TABLE = (By.XPATH, "//div[contains(@class,'ant-table') and .//table]")
    ROW_BY_CODE = lambda self, code: (
        By.XPATH, f"//table//tbody/tr[.//td[normalize-space()='{code}']]"
    )
    BTN_VER_IN_ROW = (By.XPATH, ".//button[.//span[normalize-space()='Ver']]")

    # Buscador
    SEARCH_INPUT = (
        By.XPATH,
        "//span[contains(@class,'ant-input-group')]//input[@placeholder='Buscar por código o tipo de solicitud']"
    )
    SEARCH_BTN = (
        By.XPATH,
        "//span[contains(@class,'ant-input-group')]//button[contains(@class,'ant-input-search-button')]"
    )

    # Paginación
    PAGINATION_NEXT = (
        By.XPATH,
        "//ul[contains(@class,'ant-pagination')]//li[contains(@class,'ant-pagination-next') and not(contains(@class,'disabled'))]"
    )

    LIST_TABLE = (By.XPATH, "//div[contains(@class,'ant-table') and .//table]")
    SEARCH_BOX = (By.XPATH, "//input[contains(@placeholder,'Buscar')]")
    SPINNER    = (By.CSS_SELECTOR, ".ant-spin-spinning")  # AntD Spin visible

    def __init__(self, driver, timeout=20):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    # ---------- Carga de vista ----------
    def wait_loaded(self, evidencia=None):
        w = WebDriverWait(self.driver, 20)
        # 1) URL correcta
        w.until(EC.url_contains("/generar-contratos"))
        # 2) Espera a que monte algo de la vista
        w.until(EC.presence_of_element_located(self.SEARCH_BOX))
        # 3) Espera que NO haya spinner visible (o que al menos aparezca la tabla)
        try:
            w.until(EC.invisibility_of_element_located(self.SPINNER))
        except TimeoutException:
            # fallback: si no desaparece, pero ya hay tabla, seguimos
            w.until(EC.presence_of_element_located(self.LIST_TABLE))

        # micro-pausa para terminar animaciones y asegurar captura limpia
        try:
            WebDriverWait(self.driver, 2).until(
                lambda d: len(d.find_elements(*self.SPINNER)) == 0
            )
        except Exception:
            pass

        if evidencia:
            evidencia("generar_contratos_listado_visible")

    # ---------- Búsqueda ----------
    def search_by_code(self, code: str, evidencia=None):
        """
        Escribe el código en el buscador y pulsa ENTER o el botón de lupa.
        """
        used = False
        try:
            ipt = self.wait.until(EC.presence_of_element_located(self.SEARCH_INPUT))
            ipt.clear()
            ipt.send_keys(code)
            ipt.send_keys(Keys.ENTER)
            used = True
            if evidencia:
                evidencia(f"generar_contratos_search_enter__{code}")
        except TimeoutException:
            # Si no hay input, no pasa nada: devolveremos False y se usará paginación
            pass
        except Exception:
            # Fallback al botón de buscar si existe
            try:
                btn = self.driver.find_element(*self.SEARCH_BTN)
                btn.click()
                used = True
                if evidencia:
                    evidencia(f"generar_contratos_search_btn__{code}")
            except Exception:
                pass

        # Si usamos buscador, espera refresco mínimo de la tabla
        if used:
            try:
                self.wait.until(EC.presence_of_element_located(self.TABLE))
            except TimeoutException:
                pass
        return used

    def _find_row_current_page(self, code: str, timeout=5):
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(self.ROW_BY_CODE(code))
            )
        except TimeoutException:
            return None

    def ensure_row_visible(self, code: str, evidencia=None):
        """
        Asegura que la fila con el 'code' sea visible:
        1) Intenta buscador.
        2) Si no, recorre paginación 'Siguiente' hasta hallarla.
        """
        used_search = self.search_by_code(code, evidencia=evidencia)

        # Intento 1: página actual
        row = self._find_row_current_page(code, timeout=6 if used_search else 4)
        if row:
            if evidencia:
                evidencia(f"generar_contratos_row_encontrada__{code}")
            return row

        # Intento 2: paginación
        page_hops = 0
        while True:
            row = self._find_row_current_page(code, timeout=3)
            if row:
                if evidencia:
                    evidencia(f"generar_contratos_row_encontrada__{code}")
                return row

            # Buscar botón "Siguiente" habilitado
            try:
                next_btn = self.driver.find_element(*self.PAGINATION_NEXT)
            except NoSuchElementException:
                break  # No hay más páginas

            try:
                self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", next_btn)
            except Exception:
                pass

            try:
                next_btn.click()
            except Exception:
                self.driver.execute_script("arguments[0].click();", next_btn)

            page_hops += 1
            if evidencia:
                evidencia(f"generar_contratos_paginacion_click_{page_hops}")

        # Si se usó buscador, un último intento con espera un poco mayor
        if used_search:
            row = self._find_row_current_page(code, timeout=8)
            if row:
                if evidencia:
                    evidencia(f"generar_contratos_row_encontrada__{code}")
                return row

        raise AssertionError(f"No se encontró el código '{code}' en Generar contratos.")

    # ---------- Acción: Ver ----------
    def click_ver(self, code: str, evidencia=None):
        row = self.ensure_row_visible(code, evidencia=evidencia)

        btn_ver = row.find_element(*self.BTN_VER_IN_ROW)
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn_ver)
        except Exception:
            pass
        try:
            btn_ver.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", btn_ver)

        # 1) URL correcta
        WebDriverWait(self.driver, 15).until(EC.url_contains(self.DEST_URL_FRAGMENT))

        # 2) Yield para que React monte
        try:
            WebDriverWait(self.driver, 8).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        except Exception:
            pass

        # 3) Anclas “cualesquiera”
        wait_any = WebDriverWait(self.driver, 12)
        try:
            wait_any.until(
                lambda d: (
                    len(d.find_elements(*self.DEST_HEADER_ANY)) > 0 or
                    len(d.find_elements(*self.DEST_TABLE_ANY))  > 0 or
                    len(d.find_elements(*self.DEST_MAIN_BLOCK)) > 0 or
                    len(d.find_elements(*self.DEST_TITLE_NICE)) > 0
                )
            )
        except TimeoutException:
            pass

        # 3.5) ***Nuevo***: espera a que desaparezca el spinner;
        #      si no desaparece, al menos que haya tabla presente.
        try:
            WebDriverWait(self.driver, 10).until(
                EC.invisibility_of_element_located(self.SPINNER)
            )
        except TimeoutException:
            # Fallback: si aún hay spinner, pero ya hay tabla, seguimos.
            WebDriverWait(self.driver, 6).until(
                EC.presence_of_element_located(self.DEST_TABLE_ANY)
            )

        # 4) Evidencia ya sin loader
        if evidencia:
            try:
                self.driver.execute_script("window.scrollTo(0,0)")
            except Exception:
                pass
            evidencia(f"generar_contratos_destino_visible__{code}")

    def click_contrato(self, code: str, evidencia=None):
        row = self.ensure_row_visible(code, evidencia=evidencia)

        # Prioriza “Contrato”; si no existe, cae a “Ver información”
        try:
            btn = row.find_element(*self.BTN_CONTRATO_IN_ROW)
        except Exception:
            btn = row.find_element(*self.BTN_VER_INFO_IN_ROW)

        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
        except Exception:
            pass

        try:
            btn.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", btn)

        WebDriverWait(self.driver, 20).until(EC.url_contains(self.DEST_URL_FRAGMENT_CONTRATO))

        # Pequeño yield
        try:
            WebDriverWait(self.driver, 8).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        except Exception:
            pass

        if evidencia:
            evidencia(f"generar_contratos_click_contrato__{code}")

class GenerarContratosDetallePage:
    # ---- Anclas de la vista de detalle ----
    HEADER_DOCENTES = (
        By.XPATH,
        "//*[contains(@class,'ant-page-header') or contains(@class,'ant-typography')]"
        "//*[normalize-space()='Docentes requeridos en la solicitud']"
    )
    TABLA = (By.XPATH, "//div[contains(@class,'ant-table')]//table")

    # ---- Botón "Contrato" en fila por nombre (y fallback al primero) ----
    BTN_CONTRATO_BY_NAME = lambda self, nombre: (
        By.XPATH,
        f"//table//tr[.//td[normalize-space()='{nombre}']]//button[.//span[normalize-space()='Contrato']]"
    )
    BTN_CONTRATO_FIRST = (By.XPATH, "//table//tr//button[.//span[normalize-space()='Contrato']]")

    # ---- Marcar como finalizada ----
    BTN_MARCAR_FINALIZADA = (
        By.XPATH,
        "//button[.//span[normalize-space()='Marcar como finalizada']]"
    )
    MODAL_VISIBLE = (
        By.XPATH,
        "//div[contains(@class,'ant-modal') and not(contains(@class,'ant-modal-hidden'))]"
    )
    MODAL_CONFIRM = (
        By.XPATH,
        "//div[contains(@class,'ant-modal')]//button[.//span[normalize-space()='Confirmar'] or .//span[normalize-space()='Aceptar']]"
    )
    TOAST_FINALIZADO_OK = (
        By.XPATH,
        "//div[contains(@class,'ant-message') and (contains(.,'finalizado con éxito') or contains(.,'Finalizado con éxito') or contains(.,'finalizada con éxito'))]"
    )

    # ---- Navegación a “Solicitudes finalizadas” (tolerante) ----
    # Cubrimos tanto un menú directo a “Solicitudes finalizadas” como el módulo “Solicitudes y acuerdos”
    LINK_SOL_FINALIZADAS = (
        By.XPATH,
        "//a[contains(@href,'solicitudes-finalizadas') or contains(@href,'solicitudes-y-acuerdos')]["
        " contains(normalize-space(.),'Solicitudes finalizadas')"
        " or contains(normalize-space(.),'Solicitudes y acuerdos')"
        "]"
    )

    # ---- Spinners / espera ----
    SPINNER = (By.CSS_SELECTOR, ".ant-spin-spinning")

    # (opcional) tabla en el destino de finalizadas
    LIST_ANY_TABLE = (By.XPATH, "//div[contains(@class,'ant-table') and .//table]")

    def __init__(self, driver, timeout=15):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    # ---------- helpers ----------
    def _wait_spinner_out(self, extra_seconds: int = 0):
        try:
            WebDriverWait(self.driver, 10 + max(0, extra_seconds)).until(
                EC.invisibility_of_element_located(self.SPINNER)
            )
        except TimeoutException:
            # si no desaparece, seguimos (no bloqueamos la prueba)
            pass

    # ---------- carga de la vista ----------
    def wait_loaded(self, evidencia=None):
        # Encabezado o tabla visible
        try:
            self.wait.until(EC.visibility_of_element_located(self.HEADER_DOCENTES))
        except TimeoutException:
            pass
        self.wait.until(EC.presence_of_element_located(self.TABLA))
        if evidencia:
            evidencia("gc_detalle__docentes_visible")

    # ---------- abrir contrato por nombre ----------
    def click_contrato_by_name(self, nombre, evidencia=None):
        try:
            btn = self.wait.until(EC.element_to_be_clickable(self.BTN_CONTRATO_BY_NAME(nombre)))
        except Exception:
            btn = self.wait.until(EC.element_to_be_clickable(self.BTN_CONTRATO_FIRST))
        try:
            btn.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", btn)
        if evidencia:
            evidencia(f"gc_detalle__click_contrato__{nombre or 'first'}")

    # ---------- marcar como finalizada ----------
    def marcar_como_finalizada(self, evidencia=None):
        self.wait_loaded()
        btn = self.wait.until(EC.element_to_be_clickable(self.BTN_MARCAR_FINALIZADA))
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
        except Exception:
            pass
        try:
            btn.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", btn)

        # Modal visible
        self.wait.until(EC.visibility_of_element_located(self.MODAL_VISIBLE))
        if evidencia:
            evidencia("gc_detalle__modal_finalizar_visible")

        # Confirmar
        conf = self.wait.until(EC.element_to_be_clickable(self.MODAL_CONFIRM))
        try:
            conf.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", conf)

        # Toast finalizado + pequeño respiro
        self.wait.until(EC.presence_of_element_located(self.TOAST_FINALIZADO_OK))
        if evidencia:
            evidencia("gc_detalle__finalizado_ok_toast")

    # ---------- ir a “Solicitudes finalizadas” ----------
    def ir_a_solicitudes_finalizadas(self, evidencia=None):
        link = self.wait.until(EC.element_to_be_clickable(self.LINK_SOL_FINALIZADAS))
        try:
            link.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", link)

        # Espera de redibujo básico
        self._wait_spinner_out()
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(self.LIST_ANY_TABLE)
            )
        except TimeoutException:
            # no todas las vistas tienen tabla inmediata; no bloqueamos
            pass

        if evidencia:
            evidencia("gc_detalle__go_solicitudes_finalizadas")