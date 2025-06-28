import json, datetime, os
from datetime import datetime
import paho.mqtt.client as mqtt

def salvar_historico(novo_gesto):
    # Lê o histórico existente ou cria uma lista vazia se o arquivo não existir
    if os.path.exists("data/historico_gestos.json"):
        with open('data/historico_gestos.json', 'r', encoding='utf-8') as f:
            try:
                historico = json.load(f)
            except json.JSONDecodeError:
                historico = []
    else:
        historico = []
    
    print(novo_gesto)

    # Novo elemento a ser adicionado
    for i in range(len(novo_gesto)):
        if novo_gesto[i] == 'D':
            novo_gesto[i] = 'Direita'
        elif novo_gesto[i] == 'E':
            novo_gesto[i] = 'Esquerda'
        elif novo_gesto[i] == 'C':
            novo_gesto[i] = 'Cima'
        elif novo_gesto[i] == 'B':
            novo_gesto[i] = 'Baixo'
        elif novo_gesto[i] == 'F':
            novo_gesto[i] = 'Frente'
        elif novo_gesto[i] == 'T':
            novo_gesto[i] = 'Trás'

    novo_elemento = {
        "novo_gesto": novo_gesto,
        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    historico.append(novo_elemento)

    # Salva de volta no arquivo
    with open("data/historico_gestos.json", 'w', encoding='utf-8') as f:
        json.dump(historico, f, ensure_ascii=False, indent=4)

    return True  # ou simplesmente não retornar nada


def listar_historico():
    with open('data/historico_gestos.json', 'r', encoding='utf-8') as arquivo:
        print("Abriu")
        return json.load(arquivo)
