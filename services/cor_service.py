import json

def listar_cor():
    with open('data/cor.json', 'r', encoding='utf-8') as arquivo:
        print("Abriu")
        return json.load(arquivo)