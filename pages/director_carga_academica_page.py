from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class DirectorCargaAcademicaPage:
    # Botón principal "Generar nueva carga académica"
    BTN_GENERAR_CARGA = (
        By.XPATH,
        "//button[span[normalize-space()='Generar nueva carga académica']]"
    )

    # Botón Aceptar del modal de confirmación
    # ¿Generar carga académica para el ciclo en curso?
    CONFIRM_BTN_ACEPTAR = (
        By.XPATH,
        "//div[contains(@class,'ant-modal') "
        "  and .//*[contains(normalize-space(), 'Generar carga académica para el ciclo en curso')]]"
        "//button[span[normalize-space()='Aceptar']]"
    )

    # Modal de ERROR por carga duplicada (buscamos el texto largo del mensaje)
    ERROR_MODAL = (
        By.XPATH,
        "//div[contains(@class,'ant-modal') "
        "  and .//div[contains(@class,'ant-modal-confirm-content') "
        "           and contains(normalize-space(),"
        "               'No se puede Registrar carga academica de esta escuela ya que esta ya posee una creada')]]"
    )

    SEARCH_INPUT = (By.CSS_SELECTOR, "input[placeholder='Buscar por nombre']")
    SEARCH_BUTTON = (By.CSS_SELECTOR, ".ant-input-search-button")
    TABLE_WRAPPER = (By.CSS_SELECTOR, ".ant-table-wrapper.al-table")
    TABLE_ROWS = (
        By.CSS_SELECTOR,
        ".ant-table-wrapper.al-table tbody.ant-table-tbody tr.ant-table-row"
    )

    # Botón Aceptar de ese mismo modal de error
    ERROR_BTN_ACEPTAR = (
        By.XPATH,
        "//div[contains(@class,'ant-modal') "
        "  and .//div[contains(@class,'ant-modal-confirm-content') "
        "           and contains(normalize-space(),"
        "               'No se puede Registrar carga academica de esta escuela ya que esta ya posee una creada')]]"
        "//button[span[normalize-space()='Aceptar']]"
    )

    # Estado "No hay datos"
    EMPTY_PLACEHOLDER = (
        By.CSS_SELECTOR,
        ".ant-table-wrapper.al-table .ant-table-placeholder .ant-empty-description"
    )

    def __init__(self, driver, timeout: int = 15):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def is_on_page(self) -> bool:
        """
        Validación ligera: sólo revisamos la URL.
        Evita flakiness por renders lentos del header.
        """
        return "/carga-academica" in self.driver.current_url
    
    # =============== LISTADO ===============

    def wait_list_loaded(self):
        """Espera a que se vea el buscador y que la tabla tenga al menos una fila."""
        self.wait.until(EC.visibility_of_element_located(self.SEARCH_INPUT))
        self.wait.until(EC.visibility_of_element_located(self.TABLE_WRAPPER))

        def _rows_present(drv):
            rows = drv.find_elements(*self.TABLE_ROWS)
            return len(rows) > 0

        self.wait.until(_rows_present)

    def count_cargas(self) -> int:
        """Devuelve cuántas filas de carga académica hay en la tabla."""
        rows = self.driver.find_elements(*self.TABLE_ROWS)
        return len(rows)

    def get_rows_text(self):
        """Devuelve el texto de cada fila (por si quieres asserts más específicos)."""
        rows = self.driver.find_elements(*self.TABLE_ROWS)
        return [r.text for r in rows]
    
     # =============== BÚSQUEDA ===============

    def _do_search(self, text: str):
        """Escribe en la barra de búsqueda y hace clic en la lupa."""
        box = self.wait.until(EC.element_to_be_clickable(self.SEARCH_INPUT))
        box.click()
        box.clear()
        box.send_keys(text)

        btn = self.driver.find_element(*self.SEARCH_BUTTON)
        self.driver.execute_script("arguments[0].click();", btn)

    def search_carga(self, text: str):
        """
        Lanza la búsqueda pero NO asume si habrá resultados o no.
        El caller se encarga de esperar filas o 'No hay datos'.
        """
        self._do_search(text)

    def wait_row_with_text(self, text: str, timeout: int = 15) -> bool:
        """Espera a que aparezca al menos una fila que contenga `text`."""
        def _row_with_text(drv):
            rows = drv.find_elements(*self.TABLE_ROWS)
            if not rows:
                return False
            for r in rows:
                if text.lower() in r.text.lower():
                    return True
            return False

        try:
            WebDriverWait(self.driver, timeout).until(_row_with_text)
            return True
        except TimeoutException:
            return False

    def wait_no_data_message(self, timeout: int = 15) -> bool:
        """
        Espera el placeholder de tabla vacía y valida que el texto contenga
        'No hay datos' o 'No data'.
        """
        try:
            el = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(self.EMPTY_PLACEHOLDER)
            )
            text = el.text.strip().lower()
            return "no hay datos" in text or "no data" in text
        except TimeoutException:
            return False
    
    # =============== CREACIÓN / ERRORES ===============

    def click_generar_nueva_carga(self):
        btn = self.wait.until(EC.element_to_be_clickable(self.BTN_GENERAR_CARGA))
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", btn
        )
        self.driver.execute_script("arguments[0].click();", btn)

    def confirmar_generar_carga(self):
        """
        Hace clic en Aceptar del modal de confirmación.
        """
        btn_ok = self.wait.until(
            EC.element_to_be_clickable(self.CONFIRM_BTN_ACEPTAR)
        )
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", btn_ok
        )
        self.driver.execute_script("arguments[0].click();", btn_ok)

    def esperar_error_carga_ya_existente(self, timeout: int = 15) -> bool:
        """
        Espera a que aparezca el modal de error por carga duplicada.
        Devuelve True si aparece, False si no.
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(self.ERROR_MODAL)
            )
            return True
        except TimeoutException:
            print("[DEBUG] No apareció el modal de Error de carga académica duplicada.")
            return False

    def cerrar_modal_error(self):
        """
        Clic en Aceptar del modal de error, si está visible.
        """
        try:
            btn = self.wait.until(
                EC.element_to_be_clickable(self.ERROR_BTN_ACEPTAR)
            )
            self.driver.execute_script("arguments[0].click();", btn)
        except TimeoutException:
            print("[DEBUG] No se pudo hacer clic en 'Aceptar' del modal de Error.")
