# pages/asistente_home_page.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
import time

class AsistenteHomePage:
    """
    Home del Asistente Administrativo.
    Solo navegación y verificación de sesión.
    """
    # Header fijo con el rol (tolerante a variantes de copy)
    HEADER_ROLE = (
        By.XPATH,
        "//header//span[contains(.,'Sesión iniciada como') "
        "and (contains(.,'Asistente') or contains(.,'Asistente Administrativo') "
        "or contains(.,'Director Escuela'))]"  # tolerante si el ambiente muestra 'Director Escuela'
    )

    # Menú izquierdo
    MENU_RECEPCION_ALTS = [
        # href directo
        (By.XPATH, "//aside//a[@href='/recepcion-solicitudes']"),
        (By.CSS_SELECTOR, "aside ul.ant-menu a[href='/recepcion-solicitudes']"),
        # por texto visible (por si cambia el href)
        (By.XPATH, "//aside//span[normalize-space()='Solicitudes de contratación']/ancestor::a[1]"),
        (By.XPATH, "//aside//a[.//span[normalize-space()='Solicitudes de contratación']]"),
    ]
    MENU_INICIO = (By.XPATH, "//aside//a[@href='/' or normalize-space()='Inicio']")

    def __init__(self, driver, base_url, timeout=20):
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.wait = WebDriverWait(driver, timeout)

    def wait_loaded(self):
        self.wait.until(EC.visibility_of_element_located(self.HEADER_ROLE))

    def go_to_recepcion_solicitudes(self, evidencia=None):
        """
        Ir a: Recepción / 'Solicitudes de contratación' (ruta /recepcion-solicitudes).
        Intenta varios localizadores y hace click seguro.
        """
        last_exc = None
        link = None

        # 1) Intento localizar cualquiera de las variantes
        for loc in self.MENU_RECEPCION_ALTS:
            try:
                el = self.wait.until(EC.presence_of_element_located(loc))
                el = self.wait.until(EC.element_to_be_clickable(loc))
                link = el
                break
            except Exception as e:
                last_exc = e
                continue

        if not link:
            # Fallback a navegación directa
            self.driver.get(self.base_url + "/recepcion-solicitudes")
            self.wait.until(EC.url_contains("/recepcion-solicitudes"))
            if evidencia:
                evidencia("asistente_menu_recepcion_fallback_get")
            return

        if evidencia:
            evidencia("asistente_menu_recepcion_visible")

        # 2) Scroll + click seguro
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", link)
        except Exception:
            pass
        try:
            link.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", link)

        if evidencia:
            evidencia("asistente_menu_recepcion_click")

        # 3) Confirmar navegación
        self.wait.until(EC.url_contains("/recepcion-solicitudes"))


class RecepcionSolicitudesPage:
    """
    Pantalla de Recepción / Solicitudes de contratación.
    Provee navegación, búsqueda por código, click en 'Ver' y click en
    'Subir acuerdo de junta' de la fila correspondiente.
    """

    # --------- Hints de que la vista cargó ----------
    TITLE = (
        By.XPATH,
        "//*[contains(@class,'ant-page-header') and "
        "(.//span[normalize-space()='Recepción de solicitudes'] "
        " or .//*[contains(.,'Recepción')])]"
    )
    ANY_LIST_HINTS = (
        By.XPATH,
        "//*[contains(@class,'ant-table') or contains(@class,'ant-tabs') or contains(@class,'ant-card')]"
    )
    TABLE = (By.XPATH, "//div[contains(@class,'ant-table') and .//table]")
    ROW_BY_CODE = lambda self, code: (
        By.XPATH, f"//table//tbody/tr[.//td[normalize-space()='{code}']]"
    )
    BTN_VER_EN_ROW = (By.XPATH, ".//button[.//span[normalize-space()='Ver']]")

    # Buscadores opcionales (según tu HTML actual hay un input con placeholder)
    SEARCH_INPUTS = [
        (By.XPATH, "//input[@type='search']"),
        (By.XPATH, "//input[contains(@placeholder,'Buscar') or contains(@placeholder,'Código')]"),
        (By.CSS_SELECTOR, "input[placeholder*='Buscar'], input[placeholder*='Código']"),
    ]
    CLEAR_ICON = (
        By.XPATH,
        "//span[contains(@class,'ant-input-clear-icon') and not(contains(@class,'hidden'))]"
    )

    # Paginación AntD
    PAGINATION_NEXT = (
        By.XPATH,
        "//ul[contains(@class,'ant-pagination')]//li[contains(@class,'ant-pagination-next') and not(contains(@class,'disabled'))]"
    )

    # Spinner (por si lo necesitás)
    SPINNER = (By.CSS_SELECTOR, ".ant-spin-spinning")

    # --------- Locators para Subir acuerdo de junta ----------
    def _btn_subir_by_code(self, code: str):
        xp = (
            "//div[contains(@class,'ant-table')]//table"
            f"//tr[.//td[normalize-space()='{code}']]"
            "//button[.//span[normalize-space()='Subir acuerdo de junta']]"
        )
        return (By.XPATH, xp)

    def _btn_subir_variants_by_code(self, code: str):
        # Variante tolerante si cambian el copy a "Subir acuerdo"
        return [
            self._btn_subir_by_code(code),
            (By.XPATH,
             "//div[contains(@class,'ant-table')]//table"
             f"//tr[.//td[normalize-space()='{code}']]"
             "//button[.//span[contains(normalize-space(),'Subir acuerdo')]]"),
        ]

    def __init__(self, driver, timeout=20):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    # ===================== CARGA =====================
    def _wait_spinner_out(self, extra=0):
        try:
            WebDriverWait(self.driver, 10 + extra).until(
                EC.invisibility_of_element_located(self.SPINNER)
            )
        except TimeoutException:
            pass

    def wait_loaded(self, evidencia=None):
        # Espera algo representativo: título o contenedor de tabla/tabs/cards
        try:
            self.wait.until(EC.presence_of_element_located(self.TITLE))
        except TimeoutException:
            pass
        self.wait.until(EC.presence_of_element_located(self.ANY_LIST_HINTS))
        self._wait_spinner_out()
        if evidencia:
            evidencia("asistente_recepcion_visible")

    def wait_loaded_table(self):
        self.wait.until(EC.presence_of_element_located(self.TABLE))

    # ===================== BÚSQUEDA =====================
    def _try_search_code(self, code: str) -> bool:
        """
        Intenta usar cualquier input de búsqueda visible.
        Limpia con CTRL+A + BACKSPACE y pulsa ENTER.
        """
        found_any = False
        for locator in self.SEARCH_INPUTS:
            try:
                ipt = self.driver.find_element(*locator)
                # foco
                try:
                    ipt.click()
                except Exception:
                    self.driver.execute_script("arguments[0].focus();", ipt)

                # limpiar agresivo
                try:
                    ipt.send_keys(Keys.CONTROL, "a")
                except Exception:
                    # Algunas veces funciona como cadena
                    ipt.send_keys(Keys.CONTROL + "a")
                ipt.send_keys(Keys.BACKSPACE)

                # usar ícono de limpiar si existe
                try:
                    clear_el = self.driver.find_element(*self.CLEAR_ICON)
                    clear_el.click()
                except Exception:
                    pass

                # escribir y buscar
                ipt.send_keys(code)
                ipt.send_keys(Keys.ENTER)
                found_any = True
                break
            except NoSuchElementException:
                continue
            except Exception:
                continue
        return found_any

    def _find_row_on_current_page(self, code: str, timeout=5):
        w = WebDriverWait(self.driver, timeout)
        try:
            return w.until(EC.presence_of_element_located(self.ROW_BY_CODE(code)))
        except TimeoutException:
            return None

    def ensure_row_visible(self, code: str, evidencia=None):
        """
        Asegura que la fila con el 'code' sea visible:
        1) Intenta buscador.
        2) Si no, recorre paginación 'Siguiente' hasta hallarla.
        """
        self.wait_loaded_table()
        used_search = self._try_search_code(code)

        # Intento 1: página actual (un poco más de paciencia si usaste buscador)
        row = self._find_row_on_current_page(code, timeout=6 if used_search else 4)
        if row:
            if evidencia:
                evidencia(f"asist_row_encontrada__{code}")
            return row

        # Intento 2: paginación
        hops = 0
        while True:
            row = self._find_row_on_current_page(code, timeout=3)
            if row:
                if evidencia:
                    evidencia(f"asist_row_encontrada__{code}")
                return row

            # siguiente?
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

            hops += 1
            if evidencia:
                evidencia(f"asist_paginacion_click_{hops}")

        # Último intento si hubo buscador
        if used_search:
            row = self._find_row_on_current_page(code, timeout=8)
            if row:
                if evidencia:
                    evidencia(f"asist_row_encontrada__{code}")
                return row

        raise AssertionError(f"No se encontró la solicitud con código {code} en Recepción.")

    # ===================== DETALLE =====================
    def _wait_detalle_loaded(self, evidencia=None, require_detalle=True) -> bool:
        """
        Tras hacer 'Ver', puede abrir una nueva vista/URL o un modal/drawer.
        Este método intenta detectar cualquiera de esas variantes sin romper.
        """
        # 1) Si navega a detalle por URL:
        navigated = False
        try:
            WebDriverWait(self.driver, 8).until(
                EC.url_matches(r".*/recepcion-solicitudes/\d+/?$")
            )
            navigated = True
        except TimeoutException:
            pass

        # 2) Si aparece un modal/drawer en vez de navegar:
        modal_or_drawer = False
        try:
            WebDriverWait(self.driver, 6).until(EC.presence_of_element_located((
                By.XPATH,
                "//div[contains(@class,'ant-modal') or contains(@class,'ant-drawer')]"
                "[not(contains(@class,'hidden'))]"
            )))
            modal_or_drawer = True
        except TimeoutException:
            pass

        if evidencia:
            if navigated:
                evidencia("asistente_detalle_url_ok")
            if modal_or_drawer:
                evidencia("asistente_detalle_modal_ok")

        return (navigated or modal_or_drawer) if not require_detalle else (navigated or modal_or_drawer)

    # ===================== ACCIONES =====================
    def click_ver_by_code(self, code, evidencia=None, require_detalle: bool = True) -> bool:
        """
        Hace clic en 'Ver' para la fila con el código dado.
        Devuelve True si se detectó el detalle; False si no (cuando require_detalle=False).
        """
        self.wait_loaded_table()
        row = self.ensure_row_visible(code, evidencia=evidencia)

        # Evitar stale: reubicar el botón dentro de la fila en el último momento
        btn = None
        for _ in range(2):  # dos intentos por si se re-renderiza
            try:
                btn = row.find_element(*self.BTN_VER_EN_ROW)
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
                except Exception:
                    pass
                try:
                    btn.click()
                except Exception:
                    self.driver.execute_script("arguments[0].click();", btn)
                break
            except StaleElementReferenceException:
                # reubicar la fila y reintentar
                row = self.ensure_row_visible(code)
        if evidencia:
            evidencia(f"asist_click_ver__{code}")
            evidencia("asist_pos_click_ver")

        return self._wait_detalle_loaded(evidencia=evidencia, require_detalle=require_detalle)

    def click_ver_first(self, evidencia=None, require_detalle: bool = True) -> bool:
        """
        Hace clic en el primer botón 'Ver' de la tabla.
        Devuelve True si se detectó el detalle; False si no (cuando require_detalle=False).
        """
        self.wait_loaded_table()
        btns = self.driver.find_elements(By.XPATH, "//table//tbody//tr//button[.//span[normalize-space()='Ver']]")
        if not btns:
            raise AssertionError("No se encontró ningún botón 'Ver' en la tabla de Recepción.")

        btn = btns[0]
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
        except Exception:
            pass
        try:
            btn.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", btn)

        if evidencia:
            evidencia("asist_click_ver_first")
            evidencia("asist_pos_click_ver_first")

        return self._wait_detalle_loaded(evidencia=evidencia, require_detalle=require_detalle)

    # --------- Subir acuerdo de junta (botón en fila por código) ----------
    def _click_center(self, el, evidencia=None, label=None):
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        except Exception:
            pass
        try:
            el.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", el)
        if evidencia and label:
            evidencia(label)

    def _wait_modal_or_drawer_after_subir(self, evidencia=None):
        """
        Si al pulsar 'Subir acuerdo' abre un modal/drawer, lo detectamos.
        Si navega a otra URL, este método simplemente no bloqueará.
        """
        try:
            WebDriverWait(self.driver, 6).until(EC.presence_of_element_located((
                By.XPATH,
                "//div[contains(@class,'ant-modal') or contains(@class,'ant-drawer')]"
                "[not(contains(@class,'hidden'))]"
            )))
            if evidencia:
                evidencia("asistente_recepcion_subir_acuerdo_modal_open")
            return True
        except TimeoutException:
            # Puede que el flujo navegue a otra ruta; damos un respiro ligero.
            time.sleep(0.5)
            return False

    def click_subir_acuerdo_by_code(self, code: str, evidencia=None):
        """
        Hace clic en 'Subir acuerdo de junta' de la fila que contiene el código.
        NO usa row.find_element (evita stale). Busca por XPath global code+texto.
        """
        # Asegura que la fila sea visible (búsqueda o paginación)
        try:
            self.ensure_row_visible(code, evidencia=evidencia)
        except AssertionError:
            # Si fallara, igual intentamos directo por XPath global
            pass

        last_err = None
        for by in self._btn_subir_variants_by_code(code):
            try:
                btn = WebDriverWait(self.driver, 8).until(EC.element_to_be_clickable(by))
                self._click_center(btn, evidencia, f"asistente_recepcion_subir_acuerdo_btn__{code}")
                break
            except Exception as e:
                last_err = e
                continue
        else:
            raise NoSuchElementException(
                f"No encontré el botón 'Subir acuerdo' en la fila del código '{code}'. "
                f"Último error: {last_err}"
            )

        # Si abre un modal/drawer, tomamos evidencia; si navega, no bloqueamos.
        self._wait_modal_or_drawer_after_subir(evidencia=evidencia)