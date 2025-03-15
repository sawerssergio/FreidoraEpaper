# Documentación del Código: Funcionamiento de E-paper, Lectura de Temperatura, MQTT y ArduinoOTA

Este código está diseñado para un dispositivo IoT que utiliza un ESP32 para leer la temperatura de un sensor MAX31865, mostrar información en una pantalla E-paper, conectarse a una red WiFi, comunicarse mediante MQTT y permitir actualizaciones OTA (Over-The-Air). A continuación, se detalla el funcionamiento del código.

---

## **Tabla de Contenidos**
1. [Descripción General](#1-descripción-general)
2. [Configuración Principal](#2-configuración-principal)
3. [Variables y Configuraciones](#3-variables-y-configuraciones)
4. [Funciones de Pantalla](#4-funciones-de-pantalla)
5. [Conectividad WiFi y MQTT](#5-conectividad-wifi-y-mqtt)
6. [Configuración OTA](#6-configuración-ota)
7. [Manejo de MQTT y Entradas](#7-manejo-de-mqtt-y-entradas)
8. [Setup y Loop](#8-setup-y-loop)
9. [Consideraciones Adicionales](#9-consideraciones-adicionales)

---

## **1. Descripción General**
El código está diseñado para un dispositivo IoT que realiza las siguientes funciones:
- **Lectura de temperatura**: Utiliza un sensor MAX31865 para medir la temperatura.
- **Pantalla E-paper**: Muestra información en una pantalla E-paper, incluyendo la temperatura, estado de WiFi, estado de MQTT y mensajes personalizados.
- **Comunicación MQTT**: Se conecta a un servidor MQTT para enviar y recibir datos.
- **Actualización OTA**: Permite actualizar el firmware del dispositivo de forma remota.
- **Control de relés**: Controla hasta 4 relés mediante comandos MQTT.
- **Entradas digitales**: Lee el estado de 3 pulsadores y publica su estado en MQTT.

---

## **2. Configuración Principal**
### **Pines y Configuración Inicial**
- **Pulsadores**: Se utilizan 3 pulsadores conectados a los pines GPIO 36, 39 y 34.
- **Relés**: Se controlan 4 relés conectados a los pines GPIO 33, 25, 26 y 27.
- **Sensor MAX31865**: Configurado en modo 3 hilos, con pines CS (5), CLK (18), MOSI (23) y MISO (19).

### **Configuración WiFi/MQTT**
- **SSID y contraseña**: Se define la red WiFi a la que se conectará el dispositivo.
- **Servidor MQTT**: Dirección IP del servidor MQTT y credenciales de acceso.
- **Dirección IP estática**: Se configura una IP estática para el dispositivo.

### **Configuración E-Paper**
- **Pines E-Paper**: Se definen los pines para la comunicación SPI con la pantalla E-paper.
- **Pantalla**: Se utiliza una pantalla GxEPD2 de 7.5 pulgadas.

---

## **3. Variables y Configuraciones**
### **Variables Globales**
- **Textos de las áreas**: Se almacenan los textos que se muestran en las diferentes áreas de la pantalla E-paper.
- **Temporizadores**: Se utilizan para controlar la frecuencia de actualización de la temperatura, la pantalla y la verificación de conexiones.

### **Librerías Utilizadas**
- **WiFi**: Para la conexión a la red WiFi.
- **PubSubClient**: Para la comunicación MQTT.
- **Adafruit_MAX31865**: Para la lectura del sensor de temperatura.
- **GxEPD2_BW**: Para controlar la pantalla E-paper.
- **Preferences**: Para almacenar datos persistentes en la memoria no volátil del ESP32.
- **ArduinoOTA**: Para permitir actualizaciones OTA.

---

## **4. Funciones de Pantalla**
### **`drawCenteredText`**
- **Descripción**: Dibuja un texto centrado en un área específica de la pantalla.
- **Parámetros**:
  - `text`: Texto a mostrar.
  - `font`: Fuente a utilizar.
  - `x_area`, `y_area`, `w_area`, `h_area`: Coordenadas y dimensiones del área.

### **`updateArea`**
- **Descripción**: Actualiza una área específica de la pantalla con un texto.
- **Parámetros**:
  - `text`: Texto a mostrar.
  - `font`: Fuente a utilizar.
  - `x_area`, `y_area`, `w_area`, `h_area`: Coordenadas y dimensiones del área.

### **`actualizarArea`**
- **Descripción**: Actualiza el contenido de una de las 5 áreas de la pantalla.
- **Parámetros**:
  - `texto`: Texto a mostrar.
  - `area`: Número del área a actualizar (1-5).

### **`dibujarPantallaCompleta`**
- **Descripción**: Redibuja toda la pantalla con los textos actuales de las áreas.

---

## **5. Conectividad WiFi y MQTT**
### **`conectarWiFi`**
- **Descripción**: Conecta el dispositivo a la red WiFi configurada.
- **Comportamiento**: Intenta conectarse hasta 20 veces. Si no lo logra, muestra un mensaje de error.

### **`conectarMQTT`**
- **Descripción**: Conecta el dispositivo al servidor MQTT.
- **Comportamiento**: Si la conexión es exitosa, se suscribe a los topics `relay/#`, `display/#`, `reset` y `refresh`.

---

## **6. Configuración OTA**
### **`configurarOTA`**
- **Descripción**: Configura el servicio OTA para permitir actualizaciones remotas.
- **Comportamiento**: Define un nombre de host y una contraseña para el servicio OTA. Maneja eventos como inicio, progreso, finalización y errores de la actualización.

---

## **7. Manejo de MQTT y Entradas**
### **`callback`**
- **Descripción**: Función que se ejecuta cuando llega un mensaje MQTT.
- **Comportamiento**:
  - Controla los relés si el mensaje llega al topic `relay/#`.
  - Actualiza las áreas de la pantalla si el mensaje llega al topic `display/#`.
  - Reinicia el dispositivo si el mensaje llega al topic `reset`.
  - Redibuja la pantalla si el mensaje llega al topic `refresh`.

### **`verificarEntradas`**
- **Descripción**: Lee el estado de los pulsadores y publica su estado en MQTT.
- **Comportamiento**: Publica "ON" o "OFF" en los topics `valvula`, `tempHot` y `tapa` según el estado de los pulsadores.

---

## **8. Setup y Loop**
### **`setup`**
- **Descripción**: Inicializa el dispositivo.
- **Comportamiento**:
  - Inicia la comunicación serial.
  - Configura los pines de los relés y pulsadores.
  - Inicializa la pantalla E-paper.
  - Conecta a WiFi y MQTT.
  - Configura el servicio OTA.

### **`loop`**
- **Descripción**: Bucle principal del programa.
- **Comportamiento**:
  - Verifica la conexión WiFi y MQTT.
  - Actualiza la temperatura y la publica en MQTT.
  - Verifica el estado de los pulsadores.
  - Maneja las actualizaciones OTA.

---

## **9. Consideraciones Adicionales**
- **Memoria no volátil**: Se utiliza la librería `Preferences` para almacenar el texto del área 1 de la pantalla, de modo que persista después de un reinicio.
- **Eficiencia energética**: La pantalla E-paper entra en modo de hibernación cuando no está en uso para ahorrar energía.

# Resumen de Comandos MQTT

A continuación, se presenta un resumen de los comandos MQTT utilizados en el código, junto con su funcionalidad y cómo interactúan con el dispositivo IoT.

---

## **1. Comandos para Control de Relés**
### **Topic: `relay/#`**
- **Descripción**: Controla el estado de los relés conectados al dispositivo.
- **Formato**: `relay/<número_relé>`
- **Valores**:
  - `ON`: Activa el relé.
  - `OFF`: Desactiva el relé.
- **Ejemplos**:
  - `relay/0 ON`: Activa el relé 0.
  - `relay/1 OFF`: Desactiva el relé 1.

---

## **2. Comandos para Actualizar la Pantalla E-Paper**
### **Topic: `display/#`**
- **Descripción**: Actualiza el contenido de una de las 5 áreas de la pantalla E-paper.
- **Formato**: `display/<número_área>`
- **Valores**: Cualquier texto que se desee mostrar en el área correspondiente.
- **Áreas**:
  - `1`: Área grande (fuente grande, para numero de freidora).
  - `2`: Área de mensajes (fuente mediana).
  - `3`: Área de estado de IP (fuente pequeña).
  - `4`: Área de estado de MQTT (fuente pequeña).
  - `5`: Área de estado de WiFi (fuente pequeña).
- **Ejemplos**:
  - `display/1 25.5°C`: Muestra "10" en el área 1 es ideal que solo sea nuemrico.
  - `display/2 MENSAJE OK`: Muestra "MENSAJE OK" en el área 2.

---

## **3. Comandos para Reiniciar el Dispositivo**
### **Topic: `reset`**
- **Descripción**: Reinicia el dispositivo ESP32.
- **Valores**:
  - `ON`: Reinicia el dispositivo.
- **Ejemplo**:
  - `reset ON`: Reinicia el dispositivo.

---

## **4. Comandos para Refrescar la Pantalla**
### **Topic: `refresh`**
- **Descripción**: Redibuja toda la pantalla E-paper con los textos actuales.
- **Valores**:
  - `ON`: Redibuja la pantalla.
- **Ejemplo**:
  - `refresh ON`: Redibuja la pantalla.

---

## **5. Comandos para Publicar el Estado de los Pulsadores**
### **Topics: `valvula`, `tempHot`, `tapa`**
- **Descripción**: Publica el estado de los pulsadores conectados al dispositivo.
- **Valores**:
  - `ON`: El pulsador está presionado.
  - `OFF`: El pulsador no está presionado.
- **Ejemplos**:
  - `valvula ON`: Indica que el pulsador de la válvula está presionado.
  - `tempHot OFF`: Indica que el pulsador de temperatura caliente no está presionado.

---

## **6. Comandos para Publicar la Temperatura**
### **Topic: `temperatura`**
- **Descripción**: Publica la temperatura medida por el sensor MAX31865.
- **Valores**: Valor numérico de la temperatura en grados Celsius.
- **Ejemplo**:
  - `temperatura 25.5`: Publica una temperatura de 25.5°C.

---

## **Resumen de Topics MQTT**
| **Topic**       | **Descripción**                          | **Valores**       | **Ejemplo**              |
|------------------|------------------------------------------|-------------------|--------------------------|
| `relay/#`        | Control de relés                        | `ON`, `OFF`       | `relay/0 ON`             |
| `display/#`      | Actualización de áreas de la pantalla    | Texto             | `display/1 5`       |
| `reset`          | Reinicia el dispositivo                 | `ON`              | `reset ON`               |
| `refresh`        | Redibuja la pantalla E-paper            | `ON`              | `refresh ON`             |
| `valvula`        | Estado del pulsador de la válvula       | `ON`, `OFF`       | `valvula ON`             |
| `tempHot`        | Estado del pulsador de temperatura      | `ON`, `OFF`       | `tempHot OFF`            |
| `tapa`           | Estado del pulsador de la tapa          | `ON`, `OFF`       | `tapa ON`                |
| `temperatura`    | Publica la temperatura medida           | Valor numérico    | `temperatura 25.5`       |

---

Este resumen proporciona una visión clara de cómo interactuar con el dispositivo IoT mediante MQTT. Cada comando tiene un propósito específico y permite controlar y monitorear el dispositivo de manera remota.
- **Seguridad OTA**: Se recomienda cambiar la contraseña OTA por una más segura antes de implementar el dispositivo en producción.

---

Este código es adecuado para aplicaciones industriales o domésticas donde se requiera monitoreo y control remoto, como en sistemas de climatización, control de procesos o automatización del hogar.
