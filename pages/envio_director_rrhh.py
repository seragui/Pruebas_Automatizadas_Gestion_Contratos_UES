from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException

def enviar_a_rrhh(driver, evidencia, timeout=20):
    wait = WebDriverWait(driver, timeout)

    # Botón "Terminar registro de candidatos y enviar a RRHH"
    btn = wait.until(EC.element_to_be_clickable((
        By.XPATH, "//button[.//span[normalize-space()='Terminar registro de candidatos y enviar a RRHH']]"
    )))
    try:
        ActionChains(driver).move_to_element(btn).perform()
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
    except Exception:
        pass
    evidencia("btn_enviar_rrhh_visible")

    try:
        btn.click()
    except Exception:
        driver.execute_script("arguments[0].click();", btn)
    evidencia("click_enviar_rrhh")

    # Confirm modal (si aparece)
    try:
        confirm = wait.until(EC.element_to_be_clickable((
            By.XPATH, "//div[contains(@class,'ant-modal-root')]//button[.//span[normalize-space()='Sí' or normalize-space()='Aceptar' or normalize-space()='OK']]"
        )))
        evidencia("modal_confirm_rrhh_visible")
        confirm.click()
        evidencia("modal_confirm_rrhh_click")
    except TimeoutException:
        pass

    # Éxito: toast o cambio de step o regreso al listado
    ok = False
    try:
        wait.until(EC.visibility_of_element_located((
            By.XPATH, "//div[contains(@class,'ant-message')]//*[contains(translate(.,'ÉEXITOENVIADO','éexitoenviado'),'éxito') or contains(translate(.,'ÉEXITOENVIADO','éexitoenviado'),'enviado')]"
        )))
        evidencia("toast_envio_rrhh_ok")
        ok = True
    except TimeoutException:
        pass

    if not ok:
        try:
            wait.until(EC.presence_of_element_located((
                By.XPATH,
                "//div[contains(@class,'ant-steps-item') and contains(@class,'ant-steps-item-process')]"
                "//div[contains(@class,'ant-steps-item-title')][normalize-space()='Finalización de solicitud de contratación' or normalize-space()='Revision de solicitud de contratación por Recursos Humanos']"
            )))
            evidencia("step_cambiado_envio_rrhh")
            ok = True
        except TimeoutException:
            pass

    if not ok:
        try:
            wait.until(EC.url_contains("/contratos"))
            evidencia("navegacion_listado_contratos_post_envio")
            ok = True
        except TimeoutException:
            pass

    assert ok, "No se pudo confirmar el envío a RRHH."

def assert_modal_envio_rrhh_y_cerrar(driver, evidencia, timeout=15):
    wait = WebDriverWait(driver, timeout)

    # Espera el modal visible
    modal = wait.until(EC.visibility_of_element_located((
        By.XPATH, "//div[contains(@class,'ant-modal-root')]//div[contains(@class,'ant-modal-content')]"
    )))
    evidencia("modal_envio_rrhh_visible")

    # Valida el título
    titulo = wait.until(EC.visibility_of_element_located((
        By.XPATH, "//div[contains(@class,'ant-modal-root')]//div[contains(@class,'ant-modal-title')]"
                  "[normalize-space()='Envío de solicitud a RRHH']"
    )))
    assert "Envío de solicitud a RRHH" in titulo.text.strip(), "El título del modal no coincide."

    # Valida el mensaje
    msg = wait.until(EC.visibility_of_element_located((
        By.XPATH, "//div[contains(@class,'ant-modal-root')]//div[contains(@class,'ant-modal-body')]"
                  "//*[contains(normalize-space(),'se ha enviado con éxito')]"
    )))
    evidencia("modal_envio_rrhh_texto")
    assert "se ha enviado con éxito" in msg.text, "El mensaje del modal no indica éxito."

    # Clic en Aceptar
    btn_ok = wait.until(EC.element_to_be_clickable((
        By.XPATH, "//div[contains(@class,'ant-modal-root')]//button[.//span[normalize-space()='Aceptar']]"
    )))
    btn_ok.click()
    evidencia("modal_envio_rrhh_aceptar_click")

    # Espera a que el modal desaparezca
    wait.until(EC.invisibility_of_element_located((
        By.XPATH, "//div[contains(@class,'ant-modal-root')]//div[contains(@class,'ant-modal-content')]"
    )))