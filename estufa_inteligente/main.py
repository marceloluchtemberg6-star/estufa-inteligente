from machine import Pin, ADC
import dht
import time
import network
from umqtt.simple import MQTTClient

SSID = "Wokwi-GUEST"
PASSWORD = ""

MQTT_BROKER = "test.mosquitto.org"
CLIENT_ID = "marcelo_estufa_01"

TOPIC_TEMP = b"marcelo/estufa/temp"
TOPIC_LUZ = b"marcelo/estufa/luz"
TOPIC_CMD = b"marcelo/estufa/cmd"
TOPIC_REARME = b"marcelo/estufa/rearme"

dht_pin = Pin(4)
ldr = ADC(Pin(34))

led_vermelho = Pin(19, Pin.OUT)
led_azul = Pin(5, Pin.OUT)

sensor = dht.DHT22(dht_pin)
ldr.atten(ADC.ATTN_11DB)

limite_escuro = 2000

def conecta_wifi():
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.connect(SSID, PASSWORD)

    print("Conectando WiFi...")
    while not wifi.isconnected():
        time.sleep(1)

    print("WiFi conectado!")

def rearmar_sistema():
    print("REARMANDO SISTEMA...")
    led_azul.off()
    led_vermelho.off()
    print("Sistema REARMADO!")

def chegou_mensagem(topic, msg):
    print(topic, msg)

    if msg == b"IRRIGAR_ON":
        led_azul.on()

    elif msg == b"IRRIGAR_OFF":
        led_azul.off()

    elif msg == b"REARME":
        rearmar_sistema()

def conecta_mqtt():
    client = MQTTClient(CLIENT_ID, MQTT_BROKER)
    client.set_callback(chegou_mensagem)
    client.connect()

    client.subscribe(TOPIC_CMD)
    client.subscribe(TOPIC_REARME)

    print("MQTT conectado!")
    return client

conecta_wifi()
client = conecta_mqtt()

while True:
    try:
        sensor.measure()
        temp = sensor.temperature()
        umid = sensor.humidity()
        luz = ldr.read()

        print(temp, umid, luz)

        if luz < limite_escuro:
            led_vermelho.on()
        else:
            led_vermelho.off()

        client.publish(TOPIC_TEMP, str(temp))
        client.publish(TOPIC_LUZ, str(luz))

        client.check_msg()

        time.sleep(2)

    except Exception as e:
        print("Erro:", e)
