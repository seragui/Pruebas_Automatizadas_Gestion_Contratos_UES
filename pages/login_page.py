from selenium.webdriver.common.by import By
from .base_page import BasePage

class LoginPage(BasePage):
    # Ant Design: ids visibles en tu captura
    EMAIL = (By.ID, "basic_email")
    PASSWORD = (By.ID, "basic_password")
    # Botón de submit dentro del form (ajusta el id del form si cambia)
    BTN_LOGIN = (By.CSS_SELECTOR, "form#basic button[type='submit'], button[type='submit']")

    # Ejemplo de mensaje de error AntD (opcional, si validás errores)
    ERROR_MSG = (By.CSS_SELECTOR, ".ant-form-item-explain-error")

    def open_login(self):
        self.open("/")

    def login_as(self, email: str, password: str):
        self.type_safely(self.EMAIL, email)
        self.type_safely(self.PASSWORD, password)
        self.click(self.BTN_LOGIN)
    
    def is_login_screen(self) -> bool:
    # True si está visible el input de email o el form de login (AntD)
        try:
            els = self.driver.find_elements(*self.EMAIL)
            if els and els[0].is_displayed():
                return True
        except Exception:
            pass
        try:
            forms = self.driver.find_elements(By.CSS_SELECTOR, "form#basic")
            if forms:
                return True
        except Exception:
            pass
        return False


    def is_logged_in(self) -> bool:
        """Ajusta esto a un selector que solo exista tras login."""
        try:
            # Ejemplo: un avatar, badge, o el layout del dashboard
            self.wait_visible((By.CSS_SELECTOR, "[data-test='user-badge'], .ant-layout"))
            return True
        except Exception:
            return False

    def error_text(self):
        try:
            return self.text_of(self.ERROR_MSG)
        except Exception:
            return ""
