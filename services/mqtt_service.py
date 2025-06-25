import paho.mqtt.client as mqtt
import time
import json
from services.playlists_service import listar_playlists

# Configurações MQTT
MQTT_BROKER = "192.168.0.100"
MQTT_PORT = 1883
MQTT_TOPIC_PUBLISH = "sabre/gesto"
MQTT_TOPIC_SUBSCRIBE = "clima/atual"
MQTT_USERNAME = "mqttuser"
MQTT_PASSWORD = "1234"

MQTT_TOPIC_PUBLISH_ROTINA = "ver/rotina"
MQTT_TOPIC_SUBSCRIBE_ROTINA = "receber/rotina"

MQTT_TOPIC_PUBLISH_SPOTIFY = "envia/playlist"
MQTT_TOPIC_SUBSCRIBE_SPOTIFY = ""

clima_recebido = None


def publicar_gesto(gesto: str):
    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()

        result = client.publish(MQTT_TOPIC_PUBLISH, gesto)
        result.wait_for_publish()
        print(f"[MQTT] Gesto '{gesto}' publicado com sucesso.")

        client.loop_stop()
        client.disconnect()

    except Exception as e:
        print(f"[MQTT ERRO] Falha ao publicar gesto '{gesto}': {e}")
        raise e


def on_message(client, userdata, msg):
    global clima_recebido
    try:
        payload = msg.payload.decode('utf-8')
        clima_recebido = json.loads(payload)
        print(f"[MQTT] JSON recebido: {clima_recebido}")
    except Exception as e:
        print(f"[MQTT ERRO] Falha ao processar mensagem: {e}")


def solicitar_clima(timeout=10):
    global clima_recebido
    clima_recebido = None

    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.on_message = on_message

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()

        client.subscribe(MQTT_TOPIC_SUBSCRIBE)
        time.sleep(0.2)  # Aguarda o subscribe completar

        # Publica exatamente "refresh_clima" com aspas duplas
        client.publish(MQTT_TOPIC_PUBLISH, '"refresh_clima"')
        print(f"[MQTT] Pedido enviado com sucesso: refresh_clima")

        # Aguarda resposta
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
        print(f"[ERRO] Falha ao atualizar rotinas: {e}")

def solicitar_rotinas(timeout=10):
    global clima_recebido
    clima_recebido = None

    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.on_message = on_message

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()

        client.subscribe(MQTT_TOPIC_SUBSCRIBE_ROTINA)
        time.sleep(0.2)  # Aguarda o subscribe completar

        # Publica exatamente "refresh_clima" com aspas duplas
        client.publish(MQTT_TOPIC_PUBLISH_ROTINA, '"refresh_rotinas"')
        print(f"[MQTT] Pedido enviado com sucesso: refresh_clima")

        # Aguarda resposta
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

def publicar_spotify(genero: str):

    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    playlists = listar_playlists()
    print(str(playlists[str(genero)]))
    montagem_envio = "{ \"playlist_id\": \"spotify:playlist:" + str(playlists[str(genero)]) + "\"}"
    print(montagem_envio)
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()

        result = client.publish(MQTT_TOPIC_PUBLISH_SPOTIFY, montagem_envio)
        result.wait_for_publish()
        print(f"[MQTT] Gesto '{genero}' publicado com sucesso.")

        client.loop_stop()
        client.disconnect()

    except Exception as e:
        print(f"[MQTT ERRO] Falha ao publicar gesto '{genero}': {e}")
        raise e
    

# Exemplo de uso
if __name__ == "__main__":
    try:
        clima = publicar_spotify("{ \"playlist_id\": \"spotify:playlist:2Jn9nUxpy79EN8PlbAGyFA?si=Z0IOkpAVTv292ggT0XgRLA&pi=dl5kH71-SQm7A\"}")
        print(f"\n➡️ Resultado final:\n{json.dumps(clima, indent=2)}")
    except Exception as e:
        print(f"[ERRO GERAL] {e}")