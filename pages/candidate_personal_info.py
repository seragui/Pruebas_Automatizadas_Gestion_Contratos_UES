from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.common.exceptions import NoSuchElementException
import random


class CandidatePersonalInfoStep1Page:
    """
    Paso 1 del wizard de información personal del candidato: Nacionalidad.
    """

    # Paso 1 activo en el wizard (Nacionalidad)
    STEP_NACIONALIDAD_ACTIVE = (
        By.XPATH,
        "//div[contains(@class,'ant-steps-item-active')]"
        "//div[contains(@class,'ant-steps-item-title') and normalize-space()='Nacionalidad']"
    )

    # Radio group de nacionalidad
    RADIO_GROUP = (By.ID, "is_foreign")

    # Opción "Salvadoreño"
    RADIO_SALVADORENO = (
        By.XPATH,
        "//div[@id='is_foreign']"
        "//label[.//span[normalize-space()='Salvadoreño']]"
    )

    # Botón "Siguiente"
    BTN_SIGUIENTE = (
        By.XPATH,
        "//div[contains(@class,'steps-action')]"
        "//button[.//span[normalize-space()='Siguiente']]"
    )

    def __init__(self, driver, timeout: int = 15):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def wait_loaded(self):
        """
        Espera a que el paso 1 (Nacionalidad) esté visible y listo para interactuar.
        """
        self.wait.until(EC.visibility_of_element_located(self.STEP_NACIONALIDAD_ACTIVE))
        self.wait.until(EC.visibility_of_element_located(self.RADIO_GROUP))
        self.wait.until(EC.element_to_be_clickable(self.RADIO_SALVADORENO))

    def seleccionar_salvadoreno(self):
        """
        Marca la opción 'Salvadoreño'.
        """
        radio = self.wait.until(EC.element_to_be_clickable(self.RADIO_SALVADORENO))
        try:
            radio.click()
        except Exception:
            # Por si AntD mete overlay/animaciones
            self.driver.execute_script("arguments[0].click();", radio)

    def click_siguiente(self):
        """
        Da clic en el botón 'Siguiente' para avanzar al siguiente paso del wizard.
        """
        btn = self.wait.until(EC.element_to_be_clickable(self.BTN_SIGUIENTE))
        try:
            btn.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", btn)

class CandidatePersonalInfoStep2Page:
    """
    Paso 2 del wizard de información personal del candidato: Datos generales.
    """

    # Paso 2 activo en el wizard
    STEP_DATOS_GENERALES_ACTIVE = (
        By.XPATH,
        "//div[contains(@class,'ant-steps-item-active')]"
        "//div[contains(@class,'ant-steps-item-title') and normalize-space()='Datos generales']"
    )

    # Inputs de nombres y apellidos
    FIRST_NAME_INPUT = (By.ID, "first_name")
    MIDDLE_NAME_INPUT = (By.ID, "middle_name")
    LAST_NAME_INPUT = (By.ID, "last_name")

    # Estado civil (select)
    CIVIL_STATUS_SELECT = (
        By.XPATH,
        "//input[@id='civil_status']/ancestor::div[contains(@class,'ant-select')]"
    )

    # Género (select)
    GENDER_SELECT = (
        By.XPATH,
        "//input[@id='gender']/ancestor::div[contains(@class,'ant-select')]"
    )

    # Conocido por (opcional)
    KNOWN_AS_INPUT = (By.ID, "know_as")

    # Fecha de nacimiento (date picker)
    BIRTHDATE_INPUT = (By.ID, "birth_date")

    # Profesión / oficio
    PROFESSIONAL_TITLE_INPUT = (By.ID, "professional_title")

    # ¿Posee otro título? (radio)
    OTHER_TITLE_RADIO_YES = (
        By.XPATH,
        "//div[@id='other_title']//label[.//span[normalize-space()='Si']]"
    )
    OTHER_TITLE_RADIO_NO = (
        By.XPATH,
        "//div[@id='other_title']//label[.//span[normalize-space()='No']]"
    )

    # Dirección de residencia
    ADDRESS_TEXTAREA = (By.ID, "address")

    # Distrito (select con buscador)
    DISTRITO_SELECT = (
        By.XPATH,
        "//input[@id='distrito_id']/ancestor::div[contains(@class,'ant-select')]"
    )
    DISTRITO_SEARCH_INPUT = (By.ID, "distrito_id")

    # Botones de navegación
    BTN_SIGUIENTE = (
        By.XPATH,
        "//div[contains(@class,'steps-action')]"
        "//button[.//span[normalize-space()='Siguiente']]"
    )

    def __init__(self, driver, timeout: int = 15):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def wait_loaded(self):
        """
        Espera a que el paso 2 (Datos generales) esté visible y listo.
        """
        self.wait.until(EC.visibility_of_element_located(self.STEP_DATOS_GENERALES_ACTIVE))
        self.wait.until(EC.visibility_of_element_located(self.FIRST_NAME_INPUT))
        self.wait.until(EC.visibility_of_element_located(self.LAST_NAME_INPUT))

    def fill_names(self, first_name: str, middle_name: str, last_name: str):
        self._type(self.FIRST_NAME_INPUT, first_name)
        self._type(self.MIDDLE_NAME_INPUT, middle_name)
        self._type(self.LAST_NAME_INPUT, last_name)

    def _open_select(self, select_locator):
        """
        Hace scroll al <Select> de AntD y lo abre con click.
        """
        container = self.wait.until(EC.element_to_be_clickable(select_locator))
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", container
        )
        try:
            container.click()
        except Exception:
            # fallback por si hay overlays raros
            self.driver.execute_script("arguments[0].click();", container)

    # ------------------------------------------------------------------
    # Helper genérico para elegir una opción del dropdown por texto
    # ------------------------------------------------------------------
    def _pick_from_dropdown(self, option_text: str):
        """
        Selecciona una opción de cualquier dropdown de AntD usando el texto 
        visible de la opción (lo que tú ves en pantalla).
        """
        target_norm = option_text.strip().lower()

        # Esperar a que aparezca al menos UNA opción
        self.wait.until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[contains(@class,'ant-select-item-option')]")
            )
        )

        options = self.driver.find_elements(
            By.XPATH,
            "//div[contains(@class,'ant-select-item-option')]"
        )

        visibles = []
        objetivo = None

        for opt in options:
            txt = opt.text.strip()
            if not txt:
                continue
            visibles.append(txt)
            if txt.strip().lower() == target_norm:
                objetivo = opt
                break

        if not objetivo:
            # Debug friendly
            raise NoSuchElementException(
                f"No se encontró opción con texto '{option_text}'. "
                f"Opciones visibles: {visibles}"
            )

        # Scroll al centro y click
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", objetivo
        )
        objetivo.click()

    # ------------------------------------------------------------------
    # Acciones de alto nivel
    # ------------------------------------------------------------------
    def select_civil_status(self, option_text: str):
        """
        Selecciona estado civil: 'Soltero', 'Casado/a', 'Viudo/a', etc.
        """
        self._open_select(self.CIVIL_STATUS_SELECT)
        self._pick_from_dropdown(option_text)

    def select_gender(self, option_text: str):
        """
        Selecciona género: 'Masculino' o 'Femenino'.
        """
        self._open_select(self.GENDER_SELECT)
        self._pick_from_dropdown(option_text)

    def fill_birth_date(self, date_str: str):
        """
        Llena la fecha de nacimiento en el DatePicker de AntD.
        Estrategia:
          1. Hacer clic en el input.
          2. Quitar readonly para poder tipear.
          3. Ctrl+A, Delete.
          4. Escribir la fecha en formato dd/MM/YYYY.
          5. Hacer blur/tab para que el componente la tome.
        """
        # Esperar a que el input esté presente/clickable
        input_elem = self.wait.until(
            EC.element_to_be_clickable(self.BIRTHDATE_INPUT)
        )

        # Quitar readonly para permitir send_keys
        self.driver.execute_script(
            "arguments[0].removeAttribute('readonly');", input_elem
        )

        # Click sobre el campo
        input_elem.click()

        # Limpiar contenido
        input_elem.send_keys(Keys.CONTROL + "a")
        input_elem.send_keys(Keys.DELETE)

        # Escribir la fecha dd/MM/YYYY
        input_elem.send_keys(date_str)

        # Forzar blur para que AntD "confirme" el valor
        self.driver.execute_script("arguments[0].blur();", input_elem)
        # Como refuerzo, también mandamos un TAB
        input_elem.send_keys(Keys.TAB)

    def set_profession_title(self, title: str):
        self._type(self.PROFESSIONAL_TITLE_INPUT, title)

    def set_other_title(self, has_other: bool):
        locator = self.OTHER_TITLE_RADIO_YES if has_other else self.OTHER_TITLE_RADIO_NO
        self._click(locator)

    def set_address(self, address: str):
        self._type(self.ADDRESS_TEXTAREA, address)

    def select_distrito(self, distrito_text: str):
        """
        Para el distrtito usaremos siempre 'San Salvador'
        """
        # Abre el select
        self._click(self.DISTRITO_SELECT)
        search_input = self.wait.until(EC.visibility_of_element_located(self.DISTRITO_SEARCH_INPUT))
        search_input.clear()
        search_input.send_keys(distrito_text)
        search_input.send_keys(Keys.ENTER)

    def click_siguiente(self):
        self._click(self.BTN_SIGUIENTE)

    # ==== helpers internos ====

    def _click(self, locator):
        elem = self.wait.until(EC.element_to_be_clickable(locator))
        try:
            elem.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", elem)

    def _type(self, locator, text: str):
        elem = self.wait.until(EC.visibility_of_element_located(locator))
        elem.clear()
        elem.send_keys(text)

    def _open_select(self, select_locator):
        select_elem = self.wait.until(EC.element_to_be_clickable(select_locator))
        try:
            select_elem.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", select_elem)

class CandidatePersonalInfoStep3Page:
    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    # --------- Locators ---------
    DUI_INPUT = (By.ID, "dui_number")
    DUI_EXPIRATION_INPUT = (By.ID, "dui_expiration_date")
    NUP_INPUT = (By.ID, "nup")
    ISSS_INPUT = (By.ID, "isss_number")
    ALT_MAIL_INPUT = (By.ID, "alternate_mail")

    
    BANK_SELECT_TRIGGER = (
        By.XPATH,
        "//label[@for='bank_id']"
        "/ancestor::div[contains(@class,'ant-form-item-row')]"
        "//div[contains(@class,'ant-select-selector')]"
    )

    BANK_ACCOUNT_TYPE_TRIGGER = (
        By.XPATH,
        "//label[@for='bank_account_type']"
        "/ancestor::div[contains(@class,'ant-form-item-row')]"
        "//div[contains(@class,'ant-select-selector')]"
    )

    BANK_ACCOUNT_NUMBER_INPUT = (By.ID, "bank_account_number")
    TELEPHONE_INPUT = (By.ID, "telephone")
    ALT_TELEPHONE_INPUT = (By.ID, "alternate_telephone")

    NEXT_BUTTON = (
        By.XPATH,
        "//div[contains(@class,'steps-action')]//button[span[normalize-space()='Siguiente']]"
    )

    # --------- Helpers internos para selects (Ant Design) ---------

    def _open_select(self, trigger_locator):
        trigger = self.wait.until(
            EC.element_to_be_clickable(trigger_locator)
        )
        trigger.click()

    def _get_open_dropdown_options(self):
        dropdown = self.wait.until(
            EC.visibility_of_element_located(
                (
                    By.CSS_SELECTOR,
                    ".ant-select-dropdown:not(.ant-select-dropdown-hidden)"
                )
            )
        )
        options = dropdown.find_elements(
            By.CSS_SELECTOR,
            ".ant-select-item-option"
        )
        return dropdown, options

    def _pick_from_dropdown_by_text(self, text: str):
        dropdown, options = self._get_open_dropdown_options()

        for opt in options:
            span = opt.find_element(
                By.CSS_SELECTOR,
                ".ant-select-item-option-content"
            )
            if span.text.strip() == text.strip():
                self.driver.execute_script("arguments[0].scrollIntoView(true);", opt)
                opt.click()
                return

        visible = [opt.text for opt in options]
        raise Exception(
            f"No se encontró opción con texto '{text}'. Opciones visibles: {visible}"
        )

    def _pick_from_dropdown_random(self):
        dropdown, options = self._get_open_dropdown_options()
        if not options:
            raise Exception("No hay opciones visibles en el dropdown.")

        opt = random.choice(options)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", opt)
        opt.click()

    def _pick_from_dropdown(self, text: str):
        """
        Wrapper para mantener el mismo nombre que usamos en otros PageObjects.
        """
        return self._pick_from_dropdown_by_text(text)

    # --------- Acciones de alto nivel ---------

    def wait_loaded(self):
        # Consideramos que el Step 3 está listo cuando el input de DUI está visible
        self.wait.until(
            EC.visibility_of_element_located(self.DUI_INPUT)
        )

    def fill_dui(self, dui: str):
        el = self.wait.until(EC.element_to_be_clickable(self.DUI_INPUT))
        el.clear()
        el.send_keys(dui)

    def fill_dui_expiration_date(self, date_str: str):
        """
        date_str en formato YYYY-MM-DD, como pediste.
        El input es readonly, así que quitamos el atributo por JS, tipeamos y hacemos TAB.
        """
        el = self.wait.until(
            EC.visibility_of_element_located(self.DUI_EXPIRATION_INPUT)
        )

        # quitar readonly
        self.driver.execute_script("arguments[0].removeAttribute('readonly');", el)

        el.click()
        el.clear()
        el.send_keys(date_str)
        # forzamos blur para que React/AntD lo tome
        el.send_keys(Keys.TAB)

    def fill_nup(self, nup: str):
        el = self.wait.until(EC.element_to_be_clickable(self.NUP_INPUT))
        el.clear()
        el.send_keys(nup)

    def fill_isss(self, isss: str):
        el = self.wait.until(EC.element_to_be_clickable(self.ISSS_INPUT))
        el.clear()
        el.send_keys(isss)

    def fill_alternate_email(self, email: str):
        el = self.wait.until(EC.element_to_be_clickable(self.ALT_MAIL_INPUT))
        el.clear()
        el.send_keys(email)

    def select_random_bank(self):
        self._open_select(self.BANK_SELECT_TRIGGER)
        self._pick_from_dropdown_random()

    def select_account_type_ahorro(self):
        """
        Abre el combo de 'Tipo de cuenta' y selecciona siempre
        la opción 'Cuenta de Ahorro' (tal como aparece en el UI).
        """
        self._open_select(self.BANK_ACCOUNT_TYPE_TRIGGER)
        # 👇 OJO: coincide con la opción real del dropdown
        self._pick_from_dropdown("Cuenta de Ahorro")

    def fill_bank_account_number(self, acc_number: str):
        el = self.wait.until(
            EC.element_to_be_clickable(self.BANK_ACCOUNT_NUMBER_INPUT)
        )
        el.clear()
        el.send_keys(acc_number)

    def fill_telephone(self, phone: str):
        """
        phone con formato 7xxx-xxxx o 6xxx-xxxx.
        """
        el = self.wait.until(
            EC.element_to_be_clickable(self.TELEPHONE_INPUT)
        )
        el.clear()
        el.send_keys(phone)

    def fill_alt_telephone(self, phone: str):
        el = self.wait.until(
            EC.element_to_be_clickable(self.ALT_TELEPHONE_INPUT)
        )
        el.clear()
        el.send_keys(phone)

    def click_siguiente(self):
        btn = self.wait.until(
            EC.element_to_be_clickable(self.NEXT_BUTTON)
        )
        btn.click()

class CandidatePersonalInfoStep4Page:
    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    # --------- Locators ---------
    # Botón "Aceptar" del modal de Información Laboral
    MODAL_ACCEPT_BUTTON = (
        By.XPATH,
        "//div[contains(@class,'ant-modal')]"
        "//button[span[normalize-space()='Aceptar']]"
    )

    # Radio group "Es empleado de la universidad"
    IS_EMPLOYEE_GROUP = (By.ID, "is_employee")

    RADIO_SI_LABEL = (
        By.XPATH,
        "//div[@id='is_employee']"
        "//label[span[normalize-space()='Sí']]"
    )

    RADIO_NO_LABEL = (
        By.XPATH,
        "//div[@id='is_employee']"
        "//label[span[normalize-space()='No']]"
    )

    # Botón "Revisar información"
    REVIEW_BUTTON = (
        By.XPATH,
        "//div[contains(@class,'steps-action')]"
        "//button[span[normalize-space()='Revisar información']]"
    )

    # --------- Acciones ---------

    def wait_loaded(self):
        """
        Consideramos el step 4 cargado cuando se ve el grupo de radios
        'is_employee' (aunque haya modal encima).
        """
        self.wait.until(EC.visibility_of_element_located(self.IS_EMPLOYEE_GROUP))

    def close_info_modal_if_present(self):
        """
        Si el modal 'Información Laboral' está visible, hace clic en Aceptar.
        Si no aparece, continúa sin lanzar error.
        """
        try:
            btn = self.wait.until(
                EC.element_to_be_clickable(self.MODAL_ACCEPT_BUTTON)
            )
            btn.click()
            # Esperamos a que el modal desaparezca
            self.wait.until(
                EC.invisibility_of_element_located(self.MODAL_ACCEPT_BUTTON)
            )
        except TimeoutException:
            # No se mostró el modal, seguimos normal
            pass

    def set_is_employee(self, is_employee: bool):
        """
        Marca Sí o No en 'Es empleado de la universidad'.
        """
        locator = self.RADIO_SI_LABEL if is_employee else self.RADIO_NO_LABEL
        el = self.wait.until(EC.element_to_be_clickable(locator))
        el.click()

    def click_revisar_informacion(self):
        """
        Click en el botón 'Revisar información' para pasar al paso 5.
        """
        btn = self.wait.until(EC.element_to_be_clickable(self.REVIEW_BUTTON))
        btn.click()
        
class CandidatePersonalInfoReviewPage:
    """
    Step 5: Revisión de la información personal.
    Aquí se ve el resumen y el botón 'Registrar mi información'.
    """

    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    # Botón "Registrar mi información"
    REGISTER_BUTTON = (
        By.XPATH,
        "//div[contains(@class,'steps-action')]"
        "//button[span[normalize-space()='Registrar mi información']]"
    )

    def wait_loaded(self):
        # Consideramos que está cargado cuando se ve el botón Registrar mi información
        self.wait.until(EC.visibility_of_element_located(self.REGISTER_BUTTON))

    # ---------- helpers para leer el resumen ----------

    def _get_desc_value(self, label_text: str) -> str:
        """
        Busca en la tabla de descripciones el valor que corresponde
        a la etiqueta (Primer nombre, Segundo nombre, Apellido, etc).
        """
        locator = (
            By.XPATH,
            "//span[contains(@class,'ant-descriptions-item-label') "
            f"and normalize-space()='{label_text}']"
            "/following-sibling::span[contains(@class,'ant-descriptions-item-content')]"
        )
        el = self.wait.until(EC.visibility_of_element_located(locator))
        return el.text.strip()

    def get_full_name_lower(self) -> str:
        """
        Retorna 'primer segundo apellidos' en minúsculas.
        (Ej: 'juan carlos pérez gómez')
        """
        first = self._get_desc_value("Primer nombre")
        second = self._get_desc_value("Segundo nombre")
        last = self._get_desc_value("Apellido")
        full = f"{first} {second} {last}".strip()
        return full.lower()

    def click_registrar_informacion(self):
        btn = self.wait.until(EC.element_to_be_clickable(self.REGISTER_BUTTON))
        btn.click()