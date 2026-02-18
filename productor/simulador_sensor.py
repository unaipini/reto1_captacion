import json
import os
import time
import random
import numpy as np
import paho.mqtt.client as mqtt

# Función auxiliar para leer variables de entorno (docker-compose)
def leer_config(clave, valor_por_defecto):
    return os.environ.get(clave, valor_por_defecto)

# Función para generar datos realistas (no aleatorios puros)
def generar_dato(media, variacion):
    # Usamos distribución normal (curva de campana)
    valor = np.random.normal(float(media), variacion)
    return round(valor, 2)

def main():
    # 1. Configuración desde Docker
    broker = leer_config("HOST_BROKER", "localhost")
    puerto = int(leer_config("PUERTO_BROKER", "1883"))
    tema = leer_config("TEMA_PUBLICACION", "invernadero/pruebas")
    sensor_id = leer_config("ID_SENSOR", "sensor_desconocido")
    intervalo = int(leer_config("INTERVALO", "5"))

    # Valores ideales del cultivo (definidos en docker-compose)
    temp_media = float(leer_config("TEMP_IDEAL", "20"))
    hum_media = float(leer_config("HUMEDAD_IDEAL", "50"))
    luz_media = float(leer_config("LUZ_IDEAL", "500"))
    ph_medio = float(leer_config("PH_IDEAL", "7"))

    # 2. Conexión MQTT
    cliente = mqtt.Client(client_id=sensor_id)
    
    print(f"[SENSOR] Conectando a {broker}...")
    try:
        cliente.connect(broker, puerto, 60)
        cliente.loop_start() # Arranca el hilo de red en segundo plano
        print(f"[SENSOR] Conectado y listo para enviar datos de {sensor_id}")
    except Exception as e:
        print(f"[SENSOR] Error al conectar: {e}")
        return

    # 3. Bucle infinito de envío de datos
    try:
        while True:
            # Creamos el paquete de datos (Diccionario)
            datos = {
                "sensor_id": sensor_id,
                "timestamp": int(time.time() * 1000), # Tiempo actual
                "temperatura": generar_dato(temp_media, 1.5), # Varía +/- 1.5 grados
                "humedad": generar_dato(hum_media, 5.0),      # Varía +/- 5%
                "luminosidad": generar_dato(luz_media, 50),   # Varía +/- 50 lumens
                "ph_suelo": generar_dato(ph_medio, 0.2)       # Varía +/- 0.2
            }

            # Convertimos a texto JSON
            mensaje_json = json.dumps(datos)

            # Publicamos
            cliente.publish(tema, mensaje_json)
            
            # Mostramos por pantalla (logs)
            print(f"[ENVIADO] -> {tema}: {mensaje_json}")

            # Esperamos X segundos
            time.sleep(intervalo)

    except KeyboardInterrupt:
        print("[SENSOR] Deteniendo sensor...")
        cliente.loop_stop()
        cliente.disconnect()

if __name__ == "__main__":
    main()