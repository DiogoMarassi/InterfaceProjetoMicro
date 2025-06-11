import paho.mqtt.client as mqtt

def publicar_gesto(gesto: str):
    MQTT_BROKER = "192.168.0.50"
    MQTT_PORT = 1883
    MQTT_TOPIC = "sabre/gesto"
    MQTT_USERNAME = "mqttuser"
    MQTT_PASSWORD = "1234"

    payload = f'"{gesto}"'  # mantém aspas externas como no seu exemplo

    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.publish(MQTT_TOPIC, payload)
        client.disconnect()
        print(f"[MQTT] Gesto '{gesto}' publicado com sucesso.")
    except Exception as e:
        print(f"[MQTT ERRO] Falha ao publicar gesto '{gesto}': {e}")
