from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from .base_page import BasePage

class LogoutBar(BasePage):
    # 1) posibles triggers para abrir el dropdown (ajusta o añade data-test="user-menu")
    TRIGGERS = [
        (By.CSS_SELECTOR, "[data-test='user-menu']"),
        (By.CSS_SELECTOR, ".ant-dropdown-trigger"),
        (By.CSS_SELECTOR, ".ant-avatar, .ant-avatar-square, .ant-avatar-circle"),
        (By.CSS_SELECTOR, "[aria-label='account'], [aria-label='user']"),
    ]

    # 2) XPaths robustos para el item "Cerrar Sesión"
    MENU_ITEM_XPATHS = [
        # li con role=menuitem y un span cuyo texto sea Cerrar Sesión (con espacios normalizados)
        (By.XPATH, "//li[@role='menuitem'][.//span[normalize-space()='Cerrar Sesión']]"),
        # alternativas por si varía mayúsculas/acentos
        (By.XPATH, "//li[@role='menuitem'][.//span[contains(translate(normalize-space(.),'ÁÉÍÓÚáéíóú','AEIOUaeiou'),'Cerrar Sesion')]]"),
        # genérico: cualquier li de menú que contenga el texto
        (By.XPATH, "//li[contains(@class,'ant-dropdown-menu-item')][.//span[normalize-space()='Cerrar Sesión']]"),
    ]

    def open_menu_if_needed(self):
        # intenta abrir el menú si aún no está visible
        for loc in self.TRIGGERS:
            try:
                btn = self.wait_clickable(loc)
                ActionChains(self.driver).move_to_element(btn).pause(0.1).click(btn).perform()
                # si ya aparece algún item de menú, salimos
                WebDriverWait(self.driver, 5).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, ".ant-dropdown, .ant-dropdown-menu"))
                )
                return
            except Exception:
                continue
        # si no hay trigger, asumimos que ya está abierto (p. ej. lo abrió la app)

    def do_logout(self):
        self.open_menu_if_needed()

        last_err = None
        for loc in self.MENU_ITEM_XPATHS:
            try:
                self.click(loc)  # usa el click con espera de BasePage
                # esperar a que el overlay desaparezca (menú cerrado)
                WebDriverWait(self.driver, 5).until(
                    EC.invisibility_of_element_located((By.CSS_SELECTOR, ".ant-dropdown, .ant-dropdown-menu"))
                )
                return True
            except Exception as e:
                last_err = e
                continue

        raise TimeoutException(
            "No se encontró el item de menú 'Cerrar Sesión'. "
            "Ajusta el selector o agrega data-test='logout' y apunta a [data-test='logout']."
        )
