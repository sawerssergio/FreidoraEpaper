# Documentación del Circuito: Control de Freidoras a Gas con e-Paper IoT

Este documento describe el diseño y funcionamiento de un circuito para controlar freidoras a gas utilizando una pantalla E-paper y comunicación IoT (Internet de las Cosas). El sistema permite monitorear y controlar la temperatura, así como gestionar relés para el encendido y apagado de las freidoras.

---

## **Tabla de Contenidos**
1. [Descripción General](#1-descripción-general)
2. [Lista de Componentes](#2-lista-de-componentes)
3. [Esquemático del Circuito](#3-esquemático-del-circuito)
4. [Explicación de Conexiones](#4-explicación-de-conexiones)
5. [Funcionamiento del Circuito](#5-funcionamiento-del-circuito)
6. [Consideraciones Adicionales](#6-consideraciones-adicionales)

---

## **1. Descripción General**
Este circuito está diseñado para controlar freidoras a gas utilizando una pantalla E-paper y comunicación IoT. El sistema permite:
- Monitorear la temperatura en tiempo real mediante un sensor PT100/PT1000.
- Controlar el encendido y apagado de las freidoras mediante relés.
- Mostrar información en una pantalla E-paper, incluyendo la temperatura y el estado del sistema.
- Permitir actualizaciones de firmware de forma remota (OTA).

---

## **2. Lista de Componentes**
A continuación, se detallan los componentes principales utilizados en el circuito:

| **Componente**               | **Cantidad** | **Especificaciones**                     |
|-------------------------------|--------------|------------------------------------------|
| ESP32-WROOM-32               | 1            | Microcontrolador WiFi/Bluetooth          |
| MAX31865ATP+                 | 1            | Sensor de temperatura PT100/PT1000       |
| Pantalla E-paper             | 1            | GxEPD2 7.5 pulgadas, 800x480 píxeles     |
| Relés (APAN3112)             | 4            | Relé de 5V, 10A                         |
| Pulsadores (TS-1101-C-W)     | 2            | Pulsadores normalmente abiertos (NO)     |
| Diodos (1N4148WS-2)          | 4            | Diodos de protección para relés          |
| Transistores (S8050-MS)      | 4            | Transistores NPN para control de relés   |
| Regulador de voltaje (LM2596)| 1            | Convertidor DC-DC 24V a 5V               |
| Fusible (5x20 BLX-A)         | 1            | Fusible de 5x20 mm                       |
| Capacitores (100nF, 10uF, etc)| Varios       | Para filtrado y estabilización           |
| Resistencias (10kΩ, 1kΩ, etc)| Varios       | Para pull-down, divisores de voltaje, etc|

---

## **3. Esquemático del Circuito**
El esquemático del circuito muestra las conexiones entre los componentes principales. A continuación, se describen las conexiones clave:

### **Conexiones Principales**

![image](https://github.com/user-attachments/assets/b47f19a1-da43-4420-ba91-ff92cb015148)


- **ESP32**:
  - GPIO 34, 35, 32, 33 → Control de relés.
  - GPIO 14, 12, 13, 15 → Comunicación SPI con la pantalla E-paper.
  - GPIO 18, 19, 23 → Comunicación SPI con el sensor MAX31865.
  - GPIO 0 → Botón de reinicio (BOOT).
  - GPIO 2 → LED indicador.
- **Sensor MAX31865**:
  - Conectado al ESP32 mediante SPI (pines CS, CLK, MOSI, MISO).
  - Configurado en modo 3 hilos para medir la temperatura.
- **Pantalla E-paper**:
  - Conectada al ESP32 mediante SPI (pines CLK, MISO, MOSI, CS, DC, RST, BUSY).
  - Muestra información en tiempo real, como la temperatura y el estado del sistema.
- **Relés**:
  - Controlados por transistores S8050-MS.
  - Cada relé tiene un diodo de protección (1N4148WS-2) para evitar picos de voltaje.
- **Fuente de Alimentación**:
  - Convertidor DC-DC LM2596 para convertir 24V a 5V.
  - Fusible de protección en la entrada de 24V.

---

## **4. Explicación de Conexiones**
### **Pulsadores**
- Cada pulsador está conectado a un pin GPIO del ESP32 y a tierra (GND) a través de una resistencia pull-down de 10kΩ.
- Esto permite leer el estado del pulsador (HIGH o LOW) cuando se presiona o suelta.

### **Relés**
- Los relés están conectados a los pines GPIO del ESP32 para ser controlados digitalmente.
- Cada relé tiene un diodo de protección en paralelo para evitar picos de voltaje.

### **Sensor MAX31865**
- Conectado al ESP32 mediante SPI (pines CS, CLK, MOSI, MISO).
- Utiliza una configuración de 3 hilos para medir la temperatura.

### **Pantalla E-paper**
- Conectada al ESP32 mediante SPI (pines CLK, MISO, MOSI, CS, DC, RST, BUSY).
- Muestra información en tiempo real, como la temperatura y el estado del sistema.

---

## **5. Funcionamiento del Circuito**
El circuito funciona de la siguiente manera:
1. **Inicialización**:
   - El ESP32 se inicia y conecta a la red WiFi.
   - La pantalla E-paper muestra un mensaje de bienvenida.
2. **Lectura de Temperatura**:
   - El sensor MAX31865 mide la temperatura y envía los datos al ESP32.
   - La temperatura se muestra en la pantalla E-paper.
3. **Control de Relés**:
   - El ESP32 recibe comandos MQTT para activar o desactivar los relés.
   - Los relés controlan dispositivos externos, como luces o motores.
4. **Actualización OTA**:
   - El ESP32 permite actualizaciones de firmware de forma remota mediante OTA.
5. **Manejo de Pulsadores**:
   - El estado de los pulsadores se publica en MQTT para su monitoreo remoto.

---

## **6. Consideraciones Adicionales**
### **Precauciones**
- Asegúrate de que la fuente de alimentación sea adecuada para los relés y el ESP32.
- Usa diodos de protección en los relés para evitar daños por picos de voltaje.

### **Mejoras**
- Agregar un sistema de respaldo de batería para evitar cortes de energía.
- Implementar un sistema de registro de datos para almacenar la temperatura en una base de datos.

