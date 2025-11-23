# --- ensure project root in sys.path ---
import sys, os, time
import allure
from _pytest.config import Config 
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
# --------------------------------------

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from config.config import settings
from datetime import datetime

# ========================
# Opciones de pytest
# ========================

def pytest_addoption(parser):
    parser.addoption("--browser", action="store", default=settings.BROWSER,
                     help="chrome|firefox|edge")
    parser.addoption("--headless", action="store", default=str(settings.HEADLESS).lower(),
                     help="true|false")

# ========================
# Fixtures base
# ========================

@pytest.fixture(scope="session")
def base_url():
    return settings.BASE_URL

@pytest.fixture(scope="session")
def qa_creds():
    return {
        "email": os.getenv("QA_USER_EMAIL", "qa.user@tu-app.com"),
        "password": os.getenv("QA_USER_PASS", "SuperSecreta123!")
    }

@pytest.fixture
def director_creds():
    return {
        "email": "director@ues.edu.sv",
        "password": "Password.1",
    }

@pytest.fixture(scope="session")
def candidate_creds():
    return {
        "email": os.getenv("CANDIDATE_USER_EMAIL", "candidato.qa@tu-app.com"),
        "password": os.getenv("CANDIDATE_USER_PASS", "SuperSecreta123!")
    }

@pytest.fixture
def rrhh_creds():
    email = os.getenv("RRHH_EMAIL")
    password = os.getenv("RRHH_PASSWORD")

    assert email, "Falta la variable de entorno RRHH_EMAIL en el .env"
    assert password, "Falta la variable de entorno RRHH_PASSWORD en el .env"

    return {
        "email": email,
        "password": password,
    }


@pytest.fixture(scope="session")
def financiero_creds():
    email = os.getenv("FINANCIERO_USER_EMAIL")
    password = os.getenv("FINANCIERO_USER_PASS")

    assert email, "Falta la variable de entorno FINANCIERO_EMAIL en el .env"
    assert password, "Falta la variable de entorno FINANCIERO_PASSWORD en el .env"

    return {
        "email": email,
        "password": password,
    }


@pytest.fixture(scope="session")
def admin_creds():
    email = os.getenv("ADMIN_USER_EMAIL")
    password = os.getenv("ADMIN_USER_PASS")

    assert email, "Falta la variable de entorno ADMIN_EMAIL en el .env"
    assert password, "Falta la variable de entorno ADMIN_PASSWORD en el .env"

    return {
        "email": email,
        "password": password,
    }


@pytest.fixture(scope="function")
def driver(request):
    browser  = request.config.getoption("--browser")
    headless = request.config.getoption("--headless") == "true"
    keep_open = os.getenv("KEEP_BROWSER_OPEN", "0") == "1"

    if browser == "chrome":
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        else:
            # Solo en modo visual:
            options.add_experimental_option("detach", True)  # deja Chrome abierto
            options.add_argument("--start-maximized")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        drv = webdriver.Chrome(options=options)

    elif browser == "firefox":
        options = FirefoxOptions()
        if headless:
            options.add_argument("-headless")
        drv = webdriver.Firefox(options=options)

    elif browser == "edge":
        options = EdgeOptions()
        if headless:
            options.add_argument("headless")
        drv = webdriver.Edge(options=options)

    else:
        raise ValueError(f"Navegador no soportado: {browser}")

    drv.implicitly_wait(settings.IMPLICIT_WAIT)
    drv.set_page_load_timeout(settings.PAGELOAD_TIMEOUT)
    yield drv

    if not keep_open:
        drv.quit()

@pytest.fixture       
def cod_cache(request):
    """Pequeño wrapper para guardar/leer el último código entre tests."""
    cache = request.config.cache
    KEY = "gc/ultimo_codigo"

    def set_code(code: str):
        cache.set(KEY, code)

    def get_code(default=None):
        return cache.get(KEY, default)

    return {"set": set_code, "get": get_code}

@pytest.fixture
def candidate_name_cache(request):
    """
    Wrapper para guardar/leer el nombre completo del candidato entre tests.
    """
    cache = request.config.cache
    KEY = "gc/candidate_full_name"

    def set_name(name: str):
        cache.set(KEY, name)

    def get_name(default=None):
        return cache.get(KEY, default)

    return {"set": set_name, "get": get_name}

@pytest.fixture
def materia_grupo_label():
    """
    Devuelve el texto completo del detalle de la materia/grupo
    desde el entorno (.env).
    """
    value = os.getenv("CONTRACT_SUBJECT_GROUP")
    if not value:
        pytest.skip(
            "No se ha configurado CONTRACT_SUBJECT_GROUP en el .env; "
            "define la materia a usar antes de correr este test."
        )
    return value

# ========================
# Utilidades de evidencia
# ========================

# screenshot automático en fallas

def _ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def save_screenshot_file(driver, name: str) -> str:
    """
    Guarda un PNG en disco (para conservar archivo físico).
    Retorna la ruta.
    """
    _ensure_dir("reports/screenshots")
    ts = time.strftime("%Y%m%d_%H%M%S")
    path = f"reports/screenshots/{ts}_{name}.png"
    driver.save_screenshot(path)
    return path

def snap_and_attach(request, driver, name: str) -> str:
    """
    Guarda el archivo y también lo adjunta embebido al HTML.
    Devuelve la ruta del archivo guardado.
    """
    path = save_screenshot_file(driver, name)
    attach_png_to_report(request, driver, name)
    print(f"[EVIDENCIA] {name} -> {path}")
    return path

def attach_png_to_report(request, driver, name: str):
    """
    Adjunta PNG embebido al reporte HTML (pytest-html).
    Requiere ejecutar con:
      --html=reports/report.html --self-contained-html
    """
    png_bytes = driver.get_screenshot_as_png()
    pytest_html = request.config.pluginmanager.getplugin("html")
    if pytest_html is None:
        # pytest-html no está activo; evitar crash
        return
    extra = getattr(request.node, "extra", [])
    extra.append(pytest_html.extras.png(png_bytes, name))
    request.node.extra = extra

@pytest.fixture
def evidencia(request, driver):
    """
    Helper:
        evidencia("antes_de_submit")

    Hace 3 cosas:
    - Guarda PNG en reports/screenshots
    - Lo adjunta al reporte HTML (pytest-html)
    - Lo adjunta al reporte de Allure
    """
    def _take(name: str):
        # 1) Screenshot como bytes (para Allure)
        png_bytes = driver.get_screenshot_as_png()

        # 2) Adjuntar a Allure
        try:
            allure.attach(
                png_bytes,
                name=name,
                attachment_type=allure.attachment_type.PNG,
            )
        except Exception:
            # Por si se ejecuta sin allure-pytest, que no truene
            pass

        # 3) Mantener tu flujo actual (disco + pytest-html)
        return snap_and_attach(request, driver, name)

    return _take

# ========================
# Screenshot automático en fallas
# (adjunta al HTML y guarda archivo)
# ========================

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    - Mantiene tu screenshot en fallas.
    - Además, si pytest-html está activo, adjunta la imagen al reporte.
    """
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call":
        d = item.funcargs.get("driver")
        if d and rep.failed:
            # Guardar en carpeta simple (legacy)
            os.makedirs("screenshots", exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            legacy_path = f"screenshots/{item.name}_{ts}.png"
            d.save_screenshot(legacy_path)

            # 2) Adjuntar a Allure
            try:
                png_bytes = d.get_screenshot_as_png()
                allure.attach(
                    png_bytes,
                    name=f"FAIL_{item.name}",
                    attachment_type=allure.attachment_type.PNG,
                )
            except Exception:
                pass

            # 3) Adjuntar al HTML y guardar en reports/
            try:
                pytest_html = item.config.pluginmanager.getplugin("html")
                if pytest_html:
                    png_bytes = d.get_screenshot_as_png()
                    extra = getattr(item, "extra", [])
                    extra.append(pytest_html.extras.png(png_bytes, f"FAIL_{item.name}"))
                    item.extra = extra
                    save_screenshot_file(d, f"FAIL_{item.name}")
            except Exception:
                pass