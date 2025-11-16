from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class DirectorHomePage:
    ROLE_BANNER = (By.XPATH, "//header[contains(@class,'ant-layout-header')]//span[contains(normalize-space(),'Sesión iniciada como')]")
    ANY_STAT_CARD = (By.XPATH, "//*[@class='ant-card' and .//div[contains(@class,'ant-statistic')]]")
    ANY_CARD      = (By.CSS_SELECTOR, ".ant-card")  # señal más laxa
    SIDE_MENU     = (By.CSS_SELECTOR, "aside.ant-layout-sider .ant-menu")
    MENU_CONTRATOS = (By.XPATH, "//aside//a[@href='/contratos' and normalize-space()='Solicitudes de contratación']")

    def __init__(self, driver, base_url: str, timeout: int = 15):
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.wait = WebDriverWait(driver, timeout)

    def _wait_any(self, conditions, timeout=None):
        """Devuelve True cuando cualquiera de las condiciones se cumple."""
        w = self.wait if timeout is None else WebDriverWait(self.driver, timeout)
        last = None
        for _ in range(2):  # dos pasadas rápidas
            for cond in conditions:
                try:
                    w.until(cond)
                    return True
                except Exception as e:
                    last = e
        if last:
            raise last
        return False

    def wait_loaded(self):
        """
        Señales tolerantes de que la Home cargó:
        - aparece el banner de rol, o
        - vemos el menú lateral listo, o
        - se ve alguna card (estadística o cualquier .ant-card), o
        - ya está visible el ítem 'Solicitudes de contratación'
        """
        self._wait_any([
            EC.visibility_of_element_located(self.ROLE_BANNER),
            EC.visibility_of_element_located(self.SIDE_MENU),
            EC.visibility_of_element_located(self.ANY_STAT_CARD),
            EC.visibility_of_element_located(self.ANY_CARD),
            EC.visibility_of_element_located(self.MENU_CONTRATOS),
        ], timeout=20)

    def get_role_banner_text(self) -> str:
        try:
            return WebDriverWait(self.driver, 3).until(
                EC.visibility_of_element_located(self.ROLE_BANNER)
            ).text.strip()
        except Exception:
            return ""  # no todos los roles muestran banner siempre

    def go_to_contratos(self):
        self.wait.until(EC.element_to_be_clickable(self.MENU_CONTRATOS)).click()
