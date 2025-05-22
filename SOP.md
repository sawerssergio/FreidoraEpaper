# Guía de Instalación Paso a Paso para el Código E-paper con MQTT y OTA

## Requisitos Previos PCB FREIDORAS V1.1 
1. **Hardware necesario**: (omitir)
   - Placa ESP32 (recomendado AWK-3131)
   - Pantalla E-paper de 7.5" compatible con GxEPD2
   - Módulo MAX31865 para lectura de temperatura
   - 4 relés
   - 3 pulsadores
   - Fuente de alimentación adecuada

2. **Software necesario**: (Nesesario)
   - Arduino IDE (última versión)
   - ESP32 board package instalado en Arduino IDE
   - Las siguientes librerías (instalables via Library Manager):
     - WiFi
     - PubSubClient
     - Adafruit MAX31865
     - GxEPD2
     - Adafruit GFX Library
     - Preferences
   - Instal driver CP2102para comunicacion serial (https://www.silabs.com/developer-tools/usb-to-uart-bridge-vcp-drivers?tab=downloads)

## Paso 1: Instalación del Entorno de Desarrollo

1. Instala Arduino IDE desde [el sitio oficial](https://www.arduino.cc/en/software)
2. Abre Arduino IDE y ve a `Archivo > Preferencias`
3. En "Gestor de URLs Adicionales de Tarjetas", añade:
   ```
   https://raw.githubusercontent.com/espressif/arduino-esp32/gh-pages/package_esp32_index.json
   ```
4. Ve a `Herramientas > Placa > Gestor de tarjetas` y busca "esp32"
5. Instala "ESP32 by Espressif Systems"

## Paso 2: Instalación de Librerías

1. Ve a `Herramientas > Administrar bibliotecas`
2. Busca e instala las siguientes librerías:
   - "WiFi" (incluida con ESP32)
   - "PubSubClient" by Nick O'Leary
   - "Adafruit MAX31865 library" by Adafruit
   - "GxEPD2" by Jean-Marc Zingg
   - "Adafruit GFX Library" by Adafruit
   - "Preferences" (incluida con ESP32)

## Paso 3: Configuración del Proyecto

1. Crea una nueva carpeta para tu proyecto
2. Dentro de la carpeta, crea un nuevo archivo `.ino` con el código proporcionado
3. Crea una subcarpeta llamada `data` dentro de la carpeta del proyecto
4. En la carpeta `data`, añade el archivo `logo.h` que contiene el bitmap para el logo

## Paso 4: Conexión del Hardware (Omitir)

Conecta los componentes según esta tabla:

| Componente      | Pin ESP32 |
|-----------------|-----------|
| MAX31865 CS     | 5         |
| MAX31865 CLK    | 18        |
| MAX31865 MOSI   | 23        |
| MAX31865 MISO   | 19        |
| EPD CLK         | 14        |
| EPD MISO        | 13        |
| EPD MOSI        | 12        |
| EPD CS          | 15        |
| EPD DC          | 32        |
| EPD RST         | 21        |
| EPD BUSY        | 22        |
| Pulsador 1      | 36        |
| Pulsador 2      | 39        |
| Pulsador 3      | 34        |
| Relé 1          | 33        |
| Relé 2          | 25        |
| Relé 3          | 26        |
| Relé 4          | 27        |

## Paso 5: Configuración de Red

Modifica estas constantes en el código con tus datos de red:

```cpp
const char* ssid = "vip";
const char* password = "60771800";
const char* mqtt_server = "172.19.32.223";
const char* mqtt_user = "velarde";
const char* mqtt_password = "1234";

IPAddress local_IP(172, 19, 32, 200);
IPAddress gateway(172, 19, 32, 1);
IPAddress subnet(255, 255, 255, 0);
```

## Paso 6: Configuración OTA

Modifica estas líneas si deseas cambiar la configuración OTA:

```cpp
ArduinoOTA.setHostname("FreidoraIoT");
ArduinoOTA.setPassword("12345");
```

## Paso 7: Compilación y Carga del Código

1. Selecciona la placa correcta en `Herramientas > Placa > ESP32 Arduino` (elige tu modelo específico)
2. Configura el Puerto COM correcto
3. Establece la velocidad de upload a 115200
4. Haz clic en el botón "Subir" para compilar y cargar el código

## Paso 8: Configuración del Servidor MQTT

1. Asegúrate de tener un broker MQTT funcionando en `172.19.32.223` (o cambia la IP)
2. Crea los usuarios/configuración necesaria en tu broker MQTT

## Paso 9: Pruebas Iniciales

1. Conecta la alimentación al dispositivo
2. Observa la pantalla E-paper:
   - Debería mostrar el logo inicial
   - La IP asignada
   - El estado de WiFi y MQTT
3. Verifica que puedas conectarte via OTA:
   - Desde Arduino IDE, ve a `Herramientas > Puerto` y busca el dispositivo OTA

## Paso 10: Operación Normal

El dispositivo ahora debería:
- Mostrar la temperatura leída por el MAX31865
- Reaccionar a comandos MQTT en los topics:
  - `relay/#` para controlar relés
  - `display/#` para actualizar áreas de la pantalla
  - `reset` para reiniciar el dispositivo
  - `refresh` para refrescar la pantalla
- Permitir actualizaciones OTA

## Solución de Problemas Comunes

1. **WiFi no se conecta**:
   - Verifica SSID y contraseña
   - Comprueba que la red está disponible
   - Verifica la configuración IP estática

2. **MQTT no se conecta**:
   - Verifica que el broker MQTT está funcionando
   - Comprueba usuario y contraseña
   - Verifica que no hay firewalls bloqueando el puerto 1883

3. **Pantalla no funciona**:
   - Verifica todas las conexiones del E-paper
   - Comprueba que tienes instalada la librería GxEPD2 correcta
   - Asegúrate de que el modelo de pantalla coincide con el definido en el código (GxEPD2_750_T7)

4. **Temperatura no se lee**:
   - Verifica las conexiones del MAX31865
   - Comprueba que el sensor PT100 está bien conectado
   - Verifica la configuración de 3 hilos (3WIRE) en el código
