// =================================================================
//      Funcion E-paper Lectura temperatura, MQTT, arduinoOTA
//          Se recomienda usar AWK-3131 Series Industrial 
//             IEEE 802.11n wireless AP/bridge/client
// =================================================================

#include <WiFi.h>
#include <PubSubClient.h>
#include <Adafruit_MAX31865.h>
#include <GxEPD2_BW.h>
#include <Fonts/FreeMonoBold12pt7b.h>
#include <Fonts/FreeMonoBold16pt7b.h>
#include <Fonts/FreeMonoBold24pt7b.h>
#include <Fonts/FreeMonoBold60pt7b.h>
#include <logo.h>
#include <Preferences.h>
#include <ArduinoOTA.h> 

// =================================================================
//                 CONFIGURACIÓN PRINCIPAL
// =================================================================

const int pulsadorGPIO1 = 36;
const int pulsadorGPIO2 = 39;
const int pulsadorGPIO3 = 34;

#define NUM_RELAYS 4
const int relayPins[NUM_RELAYS] = {33, 25, 26, 27};

// Configuración MAX31865
#define RTD_CS   5
#define RTD_CLK  18
#define RTD_MOSI 23
#define RTD_MISO 19

Adafruit_MAX31865 thermo(RTD_CS, RTD_MOSI, RTD_MISO, RTD_CLK);

// =================================================================
//                 VARIABLES EN FUNCION LA RED
// =================================================================

// Configuración WiFi/MQTT
const char* ssid = "iPhone de Sergio";
const char* password = "sawers88";
const char* mqtt_server = "200.58.77.84";
const char* mqtt_user = "villa";
const char* mqtt_password = "sawers";

IPAddress local_IP(172, 20, 10, 5);
IPAddress gateway(172, 20, 10, 1);
IPAddress subnet(255, 255, 255, 0);
IPAddress primaryDNS(172, 20, 10, 1);
IPAddress secondaryDNS(8, 8, 4, 4);


// Configuración E-Paper
#define EPD_CLK   14
#define EPD_MISO  13
#define EPD_MOSI  12
#define EPD_CS    15
#define EPD_DC    32
#define EPD_RST   21
#define EPD_BUSY  22

GxEPD2_BW<GxEPD2_750_T7, GxEPD2_750_T7::HEIGHT> display(GxEPD2_750_T7(EPD_CS, EPD_DC, EPD_RST, EPD_BUSY));

// =================================================================
//                 VARIABLES GLOBALES
// =================================================================
WiFiClient espClient;
PubSubClient client(espClient);
Preferences preferences;

String area1Text = "-";
String area2Text = "MENSAJE OK";
String area3Text = "IP: ---.---.---.---";
String area4Text = "MQTT: OFF";
String area5Text = "WIFI: OFF";

unsigned long lastTempUpdate = 0;
unsigned long lastDisplayUpdate = 0;
unsigned long lastReconnectAttempt = 0;
unsigned long lastFcCheck = 0;
unsigned long lastWifiCheck = 0;
wl_status_t lastWifiStatus = WL_IDLE_STATUS;

// =================================================================
//                 FUNCIONES DE PANTALLA
// =================================================================
void drawCenteredText(const char* text, const GFXfont* font, uint16_t x_area, uint16_t y_area, uint16_t w_area, uint16_t h_area) {
  int16_t tx, ty;
  uint16_t tw, th;
  display.setFont(font);
  display.setTextColor(GxEPD_BLACK);
  display.getTextBounds(text, 0, 0, &tx, &ty, &tw, &th);

  uint16_t x = x_area + (w_area - tw)/2 - tx;
  uint16_t y = y_area + (h_area/2) + (th/2) - ty;
  y -= 20;

  display.setCursor(x, y);
  display.print(text);
}

void updateArea(const char* text, const GFXfont* font, uint16_t x_area, uint16_t y_area, uint16_t w_area, uint16_t h_area) {
  display.setPartialWindow(x_area, y_area, w_area, h_area);
  display.firstPage();
  do {
    //display.fillScreen(GxEPD_WHITE);
    drawCenteredText(text, font, x_area, y_area, w_area, h_area);
    display.fillRect(0, 288, 800, 12, GxEPD_BLACK);
    display.fillRect(200, 300, 12, 180, GxEPD_BLACK);
    display.fillRect(588, 300, 12, 180, GxEPD_BLACK);
  } while (display.nextPage());
}

void actualizarArea(const String& texto, int area) {
  switch(area) {
    case 1:
      area1Text = texto;
      updateArea(area1Text.c_str(), &FreeMonoBold60pt7b, 0, 210, 180, 250);
      preferences.begin("epaper", false);
      preferences.putString("area1", area1Text);
      preferences.end();
      break;
    case 2:
      area2Text = texto;
      updateArea(area2Text.c_str(), &FreeMonoBold16pt7b, 212, 300, 376, 90);
      break;
    case 3:
      area3Text = texto;
      updateArea(area3Text.c_str(), &FreeMonoBold12pt7b, 212, 390, 376, 90);
      break;
    case 4:
      area4Text = texto;
      updateArea(area4Text.c_str(), &FreeMonoBold12pt7b, 600, 300, 200, 90);
      break;
    case 5:
      area5Text = texto;
      updateArea(area5Text.c_str(), &FreeMonoBold12pt7b, 600, 390, 200, 90);
      break;
  }
}

void dibujarPantallaCompleta() {
  display.setFullWindow();
  display.firstPage();
  do {
    display.fillScreen(GxEPD_WHITE);
    display.drawBitmap(233, 16, kingdomlogoking, 334, 256, GxEPD_BLACK);
    display.fillRect(0, 288, 800, 12, GxEPD_BLACK);
    display.fillRect(200, 300, 12, 180, GxEPD_BLACK);
    display.fillRect(588, 300, 12, 180, GxEPD_BLACK);

    drawCenteredText(area1Text.c_str(), &FreeMonoBold60pt7b, 0, 210, 180, 250);
    drawCenteredText(area2Text.c_str(), &FreeMonoBold16pt7b, 212, 300, 376, 90);
    drawCenteredText(area3Text.c_str(), &FreeMonoBold12pt7b, 212, 390, 376, 90);
    drawCenteredText(area4Text.c_str(), &FreeMonoBold12pt7b, 600, 300, 200, 90);
    drawCenteredText(area5Text.c_str(), &FreeMonoBold12pt7b, 600, 390, 200, 90);
  } while (display.nextPage());
  //display.hibernate();
}

// =================================================================
//                 CONECTIVIDAD
// =================================================================
void conectarWiFi() {
  if (!WiFi.config(local_IP, gateway, subnet, primaryDNS, secondaryDNS)) {
    actualizarArea("ERROR IP", 3);
  }

  WiFi.begin(ssid, password);
  actualizarArea("CONECTANDO...", 3);

  int intentos = 0;
  while (WiFi.status() != WL_CONNECTED && intentos++ < 20) {
    delay(500);
    display.hibernate();
    display.init(0);
  }

  if (WiFi.isConnected()) {
    actualizarArea("IP: " + WiFi.localIP().toString(), 3);
  } else {
    actualizarArea("ERROR WIFI", 3);
  }
}

void conectarMQTT() {
  if (client.connect("FreidoraIoT", mqtt_user, mqtt_password)) {
    client.subscribe("relay/#");      // Suscríbete al topic "relay"
    client.subscribe("display/#");    // Suscríbete al topic "display/1 etc.."
    client.subscribe("reset");        // Suscríbete al topic "reset"
    client.subscribe("refresh");      // Suscríbete al topic "refresh"
    actualizarArea("MQTT: OK", 4);
  } else {
    actualizarArea("MQTT: ERROR", 4);
  }
}

// =================================================================
//                 CONFIGURACIÓN OTA
// =================================================================
void configurarOTA() {
  ArduinoOTA.setHostname("FreidoraIoT");  // Nombre del dispositivo OTA
  // Configurar contraseña OTA
  ArduinoOTA.setPassword("12345"); // <-- Añade tu contraseña aquí

  ArduinoOTA.onStart([]() {
    String type;
    if (ArduinoOTA.getCommand() == U_FLASH) {
      type = "sketch";
    } else {  // U_SPIFFS
      type = "filesystem";
    }
    Serial.println("Iniciando actualización OTA: " + type);
    actualizarArea("OTA UPDATE", 2);
  });

  ArduinoOTA.onEnd([]() {
    Serial.println("\nActualización completada");
    actualizarArea("OTA COMPLETE", 2);
  });

  ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
    Serial.printf("Progreso: %u%%\r", (progress / (total / 100)));
    actualizarArea("OTA: " + String(progress / (total / 100)) + "%", 2);
  });

  ArduinoOTA.onError([](ota_error_t error) {
    Serial.printf("Error[%u]: ", error);
    if (error == OTA_AUTH_ERROR) {
      Serial.println("Error de autenticación");
      actualizarArea("OTA ERROR: AUTH", 2);
    } else if (error == OTA_BEGIN_ERROR) {
      Serial.println("Error al iniciar");
      actualizarArea("OTA ERROR: BEGIN", 2);
    } else if (error == OTA_CONNECT_ERROR) {
      Serial.println("Error de conexión");
      actualizarArea("OTA ERROR: CONNECT", 2);
    } else if (error == OTA_RECEIVE_ERROR) {
      Serial.println("Error de recepción");
      actualizarArea("OTA ERROR: RECEIVE", 2);
    } else if (error == OTA_END_ERROR) {
      Serial.println("Error al finalizar");
      actualizarArea("OTA ERROR: END", 2);
    }
  });

  ArduinoOTA.begin();
  actualizarArea("OTA LISTO", 2);
}


// =================================================================
//                        MQTT Y ENTRADAS 
// =================================================================
void callback(char* topic, byte* payload, unsigned int length) {
  char mensaje[50];
  length = length < 49 ? length : 49;
  memcpy(mensaje, payload, length);
  mensaje[length] = '\0';

  if (strncmp(topic, "relay/", 6) == 0) {
    int relay = atoi(topic + 6);
    if (relay >= 0 && relay < NUM_RELAYS) {
      digitalWrite(relayPins[relay], strcmp(mensaje, "ON") == 0 ? HIGH : LOW);
    }
  }
  else if (strncmp(topic, "display/", 8) == 0) {
    int area = atoi(topic + 8);
    if (area >= 1 && area <= 5) {
      actualizarArea(String(mensaje), area);
    }
  }else if (strcmp(topic, "reset") == 0) { // Nueva condición para reset
    if (strcmp(mensaje, "ON") == 0) {
      ESP.restart(); // Reinicia el ESP32
    }
  } else if (strcmp(topic, "refresh") == 0) { // Nueva condición para refresh
    if (strcmp(mensaje, "ON") == 0) {
      dibujarPantallaCompleta(); // Redibuja la pantalla completa
    }
  }
}

void verificarEntradas() {
  static bool estadoAnterior[3] = {LOW, LOW, LOW};
  bool estadosActuales[3] = {
    digitalRead(pulsadorGPIO1),
    digitalRead(pulsadorGPIO2),
    digitalRead(pulsadorGPIO3)
  };

  const char* topics[3] = {"valvula", "tempHot", "tapa"};
  for (int i = 0; i < 3; i++) {
    if (estadosActuales[i] != estadoAnterior[i]) {
      client.publish(topics[i], estadosActuales[i] ? "ON" : "OFF");
      estadoAnterior[i] = estadosActuales[i];
    }
  }
}

// =================================================================
//                 SETUP Y LOOP
// =================================================================
void setup() {
  Serial.begin(115200);

  preferences.begin("epaper", true);
  area1Text = preferences.getString("area1", "-");
  preferences.end();

  SPI.begin(EPD_CLK, EPD_MISO, EPD_MOSI, EPD_CS);
  display.init(0);
  display.setRotation(0);
  dibujarPantallaCompleta();

  for (int i = 0; i < NUM_RELAYS; i++) {
    pinMode(relayPins[i], OUTPUT);
    digitalWrite(relayPins[i], LOW);
  }
  pinMode(pulsadorGPIO1, INPUT_PULLDOWN);
  pinMode(pulsadorGPIO2, INPUT_PULLDOWN);
  pinMode(pulsadorGPIO3, INPUT_PULLDOWN);

  thermo.begin(MAX31865_3WIRE);
  conectarWiFi();
  ArduinoOTA.setHostname("FreidoraIoT");
  ArduinoOTA.begin();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  conectarMQTT();
}

void loop() {
  unsigned long ahora = millis();

  // Control WiFi
  if (ahora - lastWifiCheck > 5000) {
    wl_status_t currentStatus = WiFi.status();
    if (currentStatus != lastWifiStatus) {
      if (currentStatus == WL_CONNECTED) {
        actualizarArea("WIFI: OK", 5);
      } else {
        actualizarArea("WIFI: OFF", 5);
      }
      lastWifiStatus = currentStatus;
    }
    lastWifiCheck = ahora;
  }

  // Control MQTT
  if (!client.connected() && (ahora - lastReconnectAttempt > 5000)) {
    actualizarArea("RECONEC...", 4);
    conectarMQTT();
    lastReconnectAttempt = ahora;
  }
  client.loop();

  // Actualizar temperatura
  if (ahora - lastTempUpdate > 2000) {
    float temp = thermo.temperature(100.0, 430.0);
    if (!thermo.readFault()) {
      client.publish("temperatura", String(temp).c_str());
    }
    lastTempUpdate = ahora;
  }

  // Verificar entradas
  if (ahora - lastFcCheck > 100) {
    verificarEntradas();
    lastFcCheck = ahora;
  }
  // Manejo de OTA
  ArduinoOTA.handle();
}