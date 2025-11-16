from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

class BasePage:
    def __init__(self, driver, base_url):
        self.driver = driver
        self.base_url = base_url
        self.wait = WebDriverWait(self.driver, 15)

    def open(self, path: str = ""):
        url = self.base_url.rstrip("/") + "/" + path.lstrip("/")
        self.driver.get(url)

    def wait_visible(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def wait_clickable(self, locator):
        return self.wait.until(EC.element_to_be_clickable(locator))

    def click(self, locator):
        self.wait_clickable(locator).click()

    def type(self, locator, text, clear: bool = True):
        el = self.wait_visible(locator)
        if clear:
            try:
                el.clear()
            except Exception:
                pass
        el.send_keys(text)

    # Limpieza “segura” para inputs de Ant Design
    def type_safely(self, locator, text):
        el = self.wait_visible(locator)
        el.click()
        el.send_keys(Keys.CONTROL, "a")
        el.send_keys(Keys.DELETE)
        el.send_keys(text)

    def text_of(self, locator) -> str:
        return self.wait_visible(locator).text
