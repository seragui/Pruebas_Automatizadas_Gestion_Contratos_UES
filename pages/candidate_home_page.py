from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class CandidateHomePage:
    # Banner superior: "Sesión iniciada como Candidato — ..."
    ROLE_BANNER = (
        By.XPATH,
        "//header[contains(@class,'ant-layout-header')]"
        "//span[contains(normalize-space(),'Sesión iniciada como') and .//b[normalize-space()='Candidato']]"
    )

    # Título central: "Bienvenido al sistema: Candidato ..."
    WELCOME_TITLE = (
        By.XPATH,
        "//header[contains(@class,'ant-layout-header')]"
        "//span[contains(normalize-space(),'Sesión iniciada como') and contains(.,'Candidato')]"
    )

    # Botón "Ingresar datos personales"
    BTN_DATOS_PERSONALES = (
        By.XPATH,
        "//button[.//span[normalize-space()='Ingresar datos personales']]"
    )

    AVATAR_MENU = (By.CSS_SELECTOR, "header .ant-avatar.ant-dropdown-trigger")
    MI_PERFIL_LINK = (
        By.XPATH,
        "//ul[contains(@class,'ant-dropdown-menu')]"
        "//a[@href='/perfil' and normalize-space(text())='Mi perfil']"
    )

    def __init__(self, driver, base_url: str, timeout: int = 15):
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.wait = WebDriverWait(driver, timeout)

    def wait_home_loaded(self):
        """
        Espera a que el home del candidato esté listo para interactuar.
        """
        self.wait.until(EC.visibility_of_element_located(self.ROLE_BANNER))
        self.wait.until(EC.visibility_of_element_located(self.WELCOME_TITLE))
        #self.wait.until(EC.element_to_be_clickable(self.BTN_DATOS_PERSONALES))

    def click_ingresar_datos_personales(self):
        """
        Da clic al botón 'Ingresar datos personales'.
        """
        btn = self.wait.until(EC.element_to_be_clickable(self.BTN_DATOS_PERSONALES))
        try:
            btn.click()
        except Exception:
            # Fallback por si hay overlay / animación de AntD
            self.driver.execute_script("arguments[0].click();", btn)

    def is_on_personal_info_page(self) -> bool:
        """
        Verifica que se redirigió a la ruta de información personal.
        (AntD codifica la ñ, así que solo buscamos 'informaci').
        """
        url = self.driver.current_url
        return "/informaci" in url  # cubre /información-personal codificada
    
    def open_profile(self, timeout: int = 10):
        """
        Abre el menú del avatar y navega a la opción 'Mi perfil'.
        """
        wait = WebDriverWait(self.driver, timeout)

        avatar = wait.until(EC.element_to_be_clickable(self.AVATAR_MENU))
        avatar.click()

        link = wait.until(EC.element_to_be_clickable(self.MI_PERFIL_LINK))
        link.click()

    