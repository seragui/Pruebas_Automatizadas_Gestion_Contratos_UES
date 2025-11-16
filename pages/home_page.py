from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class HomePage:
    # Menú lateral (expandido o colapsado, tu HTML está expandido)
    USERS_MENU = (By.XPATH, "//ul[contains(@class,'ant-menu')]//a[@href='/usuarios']")

    def __init__(self, driver, base_url, timeout=20):
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.wait = WebDriverWait(driver, timeout)

    def go_to_users(self):
        # Espera a que el menú esté clickeable (ya estás logueado y en /)
        link = self.wait.until(EC.element_to_be_clickable(self.USERS_MENU))
        try:
            link.click()
        except Exception:
            # Fallback JS por si hay overlay de animación
            self.driver.execute_script("arguments[0].click();", link)
