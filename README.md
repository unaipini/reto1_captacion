Práctica: Captura de Datos con Docker Compose y MQTT

## 1. Miembros del equipo

- Imanol Lama 
- Unai Pinilla  
- Juan Mari Diaz 


## 2. Descripción del proyecto

El objetivo de esta práctica es diseñar e implementar un sistema de **adquisición automatizada de datos** utilizando contenedores Docker.

Se ha desarrollado una arquitectura basada en el modelo 'publish/subscribe con MQTT', donde:

- Un contenedor simula un sensor agrícola que genera datos sintéticos.
- Un broker MQTT distribuye los mensajes.
- Un contenedor consumidor recibe los datos y los almacena en una base de datos PostgreSQL.
- Se valida el almacenamiento mediante consultas SQL.

Toda la infraestructura está orquestada con Docker Compose.


## 3. Arquitectura del sistema

Arquitectura implementada:

Sensor (Producer)
↓
MQTT Broker (Mosquitto)
↓
Consumidor (Subscriber)
↓
Base de datos PostgreSQL


### Componentes

- 'sensor_tierra' → Genera datos sintéticos cada X segundos.
- 'mosquitto' → Broker MQTT.
- 'cerebro_datos' → Suscriptor que almacena datos en la BD.
- 'base_datos' → PostgreSQL.


## 4. Caracterización del dato

- Tipo de dato: Semiestructurado  
- Formato: JSON  
- Frecuencia: 1 mensaje cada 5 segundos (configurable)  
- Dominio: Sensores agrícolas (invernadero)  

### Campos enviados

- 'id_sensor'
- 'timestamp' (millis)
- 'temperatura'
- 'humedad'
- 'luz'
- 'ph'

### Generación de datos

Los valores se generan utilizando una **distribución normal (gaussiana)** con un valor ideal configurable, simulando el comportamiento real de sensores físicos.


## 5. Explicación de los pasos seguidos

1. Diseño de arquitectura basada en MQTT.
2. Configuración del broker Mosquitto en Docker.
3. Desarrollo del productor en Python usando `paho-mqtt`.
4. Generación de datos sintéticos con distribución normal.
5. Desarrollo del consumidor:
   - Suscripción a topic `invernadero/#`
   - Conexión a PostgreSQL
   - Inserción de registros en la base de datos.
6. Validación mediante consultas SQL.
7. Orquestación completa mediante Docker Compose.

---

## 6. Instrucciones de uso

### Requisitos

- Docker
- Docker Compose

### Arranque del sistema

```bash
docker compose up --build
El sistema iniciará:

Broker MQTT

Base de datos

Sensor productor

Consumidor

Verificación del almacenamiento
Abrir otra terminal:

docker exec -it <nombre_contenedor_postgres> psql -U deusto -d invernadero_db
Dentro de PostgreSQL:

SELECT COUNT(*) FROM mediciones;
SELECT * FROM mediciones ORDER BY id DESC LIMIT 5;
El número de registros aumentará cada 5 segundos.

Parar el sistema
docker compose down
Para borrar datos persistentes:

docker compose down -v

## 7. Problemas / Retos encontrados

Sincronización de arranque entre contenedores.

Configuración correcta de variables de entorno.

Gestión de conexión entre contenedores mediante nombre de servicio (no localhost).

Alineación de credenciales entre consumidor y base de datos.

## 8. Alternativas posibles

Uso de API REST en lugar de MQTT.

Uso de RabbitMQ o Kafka como sistema de mensajería.

Uso de MongoDB como base de datos NoSQL.

Implementación de QoS en MQTT.

Uso de autenticación y TLS en el broker.

## 9. Posibles vías de mejora

Añadir control de calidad del dato.

Implementar validación de esquema JSON.

Incorporar dashboard de visualización (Grafana).

Añadir autenticación al broker MQTT.

Escalado horizontal del consumidor.

Implementar métricas y monitorización.

## 10. Conclusión
Se ha desarrollado una solución funcional de captura y almacenamiento de datos basada en tecnologías de contenedorización y mensajería ligera.

El sistema demuestra:

Captura automatizada de datos

Comunicación desacoplada mediante MQTT

Persistencia estructurada en base de datos

Validación efectiva del almacenamiento

La arquitectura es escalable, modular y fácilmente extensible a entornos industriales o IoT reales.
