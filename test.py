import paho.mqtt.client as mqtt
import json

msg = [{
    "gesto": ["A", "B"],
    "significado": "teste",
    "cor": "azul"
}]

client = mqtt.Client()
client.enable_logger()
client.connect("192.168.0.136", 1883, 60)

result = client.publish("sabre/comando/gesto", json.dumps(msg), retain=False)
result.wait_for_publish()

print(f"Publish RC: {result.rc}")
client.disconnect()
