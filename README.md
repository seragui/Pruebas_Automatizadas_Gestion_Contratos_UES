# Pruebas Automatizadas – Sistema de Gestión de Contratos FIA-UES

Este repositorio contiene la suite de **pruebas automatizadas** para el sistema web de **Gestión de Contratos de Docentes de la FIA-UES**.  
Incluye pruebas de:

- **UI (Frontend)** con Selenium + Pytest + Page Object Model (POM).
- **API REST** con Postman + Newman.
- **Rendimiento** con Apache JMeter.
- **Seguridad** con OWASP ZAP.

El objetivo es proporcionar una base reproducible de pruebas para respaldar la **tesina de aseguramiento de calidad** del sistema.

---

## 1. Estructura del proyecto

```text
.
├── config/
│   └── config.py                 # Carga de variables de entorno (.env)
├── pages/
│   ├── base_page.py              # Page Object base (helpers genéricos)
│   └── ...                       # Page Objects por módulo/rol
├── tests/
│   ├── functional/               # Pruebas funcionales de UI (flujos completos)
│   ├── security/                 # Pruebas de seguridad de rutas (RBAC, accesos)
│   ├── resources/
│   │   └── docs/                 # Documentos de prueba (DUI, CV, declaraciones, etc.)
│   ├── utils/
│   │   ├── generador_duis.py     # Utilidades para generación/validación de DUI
│   │   └── shared_state.py       # Estado compartido entre pruebas
│   ├── conftest.py               # Fixtures de Pytest (driver, evidencias, etc.)
│   └── pytest.ini                # Configuración de Pytest y markers
├── api_test/
│   ├── GESTION_CONTRATOS.postman_collection.json
│   ├── QA_GESTION_CONTRATOS.postman_environment.json
│   └── reports/
│       └── newman/               # Reportes HTML generados por Newman
├── peformance_test/
│   └── PRUEBAS_RENDIMIENTO.jmx   # Script de JMeter para pruebas de rendimiento
├── results_security/
│   └── 2025-11-21-ZAP-Report-.html   # Reporte de OWASP ZAP
├── reports/
│   └── report_defensa.html       # Ejemplo de reporte pytest-html
├── allure-results/               # Resultados crudos para Allure
├── screenshots/                  # Capturas de pantalla de evidencias
├── artifacts/                    # Evidencias adicionales (HTML, PNG) de errores
└── README.md

## 2. Requisitos previos

- **Python** 3.10 o superior (se ha probado con Python 3.13).
- **Google Chrome** (u otro navegador compatible).
- **ChromeDriver** (o driver correspondiente, alineado con la versión del navegador).
- **Node.js + npm** (para ejecutar Newman).
- **Apache JMeter** (para pruebas de rendimiento).
- **OWASP ZAP** (para pruebas de seguridad, opcional si solo se revisan reportes).

Dependencias Python principales:

- `pytest`
- `selenium`
- `allure-pytest`
- `pytest-html`
- `python-dotenv`
- Otras librerías listadas en `requirements.txt` (si aplica).

---

## 3. Configuración inicial

### 3.1. Crear y activar entorno virtual (opcional, recomendado)

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/MacOS
source .venv/bin/activate
