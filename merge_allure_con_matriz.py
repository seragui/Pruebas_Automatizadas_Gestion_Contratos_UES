import json
import re
from pathlib import Path

import pandas as pd

# ================= CONFIGURACIÓN =================

# Ruta del archivo de la matriz de casos de prueba
MATRIZ_FILE = "Matriz Casos de Pruebas/MATRIZ DE PRUEBAS.xlsx"

# Nombre de la hoja dentro del Excel
HOJA_MATRIZ = "MATRIZ DE CASOS DE PRUEBA"

# Carpeta donde pytest genera los resultados de Allure (UI/Selenium)
# Debe coincidir con el --alluredir que usas en pytest
ALLURE_DIR = "allure-results_prueba"

# Archivo JSON generado por Newman (API)
# Debe coincidir con el --reporter-json-export que uses
NEWMAN_JSON = "api_test/reports/newman/newman_results_sin_contratacion.json"

# Archivo de salida (nuevo Excel con todas las columnas adicionales)
OUTPUT_FILE = "MATRIZ_DE_PRUEBAS_CON_AUTOMATIZACION.xlsx"

# =================================================


CP_REGEX = re.compile(r"cp[_\s-]?(\d+)", re.IGNORECASE)


def infer_cp_from_text(text: str) -> str | None:
    """
    Busca un patrón cpXX en el texto y devuelve CP_XX.
    Coincide con variantes tipo: cp03, cp_03, cp-03, CP3, CP_3, etc.
    """
    if not text:
        return None

    match = CP_REGEX.search(text)
    if not match:
        return None

    num = int(match.group(1))
    return f"CP_{num:02d}"


# ================= ALLURE (UI / SELENIUM) =================


def leer_resultados_allure(allure_dir: str) -> pd.DataFrame:
    """
    Lee todos los archivos *-result.json de la carpeta de Allure y construye un DataFrame
    con los tests de UI, incluyendo un ID_CASO inferido a partir de cpXX en fullName/name
    y propagado por suite cuando aplica.
    """
    rows = []
    allure_path = Path(allure_dir)

    if not allure_path.exists():
        raise FileNotFoundError(f"No se encontró la carpeta {allure_dir}")

    for result_file in allure_path.glob("*-result.json"):
        with open(result_file, encoding="utf-8") as f:
            data = json.load(f)

        labels = {
            label.get("name"): label.get("value")
            for label in data.get("labels", [])
            if "name" in label and "value" in label
        }

        suite = labels.get("suite", "")          # p.ej. 'test_02_create_multiple_users'
        status = data.get("status")              # passed / failed / skipped
        name = data.get("name") or ""            # nombre lógico del test
        full_name = data.get("fullName") or ""   # p.ej. 'functional.test_02...#test_cp03...'

        start = data.get("start")
        stop = data.get("stop")

        if start is None or stop is None:
            # Sin tiempos no podemos calcular duración
            continue

        duration_sec = (stop - start) / 1000.0

        # Primera inferencia de CP: priorizar fullName y luego name
        cp_raw = infer_cp_from_text(full_name)
        if cp_raw is None:
            cp_raw = infer_cp_from_text(name)

        rows.append(
            {
                "file": result_file.name,
                "suite": suite,
                "fullName": full_name,
                "ID_CASO_RAW": cp_raw,  # CP detectado directamente por cpXX (si existe)
                "test_name": name,
                "status": status,
                "duration_sec": duration_sec,
            }
        )

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)

    # Propagar CP por archivo (suite) cuando hay exactamente un CP en esa suite
    suite_to_cps = (
        df.dropna(subset=["ID_CASO_RAW"])
        .groupby("suite")["ID_CASO_RAW"]
        .unique()
    )

    suite_to_single_cp = {
        suite: cps[0]
        for suite, cps in suite_to_cps.items()
        if len(cps) == 1
    }

    df["ID_CASO"] = df["ID_CASO_RAW"]
    df["ID_CASO"] = df["ID_CASO"].fillna(df["suite"].map(suite_to_single_cp))

    return df


def resumir_allure_por_cp(df_results: pd.DataFrame) -> pd.DataFrame:
    """
    A partir del DataFrame de resultados de Allure, agrupa por ID_CASO y devuelve:

    - Tiempo_Ejecucion_Automatizada_seg (UI/Selenium)
    - Resultado_Automatizado (UI/Selenium)
    """
    df = df_results.dropna(subset=["ID_CASO"])
    if df.empty:
        return pd.DataFrame()

    def resumen_status(series: pd.Series) -> str:
        if (series == "failed").any():
            return "FAILED"
        if (series == "passed").any():
            return "PASSED"
        return "SKIPPED"

    agg = (
        df.groupby("ID_CASO")
        .agg(
            Tiempo_Ejecucion_Automatizada_seg=("duration_sec", "sum"),
            Resultado_Automatizado=("status", resumen_status),
        )
        .reset_index()
    )

    return agg


# ================= NEWMAN (API) =================


def leer_ejecuciones_newman(json_path: str) -> pd.DataFrame:
    """
    Lee el archivo JSON generado por Newman y devuelve un DataFrame
    con una fila por ejecución (request) asociada a un CP.

    Columnas:
    - ID_CASO
    - request_name
    - status_api (PASSED/FAILED)
    - duration_api_sec
    """
    path = Path(json_path)
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el archivo de resultados de Newman: {json_path}")

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    executions = data.get("run", {}).get("executions", [])
    rows = []

    for exec_ in executions:
        item = exec_.get("item", {}) or {}
        name = item.get("name", "") or ""

        cp_id = infer_cp_from_text(name)
        if cp_id is None:
            # Si la request no tiene CP en el nombre, no la consideramos
            continue

        assertions = exec_.get("assertions", []) or []
        failed = any(a.get("error") for a in assertions)
        status = "FAILED" if failed else "PASSED"

        response = exec_.get("response") or {}
        response_time_ms = response.get("responseTime", exec_.get("responseTime", 0))
        duration_sec = response_time_ms / 1000.0

        rows.append(
            {
                "ID_CASO": cp_id,
                "request_name": name,
                "status_api": status,
                "duration_api_sec": duration_sec,
            }
        )

    if not rows:
        return pd.DataFrame()

    return pd.DataFrame(rows)


def resumir_newman_por_cp(df_exec: pd.DataFrame) -> pd.DataFrame:
    """
    A partir del DataFrame de ejecuciones de Newman, agrupa por CP (ID_CASO) y devuelve:

    - Tiempo_Ejecucion_API_seg
    - Resultado_API
    """
    if df_exec.empty:
        return pd.DataFrame()

    def resumen_status(series: pd.Series) -> str:
        if (series == "FAILED").any():
            return "FAILED"
        if (series == "PASSED").any():
            return "PASSED"
        return "SKIPPED"

    agg = (
        df_exec.groupby("ID_CASO")
        .agg(
            Tiempo_Ejecucion_API_seg=("duration_api_sec", "sum"),
            Resultado_API=("status_api", resumen_status),
        )
        .reset_index()
    )

    return agg


# ================= MATRIZ =================


def agregar_resultados_a_matriz():
    # 1. Leer matriz original
    print(f"Leyendo matriz desde: {MATRIZ_FILE}")
    matriz = pd.read_excel(MATRIZ_FILE, sheet_name=HOJA_MATRIZ)

    # 2. UI/Selenium (Allure)
    print(f"Leyendo resultados de Allure desde: {ALLURE_DIR}")
    df_allure_raw = leer_resultados_allure(ALLURE_DIR)

    if df_allure_raw.empty:
        print("No se encontraron resultados en los JSON de Allure")
        agg_ui = pd.DataFrame()
    else:
        agg_ui = resumir_allure_por_cp(df_allure_raw)
        print("Resumen UI por ID_CASO (primeras filas):")
        print(agg_ui.head())

    # 3. API (Newman)
    try:
        print(f"Leyendo resultados de Newman desde: {NEWMAN_JSON}")
        df_newman_exec = leer_ejecuciones_newman(NEWMAN_JSON)
    except FileNotFoundError as e:
        print(str(e))
        df_newman_exec = pd.DataFrame()

    if df_newman_exec.empty:
        print("No se encontraron ejecuciones de API asociadas a CP en Newman")
        agg_api = pd.DataFrame()
    else:
        agg_api = resumir_newman_por_cp(df_newman_exec)
        print("Resumen API por ID_CASO (primeras filas):")
        print(agg_api.head())

    # 4. Merge con la matriz
    matriz_ext = matriz.copy()

    if not agg_ui.empty:
        matriz_ext = matriz_ext.merge(
            agg_ui,
            on="ID_CASO",
            how="left",
            validate="1:1",
        )

    if not agg_api.empty:
        # Si ya se hizo un merge anterior, es posible que algunas filas no tengan CP en API y viceversa;
        # seguimos usando 1:1 porque por ID_CASO no debe haber duplicados en los agregados.
        matriz_ext = matriz_ext.merge(
            agg_api,
            on="ID_CASO",
            how="left",
            validate="1:1",
        )

    # 5. Calcular tiempo total (UI + API) en segundos
    if "Tiempo_Ejecucion_Automatizada_seg" in matriz_ext.columns or "Tiempo_Ejecucion_API_seg" in matriz_ext.columns:
        matriz_ext["Tiempo_Total_Automatizado_seg"] = (
            matriz_ext.get("Tiempo_Ejecucion_Automatizada_seg", 0).fillna(0)
            + matriz_ext.get("Tiempo_Ejecucion_API_seg", 0).fillna(0)
        )

    # 6. Guardar nuevo archivo
    print(f"Guardando matriz extendida en: {OUTPUT_FILE}")
    matriz_ext.to_excel(OUTPUT_FILE, index=False)
    print("Proceso finalizado")


if __name__ == "__main__":
    agregar_resultados_a_matriz()
