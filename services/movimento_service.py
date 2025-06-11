import json
import os

DATA_PATH = os.path.join("data", "movimentos.json")

def carregar_movimentos():
    if not os.path.exists(DATA_PATH):
        return []
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_movimentos(movimentos):
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(movimentos, f, indent=4, ensure_ascii=False)

def adicionar_movimento(gesto, significado):
    movimentos = carregar_movimentos()

    # Verifica se já existe um gesto com o mesmo nome
    if any(m["gesto"].lower() == gesto.lower() for m in movimentos):
        raise ValueError(f"Gesto '{gesto}' já existe.")

    movimentos.append({
        "gesto": gesto,
        "significado": significado
    })
    salvar_movimentos(movimentos)


def remover_movimento(gesto):
    movimentos = carregar_movimentos()
    movimentos = [m for m in movimentos if m["gesto"] != gesto]
    salvar_movimentos(movimentos)
