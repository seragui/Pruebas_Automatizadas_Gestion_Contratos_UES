from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class RRHHCandidateDocumentsPage:
    HEADER = (By.CSS_SELECTOR, ".ant-page-header-heading-title")
    TABLE = (By.CSS_SELECTOR, ".ant-table-wrapper")

    DUI_VERIFICAR_BTN = (
        By.XPATH,
        "//tr[@data-row-key='DUI']//button[span[normalize-space(text())='Verificar']]"
    )

    BANCO_VERIFICAR_BTN = (
        By.XPATH,
        "//tr[@data-row-key='BANCO']//button[span[normalize-space(text())='Verificar']]"
    )

    CV_VERIFICAR_BTN = (
        By.XPATH,
        "//tr[@data-row-key='CV']//button[span[normalize-space(text())='Verificar']]"
    )

    DJ_VERIFICAR_BTN = (
        By.XPATH,
        "//tr[@data-row-key='DJ']//button[span[normalize-space(text())='Verificar']]"
        # o 'DECLARACION' / 'DJ' según el atributo real
    )

    TITULO_VERIFICAR_BTN = (
        By.XPATH,
        "//tr[@data-row-key='TITULO-N']//button[span[normalize-space(text())='Verificar']]"
        # o 'TITULO' / 'TITLE' según tu tabla
    )


    MODAL_OK = (
        By.XPATH,
        "//div[contains(@class,'ant-modal-confirm')]"
        "//button[contains(@class,'ant-btn-primary')][span[normalize-space(text())='Aceptar']]"
    )

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def wait_loaded(self):
        self.wait.until(EC.visibility_of_element_located(self.HEADER))
        self.wait.until(EC.visibility_of_element_located(self.TABLE))

    def get_header_text(self) -> str:
        return self.driver.find_element(*self.HEADER).text

    def click_verificar_dui(self):
        self.wait.until(
            EC.element_to_be_clickable(self.DUI_VERIFICAR_BTN)
        ).click()

    def click_verificar_banco(self):
        self.wait.until(
            EC.element_to_be_clickable(self.BANCO_VERIFICAR_BTN)
        ).click()
    
    def click_verificar_cv(self):
        """
        Da clic en 'Verificar' para el Curriculum (fila data-row-key='CV').
        """
        self.wait.until(
            EC.element_to_be_clickable(self.CV_VERIFICAR_BTN)
        ).click()

    def click_verificar_dj(self):
        """
        Da clic en 'Verificar' para la Declaración Jurada (fila data-row-key='DJ').
        """
        self.wait.until(
            EC.element_to_be_clickable(self.DJ_VERIFICAR_BTN)
        ).click()

    # Alias amigable si quieres llamarlo 'statement'
    def click_verificar_statement(self):
        self.click_verificar_dj()

    def click_verificar_titulo(self):
        """
        Da clic en 'Verificar' para el Título (fila data-row-key='TITULO-N').
        """
        self.wait.until(
            EC.element_to_be_clickable(self.TITULO_VERIFICAR_BTN)
        ).click()

    # Alias por si en el test lo llamas en inglés
    def click_verificar_title(self):
        self.click_verificar_titulo()

    def wait_success_modal_and_accept(self):
        """
        Espera el modal de '¡Validación enviada!' y hace clic en Aceptar.
        """
        ok_btn = self.wait.until(
            EC.element_to_be_clickable(self.MODAL_OK)
        )
        ok_btn.click()
        # Esperamos a que el modal desaparezca
        self.wait.until(EC.invisibility_of_element_located(self.MODAL_OK))

class RRHHDuiValidationPage:
    # Header: "Alma Juan Carlos... - Verificación de DUI"
    HEADER_TITLE = (By.CSS_SELECTOR, ".ant-page-header-heading-title")

    # El form de validaciones
    FORM = (By.CSS_SELECTOR, ".document-validation form")

    # Botón Enviar
    SUBMIT_BTN = (
        By.XPATH,
        "//button[span[normalize-space()='Enviar']]"
    )

    # IDs de los grupos de radio que vimos en el HTML
    GROUP_IDS = [
        "dui_address",     # Dirección de residencia
        "dui_birth_date",  # Fecha de nacimiento
        "dui_civil_status",# Estado civil
        "dui_name",        # Nombre según DUI
        "dui_number",      # Número de DUI
        "dui_profession",  # Profesión según DUI
        "dui_readable",    # Legible
        "dui_unexpired",   # Fecha de vencimiento
    ]

    def __init__(self, driver, timeout=15):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def wait_loaded(self):
        # Esperar a que aparezca el header y el formulario
        self.wait.until(EC.visibility_of_element_located(self.HEADER_TITLE))
        self.wait.until(EC.visibility_of_element_located(self.FORM))

    def _select_yes_for_group(self, group_id: str):
        """
        Selecciona la opción 'Si' dentro del grupo de radio
        cuyo contenedor tiene id = group_id (ej: 'dui_address').
        """
        group = self.wait.until(
            EC.presence_of_element_located((By.ID, group_id))
        )
        # Dentro del grupo, buscar el label que contiene el texto 'Si'
        yes_label = group.find_element(
            By.XPATH,
            ".//label[.//span[normalize-space()='Si']]"
        )
        yes_label.click()

    def mark_all_yes(self):
        """
        Marca 'Si' en todas las validaciones del formulario de DUI.
        """
        for gid in self.GROUP_IDS:
            self._select_yes_for_group(gid)

    def submit(self):
        """
        Da clic en el botón Enviar.
        """
        btn = self.wait.until(EC.element_to_be_clickable(self.SUBMIT_BTN))
        btn.click()

class RRHHBankValidationPage:
    HEADER = (By.CSS_SELECTOR, ".ant-page-header-heading-title")
    FORM = (By.CSS_SELECTOR, "form.ant-form")

    BANK_NUMBER_YES = (
        By.XPATH,
        "//div[@id='bank_number']"
        "//label[contains(@class,'ant-radio-button-wrapper')"
        "       and .//span[normalize-space(text())='Si']]"
    )

    BANK_READABLE_YES = (
        By.XPATH,
        "//div[@id='bank_readable']"
        "//label[contains(@class,'ant-radio-button-wrapper')"
        "       and .//span[normalize-space(text())='Si']]"
    )

    SUBMIT_BUTTON = (
        By.XPATH,
        "//form[contains(@class,'ant-form')]//button[@type='submit']"
    )

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def wait_loaded(self):
        self.wait.until(EC.visibility_of_element_located(self.HEADER))
        self.wait.until(EC.visibility_of_element_located(self.FORM))

    def mark_all_yes(self):
        for locator in (self.BANK_NUMBER_YES, self.BANK_READABLE_YES):
            label = self.wait.until(EC.element_to_be_clickable(locator))
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});",
                label
            )
            label.click()

    def submit(self):
        btn = self.wait.until(
            EC.element_to_be_clickable(self.SUBMIT_BUTTON)
        )
        btn.click()

class RRHHCVValidationPage:
    HEADER = (By.CSS_SELECTOR, ".ant-page-header-heading-title")
    FORM = (By.CSS_SELECTOR, "form.ant-form")

    CURRICULUM_READABLE_YES = (
        By.XPATH,
        "//div[@id='curriculum_readable']"
        "//label[contains(@class,'ant-radio-button-wrapper')"
        "       and .//span[normalize-space(text())='Si']]"
    )

    SUBMIT_BUTTON = (
        By.XPATH,
        "//form[contains(@class,'ant-form')]//button[@type='submit']"
    )

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def wait_loaded(self):
        self.wait.until(EC.visibility_of_element_located(self.HEADER))
        self.wait.until(EC.visibility_of_element_located(self.FORM))
        # Opcional: garantizamos que esté el radio group
        self.wait.until(
            EC.presence_of_element_located(
                (By.ID, "curriculum_readable")
            )
        )

    def mark_all_yes(self):
        # Igual que banco, pero solo un campo
        label = self.wait.until(
            EC.element_to_be_clickable(self.CURRICULUM_READABLE_YES)
        )
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            label
        )
        label.click()

    def submit(self):
        btn = self.wait.until(
            EC.element_to_be_clickable(self.SUBMIT_BUTTON)
        )
        btn.click()

class RRHHStatementValidationPage:
    HEADER = (By.CSS_SELECTOR, ".ant-page-header-heading-title")
    FORM = (By.CSS_SELECTOR, "form.ant-form")

    STATEMENT_READABLE_YES = (
        By.XPATH,
        "//div[@id='statement_readable']"
        "//label[contains(@class,'ant-radio-button-wrapper')"
        "       and .//span[normalize-space(text())='Si']]"
    )

    SUBMIT_BUTTON = (
        By.XPATH,
        "//form[contains(@class,'ant-form')]//button[@type='submit']"
    )

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def wait_loaded(self):
        # Header visible
        self.wait.until(EC.visibility_of_element_located(self.HEADER))
        # Form visible
        self.wait.until(EC.visibility_of_element_located(self.FORM))
        # Radio group presente
        self.wait.until(
            EC.presence_of_element_located((By.ID, "statement_readable"))
        )

    def mark_all_yes(self):
        # En este caso solo hay una validación: "Declaración legible"
        label = self.wait.until(
            EC.element_to_be_clickable(self.STATEMENT_READABLE_YES)
        )
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            label
        )
        label.click()

    def submit(self):
        btn = self.wait.until(
            EC.element_to_be_clickable(self.SUBMIT_BUTTON)
        )
        btn.click()

class RRHHTituloNValidationPage:
    HEADER = (By.CSS_SELECTOR, ".ant-page-header-heading-title")
    FORM = (By.CSS_SELECTOR, "form.ant-form")

    TITLE_MINED_YES = (
        By.XPATH,
        "//div[@id='title_mined']"
        "//label[contains(@class,'ant-radio-button-wrapper')"
        "       and .//span[normalize-space(text())='Si']]"
    )

    TITLE_READABLE_YES = (
        By.XPATH,
        "//div[@id='title_readable']"
        "//label[contains(@class,'ant-radio-button-wrapper')"
        "       and .//span[normalize-space(text())='Si']]"
    )

    SUBMIT_BUTTON = (
        By.XPATH,
        "//form[contains(@class,'ant-form')]//button[@type='submit']"
    )

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def wait_loaded(self):
        # Header visible
        self.wait.until(EC.visibility_of_element_located(self.HEADER))
        # Form visible
        self.wait.until(EC.visibility_of_element_located(self.FORM))
        # Radios presentes
        self.wait.until(EC.presence_of_element_located((By.ID, "title_mined")))
        self.wait.until(EC.presence_of_element_located((By.ID, "title_readable")))

    def mark_all_yes(self):
        # Marcar "Si" en ambas validaciones
        for locator in (self.TITLE_MINED_YES, self.TITLE_READABLE_YES):
            label = self.wait.until(EC.element_to_be_clickable(locator))
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});",
                label
            )
            label.click()

    def submit(self):
        btn = self.wait.until(
            EC.element_to_be_clickable(self.SUBMIT_BUTTON)
        )
        btn.click()