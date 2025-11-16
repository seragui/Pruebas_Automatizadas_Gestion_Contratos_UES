from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys

class RRHHHomePage:
    HEADER_ROLE = (By.XPATH, "//header//span[contains(.,'Sesión iniciada como') "
                             "and (contains(.,'RRHH') or contains(.,'Recursos Humanos'))]")
    MENU_VALIDACION = (By.XPATH, "//aside//a[@href='/solicitudes' or normalize-space()='Validación de solicitudes']")

    # === NUEVO: menú y señales de la vista "Generar contratos" ===
    MENU_GENERAR = (By.XPATH, "//aside//a[@href='/generar-contratos' or normalize-space()='Generar contratos']")
    TITLE_GENERAR = (By.XPATH, "//*[contains(@class,'ant-page-header') or contains(@class,'ant-typography')]"
                               "//*[normalize-space()='Generar contratos']")
    TABLE_GENERAR = (By.XPATH, "//div[contains(@class,'ant-table') and .//table]")

    def __init__(self, driver, base_url, timeout=20):
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.wait = WebDriverWait(driver, timeout)

    def wait_loaded(self):
        self.wait.until(EC.visibility_of_element_located(self.HEADER_ROLE))

    def go_to_validacion(self, evidencia=None):
        link = self.wait.until(EC.element_to_be_clickable(self.MENU_VALIDACION))
        # Scroll por robustez (sider fijo a veces requiere bring-into-view)
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", link)
        except Exception:
            pass
        if evidencia:
            evidencia("menu_validacion_visible")
        try:
            link.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", link)
        if evidencia:
            evidencia("menu_validacion_click")

        # Confirma navegación
        self.wait.until(EC.url_contains("/solicitudes"))
    
    # === NUEVO: ir a "Generar contratos" ===
    def go_to_generar_contratos(self, evidencia=None):
        """
        Abre el módulo 'Generar contratos'. Si ya estás allí, sólo valida que la vista esté lista.
        """
        if "/generar-contratos" not in self.driver.current_url:
            try:
                link = self.wait.until(EC.element_to_be_clickable(self.MENU_GENERAR))
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", link)
                except Exception:
                    pass
                if evidencia:
                    evidencia("menu_generar_contratos_visible")
                try:
                    link.click()
                except Exception:
                    self.driver.execute_script("arguments[0].click();", link)
                if evidencia:
                    evidencia("menu_generar_contratos_click")
            except Exception:
                # Fallback por URL (por si el menú no responde)
                self.driver.get(self.base_url + "/generar-contratos")

        # Confirmar la carga de la vista
        self.wait.until(EC.url_contains("/generar-contratos"))
        self.wait.until(EC.visibility_of_element_located(self.TITLE_GENERAR))
        self.wait.until(EC.presence_of_element_located(self.TABLE_GENERAR))
        if evidencia:
            evidencia("generar_contratos_vista_lista")

class ValidacionSolicitudesPage:
    # Encabezado/página
    TITLE = (By.XPATH, "//*[contains(@class,'ant-page-header') and .//*[contains(.,'Solicitudes de contratación')]]")
    TABLE = (By.XPATH, "//div[contains(@class,'ant-table') and .//table]")
    ROW_BY_CODE = lambda self, code: (By.XPATH, f"//table//tbody/tr[.//td[normalize-space()='{code}']]")
    BTN_VER_EN_ROW = (By.XPATH, ".//button[.//span[normalize-space()='Ver solicitud']]")

    # (Opcional) posibles buscadores
    SEARCH_INPUTS = [
        (By.XPATH, "//input[@type='search']"),
        (By.XPATH, "//input[contains(@placeholder,'Buscar') or contains(@placeholder,'Código')]"),
        (By.CSS_SELECTOR, "input[placeholder*='Buscar'], input[placeholder*='Código']")
    ]

    # Paginación (AntD)
    PAGINATION_NEXT = (By.XPATH, "//ul[contains(@class,'ant-pagination')]//li[contains(@class,'ant-pagination-next') and not(contains(@class,'disabled'))]")

    def __init__(self, driver, timeout=20):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def wait_loaded(self):
        # Carga básica: título o al menos la tabla
        try:
            self.wait.until(EC.presence_of_element_located(self.TITLE))
        except TimeoutException:
            pass
        self.wait.until(EC.presence_of_element_located(self.TABLE))

    def _try_search_code(self, code):
        # Intenta escribir en un input de búsqueda si existe
        for locator in self.SEARCH_INPUTS:
            try:
                ipt = self.driver.find_element(*locator)
                ipt.clear()
                ipt.send_keys(code)
                ipt.send_keys(Keys.ENTER)
                return True
            except NoSuchElementException:
                continue
            except Exception:
                continue
        return False

    def _find_row_on_current_page(self, code, timeout=5):
        w = WebDriverWait(self.driver, timeout)
        try:
            return w.until(EC.presence_of_element_located(self.ROW_BY_CODE(code)))
        except TimeoutException:
            return None

    def ensure_row_visible(self, code, evidencia=None):
        # 1) Intenta con buscador (si hay)
        used_search = self._try_search_code(code)

        # 2) Busca en la página actual
        row = self._find_row_on_current_page(code)
        if row and evidencia:
            evidencia(f"rrhh_row_encontrada__{code}")
            return row

        # 3) Si no hay buscador o no lo encontró, paginar (AntD)
        #    Recorre páginas hasta encontrar el código o agotar "Siguiente"
        seen_pages = 0
        while True:
            row = self._find_row_on_current_page(code)
            if row:
                if evidencia:
                    evidencia(f"rrhh_row_encontrada__{code}")
                return row

            # ¿Hay siguiente?
            try:
                next_btn = self.driver.find_element(*self.PAGINATION_NEXT)
            except NoSuchElementException:
                break

            try:
                self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", next_btn)
            except Exception:
                pass
            next_btn.click()
            seen_pages += 1
            if evidencia:
                evidencia(f"rrhh_paginacion_click_{seen_pages}")

        # Si se usó buscador pero no apareció de una, reintenta una vez esperando la tabla refrescada
        if used_search:
            row = self._find_row_on_current_page(code, timeout=8)
            if row:
                if evidencia:
                    evidencia(f"rrhh_row_encontrada__{code}")
                return row

        raise AssertionError(f"No se encontró la solicitud con código {code}.")

    def click_ver_solicitud(self, code, evidencia=None):
        row = self.ensure_row_visible(code, evidencia=evidencia)
        btn = row.find_element(*self.BTN_VER_EN_ROW)
        try:
            btn.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", btn)
        if evidencia:
            evidencia(f"rrhh_click_ver_solicitud__{code}")

        # Confirma navegación a /solicitudes/validacion/:id
        self.wait.until(EC.url_contains("/solicitudes/validacion/"))

class SolicitudDetallePage:
    # Título de la vista
    TITLE = (By.XPATH, "//*[contains(@class,'ant-page-header') and .//*[normalize-space()='Validaciones de la solicitud']]")

    # Radios (Ant Design - radio button group)
    RADIO_VALIDAR_SIN_OBS = (
        By.XPATH,
        "//label[contains(@class,'ant-radio-button-wrapper')][.//span[normalize-space()='Validar sin observaciones']]"
    )
    RADIO_DEVOLVER = (
        By.XPATH,
        "//label[contains(@class,'ant-radio-button-wrapper')][.//span[normalize-space()='Devolver con observaciones']]"
    )

    # Botón Guardar
    BTN_GUARDAR = (By.XPATH, "//button[.//span[normalize-space()='Guardar']]")

    # Modal de confirmación (texto tiene un typo, usamos contains)
    # Modal visible (AntD) – evita depender del texto
    MODAL = (
        By.XPATH,
        "//div[contains(@class,'ant-modal') and not(contains(@style,'display: none'))]")

    # Botón Confirmar dentro del modal visible (el último/visible)
    MODAL_CONFIRMAR = (
        By.XPATH,
        "//div[contains(@class,'ant-modal') and not(contains(@style,'display: none'))]"
        "//button[.//span[normalize-space()='Confirmar']]")


    # Éxito: Ant message / URL de retorno
    ANY_TOAST = (By.CSS_SELECTOR, ".ant-message .ant-message-notice")
    SUCCESS_TOAST = (By.XPATH, "//div[contains(@class,'ant-message')]//span[contains(.,'validada') or contains(.,'exito') or contains(.,'éxito') or contains(.,'guardó')]")

    def __init__(self, driver, timeout=20):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def wait_loaded(self):
        self.wait.until(EC.presence_of_element_located(self.TITLE))
        # También esperamos que el grupo de radios exista
        self.wait.until(EC.presence_of_element_located(self.RADIO_VALIDAR_SIN_OBS))

    def seleccionar_validar_sin_observaciones(self, evidencia=None):
        radio = self.wait.until(EC.element_to_be_clickable(self.RADIO_VALIDAR_SIN_OBS))
        try:
            radio.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", radio)
        if evidencia:
            evidencia("rrhh_detalle_radio_validar_sin_obs")

    def guardar(self, evidencia=None):
        btn = self.wait.until(EC.element_to_be_clickable(self.BTN_GUARDAR))
        try:
            btn.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", btn)
        if evidencia:
            evidencia("rrhh_detalle_click_guardar")

        # Esperar a que aparezca un modal visible (sin depender del texto)
        modal = self.wait.until(EC.visibility_of_element_located(self.MODAL))
        if evidencia:
            evidencia("rrhh_detalle_modal_visible")

        # Confirmar
        confirmar = self.wait.until(EC.element_to_be_clickable(self.MODAL_CONFIRMAR))
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", confirmar)
        except Exception:
            pass
        try:
            confirmar.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", confirmar)
        if evidencia:
            evidencia("rrhh_detalle_modal_confirmar")


    def esperar_exito(self, evidencia=None):
        # Opción A: esperar toast de éxito
        try:
            self.wait.until(EC.visibility_of_element_located(self.ANY_TOAST))
            # si podemos, afinamos al de éxito
            try:
                self.wait.until(EC.visibility_of_element_located(self.SUCCESS_TOAST))
            except TimeoutException:
                pass
            if evidencia:
                evidencia("rrhh_detalle_toast_exito")
            return
        except TimeoutException:
            pass

        # Opción B: esperar redirección/URL de listado o finalizadas
        try:
            self.wait.until(
                lambda d: ("/solicitudes" in d.current_url) or ("/solicitudes-finalizadas" in d.current_url)
            )
            if evidencia:
                evidencia("rrhh_detalle_redirect_exito")
        except TimeoutException:
            # Si nada de lo anterior ocurrió, fallamos con contexto
            raise AssertionError("No se detectó confirmación de éxito (toast ni redirección).")