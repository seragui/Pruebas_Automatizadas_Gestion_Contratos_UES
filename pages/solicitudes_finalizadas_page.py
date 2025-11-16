from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class SolicitudesFinalizadasPage:
    """
    Vista: /solicitudes-finalizadas
    Verifica que el código de solicitud aparezca en el listado.
    """

    HEADER = (
        By.XPATH,
        "//*[contains(@class,'ant-page-header') or contains(@class,'ant-typography')]"
        "//*[normalize-space()='Solicitudes finalizadas']",
    )
    SPINNER = (By.CSS_SELECTOR, ".ant-spin-spinning")
    TABLE = (
        By.XPATH,
        "//div[contains(@class,'ant-table') and .//table]"
    )

    def __init__(self, driver, timeout=20):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def _row_by_code(self, code: str):
        """
        Fila cuya PRIMERA columna (td[1]) tiene exactamente el código.
        Se basa en la estructura del HTML que compartiste.
        """
        return (
            By.XPATH,
            (
                "//div[contains(@class,'ant-table')]"
                "//tbody[contains(@class,'ant-table-tbody')]"
                f"//tr[td[1][normalize-space()='{code}']]"
            ),
        )

    def _wait_spinner_out(self, extra=0):
        try:
            WebDriverWait(self.driver, 10 + extra).until(
                EC.invisibility_of_element_located(self.SPINNER)
            )
        except TimeoutException:
            # Si el spinner se queda pegado, no bloqueamos la prueba
            pass

    def wait_loaded(self, evidencia=None):
        # El header podría no estar siempre; al menos aseguramos la tabla
        try:
            self.wait.until(EC.presence_of_element_located(self.HEADER))
        except TimeoutException:
            pass

        self._wait_spinner_out()
        self.wait.until(EC.presence_of_element_located(self.TABLE))

        if evidencia:
            evidencia("sol_finalizadas__lista_visible")

    def assert_code_present(self, code: str, evidencia=None, timeout: int = 12):
        """
        Verifica que exista una fila con el código indicado.
        Si no aparece dentro del timeout, lanza AssertionError y toma evidencia.
        """
        self.wait_loaded(evidencia=evidencia)

        try:
            row = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(self._row_by_code(code))
            )
        except TimeoutException:
            if evidencia:
                evidencia(f"sol_finalizadas__code_not_found__{code}")
            raise AssertionError(
                f"No se encontró el código {code} en la tabla de solicitudes finalizadas."
            ) from None

        if evidencia:
            evidencia(f"sol_finalizadas__row_{code}")

        return row
