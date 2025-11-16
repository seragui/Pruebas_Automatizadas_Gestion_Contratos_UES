from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class RRHHCandidatesRegisteredPage:
    MENU_CANDIDATOS = (By.CSS_SELECTOR, "a[href='/candidatos-registrados']")
    SEARCH_INPUT = (By.CSS_SELECTOR, "input[placeholder='Buscar por nombre de candidato']")
    SEARCH_BUTTON = (By.CSS_SELECTOR, ".ant-input-search-button")
    TABLE = (By.CSS_SELECTOR, ".ant-table-wrapper")
    TABLE_ROWS = (By.CSS_SELECTOR, "tbody.ant-table-tbody tr.ant-table-row")
    NO_DATA_PLACEHOLDER = (By.CSS_SELECTOR, ".ant-table-placeholder")

    def __init__(self, driver, timeout: int = 15):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def open_from_sidebar(self):
        """Click en menú 'Candidatos registrados' y espera el buscador."""
        self.driver.find_element(*self.MENU_CANDIDATOS).click()
        self.wait.until(EC.visibility_of_element_located(self.SEARCH_INPUT))
        self.wait.until(EC.visibility_of_element_located(self.TABLE))

    def is_on_page(self) -> bool:
        return len(self.driver.find_elements(*self.SEARCH_INPUT)) > 0

    def search_candidate(self, name: str):
        """Escribe el nombre, clic en la lupa y espera que aparezca alguna fila."""
        print(f"[RRHH PAGE] Buscando candidato: {name!r}")
        box = self.wait.until(EC.element_to_be_clickable(self.SEARCH_INPUT))
        box.click()
        box.clear()
        box.send_keys(name)

        # clic al botón de búsqueda
        search_btn = self.driver.find_element(*self.SEARCH_BUTTON)
        self.driver.execute_script("arguments[0].click();", search_btn)

        # Esperar a que la tabla tenga filas y que alguna contenga el nombre
        def _row_with_name_present(drv):
            rows = drv.find_elements(*self.TABLE_ROWS)
            if not rows:
                return False
            for r in rows:
                if name.lower() in r.text.lower():
                    return True
            return False

        self.wait.until(_row_with_name_present)

    def open_control_datos_for_name(self, name: str):
        """
        Busca la fila cuyo texto contenga el nombre y da clic
        en el botón 'Control de datos' (link /validaciones/...).
        """
        rows = self.wait.until(EC.presence_of_all_elements_located(self.TABLE_ROWS))
        if not rows:
            raise AssertionError("No se encontraron filas en la tabla de candidatos.")

        target_row = None
        for r in rows:
            if name.lower() in r.text.lower():
                target_row = r
                break

        if not target_row:
            raise AssertionError(f"No se encontró ninguna fila que contenga el nombre: {name!r}")

        # Dentro de esa fila, buscamos el <a href="/validaciones/..."><button>...</button></a>
        try:
            btn = target_row.find_element(
                By.XPATH,
                ".//a[contains(@href, '/validaciones/')]/button"
            )
        except Exception as e:
            raise AssertionError(
                f"No se encontró el botón de 'Control de datos' en la fila del candidato {name!r}. "
                f"Texto de la fila: {target_row.text!r}"
            ) from e

        # Scroll y clic
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            btn
        )
        self.driver.execute_script("arguments[0].click();", btn)

    def has_candidate_in_table(self, name: str) -> bool:
        """
        Verifica si, en las filas actuales de la tabla, hay alguna
        que contenga el nombre del candidato.
        Úsalo después de `search_candidate(name)`.
        """
        rows = self.driver.find_elements(*self.TABLE_ROWS)
        for r in rows:
            if name.lower() in r.text.lower():
                return True
        return False

    def search_any_name(self, text: str):
        """
        Lanza una búsqueda genérica y espera a que la tabla se actualice con
        filas o con el placeholder de 'No hay datos'.
        """
        print(f"[RRHH PAGE] Buscando (genérico): {text!r}")
        box = self.wait.until(EC.element_to_be_clickable(self.SEARCH_INPUT))
        box.click()
        box.clear()
        box.send_keys(text)

        search_btn = self.driver.find_element(*self.SEARCH_BUTTON)
        self.driver.execute_script("arguments[0].click();", search_btn)

        # Esperar a que haya filas O aparezca el 'No hay datos'
        def _table_updated(drv):
            rows = drv.find_elements(*self.TABLE_ROWS)
            no_data = drv.find_elements(*self.NO_DATA_PLACEHOLDER)
            return bool(rows) or bool(no_data)

        self.wait.until(_table_updated)
    
    def shows_no_data_message(self) -> bool:
        """
        Devuelve True si aparece el placeholder de tabla sin datos
        y contiene el texto 'No hay datos'.
        """
        try:
            placeholder = self.wait.until(
                EC.visibility_of_element_located(self.NO_DATA_PLACEHOLDER)
            )
            return "no hay datos" in placeholder.text.lower()
        except Exception:
            return False

    