import time
import pytest
from urllib.parse import urlparse

from pages.login_page import LoginPage
from pages.home_page import HomePage

# ==========================
# Utilidades
# ==========================

def _path(url: str) -> str:
    try:
        return urlparse(url).path.rstrip("/") or "/"
    except Exception:
        return url

def _open_and_wait(driver, url: str, pause: float = 0.6):
    driver.get(url)
    time.sleep(pause)  # pequeña espera por SPA redirects

def _is_home(driver) -> bool:
    """Heurística suave para detectar Home además del path '//'."""
    p = _path(driver.current_url)
    if p in ("/", ""):
        return True
    # Heurística extra (ajusta a tu UI si quieres):
    src = (driver.page_source or "").lower()
    return "universidad de el salvador" in src or "sesión iniciada como" in src

def _assert_redirected_to_home(driver, base_url: str):
    """
    Verifica que después de intentar una ruta protegida, el usuario terminó en Inicio.
    """
    # Esperita corta por si el router cambia el path tras el paint:
    end = time.time() + 2.0
    while time.time() < end:
        if _is_home(driver):
            break
        time.sleep(0.1)

    assert _is_home(driver), f"Se esperaba redirección a Inicio; quedó en: {driver.current_url}"

# ==========================
# Rutas
# ==========================

# Rutas que DEBEN redirigir (comportamiento correcto que vamos a afirmar)
REDIRIGE_A_INICIO = [
    "/usuarios",
    "/bitacora",
    "/formatos",
    # si /autoridades-centrales debe redirigir, dejala aquí y quítala del bloque de bug
]

# Rutas que HOY presentan bug (el candidato no debería acceder, pero accede).
# Las marcamos xfail a NIVEL PARÁMETRO para reporte limpio por ruta.
PERMITE_ACCESO_ERRONEO = [
    pytest.param("/bancos", "Bancos",
                 marks=pytest.mark.xfail(strict=True, reason="Bug RBAC: permite acceso")),
    pytest.param("/tipos-de-grupos", "Tipos de grupo",
                 marks=pytest.mark.xfail(strict=True, reason="Bug RBAC: permite acceso")),
    pytest.param("/reportes/contrataciones-por-escuela-por-candidato", "Reportes",
                 marks=pytest.mark.xfail(strict=True, reason="Bug RBAC: permite acceso")),
    pytest.param("/ciclos", "Ciclos",
                 marks=pytest.mark.xfail(strict=True, reason="Bug RBAC: permite acceso")),  # quítala si candidato SÍ debe ver ciclos
]

# ==========================
# Tests
# ==========================

@pytest.fixture(scope="function")
def login_as_candidate(driver, base_url):
    login = LoginPage(driver, base_url)
    login.open_login()
    candidate_email = "sabrina_rosales@ues.edu.sv"  # AJUSTA a un usuario candidato real
    candidate_pass  = "Sabr1na.2025"                # AJUSTA si aplica
    login.login_as(candidate_email, candidate_pass)
    assert login.is_logged_in(), "No se pudo iniciar sesión como Candidato."
    time.sleep(1.5)

@pytest.mark.parametrize("ruta", REDIRIGE_A_INICIO)
def test_rbac_candidato_rutas_redirigen_a_inicio(driver, base_url, login_as_candidate, evidencia, ruta):
    url = base_url.rstrip("/") + ruta
    _open_and_wait(driver, url)
    evidencia(f"rbac_candidato__intentando_{ruta.strip('/') or 'root'}")
    _assert_redirected_to_home(driver, base_url)
    evidencia(f"rbac_candidato__redirigido_{ruta.strip('/') or 'root'}")

@pytest.mark.parametrize("ruta,titulo_esperado", PERMITE_ACCESO_ERRONEO)
def test_rbac_candidato_rutas_deberian_bloquear(driver, base_url, login_as_candidate, evidencia, ruta, titulo_esperado):
    """
    Esperamos COMPORTAMIENTO CORRECTO (bloquear/redirigir).
    Como sabemos que hoy falla (bug), el parámetro está marcado xfail.
    - Si el bug persiste -> este assert falla -> XFAILED (lo esperado).
    - Si lo corrigen -> este assert pasa -> XPASS (avisa corrección).
    """
    url = base_url.rstrip("/") + ruta
    _open_and_wait(driver, url, pause=0.8)
    evidencia(f"rbac_bug__intentando_{ruta.strip('/') or 'root'}")

    # Assert del comportamiento correcto: debería estar en home
    assert _is_home(driver), f"El candidato NO fue redirigido (quedó en {_path(driver.current_url)}); debería bloquearse."
