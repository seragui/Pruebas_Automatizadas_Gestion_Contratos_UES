from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time 

class UsersPage:
    PATH = "usuarios"

    # Encabezado de Usuarios (de tu HTML previo de la lista)
    HEADER = (By.XPATH, "//*[contains(@class,'ant-page-header')][.//span[@class='ant-page-header-heading-title' and normalize-space()='Usuarios']]"
                        " | //*[@class='ant-page-header-heading-title' and normalize-space()='Usuarios del sistema']")

    TABLE_WRAPPER = (By.CSS_SELECTOR, ".ant-table-wrapper")
    SEARCH_INPUT = (By.CSS_SELECTOR, ".ant-input-search input.ant-input")
    SEARCH_BTN   = (By.CSS_SELECTOR, ".ant-input-search-button")
    TABLE        = (By.CSS_SELECTOR, ".ant-table-wrapper .ant-table")
    ROWS         = (By.CSS_SELECTOR, ".ant-table-tbody > tr.ant-table-row")
    PAG_NEXT_BTN = (By.CSS_SELECTOR, ".ant-pagination-next button.ant-pagination-item-link")
    SPINNER      = (By.CSS_SELECTOR, ".ant-spin-spinning")  # opcional
    TBODY = (By.CSS_SELECTOR, ".ant-table-wrapper .ant-table .ant-table-tbody")

    # Encabezados / estado vacío
    THEAD_TH      = (By.CSS_SELECTOR, ".ant-table-thead th")
    EMPTY_STATE   = (By.CSS_SELECTOR, ".ant-table-placeholder")

    # Paginación / tamaño de página (AntD)
    PAG_PREV_BTN  = (By.CSS_SELECTOR, ".ant-pagination-prev button.ant-pagination-item-link")
    PAGE_ITEM     = lambda self, n: (By.CSS_SELECTOR, f".ant-pagination-item-{n}")
    PAGE_SIZE_DDP = (By.CSS_SELECTOR, ".ant-pagination-options .ant-select")
    PAGE_SIZE_OPT = lambda self, n: (By.XPATH, f"//div[contains(@class,'ant-select-item') and normalize-space()='{n} / página']")

    SORT_NAME_HEADER = (
    By.XPATH,
    "//th[contains(@class,'ant-table-cell')][.//span[contains(@class,'ant-table-column-title') and normalize-space()='Nombre']]"
    )

    # Botón/Link "Crear"
    CREATE_BTN = (By.XPATH, "//a[@href='/usuarios/crear'] | //button[.//span[normalize-space()='Crear']]")

    def __init__(self, driver, base_url, timeout=20):
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.wait = WebDriverWait(driver, timeout)

    def wait_loaded(self):
        # cualquiera de estas señales es válida
        signals = (
            EC.visibility_of_element_located(self.HEADER),
            EC.visibility_of_element_located(self.TABLE_WRAPPER),
            EC.visibility_of_element_located(self.CREATE_BTN),
        )
        last = None
        for _ in range(2):
            for sig in signals:
                try:
                    self.wait.until(sig)
                    return
                except Exception as e:
                    last = e
        raise AssertionError("No cargó la página de Usuarios.") from last

    def click_create(self):
        btn = self.wait.until(EC.element_to_be_clickable(self.CREATE_BTN))
        try:
            btn.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", btn)

    # -----------------------------
    # Helpers internos de tabla
    # -----------------------------
    def _tbody(self):
        return self.driver.find_element(*self.TBODY)

    def _wait_table_reloaded(self, old_tbody, timeout=8):
        """Espera a que el <tbody> anterior sea reemplazado (stale) y el nuevo sea visible."""
        WebDriverWait(self.driver, timeout).until(EC.staleness_of(old_tbody))
        self.wait.until(EC.visibility_of_element_located(self.TBODY))
        # si hay spinner, esperar a que desaparezca (tolerante)
        try:
            WebDriverWait(self.driver, 2).until(EC.invisibility_of_element_located(self.SPINNER))
        except Exception:
            pass

    def _wait_table_ready(self, timeout: int = 8):
        self.wait.until(EC.visibility_of_element_located(self.TABLE))
        try:
            WebDriverWait(self.driver, 2).until(EC.invisibility_of_element_located(self.SPINNER))
        except Exception:
            pass

    def _cell_nombre_in_row(self, row_el):
        # 1ra columna = "Nombre"
        return row_el.find_element(By.CSS_SELECTOR, "td:nth-child(1)")

    def _edit_btn_in_row(self, row_el):
        # botón Editar en la última celda
        return row_el.find_element(
            By.XPATH, ".//td[last()]//button[.//span[normalize-space()='Editar']]"
        )

    def _first_row_name(self) -> str:
        try:
            row = self.driver.find_elements(*self.ROWS)[0]
            return self._cell_nombre_in_row(row).text.strip()
        except Exception:
            return ""

    def contains_row_with_name(self, name: str, exact: bool = True) -> bool:
        target = name.strip().lower()
        rows = self.driver.find_elements(*self.ROWS)
        for r in rows:
            t = self._cell_nombre_in_row(r).text.strip().lower()
            if exact and t == target:
                return True
            if not exact and target in t:
                return True
        return False

    def _rows_names(self):
        rows = self.driver.find_elements(*self.ROWS)
        out = []
        for r in rows:
            try:
                out.append(self._cell_nombre_in_row(r).text.strip())
            except Exception:
                pass
        return out
    # -----------------------------
    # Acciones públicas
    # -----------------------------
    def reset_to_first_page(self):
        """Opcional: vuelve a la página 1 antes de filtrar."""
        try:
            first = self.driver.find_element(By.CSS_SELECTOR, ".ant-pagination-item-1 a, .ant-pagination-item-1")
            self.driver.execute_script("arguments[0].click();", first)
            self._wait_table_ready()
        except Exception:
            pass

    def search_by_name(self, name: str):
        """
        Simula la búsqueda tal como lo haría un usuario:
        - escribe el nombre
        - intenta click en el botón de búsqueda
        - si no pasa nada, intenta click en el icono de la lupa dentro del input
        - si aún nada, manda ENTER
        - dispara eventos input/change para AntD
        No asume que la tabla se filtrará; luego usaremos paginación para encontrar la fila.
        """
        inp = self.wait.until(EC.element_to_be_clickable(self.SEARCH_INPUT))
        inp.clear()
        inp.send_keys(name)

        # Dispara eventos que AntD suele escuchar
        try:
            self.driver.execute_script(
                "arguments[0].dispatchEvent(new Event('input', {bubbles:true}))", inp
            )
            self.driver.execute_script(
                "arguments[0].dispatchEvent(new Event('change', {bubbles:true}))", inp
            )
        except Exception:
            pass

        # 1) Click en botón grande a la derecha del input
        clicked = False
        try:
            btn = self.wait.until(EC.element_to_be_clickable(self.SEARCH_BTN))
            btn.click()
            clicked = True
        except Exception:
            clicked = False

        # 2) Si no hubo click efectivo, probar la lupa dentro del input
        if not clicked:
            try:
                icon = self.wait.until(EC.element_to_be_clickable(self.SEARCH_ICON))
                icon.click()
                clicked = True
            except Exception:
                clicked = False

        # 3) Fallback: ENTER
        if not clicked:
            try:
                inp.send_keys(Keys.ENTER)
            except Exception:
                pass

        # Pequeña espera corta para permitir cualquier actualización (sin suponer staleness)
        time.sleep(0.5)


    def wait_until_filtered_by(self, name_substr: str, timeout: int = 8):
        """Espera hasta que TODAS las filas visibles contengan la cadena en 'Nombre'."""
        q = (name_substr or "").strip().lower()

        def ok(_):
            rows = self.driver.find_elements(*self.ROWS)
            if not rows:
                return False
            for r in rows:
                try:
                    txt = self._cell_nombre_in_row(r).text.strip().lower()
                except Exception:
                    return False
                if q not in txt:
                    return False
            return True

        WebDriverWait(self.driver, timeout).until(ok)

    def assert_table_filtered_by(self, name_substr: str):
        """Asserta que todas las filas visibles contienen el filtro en la col. Nombre."""
        q = (name_substr or "").strip().lower()
        rows = self.driver.find_elements(*self.ROWS)
        assert rows, "No hay filas visibles."
        for r in rows:
            txt = self._cell_nombre_in_row(r).text.strip().lower()
            assert q in txt, f"Fila no coincide con el filtro: '{txt}'"

    def _find_row_by_name(self, name: str, exact: bool = False, max_pages: int = 5):
        """Encuentra la fila por (sub)cadena en 'Nombre'. Pagina si no aparece."""
        target = name.strip().lower()

        def matches(text):
            t = (text or "").strip().lower()
            return (t == target) if exact else (target in t)

        for _ in range(max_pages):
            rows = self.driver.find_elements(*self.ROWS)
            for r in rows:
                try:
                    if matches(self._cell_nombre_in_row(r).text):
                        return r
                except Exception:
                    continue
            # intentar siguiente página
            try:
                nxt = self.driver.find_element(*self.PAG_NEXT_BTN)
                if nxt.get_attribute("disabled"):
                    break
                nxt.click()
                self._wait_table_ready()
            except Exception:
                break
        return None

    def find_or_paginate_to_name(self, name: str, exact: bool = True, max_pages: int = 5) -> bool:
        """Si no está en la página actual, pagina hacia adelante hasta hallarlo."""
        if self.contains_row_with_name(name, exact=exact):
            return True
        for _ in range(max_pages):
            try:
                nxt = self.driver.find_element(*self.PAG_NEXT_BTN)
                if nxt.get_attribute("disabled"):
                    return False
                nxt.click()
                self._wait_table_ready()
                if self.contains_row_with_name(name, exact=exact):
                    return True
            except Exception:
                return False
        return False

    def open_edit_by_name(self, name: str, exact: bool = False) -> bool:
        """Abre la pantalla de 'Editar' para la fila cuyo nombre coincide."""
        row = self._find_row_by_name(name, exact=exact)
        if not row:
            return False
        btn = self._edit_btn_in_row(row)
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
        btn.click()
        return True
    
    def search_and_find(self, name: str, exact: bool = True, max_pages: int = 8) -> bool:
        """
        Ejecuta la búsqueda y luego intenta localizar el registro:
        - Primero verifica si ya aparece en la página actual;
        - Si no, pagina hacia adelante hasta encontrarlo.
        Devuelve True si lo encontró; False si no.
        """
        self.search_by_name(name)

        # por si la tabla no se “filtra” visualmente: intenta match en la página actual
        if self.contains_row_with_name(name, exact=exact):
            return True

        # fallback: paginar hasta hallarlo
        return self.find_or_paginate_to_name(name, exact=exact, max_pages=max_pages)
    
    # Ordenamiento (clic sobre header “Nombre”)
    def sort_by_nombre_toggle(self):
        """Hace clic sobre el encabezado 'Nombre' (cada clic alterna asc/desc/none)."""
        ths = self.driver.find_elements(*self.THEAD_TH)
        for th in ths:
            if "Nombre" in (th.text or ""):
                th.click()
                self._wait_table_ready()
                return
        raise AssertionError("No se encontró el encabezado 'Nombre'.")

    # Encabezados visibles
    def get_headers(self):
        return [th.text.strip() for th in self.driver.find_elements(*self.THEAD_TH)]

    # Cantidad de filas visibles
    def row_count(self) -> int:
        return len(self.driver.find_elements(*self.ROWS))

    # Estado vacío (sin resultados)
    def is_empty(self) -> bool:
        return len(self.driver.find_elements(*self.EMPTY_STATE)) > 0

    # Muestra de los primeros N nombres (para comparar orden/paginación sin ser frágil)
    def first_names_sample(self, k: int = 5):
        names = []
        rows = self.driver.find_elements(*self.ROWS)[:k]
        for r in rows:
            try:
                names.append(self._cell_nombre_in_row(r).text.strip())
            except Exception:
                names.append("")
        return names

    # Ir a página exacta
    def go_to_page(self, n: int) -> bool:
        try:
            self.driver.find_element(*self.PAGE_ITEM(n)).click()
            self._wait_table_ready()
            return True
        except Exception:
            return False

    # Siguiente / anterior
    def next_page(self) -> bool:
        try:
            btn = self.driver.find_element(*self.PAG_NEXT_BTN)
            if btn.get_attribute("disabled"):
                return False
            btn.click()
            self._wait_table_ready()
            return True
        except Exception:
            return False

    def prev_page(self) -> bool:
        try:
            btn = self.driver.find_element(*self.PAG_PREV_BTN)
            if btn.get_attribute("disabled"):
                return False
            btn.click()
            self._wait_table_ready()
            return True
        except Exception:
            return False

    # Cambiar tamaño de página: 10/20/50…
    def change_page_size(self, n: int) -> bool:
        try:
            self.driver.find_element(*self.PAGE_SIZE_DDP).click()
            self.wait.until(EC.element_to_be_clickable(self.PAGE_SIZE_OPT(n))).click()
            self._wait_table_ready()
            return True
        except Exception:
            return False
