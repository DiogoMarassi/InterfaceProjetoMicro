import json, datetime, os

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

    # Novo elemento a ser adicionado
    novo_elemento = {
        "novo_gesto": novo_gesto,
        "data": ""
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

