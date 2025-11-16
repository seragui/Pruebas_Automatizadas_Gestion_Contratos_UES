from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class CandidateUploadDocumentsPage():

    def __init__(self, driver, timeout=15):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    # --- ya los debes tener ---
    MENU_UPLOAD_DOCS = (By.LINK_TEXT, "Subir documentos")
    MODAL = (By.CSS_SELECTOR, ".ant-modal-content")
    MODAL_OK_BTN = (By.CSS_SELECTOR, ".ant-modal-footer .ant-btn-primary")
    UPLOAD_TITLE = (By.CSS_SELECTOR, "h3.ant-typography")

    # DUI
    DUI_INPUT = (By.ID, "documents-dui_dui")
    DUI_SUBMIT_BUTTON = (By.CSS_SELECTOR, "#documents-dui button.submit-button")

    # Curriculum
    CV_INPUT = (By.ID, "cv_cv")
    CV_SUBMIT_BUTTON = (By.CSS_SELECTOR, "#cv button.submit-button")

    # Cuenta bancaria
    ACCOUNT_INPUT = (By.ID, "documents-account_banco")
    ACCOUNT_SUBMIT_BUTTON = (By.CSS_SELECTOR, "#documents-account button.submit-button")

    # Título
    TITLE_INPUT = (By.ID, "documents-title_titulo")
    TITLE_SUBMIT_BUTTON = (By.CSS_SELECTOR, "#documents-title button.submit-button")

    # Declaración jurada
    STATEMENT_INPUT = (By.ID, "documents-permission_statement")
    STATEMENT_SUBMIT_BUTTON = (By.CSS_SELECTOR, "#documents-permission button.submit-button")

    # --- métodos que ya tenés (ejemplo) ---
    def open_from_sidebar(self):
        self.wait.until(EC.element_to_be_clickable(self.MENU_UPLOAD_DOCS)).click()

    def wait_upload_info_modal(self):
        self.wait.until(EC.visibility_of_element_located(self.MODAL))

    def accept_upload_info_modal(self):
        self.wait.until(EC.element_to_be_clickable(self.MODAL_OK_BTN)).click()
        self.wait.until(EC.invisibility_of_element_located(self.MODAL))

    def is_on_upload_page(self) -> bool:
        title = self.driver.find_element(*self.UPLOAD_TITLE).text
        return "Subir documentos" in title

    # --- helper genérico para subir archivo ---
    def _upload_generic(self, input_locator, button_locator, file_path: str) -> None:
        file_path = str(file_path)           # por si llega como Path
        input_elem = self.driver.find_element(*input_locator)
        input_elem.send_keys(file_path)      # NADA de *file_path
        self.driver.find_element(*button_locator).click()

    # --- wrappers específicos ---
    def upload_dui(self, file_path: str) -> None:
        self._upload_generic(self.DUI_INPUT, self.DUI_SUBMIT_BUTTON, file_path)

    def upload_cv(self, file_path: str) -> None:
        self._upload_generic(self.CV_INPUT, self.CV_SUBMIT_BUTTON, file_path)

    def upload_bank_account(self, file_path: str) -> None:
        self._upload_generic(self.ACCOUNT_INPUT, self.ACCOUNT_SUBMIT_BUTTON, file_path)

    def upload_title(self, file_path: str) -> None:
        self._upload_generic(self.TITLE_INPUT, self.TITLE_SUBMIT_BUTTON, file_path)

    def upload_statement(self, file_path: str) -> None:
        self._upload_generic(self.STATEMENT_INPUT, self.STATEMENT_SUBMIT_BUTTON, file_path)