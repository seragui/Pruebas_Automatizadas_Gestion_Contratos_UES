import os
from dotenv import load_dotenv

# Carga .env desde la raíz del proyecto
load_dotenv()

class Settings:
    BASE_URL = os.getenv("BASE_URL", "https://example.com")
    BROWSER = os.getenv("BROWSER", "chrome").lower()
    HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
    IMPLICIT_WAIT = int(os.getenv("IMPLICIT_WAIT", "0"))
    PAGELOAD_TIMEOUT = int(os.getenv("PAGELOAD_TIMEOUT", "30"))

# >>> esta variable debe existir <<<
settings = Settings()
