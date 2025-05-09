import network
import time

def connect_to_wifi():
    # Configura la conexión Wi-Fi
    ssid = 'ESP'
    password = '12345678'

    # Crea un objeto de red Wi-Fi
    wifi = network.WLAN(network.STA_IF)

    # Activa la interfaz de red Wi-Fi
    wifi.active(True)

    # Conéctate a la red Wi-Fi
    wifi.connect(ssid, password)

    # Espera hasta que se establezca la conexión
    while not wifi.isconnected():
        print("Conectando a la red Wi-Fi...")
        time.sleep(1)

    # Una vez conectado, muestra la dirección IP
    print("Conectado a la red Wi-Fi")
    print("Dirección IP:", wifi.ifconfig()[0])
