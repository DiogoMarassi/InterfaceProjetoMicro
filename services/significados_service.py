import json

def listar_significados():
    with open('data/significados.json', 'r', encoding='utf-8') as arquivo:
        print("Abriu")
        return json.load(arquivo)