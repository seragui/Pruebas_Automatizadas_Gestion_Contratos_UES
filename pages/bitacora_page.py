# pages/bitacora_page.py

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException


class BitacoraPage:
    """
    Page Object de la vista /bitacora
    """

    URL_PATH = "/bitacora"

    # Título de la página
    TITLE = (
        By.XPATH,
        "//span[contains(@class,'ant-page-header-heading-title') "
        "and normalize-space()='Bitácora']",
    )

    # Tabla principal de bitácora (Ant Design table)
    TABLE = (
        By.CSS_SELECTOR,
        "div.ant-table"
    )

    # Filas reales de la bitácora (ignorando la fila de medida)
    TABLE_BODY_ROWS = (
        By.XPATH,
        "//tbody[contains(@class,'ant-table-tbody')]/tr[@data-row-key]"
    )

    # Estado vacío de la tabla (cuando no hay registros)
    EMPTY_STATE = (
        By.CSS_SELECTOR,
        ".ant-empty-description"
    )

    # Select "Buscar por usuario" (el filtro de usuario de Ant Design)
    USER_SELECT = (
        By.XPATH,
        "//div[contains(@class,'ant-select') "
        "and .//span[contains(@class,'ant-select-selection-placeholder') "
        "and normalize-space()='Buscar por usuario']]"
    )

    # Input interno de búsqueda dentro del select
    USER_SEARCH_INPUT = (
        By.CSS_SELECTOR,
        "span.ant-select-selection-search input.ant-select-selection-search-input"
    )

    # Opciones del dropdown del select
    USER_OPTIONS = (
        By.CSS_SELECTOR,
        "div.ant-select-dropdown:not(.ant-select-dropdown-hidden) "
        ".ant-select-item-option"
    )

    DROPDOWN_EMPTY = (
        By.CSS_SELECTOR,
        "div.ant-select-dropdown:not(.ant-select-dropdown-hidden) "
        ".ant-empty-description"
    )

    # ------------------------------------------------------------------
    # Paginación (Ant Design)
    # ------------------------------------------------------------------
    PAGINATION_ITEMS = (
        By.CSS_SELECTOR,
        "ul.ant-pagination li.ant-pagination-item"
    )

    PAGINATION_ACTIVE_ITEM = (
        By.CSS_SELECTOR,
        "ul.ant-pagination li.ant-pagination-item-active"
    )

    PAGINATION_NEXT = (
        By.CSS_SELECTOR,
        "ul.ant-pagination li.ant-pagination-next"
    )


    def __init__(self, driver, timeout: int = 10):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    # ------------------------------------------------------------------
    # Navegación / carga
    # ------------------------------------------------------------------
    def open_direct(self, base_url: str):
        """Abre directamente /bitacora."""
        url = f"{base_url.rstrip('/')}{self.URL_PATH}"
        self.driver.get(url)

    def wait_loaded(self):
        """
        Espera a que la página de bitácora esté cargada:

        - Título 'Bitácora' visible
        - Y que haya filas ó el mensaje de 'No hay datos'
        """
        self.wait.until(EC.visibility_of_element_located(self.TITLE))

        def _tabla_lista(d):
            filas = d.find_elements(*self.TABLE_BODY_ROWS)
            empty = d.find_elements(*self.EMPTY_STATE)
            # debug opcional:
            # print(f"[DEBUG] wait_loaded -> filas={len(filas)}, empty={len(empty)}")
            return bool(filas) or bool(empty)

        self.wait.until(_tabla_lista)
    
    def is_empty_state_visible(self, timeout: int = 3) -> bool:
        """
        Devuelve True si se ve el estado vacío de la tabla
        (el texto tipo 'No hay datos'), False si no aparece
        dentro del timeout dado.
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(self.EMPTY_STATE)
            )
            return True
        except TimeoutException:
            return False
    
    def is_no_data(self) -> bool:
        """
        Devuelve True si la tabla de bitácora está vacía
        y se muestra el estado 'sin datos' (ant-empty).
        """
        # Aseguramos que la página ya cargó
        self.wait_loaded()

        # Si hay filas, NO es estado vacío
        if self.get_rows():
            return False

        # Buscar el estado vacío de Ant Design (ej. 'No hay datos')
        empty_elems = self.driver.find_elements(*self.EMPTY_STATE)
        return len(empty_elems) > 0
    
    def is_on_page(self, timeout: int = 5) -> bool:
        """
        Devuelve True si parece que estamos en la pantalla de Bitácora
        (título visible). No lanza excepción en caso negativo.
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(self.TITLE)
            )
            return True
        except TimeoutException:
            return False

    # ------------------------------------------------------------------
    # Helpers de tabla
    # ------------------------------------------------------------------
    def get_rows(self):
        """Devuelve las filas de la tabla de bitácora (solo las de datos)."""
        return self.driver.find_elements(*self.TABLE_BODY_ROWS)

    def has_rows(self) -> bool:
        """
        Indica si hay al menos una fila en la tabla.
        """
        # Por si el test llama has_rows sin haber llamado wait_loaded:
        self.wait_loaded()
        rows = self.get_rows()
        print(f"[DEBUG] Bitácora - filas encontradas: {len(rows)}")
        return len(rows) > 0
    
    def has_table_rows(self) -> bool:
        """
        Indica si hay filas en la tabla SIN asumir que la página de Bitácora
        está cargada. Útil para escenarios sin sesión o sin permisos.
        No hace waits largos, solo mira el DOM actual.
        """
        rows = self.driver.find_elements(*self.TABLE_BODY_ROWS)
        print(f"[DEBUG] Bitácora (has_table_rows) - filas encontradas: {len(rows)}")
        return len(rows) > 0

    def get_rows_text(self):
        """Devuelve el texto completo de cada fila (para asserts en tests)."""
        return [row.text for row in self.get_rows()]

    # ------------------------------------------------------------------
    # Filtro por usuario (select "Buscar por usuario")
    # ------------------------------------------------------------------
    def search_by_text(self, text: str):
        """
        Usa el select 'Buscar por usuario' para filtrar la bitácora.

        - Click en el select de 'Buscar por usuario'
        - Escribe el término
        - Selecciona la opción que contenga ese texto
        - Espera a que la tabla se refresque (haya filas o estado vacío)
        """
        # 1) Abrir el select
        select = self.wait.until(EC.element_to_be_clickable(self.USER_SELECT))
        select.click()

        # 2) Escribir en el input de búsqueda
        input_el = self.wait.until(
            EC.visibility_of_element_located(self.USER_SEARCH_INPUT)
        )
        input_el.clear()
        input_el.send_keys(text)

        # 3) Esperar opciones filtradas
        self.wait.until(
            EC.presence_of_all_elements_located(self.USER_OPTIONS)
        )

        options = self.driver.find_elements(*self.USER_OPTIONS)

        if not options:
            raise AssertionError(
                f"No se encontraron opciones en el combo de usuario para '{text}'"
            )

        # Buscar opción que contenga el texto
        target = None
        for opt in options:
            if text.lower() in opt.text.lower():
                target = opt
                break

        # Fallback: primera opción, si ninguna coincide exactamente
        if not target:
            target = options[0]

        # 4) Click en la opción
        self.driver.execute_script("arguments[0].click();", target)

        # 5) Esperar a que la tabla se refresque (filas o mensaje vacío)
        def _tabla_filtrada(d):
            filas = d.find_elements(*self.TABLE_BODY_ROWS)
            empty = d.find_elements(*self.EMPTY_STATE)
            # debug opcional:
            # print(f"[DEBUG] search_by_text -> filas={len(filas)}, empty={len(empty)}")
            return bool(filas) or bool(empty)

        self.wait.until(_tabla_filtrada)

    def search_no_results_in_dropdown(self, text: str) -> bool:
        """
        Escribe un usuario inexistente en 'Buscar por usuario' y
        retorna True si el dropdown muestra 'No hay datos'.

        OJO: aquí NO se aplica filtro en tabla, solo validamos el combo.
        """
        # 1) Abrir el select
        select = self.wait.until(EC.element_to_be_clickable(self.USER_SELECT))
        select.click()

        # 2) Escribir en el input de búsqueda
        input_el = self.wait.until(
            EC.visibility_of_element_located(self.USER_SEARCH_INPUT)
        )
        input_el.clear()
        input_el.send_keys(text)

        # 3) Esperar a que aparezca el mensaje "No hay datos" en el dropdown
        empty_el = self.wait.until(
            EC.visibility_of_element_located(self.DROPDOWN_EMPTY)
        )
        texto = empty_el.text.strip().lower()
        # opcional debug:
        # print(f"[DEBUG] dropdown empty text: {texto}")
        return "no hay datos" in texto
    
    # ------------------------------------------------------------------
    # Helpers de paginación
    # ------------------------------------------------------------------
    def has_multiple_pages(self) -> bool:
        """
        Devuelve True si la bitácora tiene más de una página en la paginación.
        """
        items = self.driver.find_elements(*self.PAGINATION_ITEMS)
        # debug opcional:
        # print(f"[DEBUG] páginas disponibles: {len(items)}")
        return len(items) > 1

    def get_active_page_number(self) -> int:
        """
        Devuelve el número de página actualmente activa en la paginación.
        """
        active = self.driver.find_element(*self.PAGINATION_ACTIVE_ITEM)
        return int(active.text.strip())

    def go_to_next_page(self):
        """
        Hace clic en 'Página siguiente' y espera a que cambien los registros.
        """
        # Tomamos la primera fila actual para detectar el cambio
        filas_antes = self.get_rows()
        first_row_before = filas_antes[0] if filas_antes else None

        # Click en 'Siguiente'
        next_btn = self.wait.until(
            EC.element_to_be_clickable(self.PAGINATION_NEXT)
        )
        next_btn.click()

        # Si había filas, esperamos a que esa primera fila se vuelva "stale"
        if first_row_before is not None:
            self.wait.until(EC.staleness_of(first_row_before))

        # Volvemos a esperar que la tabla esté lista
        self.wait_loaded()