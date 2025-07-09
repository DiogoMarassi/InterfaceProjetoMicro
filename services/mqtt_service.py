import paho.mqtt.client as mqtt
import time
import json
from services.playlists_service import listar_playlists
import requests
import threading
# =========================== CONFIGURAÇÃO DE BROKERS ===========================

# PRINCIPAL (BROKER DO LUCAS PARA CONTATO COMIGO)
BROKER_PRINCIPAL = {
    "host": "192.168.0.100",
    "port": 1883,
    "username": "mqttuser",
    "password": "1234",
}

# MEU BROKER PARA CONTATO COM GRATZ
BROKER_GESTO_DIRETO = {
    "host": "192.168.0.136",
    "port": 1883
}

# =========================== TÓPICOS POR FINALIDADE ===========================

TOPICO_GESTO_PUBLISH = "sabre/gesto"
TOPICO_CLIMA_SUBSCRIBE = "clima/atual"

TOPICO_ROTINA_PUBLISH = "ver/rotina"
TOPICO_ROTINA_SUBSCRIBE = "receber/rotina"

TOPICO_SPOTIFY_PUBLISH = "envia/playlist"
TOPICO_GESTO_DIRETO = "sabre/comando/gesto"

# +++++++++ RECEBE GESTO E PASSA PARA LUCAS 
TOPICO_FEITO = "sabre/comando/feito"

mapa_movimentos = {
    'f': 'Frente', 'F': 'Frente',
    't': 'Trás',   'T': 'Trás',
    'd': 'Direita','D': 'Direita',
    'e': 'Esquerda','E': 'Esquerda',
    'c': 'Cima',   'C': 'Cima',
    'b': 'Baixo',  'B': 'Baixo'
}

import json
import requests
from urllib.parse import quote

def on_message_nova(client, userdata, msg):
    try:
        print("ENTROU PARA ENVIAR PARA O LUCAS")
        
        # Decodifica o payload recebido
        payload = msg.payload.decode('utf-8')
        print(f"[MQTT] Mensagem recebida no tópico {msg.topic}: {payload}")
        
        # Tenta carregar o JSON
        try:
            movimentos_compactados = json.loads(payload)
        except json.JSONDecodeError as e:
            print(f"[ERRO] Payload recebido não é JSON válido: {e}")
            return

        # Aceita ["F", "T"] ou [["F", "T"]]
        if isinstance(movimentos_compactados, list):
            if len(movimentos_compactados) == 0:
                print("[AVISO] Lista de movimentos recebida está vazia.")
                return
            if isinstance(movimentos_compactados[0], list):
                movimentos_compactados = movimentos_compactados[0]
        else:
            print(f"[ERRO] Estrutura inválida: esperado lista, recebido {type(movimentos_compactados)}")
            return

        # Verifica se todos os elementos são strings de 1 caractere
        if not all(isinstance(l, str) and len(l) == 1 for l in movimentos_compactados):
            print(f"[ERRO] Lista de letras malformada: {movimentos_compactados}")
            return

        # Expande letras para nomes de gestos via mapa_movimentos
        movimentos = []
        for letra in movimentos_compactados:
            nome = mapa_movimentos.get(letra.upper())
            if not nome:
                print(f"[AVISO] Letra desconhecida recebida: {letra}")
                continue
            movimentos.append(nome)

        if not movimentos:
            print("[AVISO] Nenhum movimento válido encontrado após decodificação.")
            return

        print("MOVIMENTOS DECODIFICADOS ---------------------------")
        print(movimentos)

        # Codifica a lista para ser usada na URL com segurança
        movimentos_json = json.dumps(movimentos, ensure_ascii=False)
        movimentos_encoded = quote(movimentos_json)

        url = f"http://localhost:5000/testarMovimento/{movimentos_encoded}"
        resposta = requests.get(url)

        print(f"[MQTT → Flask] Resposta: {resposta.status_code} - {resposta.text}")

    except Exception as e:
        print(f"[MQTT ERRO] Falha ao processar mensagem recebida: {e}")


def iniciar_escuta_mqtt():
    client = mqtt.Client()
    client.connect(BROKER_GESTO_DIRETO["host"], BROKER_GESTO_DIRETO["port"], 60)
    client.subscribe(TOPICO_FEITO)
    client.on_message = on_message_nova

    client.loop_forever()

# Inicia a escuta em background junto com o Flask
def iniciar_mqtt_em_thread():
    thread = threading.Thread(target=iniciar_escuta_mqtt)
    thread.daemon = True  # finaliza com o processo principal
    thread.start()
# =========================== VARIÁVEL GLOBAL DE RESPOSTA ===========================

clima_recebido = None

# =========================== FUNÇÕES BASE GENÉRICAS ===========================

def publicar_mensagem(broker: dict, topico: str, mensagem: str, usar_auth=True):
    """Função genérica para publicar uma mensagem MQTT simples."""
    client = mqtt.Client()
    if usar_auth:
        if broker["username"] and broker["password"]:
            client.username_pw_set(broker["username"], broker["password"])

    try:
        client.connect(broker["host"], broker["port"], 60)
        client.loop_start()

        result = client.publish(topico, mensagem)
        result.wait_for_publish()
        print(f"[MQTT] Publicado com sucesso em {topico}: {mensagem}")

        client.loop_stop()
        client.disconnect()
    except Exception as e:
        print(f"[MQTT ERRO] Falha ao publicar em {topico}: {e}")
        raise e

def solicitar_dado(broker: dict, topico_publicar: str, mensagem: str, topico_resposta: str, timeout=10):
    """Função genérica para publicar uma solicitação e aguardar resposta via subscribe."""
    global clima_recebido
    clima_recebido = None

    client = mqtt.Client()
    client.username_pw_set(broker["username"], broker["password"])
    client.on_message = on_message

    try:
        client.connect(broker["host"], broker["port"], 60)
        client.loop_start()

        client.subscribe(topico_resposta)
        time.sleep(0.2)

        client.publish(topico_publicar, mensagem)
        print(f"[MQTT] Pedido publicado em {topico_publicar}: {mensagem}")

        start_time = time.time()
        while clima_recebido is None and (time.time() - start_time) < timeout:
            time.sleep(0.1)

        client.loop_stop()
        client.disconnect()

        if clima_recebido is None:
            raise TimeoutError("Timeout: Nenhuma resposta MQTT recebida.")
        return clima_recebido

    except Exception as e:
        print(f"[MQTT ERRO] {e}")
        raise e

# =========================== CALLBACK DE MENSAGENS ===========================

import time
def envia_lista_para_sabre(listaMovimentos):
    try:
        client = mqtt.Client()
        client.enable_logger()
        client.connect(BROKER_GESTO_DIRETO["host"], BROKER_GESTO_DIRETO["port"], 60)

        client.loop_start()  # <<< inicia thread de rede

        mensagem = json.dumps(listaMovimentos)
        result = client.publish(TOPICO_GESTO_DIRETO, mensagem, retain=True)
        result.wait_for_publish()

        time.sleep(0.5)  # <<< garante tempo para enviar

        client.loop_stop()
        client.disconnect()

        print(f"[MQTT] Lista enviada com sucesso: {mensagem}")
    except Exception as e:
        print(f"[MQTT ERRO] Falha ao enviar lista: {e}")


def on_message(client, userdata, msg):
    """Callback para tratamento de mensagens recebidas."""
    global clima_recebido
    try:
        payload = msg.payload.decode('utf-8')
        clima_recebido = json.loads(payload)
        print(f"[MQTT] JSON recebido: {clima_recebido}")
    except Exception as e:
        print(f"[MQTT ERRO] Falha ao processar mensagem: {e}")

# =========================== FUNÇÕES ESPECÍFICAS DE DOMÍNIO ===========================

def enviar_lingua(idioma):
    publicar_mensagem(BROKER_PRINCIPAL, "notifica/tempo", idioma)

def publicar_gesto(gesto: str):
    publicar_mensagem(BROKER_PRINCIPAL, TOPICO_GESTO_PUBLISH, gesto)

def publicar_spotify(genero: str):
    playlists = listar_playlists()
    playlist_id = playlists.get(genero)
    if not playlist_id:
        print(f"[ERRO] Gênero '{genero}' não encontrado.")
        return

    mensagem = json.dumps({
        "playlist_id": f"spotify:playlist:{playlist_id}"
    })

    publicar_mensagem(BROKER_PRINCIPAL, TOPICO_SPOTIFY_PUBLISH, mensagem)

def enviar_gesto_mqtt(dado: str):
    """Envia dado diretamente via outro broker sem autenticação."""
    publicar_mensagem(BROKER_PRINCIPAL, TOPICO_GESTO_DIRETO, dado, usar_auth=False)

def solicitar_clima(timeout=10):
    return solicitar_dado(
        broker=BROKER_PRINCIPAL,
        topico_publicar=TOPICO_GESTO_PUBLISH,
        mensagem='"refresh_clima"',
        topico_resposta=TOPICO_CLIMA_SUBSCRIBE,
        timeout=timeout
    )

def solicitar_rotinas(timeout=10):
    return solicitar_dado(
        broker=BROKER_PRINCIPAL,
        topico_publicar=TOPICO_ROTINA_PUBLISH,
        mensagem='"refresh_rotinas"',
        topico_resposta=TOPICO_ROTINA_SUBSCRIBE,
        timeout=timeout
    )

# =========================== FUNÇÕES DE ARMAZENAMENTO LOCAL ===========================

def atualizar_rotinas(dados_recebidos):
    try:
        rotinas = dados_recebidos.get('rotinas', [])
        with open('data/significados.json', 'w', encoding='utf-8') as arquivo:
            json.dump(rotinas, arquivo, ensure_ascii=False, indent=4)
        print("[OK] Arquivo rotinas.json atualizado com sucesso.")
    except Exception as e:
        print(f"[ERRO] Falha ao atualizar rotinas: {e}")

def refresh_playlist(dados_recebidos):
    try:
        rotinas = dados_recebidos.get('playlist', [])
        with open('data/´playlist.json', 'w', encoding='utf-8') as arquivo:
            json.dump(rotinas, arquivo, ensure_ascii=False, indent=4)
        print("[OK] Arquivo playlist.json atualizado com sucesso.")
    except Exception as e:
        print(f"[ERRO] Falha ao atualizar playlists: {e}")

# =========================== USO DIRETO (DEBUG) ===========================

if __name__ == "__main__":
    try:
        solicitar_rotinas()
    except Exception as e:
        print(f"[ERRO GERAL] {e}")
