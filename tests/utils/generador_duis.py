import random

def dui_dv(base8: str) -> int:
    if not (base8.isdigit() and len(base8) == 8):
        raise ValueError("Base debe tener 8 dígitos")
    pesos = [9,8,7,6,5,4,3,2]
    s = sum(int(d)*p for d,p in zip(base8, pesos))
    return (10 - (s % 10)) % 10

def dui_valido(base8: str) -> str:
    return f"{base8}-{dui_dv(base8)}"

def generar_duis(n=10):
    vistos = set()
    res = []
    while len(res) < n:
        base = f"{random.randint(0, 99999999):08d}"
        if base in vistos: 
            continue
        vistos.add(base)
        res.append(dui_valido(base))
    return res

# Ejemplos rápidos
print(dui_valido("12345678"))  # 12345678-4
print(generar_duis(1))
