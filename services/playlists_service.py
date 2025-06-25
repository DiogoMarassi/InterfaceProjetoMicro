import json

def listar_playlists():
    with open('data/playlist.json', 'r', encoding='utf-8') as arquivo:
        print("Abriu")
        return json.load(arquivo)