import json
import os
import time
import random
import numpy as np
import paho.mqtt.client as mqtt

# Recoge el valor que envía el broker
def leer_config(clave, valor_por_defecto):
    return os.environ.get(clave, valor_por_defecto)

# Función para generar datos realistas por medio de la Distribución Normal (numpy).
def generar_dato(media, variacion):
    valor = np.random.normal(float(media), variacion)
    return round(valor, 2)

def main():
    # Llama a la función leer_config() para cargar todas las variables.
    broker = leer_config("HOST_BROKER", "localhost")
    puerto = int(leer_config("PUERTO_BROKER", "1883"))
    tema = leer_config("TEMA_PUBLICACION", "invernadero/pruebas")
    id_sensor = leer_config("ID_SENSOR", "sensor_desconocido")
    intervalo = int(leer_config("INTERVALO", "5"))

    # Valores ideales del cultivo
    temp_media = float(leer_config("TEMP_IDEAL", "20"))
    hum_media = float(leer_config("HUMEDAD_IDEAL", "50"))
    luz_media = float(leer_config("LUZ_IDEAL", "500"))
    ph_medio = float(leer_config("PH_IDEAL", "7"))

    # Crea el cliente MQTT y llama al broker
    cliente = mqtt.Client(client_id=id_sensor)
    
    print(f"[SENSOR] Conectando a {broker}...")
    try:
        cliente.connect(broker, puerto, 60)
        cliente.loop_start()
        print(f"[SENSOR] Conectado y listo para enviar datos de {id_sensor}")
    except Exception as e:
        print(f"[SENSOR] Error al conectar: {e}")
        return

    # Envío de datos
    try:
        while True:
            # Crea el paquete de datos
            datos = {
                "sensor_id": id_sensor,
                "timestamp": int(time.time() * 1000),
                "temperatura": generar_dato(temp_media, 1.5), 
                "humedad": generar_dato(hum_media, 5.0),     
                "luminosidad": generar_dato(luz_media, 50),  
                "ph_suelo": generar_dato(ph_medio, 0.2)      
            }

            # Se transforma en JSON para que MQTT lo entienda.
            mensaje_json = json.dumps(datos)

            cliente.publish(tema, mensaje_json)
            
            print(f"[ENVIADO] -> {tema}: {mensaje_json}")

            time.sleep(intervalo)

    # Desconexion
    except KeyboardInterrupt:
        print("[SENSOR] Deteniendo sensor...")
        cliente.loop_stop()
        cliente.disconnect()

if __name__ == "__main__":
    main()