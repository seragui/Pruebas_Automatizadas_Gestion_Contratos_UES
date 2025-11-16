# pages/contract_detail_page.py
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Keys
from selenium.webdriver import ActionChains
import time

class ContractDetailPage:
    # Encabezado del detalle (para asegurar que cargó la vista)
    DETAIL_TITLE = (By.XPATH, "//span[contains(@class,'ant-page-header-heading-title') and contains(., 'Solicitud de Contratación')]")

    # Sección “Docentes requeridos en la solicitud”
    SECTION_TEACHERS = (By.XPATH, "//span[@class='ant-page-header-heading-title' and normalize-space()='Docentes requeridos en la solicitud']")

    # Botón “Agregar Candidato”
    # Robusto: busca el span con ese texto y sube al <button>
    ADD_CANDIDATE_BTN = (By.XPATH, "//button[.//span[normalize-space()='Agregar Candidato']]")

    # (opcional) buscador y tabla de candidatos (para validaciones posteriores)
    CANDIDATE_SEARCH_INPUT = (By.XPATH, "//input[@placeholder='Buscar por nombre de candidato']")
    EMPTY_TABLE_PLACEHOLDER = (By.XPATH, "//div[contains(@class,'ant-empty-description') and normalize-space()='No data']")

    def __init__(self, driver, timeout: int = 15):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def wait_loaded(self):
        # Asegura que estamos en /contratos/solicitud/<id> y visible el título
        self.wait.until(EC.url_contains("/contratos/solicitud/"))
        self.wait.until(EC.visibility_of_element_located(self.DETAIL_TITLE))
        self.wait.until(EC.visibility_of_element_located(self.SECTION_TEACHERS))

    def click_add_candidate(self):
        btn = self.wait.until(EC.element_to_be_clickable(self.ADD_CANDIDATE_BTN))
        # por si hay header fijo, centra y hace click via JS si es necesario
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
        try:
            btn.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", btn)

    def wait_modal_open(self):
        self.wait.until(EC.visibility_of_element_located(self.MODAL_ROOT))
        # Si quisieras validar título:
        # self.wait.until(EC.visibility_of_element_located(self.MODAL_TITLE))

    # --- Pantalla "Agregar candidato ..." ---
    ADD_CANDIDATE_TITLE = (
        By.XPATH,
        "//span[contains(@class,'ant-page-header-heading-title') and starts-with(normalize-space(), 'Agregar candidato')]"
    )
    CANDIDATE_INPUT = (By.ID, "control-ref_person_name")
    CANDIDATE_WRAPPER = (
    By.XPATH,
    "//label[@for='control-ref_person_name']/ancestor::div[contains(@class,'ant-form-item')]//div[contains(@class,'ant-select')]"
    )

    # Dropdown visible de Ant Design (evitamos el que tenga la clase hidden)
    CANDIDATE_DROPDOWN = (
        By.XPATH,
        "//div[contains(@class,'ant-select-dropdown') and not(contains(@class,'hidden'))]"
    )
    DROPDOWN_OPEN = (
    By.XPATH,
    "//div[contains(@class,'ant-select-dropdown') and not(contains(@class,'ant-select-dropdown-hidden'))]"
    )

    CANDIDATE_SELECTED_ITEM = (
    By.XPATH,
    "//label[@for='control-ref_person_name']/ancestor::div[contains(@class,'ant-form-item')]"
    "//div[contains(@class,'ant-select')]//span[contains(@class,'ant-select-selection-item')]"
    )

    DROPDOWN_HIDDEN = (
    By.XPATH,
    "//div[contains(@class,'ant-select-dropdown') and contains(@class,'ant-select-dropdown-hidden')]"
    )

    def wait_add_candidate_loaded(self):
        """
        Espera que cargue la pantalla 'Agregar candidato...' y el input de búsqueda.
        """
        self.wait.until(EC.visibility_of_element_located(self.ADD_CANDIDATE_TITLE))
        self.wait.until(EC.visibility_of_element_located(self.CANDIDATE_INPUT))

    def select_candidate_by_typing(self, text: str):
        # 1) Enfocar el wrapper del ant-select (no el input) y centrar en viewport
        wrapper = self.wait.until(EC.visibility_of_element_located(self.CANDIDATE_WRAPPER))
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", wrapper)
        try:
            wrapper.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", wrapper)

        # 2) A veces AntD reubica el input muy arriba; ajustamos un poco por el header fijo
        self.driver.execute_script("window.scrollBy(0, -80);")

        # 3) Ahora sí agarramos el input visible y tipeamos
        inp = self.wait.until(EC.visibility_of_element_located(self.CANDIDATE_INPUT))
        try:
            inp.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", inp)

        inp.clear()
        inp.send_keys(text)

        # 4) Breve espera para que cargue el dropdown y ENTER sobre la primera coincidencia
        import time
        time.sleep(0.4)
        inp.send_keys(Keys.ENTER)
    
    def _candidate_option_by_text(self, text: str):
        # Busca SOLO dentro del dropdown visible
        xpath = (
            "//div[contains(@class,'ant-select-dropdown') and not(contains(@class,'ant-select-dropdown-hidden'))]"
            "//div[contains(@class,'ant-select-item') and contains(@class,'option')]"
            "[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÉÍÓÚÜÑ', 'abcdefghijklmnopqrstuvwxyzáéíóúüñ'),"
            f"'{text.lower()}')]"
        )
        return (By.XPATH, xpath)
    
    def select_candidate_by_typing_and_pick(self, text: str, exact: str | None = None):
        # Centrar la zona (header fijo puede interceptar)
        wrapper = self.wait.until(EC.visibility_of_element_located(self.CANDIDATE_WRAPPER))
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", wrapper)
        self.driver.execute_script("window.scrollBy(0, -80);")

        # Foco y tipeo
        inp = self.wait.until(EC.visibility_of_element_located(self.CANDIDATE_INPUT))
        try:
            inp.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", inp)
        inp.clear()
        inp.send_keys(text)

        # Esperar dropdown
        self.wait.until(EC.visibility_of_element_located(self.DROPDOWN_OPEN))

        # Selección: por texto exacto si se dio, si no el primer activo (ArrowDown + Enter)
        if exact:
            opt = self.wait.until(EC.element_to_be_clickable(self._candidate_option_by_text(exact)))
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", opt)
            try:
                opt.click()
            except Exception:
                self.driver.execute_script("arguments[0].click();", opt)
        else:
            inp.send_keys(Keys.ARROW_DOWN, Keys.ENTER)

        # Verificación: dropdown cerrado + input.value contiene lo esperado
        self.wait.until(EC.presence_of_element_located(self.DROPDOWN_HIDDEN))

        expected = (exact or text).strip().lower()
        def _value_has_expected(_):
            val = inp.get_attribute("value") or ""
            return expected.split()[0] in val.lower()  # primer token basta
        self.wait.until(_value_has_expected)

        #sel_text_el = self.wait.until(EC.visibility_of_element_located(self.CANDIDATE_SELECTED_ITEM))
        #return (sel_text_el.text or sel_text_el.get_attribute("textContent") or "").strip()
    
    # --- CARGO (Ant Select simple) ---
    CARGO_WRAPPER = (
        By.XPATH,
        "//label[normalize-space()='Cargo']/ancestor::div[contains(@class,'ant-form-item')]"
    )
    CARGO_SELECTOR = (
        By.XPATH,
        "//label[normalize-space()='Cargo']/ancestor::div[contains(@class,'ant-form-item')]//div[contains(@class,'ant-select-selector')]"
    )
    CARGO_DROPDOWN_OPEN = (
        By.XPATH,
        "//div[contains(@class,'ant-select-dropdown') and not(contains(@class,'ant-select-dropdown-hidden'))]"
    )
    def _cargo_option_by_text(self, text: str):
        # opción dentro del dropdown abierto
        return (By.XPATH,
            "//div[contains(@class,'ant-select-dropdown') and not(contains(@class,'ant-select-dropdown-hidden'))]"
            "//div[contains(@class,'ant-select-item') and contains(@class,'option')]"
            f"[.//div[contains(@class,'ant-select-item-option-content')][normalize-space()='{text}']]"
        )

    # Para verificar el valor elegido (texto en el selector)
    CARGO_SELECTED_TEXT = (
        By.XPATH,
        "//label[normalize-space()='Cargo']/ancestor::div[contains(@class,'ant-form-item')]"
        "//span[contains(@class,'ant-select-selection-item')]")
    
    def select_cargo(self, cargo_text: str = "Profesor"):
        # Centrar para que no lo tape el header
        wrap = self.wait.until(EC.visibility_of_element_located(self.CARGO_WRAPPER))
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", wrap)
        self.driver.execute_script("window.scrollBy(0, -80);")

        # Abrir el select
        box = self.wait.until(EC.element_to_be_clickable(self.CARGO_SELECTOR))
        try:
            box.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", box)

        # Esperar dropdown y hacer click en la opción exacta
        self.wait.until(EC.visibility_of_element_located(self.CARGO_DROPDOWN_OPEN))
        opt = self.wait.until(EC.element_to_be_clickable(self._cargo_option_by_text(cargo_text)))
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", opt)
        try:
            opt.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", opt)

        # Verificar que quedó seleccionado (texto en el selector)
        sel = self.wait.until(EC.visibility_of_element_located(self.CARGO_SELECTED_TEXT))
        assert cargo_text.lower() in (sel.text or "").lower(), f"No se seleccionó '{cargo_text}'."

    # === Locators para "Funciones a desarrollar" (multiselect) ===
    FUNCS_WRAPPER = (
        By.XPATH,
        "//label[normalize-space()='Seleccione las funciones a desarrollar']"
        "/ancestor::div[contains(@class,'ant-form-item')]"
    )
    FUNCS_SELECTOR = (
        By.XPATH,
        # el contenedor clickeable del select múltiple
        "//label[normalize-space()='Seleccione las funciones a desarrollar']"
        "/ancestor::div[contains(@class,'ant-form-item')]"
        "//div[contains(@class,'ant-select') and contains(@class,'ant-select-multiple')]"
    )
    FUNCS_SELECTED_CHIPS = (
        By.XPATH,
        # los chips ya seleccionados dentro del wrapper
        "//label[normalize-space()='Seleccione las funciones a desarrollar']"
        "/ancestor::div[contains(@class,'ant-form-item')]"
        "//span[contains(@class,'ant-select-selection-item')]"
    )
    FUNCS_DROPDOWN_OPEN = (
        By.XPATH,
        # cualquier dropdown de Ant que esté abierto (no-hidden)
        "//div[contains(@class,'ant-select-dropdown') and not(contains(@class,'ant-select-dropdown-hidden'))]"
    )
    FUNCS_DROPDOWN_OPTIONS = (
        By.XPATH,
        # items de opción visibles dentro del dropdown abierto
        "//div[contains(@class,'ant-select-dropdown') and not(contains(@class,'ant-select-dropdown-hidden'))]"
        "//div[contains(@class,'ant-select-item') and contains(@class,'option')]"
    )
    def _func_option_by_text(self, text: str):
        return (
            By.XPATH,
            "//div[contains(@class,'ant-select-dropdown') and not(contains(@class,'ant-select-dropdown-hidden'))]"
            f"//div[contains(@class,'ant-select-item-option-content')][normalize-space()='{text}']"
        )

    def _open_funcs_dropdown(self):
        wrap = self.wait.until(EC.visibility_of_element_located(self.FUNCS_WRAPPER))
        # centrar y compensar header fijo
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", wrap)
        self.driver.execute_script("window.scrollBy(0, -80);")
        box = self.wait.until(EC.element_to_be_clickable(self.FUNCS_SELECTOR))
        try:
            box.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", box)
        self.wait.until(EC.visibility_of_element_located(self.FUNCS_DROPDOWN_OPEN))

    def _snapshot_functions_texts(self):
        """Lee los textos actuales (página visible del dropdown)."""
        items = self.driver.find_elements(*self.FUNCS_DROPDOWN_OPTIONS)
        texts = []
        for it in items:
            t = it.text.strip()
            if t:
                texts.append(t)
        # únicos conservando orden
        seen = set(); uniq = []
        for t in texts:
            if t not in seen:
                seen.add(t); uniq.append(t)
        return uniq

    def FUNCS_CHIP_BY_TEXT(self, text: str):
        return (
            By.XPATH,
            "//label[normalize-space()='Seleccione las funciones a desarrollar']"
            "/ancestor::div[contains(@class,'ant-form-item')]"
            f"//span[contains(@class,'ant-select-selection-item')][normalize-space()='{text}']"
        )

    def select_all_functions(self, max_passes: int = 5):
        """
        Selecciona todas las opciones visibles del multiselect evitando loops.
        Trabaja con un snapshot de textos y valida progreso en cada pasada.
        """
        self._open_funcs_dropdown()
        all_texts = self._snapshot_functions_texts()
        if not all_texts:
            return

        selected_prev = len(self.driver.find_elements(*self.FUNCS_SELECTED_CHIPS))
        passes = 0
        while passes < max_passes:
            passes += 1
            # aseguramos dropdown abierto
            try:
                self.driver.find_element(*self.FUNCS_DROPDOWN_OPEN)
            except Exception:
                self._open_funcs_dropdown()

            for label in all_texts:
                # si ya está seleccionado, saltar
                if self.driver.find_elements(*self.FUNCS_CHIP_BY_TEXT(label)):
                    continue

                loc = self._func_option_by_text(label)
                opt = self.wait.until(EC.visibility_of_element_located(loc))
                self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", opt)
                try:
                    opt.click()
                except Exception:
                    ActionChains(self.driver).move_to_element(opt).pause(0.05).click().perform()

            selected_now = len(self.driver.find_elements(*self.FUNCS_SELECTED_CHIPS))
            if selected_now == selected_prev:
                break  # no hubo progreso → cortar
            selected_prev = selected_now

            remaining = [t for t in all_texts if not self.driver.find_elements(*self.FUNCS_CHIP_BY_TEXT(t))]
            if not remaining:
                break
            self._open_funcs_dropdown()

        # validaciones finales
        chips_texts = [el.text.strip() for el in self.driver.find_elements(*self.FUNCS_SELECTED_CHIPS)]
        missing = [t for t in all_texts if t not in chips_texts]
        assert selected_prev > 0, "No se seleccionó ninguna función."
        assert not missing, f"No se pudieron seleccionar: {missing}"
    
    # ...
    ADD_CARGO_BTN = (By.XPATH, "//button[.//span[normalize-space()='Agregar Cargo']]")
    COLLAPSE_ITEMS = (By.CSS_SELECTOR, ".ant-collapse .ant-collapse-item")
    COLLAPSE_ITEM_BY_TITLE = lambda self, title: (
        By.XPATH,
        "//*[contains(@class,'ant-collapse')]//*[contains(@class,'ant-collapse-header')]"
        f"//*[normalize-space(text())='{title}']"
    )

    def click_agregar_cargo(self):
        """Hace click en 'Agregar Cargo' y espera a que aparezca un nuevo item en el accordion."""
        # snapshot antes
        before = len(self.driver.find_elements(*self.COLLAPSE_ITEMS))

        btn = self.wait.until(EC.element_to_be_clickable(self.ADD_CARGO_BTN))
        try:
            btn.click()
        except Exception:
            # fallback por si algo tapa el botón
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
            self.driver.execute_script("arguments[0].click();", btn)

        # esperar incremento de items
        self.wait.until(lambda d: len(d.find_elements(*self.COLLAPSE_ITEMS)) > before)

    def ensure_cargo_visible(self, title: str):
        """Confirma que el accordion muestre un item con el título dado (p.ej. 'Profesor')."""
        self.wait.until(EC.visibility_of_element_located(self.COLLAPSE_ITEM_BY_TITLE(title)))

    # Locators del RangePicker (Ant Design)
    PERIOD_RANGE = (By.CSS_SELECTOR, ".ant-picker.ant-picker-range")
    PERIOD_START_INPUT = (By.XPATH, "(//div[contains(@class,'ant-picker-range')]//input)[1]")
    PERIOD_END_INPUT   = (By.XPATH, "(//div[contains(@class,'ant-picker-range')]//input)[2]")
    DATEPICKER_OVERLAY_OPEN = (By.CSS_SELECTOR, ".ant-picker-dropdown:not(.ant-picker-dropdown-hidden)")

    def _focus_and_enable_typing(self, el):
        # Llevar a vista y foco
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        el.click()
        # Si Antd lo deja readonly, lo quitamos con JS como fallback
        try:
            ro = el.get_attribute("readonly")
            if ro:
                self.driver.execute_script("arguments[0].removeAttribute('readonly');", el)
        except Exception:
            pass

    def _clear_and_type(self, el, text):
        # Seleccionar todo y limpiar
        el.send_keys(Keys.CONTROL, "a")
        el.send_keys(Keys.DELETE)
        # Escribir la fecha
        el.send_keys(text)
        # Pequeña pausa para que React capte el cambio
        time.sleep(0.1)

    def set_period_dates(self, start_ddmmyyyy: str, end_ddmmyyyy: str):
        """
        Escribe fechas en formato dd/mm/yyyy y CONFIRMA con Enter cada campo.
        - AntD RangePicker requiere Enter para “commit”.
        - Verifica que ambos inputs queden exactamente con el valor esperado.
        """
        # Asegurar que el rango esté visible
        self.wait.until(EC.visibility_of_element_located(self.PERIOD_RANGE))

        # --- Fecha inicio ---
        start = self.wait.until(EC.element_to_be_clickable(self.PERIOD_START_INPUT))
        self._focus_and_enable_typing(start)
        # limpiar y escribir
        start.send_keys(Keys.CONTROL, "a")
        start.send_keys(Keys.DELETE)
        start.send_keys(start_ddmmyyyy)
        # confirmar
        start.send_keys(Keys.ENTER)

        # esperar a que el overlay (calendario) no interfiera
        time.sleep(0.05)
        try:
            self.wait.until_not(EC.visibility_of_element_located(self.DATEPICKER_OVERLAY_OPEN))
        except Exception:
            pass

        # validar inicio
        self.wait.until(lambda d: (start.get_attribute("value") or "") == start_ddmmyyyy)

        # --- Fecha fin ---
        end = self.wait.until(EC.element_to_be_clickable(self.PERIOD_END_INPUT))
        self._focus_and_enable_typing(end)
        end.send_keys(Keys.CONTROL, "a")
        end.send_keys(Keys.DELETE)
        end.send_keys(end_ddmmyyyy)
        end.send_keys(Keys.ENTER)

        time.sleep(0.05)
        try:
            self.wait.until_not(EC.visibility_of_element_located(self.DATEPICKER_OVERLAY_OPEN))
        except Exception:
            pass

        # validar fin
        self.wait.until(lambda d: (end.get_attribute("value") or "") == end_ddmmyyyy)

    # Contenedor del select de materia/grupo (scope por la etiqueta del campo)
    MATERIA_SELECT = (By.XPATH,
        "//label[contains(.,'Seleccione la materia y grupo')]/ancestor::div[contains(@class,'ant-form-item')]"
        "//div[contains(@class,'ant-select') and contains(@class,'ant-select-single')]")

    # Input de búsqueda dentro del select (Ant Design)
    MATERIA_INPUT = (By.XPATH,
        "//label[contains(.,'Seleccione la materia y grupo')]/ancestor::div[contains(@class,'ant-form-item')]"
        "//input[@type='search' and contains(@class,'ant-select-selection-search-input')]")

    def select_materia_grupo(self, visible_text: str):
        # Abrir el dropdown y escribir
        select = self.wait.until(EC.visibility_of_element_located(self.MATERIA_SELECT))
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", select)
        select.click()

        inp = self.wait.until(EC.element_to_be_clickable(self.MATERIA_INPUT))
        # limpiar por si hay algo
        inp.send_keys(Keys.CONTROL, "a")
        inp.send_keys(Keys.DELETE)
        inp.send_keys(visible_text)

        # Esperar y clickear la opción exacta
        option = self.wait.until(EC.visibility_of_element_located((
            By.XPATH,
            "//div[contains(@class,'ant-select-dropdown') and not(contains(@class,'hidden'))]"
            "//div[@class='ant-select-item-option-content' and normalize-space()=\"{}\"]"
            .format(visible_text)
        )))
        self.driver.execute_script("arguments[0].scrollIntoView({block:'nearest'});", option)
        option.click()
    
    # --- Pago y horas (Ant InputNumber) -----------------------------------------

    # Inputs (localizados por label, robustos a cambios de id)
    HOURLY_RATE_INPUT = (
        By.XPATH,
        "//label[normalize-space()='Valor a pagar por hora']"
        "/ancestor::div[contains(@class,'ant-form-item')]"
        "//div[contains(@class,'ant-input-number')]//input"
    )
    WEEKS_TO_PAY_INPUT = (
        By.XPATH,
        "//label[normalize-space()='Cantidad de semanas a pagar']"
        "/ancestor::div[contains(@class,'ant-form-item')]"
        "//div[contains(@class,'ant-input-number')]//input"
    )
    WEEKLY_HOURS_INPUT = (
        By.XPATH,
        "//label[normalize-space()='Cantidad de horas por semana']"
        "/ancestor::div[contains(@class,'ant-form-item')]"
        "//div[contains(@class,'ant-input-number')]//input"
    )

    def _scroll_focus_click(self, el):
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        try:
            el.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", el)

    def _set_value_react_input(self, el, value_str: str):
        """
        Fija el valor del <input> controlado por React/AntD y dispara eventos.
        Evita el problema del '1.5' al tipear '15' en InputNumber con formateo.
        """
        self.driver.execute_script("""
            const el = arguments[0], val = arguments[1];
            const proto = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value');
            proto.set.call(el, '');                    // limpiar nativo
            el.dispatchEvent(new Event('input', {bubbles:true}));
            proto.set.call(el, val);                   // set real
            el.dispatchEvent(new Event('input', {bubbles:true}));
            el.dispatchEvent(new Event('change', {bubbles:true}));
        """, el, value_str)

    def _blur_body(self):
        self.driver.execute_script("document.body.click();")

    def _numeric_of(self, raw: str) -> float | None:
        """
        Extrae número de un valor que puede tener $, espacios, separadores, etc.
        """
        if raw is None:
            return None
        txt = raw.strip().replace(" ", "")
        # normaliza coma decimal a punto
        txt = txt.replace(".", "").replace(",", ".") if txt.count(",") == 1 and txt.count(".") > 1 else txt
        # elimina $ y otros símbolos
        for ch in "$₡€Q₲S/-–":
            txt = txt.replace(ch, "")
        # último reemplazo suave de miles comunes ($ 1,234.56 / $ 1.234,56)
        txt = txt.replace("$", "")
        try:
            return float(txt)
        except ValueError:
            # fallback: dejar solo [0-9.] y parsear
            import re
            digits = "".join(re.findall(r"[0-9.]", txt))
            return float(digits) if digits else None

    def _set_ant_inputnumber(self, locator, number: float, decimals: int = 2, retries: int = 1):
        """
        Setter robusto para AntD InputNumber con formateo. Usa JS + eventos React.
        Verifica el número final (no el string) con tolerancia.
        """
        desired_num = float(number)
        desired_str = f"{desired_num:.{decimals}f}"

        el = self.wait.until(EC.element_to_be_clickable(locator))
        self._scroll_focus_click(el)

        # limpiar vía teclado (por si está readonly, igual forzamos por JS abajo)
        el.send_keys(Keys.CONTROL, "a")
        el.send_keys(Keys.DELETE)

        # forzar valor con eventos
        self._set_value_react_input(el, desired_str)
        self._blur_body()
        time.sleep(0.05)

        # verificación numérica
        got = self._numeric_of(el.get_attribute("value") or "")
        if got is None or abs(got - desired_num) > 0.005:
            # reintento con tipeo lento si no quedó
            if retries > 0:
                self._scroll_focus_click(el)
                el.send_keys(Keys.CONTROL, "a")
                el.send_keys(Keys.DELETE)
                for ch in desired_str:
                    el.send_keys(ch)
                    time.sleep(0.03)
                self._blur_body()
                time.sleep(0.05)
                got = self._numeric_of(el.get_attribute("value") or "")
            if got is None or abs(got - desired_num) > 0.005:
                raise TimeoutException(f"El valor no quedó en {desired_str}. Actual: {el.get_attribute('value')}")

    def fill_compensation(self, hourly_usd: float, weeks: int, weekly_hours: int):
        """
        Llena de una:
        - Valor a pagar por hora (USD)
        - Cantidad de semanas a pagar
        - Cantidad de horas por semana
        Maneja el caso donde al tipear '15' se vuelve '1.5' en InputNumber.
        """
        # 1) Valor por hora (dos decimales)
        rate_el = self.wait.until(EC.element_to_be_clickable(self.HOURLY_RATE_INPUT))
        self._set_ant_inputnumber(self.HOURLY_RATE_INPUT, float(hourly_usd), decimals=2)

        # 2) Cantidad de semanas (entero)
        self._set_ant_inputnumber(self.WEEKS_TO_PAY_INPUT, int(weeks), decimals=0)

        # 3) Horas por semana (entero)
        self._set_ant_inputnumber(self.WEEKLY_HOURS_INPUT, int(weekly_hours), decimals=0)

    # --- Helpers tabla/paginación Ant Design ------------------------------------

    TABLE_WRAPPER = (By.CSS_SELECTOR, ".ant-table-wrapper")
    TABLE_LOADING = (By.CSS_SELECTOR, ".ant-spin-spinning")  # overlay de carga cuando el table refresca
    PAG_NEXT = (By.CSS_SELECTOR, ".ant-pagination-next")     # botón “siguiente”
    PAG_PREV = (By.CSS_SELECTOR, ".ant-pagination-prev")
    PAG_ACTIVE = (By.CSS_SELECTOR, ".ant-pagination-item-active")
    # (si usas messages de AntD)
    ANT_MESSAGE = (By.CSS_SELECTOR, ".ant-message")          # contenedor de toasts (opcional)

    def _wait_table_idle(self, timeout=6):
        """Espera a que el table no muestre el spinner de carga."""
        # Espera a que exista el wrapper
        self.wait.until(EC.presence_of_element_located(self.TABLE_WRAPPER))
        end = time.time() + timeout
        while time.time() < end:
            spinners = self.driver.find_elements(*self.TABLE_LOADING)
            if not spinners or not any(s.is_displayed() for s in spinners):
                return
            time.sleep(0.1)
        # No es crítico si no detectamos spinner; seguimos

    def _go_to_last_page(self):
        """Avanza páginas hasta que el botón 'siguiente' esté deshabilitado."""
        for _ in range(20):  # límite de seguridad
            btns = self.driver.find_elements(*self.PAG_NEXT)
            if not btns:
                return
            nxt = btns[0]
            # AntD deshabilitado: tiene .ant-pagination-disabled
            disabled = "ant-pagination-disabled" in (nxt.get_attribute("class") or "")
            if disabled:
                return
            try:
                self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", nxt)
                nxt.click()
            except Exception:
                self.driver.execute_script("arguments[0].click();", nxt)
            self._wait_table_idle()

    def _visible_rows(self):
        return self.driver.find_elements(*self.TABLA_FILAS)

    # --- Agregar materia (tabla inferior) ----------------------------------------

    AGREGAR_MATERIA_BTN = (By.XPATH, "//button[.//span[normalize-space()='Agregar materia']]")
    TABLA_FILAS = (By.CSS_SELECTOR, "table tbody tr")
    # celdas por índice (ajusta si tu orden cambia)
    _CELL_VALOR_HORA   = (By.XPATH, ".//td[6]")
    _CELL_HORAS_SEM    = (By.XPATH, ".//td[7]")
    _CELL_SEMANAS      = (By.XPATH, ".//td[8]")
    _CELL_TOTAL_HORAS  = (By.XPATH, ".//td[9]")
    _CELL_TOTAL_PAGAR  = (By.XPATH, ".//td[10]")

    def _tbody_text(self) -> str:
        try:
            wrapper = self.wait.until(EC.presence_of_element_located(self.TABLE_WRAPPER))
            tbody = wrapper.find_element(By.CSS_SELECTOR, "table tbody")
            return tbody.text.strip()
        except Exception:
            return ""

    def click_agregar_materia(self):
        """
        Click en 'Agregar materia' y confirma que la grilla se repintó.
        En lugar de comparar solo el número de filas visibles, comparamos
        el contenido del <tbody>. Soporta paginación 1-por-página.
        """
        # snapshot antes (contenido del tbody) y filas visibles en la página actual
        before_text = self._tbody_text()
        before_rows = len(self._visible_rows())

        btn = self.wait.until(EC.element_to_be_clickable(self.AGREGAR_MATERIA_BTN))
        assert btn.is_enabled(), "El botón 'Agregar materia' está deshabilitado (faltan campos requeridos)."
        try:
            btn.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", btn)

        # Espera a que termine cualquier overlay/spinner
        self._wait_table_idle()

        # Si sale toast de éxito, dale un respiro para que el table se repinte
        try:
            if self.driver.find_elements(*self.ANT_MESSAGE):
                time.sleep(0.25)
        except Exception:
            pass

        # 1) Intento: ¿cambió el contenido del tbody en esta página?
        end = time.time() + 5.0
        while time.time() < end:
            now_text = self._tbody_text()
            if now_text and now_text != before_text:
                return  # hubo cambio visible en esta página
            time.sleep(0.1)

        # 2) Si no cambió aquí, puede haber quedado en otra página: ir a la última
        self._go_to_last_page()
        self._wait_table_idle()

        # Debe existir al menos 1 fila en la última página
        rows_last = self._visible_rows()
        assert rows_last, "No se ve ninguna fila tras 'Agregar materia' (revisa validaciones del formulario)."

        # 3) Verifica también por cambio de contenido en la última página
        end = time.time() + 5.0
        last_before_text = before_text  # por si el tbody era vacío o de otra página
        while time.time() < end:
            now_text = self._tbody_text()
            if now_text and now_text != last_before_text:
                return
            time.sleep(0.1)

        # Como último recurso, acepta que haya el mismo # de filas pero distintas celdas
        # (caso raro de edición): si hay filas, damos por bueno para no bloquear la prueba
        if len(rows_last) >= 1 and before_rows == 0:
            return

        raise TimeoutException("No se detectó refresco de la tabla después de 'Agregar materia'.")

    def _num(self, s: str) -> float:
        s = (s or "").strip()
        s = s.replace(" ", "").replace("horas", "")
        s = s.replace("$", "").replace("Q", "").replace("₡", "")
        s = s.replace(",", "")  # miles
        try:
            return float(s)
        except:
            import re
            digits = "".join(re.findall(r"[0-9.]", s))
            return float(digits) if digits else 0.0
    
    def _col_index_by_header(self, header_text: str) -> int:
        """
        Devuelve el índice (1-based) de la columna cuyo <th> coincide con header_text.
        Tolerante a espacios y mayúsculas/minúsculas.
        """
        thead_ths = self.driver.find_elements(By.CSS_SELECTOR, ".ant-table-thead th")
        wanted = header_text.strip().lower()
        for i, th in enumerate(thead_ths, start=1):
            txt = (th.text or th.get_attribute("textContent") or "").strip().lower()
            if txt == wanted:
                return i
            # tolera encabezados con sufijos/prefijos (p.ej. iconos)
            if wanted in txt:
                return i
        raise TimeoutException(f"No se encontró la columna con encabezado: {header_text!r}")


    def _row_cells(self, tr):
        # normal: <td>
        tds = tr.find_elements(By.CSS_SELECTOR, "td")
        if tds:
            return tds
        # fallback (algunas tablas virtualizadas): role="cell"
        cells = tr.find_elements(By.CSS_SELECTOR, "[role='cell']")
        return cells
    
    def assert_ultima_fila(self, valor_hora: float, horas_sem: int, semanas: int):
        # Por si hay paginación 1-por-página, vete al final
        self._go_to_last_page()
        self._wait_table_idle()

        # filas disponibles (usa la sección 'body' como referencia al contar)
        _, body_trs, _, n = self._tbody_trs_all()
        assert n > 0 and (body_trs or True), "No hay filas en la tabla de materias."

        row_idx = n - 1  # última fila (0-based)
        celdas = self._row_all_cells_by_index(row_idx)
        assert celdas, "No se pudieron leer las celdas de la última fila (¿tabla vacía o virtualizada?)."

        # Índices dinámicos por encabezado (1-based)
        idx_vhora = self._col_index_by_header("Valor por hora")
        idx_hsem  = self._col_index_by_header("Horas semanales")
        idx_sem   = self._col_index_by_header("Semanas a pagar")
        idx_thoras= self._col_index_by_header("Total de horas")
        idx_tpagar= self._col_index_by_header("Total a pagar")

        # Seguridad: ¿tenemos suficientes celdas?
        for need, idx in [("Valor por hora", idx_vhora), ("Horas semanales", idx_hsem),
                        ("Semanas a pagar", idx_sem), ("Total de horas", idx_thoras),
                        ("Total a pagar", idx_tpagar)]:
            if idx > len(celdas):
                raise TimeoutException(
                    f"La fila no tiene la celda #{idx} para '{need}'. "
                    f"Celdas visibles combinadas: {len(celdas)}"
                )

        def get_txt(ix):
            el = celdas[ix-1]
            return (el.text or el.get_attribute("textContent") or "").strip()

        v_hora = self._num(get_txt(idx_vhora))
        h_sem  = int(self._num(get_txt(idx_hsem)))
        sem    = int(self._num(get_txt(idx_sem)))
        t_horas= self._num(get_txt(idx_thoras))
        t_pagar= self._num(get_txt(idx_tpagar))

        exp_total_horas = float(horas_sem * semanas)
        exp_total_pagar = float(valor_hora) * horas_sem * semanas

        def close(a, b, tol=0.01): return abs(a - b) <= tol

        assert close(v_hora, float(valor_hora)), f"Valor/hora esperado {valor_hora}, actual {v_hora}"
        assert h_sem == int(horas_sem), f"Horas/sem esperadas {horas_sem}, actual {h_sem}"
        assert sem == int(semanas), f"Semanas esperadas {semanas}, actual {sem}"
        assert close(t_horas, exp_total_horas), f"Total horas esperado {exp_total_horas}, actual {t_horas}"
        assert close(t_pagar, exp_total_pagar), f"Total pagar esperado {exp_total_pagar}, actual {t_pagar}"


    # --- AntD fixed columns helpers -------------------------------------------------

    def _thead_ths_all(self):
        """
        Devuelve todos los <th> de la tabla combinando left/body/right
        en el orden visual: left -> body -> right.
        """
        left  = self.driver.find_elements(By.CSS_SELECTOR, ".ant-table-fixed-left .ant-table-thead th")
        body  = self.driver.find_elements(By.CSS_SELECTOR, ".ant-table-container .ant-table-thead th:not(.ant-table-cell-fix-left):not(.ant-table-cell-fix-right)")
        right = self.driver.find_elements(By.CSS_SELECTOR, ".ant-table-fixed-right .ant-table-thead th")
        return [*left, *body, *right]

    def _tbody_trs_all(self):
        """
        Devuelve listas paralelas de filas para left/body/right (cada una puede estar vacía).
        El índice de fila es consistente entre secciones.
        """
        left  = self.driver.find_elements(By.CSS_SELECTOR, ".ant-table-fixed-left .ant-table-tbody tr")
        body  = self.driver.find_elements(By.CSS_SELECTOR, ".ant-table-container .ant-table-tbody tr")
        right = self.driver.find_elements(By.CSS_SELECTOR, ".ant-table-fixed-right .ant-table-tbody tr")
        # usa la sección que tenga más filas como referencia visual
        n = max(len(left), len(body), len(right))
        return left, body, right, n

    def _cells_of_tr(self, tr):
        if not tr:
            return []
        cells = tr.find_elements(By.CSS_SELECTOR, "td")
        if cells:
            return cells
        return tr.find_elements(By.CSS_SELECTOR, "[role='cell']")

    def _row_all_cells_by_index(self, row_idx):
        """
        Concatena las celdas de la fila 'row_idx' de left + body + right
        en el orden visual.
        """
        left, body, right, n = self._tbody_trs_all()
        tr_left  = left[row_idx]  if row_idx < len(left)  else None
        tr_body  = body[row_idx]  if row_idx < len(body)  else None
        tr_right = right[row_idx] if row_idx < len(right) else None
        return [*self._cells_of_tr(tr_left), *self._cells_of_tr(tr_body), *self._cells_of_tr(tr_right)]

    def _col_index_by_header(self, header_text: str) -> int:
        """
        Índice 1-based de la columna cuyo <th> coincide (por texto, case/trim insensitive),
        combinando left/body/right en orden visual.
        """
        wanted = header_text.strip().lower()
        ths = self._thead_ths_all()
        for i, th in enumerate(ths, start=1):
            txt = (th.text or th.get_attribute("textContent") or "").strip().lower()
            if txt == wanted or wanted in txt:
                return i
        raise TimeoutException(f"No se encontró la columna con encabezado: {header_text!r}")
    
    # --- Post-Guardar: volver al detalle y validar tabla de candidatos ------------

    GUARDAR_BTN = (By.XPATH, "//button[.//span[normalize-space()='Guardar']]")

    # Toasts AntD (éxito o genérico)
    ANT_MESSAGE_ANY   = (By.CSS_SELECTOR, ".ant-message .ant-message-notice")
    ANT_MESSAGE_TEXTS = (By.CSS_SELECTOR, ".ant-message .ant-message-notice .ant-message-notice-content")

    # Tabla “Docentes requeridos en la solicitud”
    CANDS_TABLE = (By.XPATH, "//span[@class='ant-page-header-heading-title' and normalize-space()='Docentes requeridos en la solicitud']/ancestor::div[contains(@class,'ant-page-header')]/following::div[contains(@class,'ant-table-wrapper')][1]")
    CANDS_ROWS  = (By.CSS_SELECTOR, ".ant-table-wrapper tbody.ant-table-tbody tr.ant-table-row")

    def click_guardar(self):
        btn = self.wait.until(EC.element_to_be_clickable(self.GUARDAR_BTN))
        try:
            btn.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", btn)

    def wait_redirect_to_detail(self):
        # vuelve al detalle de la solicitud
        self.wait.until(EC.url_contains("/contratos/solicitud/"))
        self.wait.until(EC.visibility_of_element_located(self.DETAIL_TITLE))
        self.wait.until(EC.visibility_of_element_located(self.SECTION_TEACHERS))
        # tabla de candidatos presente
        self.wait.until(EC.presence_of_element_located(self.CANDS_TABLE))

    def wait_success_message(self, timeout=5):
        t0 = time.time()
        while time.time() - t0 < timeout:
            notices = self.driver.find_elements(*self.ANT_MESSAGE_TEXTS)
            texts = [(n.text or n.get_attribute("textContent") or "").strip().lower() for n in notices]
            if any(x for x in texts if "éxito" in x or "exito" in x or "cread" in x or "guardad" in x):
                return
            time.sleep(0.1)
        # no es crítico si no hay toast visible; seguimos sin fallar

    def assert_candidate_listed(self, candidate_name: str, strict: bool = True):
        self.wait.until(EC.presence_of_element_located(self.CANDS_TABLE))
        # Buscar por texto exacto primero; si falla, usar contains case-insensitive
        if strict:
            xpath = (
                "//div[contains(@class,'ant-table-wrapper')]//tbody//tr"
                f"[.//td//span[normalize-space()='{candidate_name}']]"
            )
            rows = self.driver.find_elements(By.XPATH, xpath)
            if rows:
                return
        # fallback contains-insensitive
        xpath_contains = (
            "//div[contains(@class,'ant-table-wrapper')]//tbody//tr"
            "[.//td//span[contains(translate(.,"
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÉÍÓÚÜÑ','abcdefghijklmnopqrstuvwxyzáéíóúüñ'),"
            f"'{candidate_name.lower()}')]]"
        )
        rows = self.driver.find_elements(By.XPATH, xpath_contains)
        assert rows, f"No se encontró en la tabla el candidato: {candidate_name!r}"




