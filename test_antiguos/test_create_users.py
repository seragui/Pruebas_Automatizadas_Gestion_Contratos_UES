# tests/functional/test_create_users.py
import time
import pytest
from faker import Faker
from pages.login_page import LoginPage
from pages.home_page import HomePage
from pages.users_page import UsersPage
from pages.create_user_page import CreateUserPage

@pytest.mark.smoke
def test_crear_un_usuario_candidato(driver, base_url, qa_creds):
    fake = Faker()

    # 1) Login
    login = LoginPage(driver, base_url)
    login.open_login()
    login.login_as(qa_creds["email"], qa_creds["password"])
    assert login.is_logged_in()

    # 2) Ir a Usuarios y abrir Crear
    home = HomePage(driver, base_url)
    home.go_to_users()
    users = UsersPage(driver, base_url)
    users.wait_loaded()
    users.click_create()

    # 3) Llenar formulario
    create = CreateUserPage(driver, base_url)
    create.wait_loaded()

    nombre = f"Candidato QA {fake.first_name()}"
    correo = f"cand_qa_{int(time.time())}_{fake.random_number(digits=4)}@example.com"

    create.set_name(nombre)
    create.set_email(correo)

    # Rol
    create.select_role("Candidato")

    # Como Candidato habilita Escuela, seleccionamos "Ingeniería de Sistemas Informáticos"
    create.wait_school_enabled()
    create.select_school("Ingeniería de Sistemas Informáticos")

    # Enviar
    create.submit()

    # (Opcional) aquí puedes verificar redirección o toast de éxito
    users.wait_loaded()  # si redirige a /usuarios
