import json
import os
import time
import psycopg2
import paho.mqtt.client as mqtt

# --- CONFIGURACIÓN ---
MQTT_BROKER = os.getenv("HOST_BROKER", "mosquitto")
MQTT_TEMA = os.getenv("TEMA_SUSCRIPCION", "invernadero/#")

# Configuración de Base de Datos
DB_HOST = os.getenv("HOST_BD", "base_datos")
DB_NAME = os.getenv("NOMBRE_BD", "invernadero_db")
DB_USER = os.getenv("USUARIO_BD", "agricultor")
DB_PASS = os.getenv("CLAVE_BD", "cosecha_segura")

def conectar_bd():
    """Intenta conectar a la BD con reintentos (por si la BD tarda en arrancar)"""
    while True:
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASS
            )
            conn.autocommit = True
            print(f"[BD] Conectado exitosamente a {DB_HOST}")
            return conn
        except Exception as e:
            print(f"[BD] Esperando a la base de datos... ({e})")
            time.sleep(2)

def crear_tabla(conn):
    """Crea la tabla 'mediciones' si no existe"""
    sql = """
    CREATE TABLE IF NOT EXISTS mediciones (
        id SERIAL PRIMARY KEY,
        sensor_id VARCHAR(50),
        fecha BIGINT,
        temperatura FLOAT,
        humedad FLOAT,
        luminosidad FLOAT,
        ph_suelo FLOAT,
        datos_crudos JSONB,
        creado_en TIMESTAMP DEFAULT NOW()
    );
    """
    with conn.cursor() as cur:
        cur.execute(sql)
    print("[BD] Tabla 'mediciones' verificada/creada.")

def guardar_lectura(conn, datos):
    """Inserta el JSON recibido en la tabla"""
    sql = """
    INSERT INTO mediciones (sensor_id, fecha, temperatura, humedad, luminosidad, ph_suelo, datos_crudos)
    VALUES (%s, %s, %s, %s, %s, %s, %s);
    """
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (
                datos.get("sensor_id"),
                datos.get("timestamp"),
                datos.get("temperatura"),
                datos.get("humedad"),
                datos.get("luminosidad"),
                datos.get("ph_suelo"),
                json.dumps(datos)
            ))
        print(f"[BD] Guardado -> Sensor: {datos.get('sensor_id')} | Temp: {datos.get('temperatura')}")
    except Exception as e:
        print(f"[ERROR BD] No se pudo guardar: {e}")

# --- FUNCIONES MQTT ---
def al_conectar(client, userdata, flags, rc):
    print(f"[MQTT] Conectado al broker. Suscribiéndose a {MQTT_TEMA}")
    client.subscribe(MQTT_TEMA)

def al_recibir_mensaje(client, userdata, msg):
    try:
        payload = msg.payload.decode("utf-8")
        datos = json.loads(payload)
        # Guardamos en la BD usando la conexión global 'conn'
        guardar_lectura(conn, datos)
    except Exception as e:
        print(f"[ERROR] Mensaje corrupto o error de proceso: {e}")

# --- BLOQUE PRINCIPAL ---
if __name__ == "__main__":
    # 1. Conectar a BD
    conn = conectar_bd()
    crear_tabla(conn)

    # 2. Configurar MQTT
    cliente_mqtt = mqtt.Client()
    cliente_mqtt.on_connect = al_conectar
    cliente_mqtt.on_message = al_recibir_mensaje

    # 3. Conectar y esperar mensajes eternamente
    print(f"[SISTEMA] Conectando a MQTT {MQTT_BROKER}...")
    cliente_mqtt.connect(MQTT_BROKER, 1883, 60)
    cliente_mqtt.loop_forever()