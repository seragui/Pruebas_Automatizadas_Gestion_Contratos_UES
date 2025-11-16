# pages/contracts_list_page.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import (
    StaleElementReferenceException,
    ElementClickInterceptedException,
    TimeoutException,
    NoSuchElementException,
)
import time

class ContractsListPage:
    # ====== Locators de la lista ======
    PAGE_TITLE = (By.XPATH, "//span[contains(@class,'ant-page-header-heading-title') and normalize-space()='Solicitudes de contratación']")

    NEW_REQUEST_BTN = (By.XPATH, "//button[.//span[normalize-space()='Generar nueva solicitud de contratación']]")
    NEW_REQUEST_FALLBACK = (By.XPATH, "//span[@class='ant-page-header-heading-extra']//button[.//span[@aria-label='plus']]")

    TABLE_HEADER = (By.XPATH, "//div[contains(@class,'ant-table-wrapper')]//thead")
    SEARCH_INPUT = (By.XPATH, "//span[contains(@class,'ant-input-search')]//input[@placeholder='Buscar por código o tipo de solicitud']")

    TABLE_WRAPPER   = (By.CSS_SELECTOR, ".ant-table")
    FECHA_HEADER    = (By.XPATH, "//div[contains(@class,'ant-table')]//th[.//span[normalize-space()='Fecha de creación']]")
    FIRST_CODE_CELL = (By.XPATH, "//div[contains(@class,'ant-table')]//tbody/tr[1]/td[1]")

    # Modal de éxito (robusto)
    SUCCESS_MODAL = (By.XPATH, "//div[contains(@class,'ant-modal-root') and .//div[contains(@class,'ant-modal-content')]]")
    MODAL_OK      = (By.XPATH, "//div[contains(@class,'ant-modal-content')]//button[.//span[normalize-space()='Aceptar']]")

    def __init__(self, driver, base_url: str, timeout: int = 15):
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.wait = WebDriverWait(driver, timeout)

    # Navegación / estado
    def open(self):
        self.driver.get(f"{self.base_url}/contratos")

    def wait_loaded(self):
        self.wait.until(EC.visibility_of_element_located(self.PAGE_TITLE))
        self.wait.until(
            EC.any_of(
                EC.visibility_of_element_located(self.TABLE_HEADER),
                EC.visibility_of_element_located(self.SEARCH_INPUT)
            )
        )

    def click_new_request(self):
        try:
            btn = self.wait.until(EC.element_to_be_clickable(self.NEW_REQUEST_BTN))
        except Exception:
            btn = self.wait.until(EC.element_to_be_clickable(self.NEW_REQUEST_FALLBACK))
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
        btn.click()

    def wait_navigated_to_creation(self, timeout: int = 15):
        """Espera URL de creación o wizard."""
        w = WebDriverWait(self.driver, timeout)
        def _is_create_url(drv):
            url = (drv.current_url or "").lower()
            return any(part in url for part in [
                "/contratos/nuevo", "/contratos/crear", "/contratos/nueva",
                "/contratos/solicitud/crear", "/contratos/solicitud/nuevo",
                "/contratos/solicitud/alta", "/contratos/wizard", "/contratos/crear-solicitud",
            ])
        try:
            w.until(_is_create_url)
            return True
        except Exception:
            return False

    # Modal de éxito
    def confirm_success_modal(self, timeout: int = 10):
        """Cierra el modal de éxito (‘Aceptar’) y espera a que desaparezca."""
        w = WebDriverWait(self.driver, timeout)
        w.until(EC.visibility_of_element_located(self.SUCCESS_MODAL))
        ok = w.until(EC.element_to_be_clickable(self.MODAL_OK))
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", ok)
        ok.click()
        w.until(EC.invisibility_of_element_located(self.SUCCESS_MODAL))

    # Tabla
    def _wait_table_ready(self, timeout: int = 10):
        self.wait.until(EC.presence_of_element_located(self.TABLE_WRAPPER))
        try:
            self.wait.until_not(EC.presence_of_element_located((By.CSS_SELECTOR, ".ant-spin-spinning")))
        except:
            pass

    def sort_by_fecha_desc(self):
        """Hace clic en el header ‘Fecha de creación’ hasta dejarlo en descendente."""
        self._wait_table_ready()
        hdr = self.wait.until(EC.element_to_be_clickable(self.FECHA_HEADER))
        for _ in range(3):
            aria = hdr.get_attribute("aria-sort")
            if aria == "descending":
                break
            hdr.click()
            time.sleep(0.3)
        self._wait_table_ready()

    def get_first_code(self) -> str:
        """Devuelve el texto del primer código en la tabla (ya ordenada)."""
        self._wait_table_ready()
        cell = self.wait.until(EC.presence_of_element_located(self.FIRST_CODE_CELL))
        return (cell.text or "").strip()

    def get_last_created_code(self, timeout: int = 10) -> str:
        """
        Re-entra a /contratos, espera, ordena desc por fecha y devuelve el código de la 1ª fila.
        """
        self.open()
        self.wait_loaded()
        self.sort_by_fecha_desc()
        cell = WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(self.FIRST_CODE_CELL)
        )
        return (cell.text or "").strip()
    
    # --- Buscador ---
    SEARCH_INPUT    = (By.XPATH, "//span[contains(@class,'ant-input-search')]//input[@placeholder='Buscar por código o tipo de solicitud']")
    SEARCH_BUTTON   = (By.CSS_SELECTOR, ".ant-input-search .ant-input-search-button")
    SEARCH_BUTTON_X = (By.XPATH, "//span[contains(@class,'ant-input-search')]//button[contains(@class,'ant-input-search-button')]")
    TABLE_SPINNER   = (By.CSS_SELECTOR, ".ant-spin-nested-loading .ant-spin-spinning")
    ROWS            = (By.XPATH, "//div[contains(@class,'ant-table')]//tbody/tr")

    def _dispatch_input_events(self, element, value: str):
        # fuerza que React/AntD detecte el cambio
        self.driver.execute_script("""
            const el = arguments[0], val = arguments[1];
            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
            nativeInputValueSetter.call(el, val);
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
        """, element, value)
    
    def _wait_table_idle(self, timeout: int = 10):
        self.wait.until(EC.presence_of_element_located(self.TABLE_WRAPPER))
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.invisibility_of_element_located(self.TABLE_SPINNER)
            )
        except Exception:
            pass
    def _first_code_equals(self, code: str) -> bool:
        try:
            first = self.driver.find_element(*self.FIRST_CODE_CELL)
            return first.text.strip() == code
        except Exception:
            return False

    def search_code(self, code: str, timeout: int = 10):
        inp = self.wait.until(EC.element_to_be_clickable(self.SEARCH_INPUT))
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", inp)
        inp.click()
        # limpiar fuerte
        inp.send_keys(Keys.CONTROL, "a")
        inp.send_keys(Keys.DELETE)

        # escribir y disparar eventos (para que React lo note)
        inp.send_keys(code)
        self._dispatch_input_events(inp, code)

        # intentar click al botón (3 estrategias)
        clicked = False
        for locator in (self.SEARCH_BUTTON, self.SEARCH_BUTTON_X):
            try:
                btn = WebDriverWait(self.driver, 3).until(EC.element_to_be_clickable(locator))
                try:
                    btn.click()
                except ElementClickInterceptedException:
                    self.driver.execute_script("arguments[0].click();", btn)
                clicked = True
                break
            except TimeoutException:
                continue

        if not clicked:
            # fallback final: ENTER
            inp.send_keys(Keys.ENTER)

        # esperar resultados: spinner + al menos 1 fila
        self._wait_table_idle(timeout)
        WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(self.ROWS))
    

    def _row_by_code_locator(self, code: str):
        # Más tolerante a espacios/caracteres invisibles
        return (
            By.XPATH,
            f"//div[contains(@class,'ant-table')]//tbody/tr[.//td[1][contains(normalize-space(), '{code}')]]"
    )
    
    def _row_exists(self, code: str, timeout: int = 6) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(self._row_by_code_locator(code))
            )
            return True
        except TimeoutException:
            return False

    def ensure_code_visible(self, code: str, timeout: int = 12):
        """
        Ejecuta search_code(code) y confirma que exista una fila con ese código.
        Reintenta con ENTER y click JS si la lupa no aplica la búsqueda.
        """
        self.search_code(code, timeout=timeout)
        if self._row_exists(code, timeout=timeout):
            return

        # Reintento: ENTER sobre el input
        try:
            inp = WebDriverWait(self.driver, 4).until(EC.element_to_be_clickable(self.SEARCH_INPUT))
            inp.click()
            inp.send_keys(Keys.ENTER)
        except Exception:
            pass

        # Click por JS a la lupa (si está)
        try:
            btn = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located(self.SEARCH_BUTTON)
            )
            self.driver.execute_script("arguments[0].click();", btn)
        except Exception:
            pass

        self._wait_table_idle(timeout)
        if not self._row_exists(code, timeout=timeout):
            time.sleep(0.5)
            if not self._row_exists(code, timeout=2):
                raise TimeoutException(f"No aparece la fila con código {code} tras buscar.")

    def wait_row_visible(self, code: str, timeout: int = 10):
        # Usa el helper robusto
        self.ensure_code_visible(code, timeout=timeout)

    def click_view_for_code(self, code: str):
        """
        Dentro de la fila del código, clic al botón 'Ver' (con fallback).
        """
        row = self.wait.until(EC.visibility_of_element_located(self._row_by_code_locator(code)))
        try:
            ver_btn = row.find_element(By.XPATH, ".//button[.//span[normalize-space()='Ver']]")
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", ver_btn)
            try:
                ver_btn.click()
            except ElementClickInterceptedException:
                self.driver.execute_script("arguments[0].click();", ver_btn)
        except NoSuchElementException:
            link = row.find_element(By.XPATH, ".//a[contains(@href, '/contratos/solicitud/')]")
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", link)
            self.driver.execute_script("arguments[0].click();", link)
            ver_btn.click()


class ContractCreateWizard:
    # ====== Step 1 ======
    STEP1_ACTIVE = (By.XPATH, "//div[contains(@class,'ant-steps-item-active')]//div[contains(@class,'ant-steps-item-title') and normalize-space()='Tipo de contratación']")
    CONTRACT_TYPE_GROUP = (By.ID, "contract_type_id")
    MODALITY_GROUP      = (By.ID, "modality")

    CONTRACT_TYPE_PRO_SERV = (By.XPATH, "//div[@id='contract_type_id']//label[.//span[normalize-space()='Contrato por Servicios Profesionales no Personales']]")
    MODALITY_PRESENCIAL    = (By.XPATH, "//div[@id='modality']//label[.//span[normalize-space()='Modalidad Presencial']]")

    NEXT_BTN = (By.XPATH, "//button[.//span[normalize-space()='Siguiente']]")

    # ====== Step 2 ======
    STEP2_TITLE   = (By.XPATH, "//div[contains(@class,'ant-steps-item-title') and normalize-space()='Cuerpo de solicitud']")
    STEP2_ACTIVE  = (By.XPATH, "//div[contains(@class,'ant-steps-item-active')]//div[contains(@class,'ant-steps-item-title') and normalize-space()='Cuerpo de solicitud']")
    RTE_EDITABLE  = (By.XPATH, "//div[contains(@class,'rdw-editor-main')]//div[@contenteditable='true']")
    PREV_BTN      = (By.XPATH, "//button[.//span[normalize-space()='Anterior']]")
    NEXT_BTN_STEP2 = (By.XPATH, "//button[.//span[normalize-space()='Siguiente']]")

    # ====== Step 3 ======
    STEP3_TITLE  = (By.XPATH, "//div[contains(@class,'ant-steps-item-title') and normalize-space()='Revisión']")
    REGISTER_BTN = (By.XPATH, "//button[.//span[normalize-space()='Registrar solicitud']]")

    def __init__(self, driver, timeout: int = 15):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    # Step 1
    def wait_step1_loaded(self):
        self.wait.until(EC.visibility_of_element_located(self.STEP1_ACTIVE))
        self.wait.until(EC.visibility_of_element_located(self.CONTRACT_TYPE_GROUP))
        self.wait.until(EC.visibility_of_element_located(self.MODALITY_GROUP))

    def select_type_and_modality(self):
        opt_type = self.wait.until(EC.element_to_be_clickable(self.CONTRACT_TYPE_PRO_SERV))
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", opt_type)
        opt_type.click()

        opt_mod = self.wait.until(EC.element_to_be_clickable(self.MODALITY_PRESENCIAL))
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", opt_mod)
        opt_mod.click()

    def click_next(self):
        btn = self.wait.until(EC.element_to_be_clickable(self.NEXT_BTN))
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
        btn.click()

    # Step 2
    def wait_step2_loaded(self, timeout: int = 15):
        WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(self.STEP2_TITLE))

    def wait_step2_active(self):
        self.wait.until(EC.visibility_of_element_located(self.STEP2_ACTIVE))
        self.wait.until(EC.visibility_of_element_located(self.RTE_EDITABLE))

    def fill_body(self, text: str):
        """
        Pega el cuerpo en el editor DraftJS de forma robusta, evitando stales.
        """
        for attempt in range(3):
            try:
                editable = self.wait.until(EC.element_to_be_clickable(self.RTE_EDITABLE))
                self.driver.execute_script("arguments[0].scrollIntoView({block:'center'}); arguments[0].focus();", editable)

                actions = ActionChains(self.driver)
                actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).send_keys(Keys.DELETE).perform()

                self.driver.execute_script("""
                    const el = arguments[0];
                    const value = arguments[1];
                    el.focus();
                    if (window.getSelection) {
                        const range = document.createRange();
                        range.selectNodeContents(el);
                        const sel = window.getSelection();
                        sel.removeAllRanges();
                        sel.addRange(range);
                    }
                    document.execCommand('insertText', false, value);
                """, editable, text)

                time.sleep(0.2)
                return
            except StaleElementReferenceException:
                if attempt == 2:
                    raise
                time.sleep(0.3)

    def click_next_step2(self):
        btn = self.wait.until(EC.element_to_be_clickable(self.NEXT_BTN_STEP2))
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
        btn.click()

    # Step 3
    def wait_step3_loaded(self, timeout: int = 15):
        WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(self.STEP3_TITLE))

    def click_register(self):
        btn = self.wait.until(EC.element_to_be_clickable(self.REGISTER_BTN))
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
        btn.click()
