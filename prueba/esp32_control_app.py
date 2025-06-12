import tkinter as tk
from tkinter import ttk, messagebox
import paho.mqtt.client as mqtt
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class ESP32ControlApp:
    def __init__(self, root):
        self.root = root
        root.title("Control Freidora IoT - ESP32")
        root.geometry("1200x850")

        # Paleta de colores
        self.colors = {
            "primary": "#2B2D42",
            "secondary": "#8D99AE",
            "accent1": "#EF233C",
            "accent2": "#D90429",
            "background": "#EDF2F4",
            "text": "#2B2D42",
            "success": "#06D6A0",
            "warning": "#FFD166",
            "danger": "#EF476F",
            "light": "#F8F9FA",
            "dark": "#212529"
        }

        # Configuración MQTT
        self.mqtt_config = {
            "broker": "172.19.32.206",
            "port": 1883,
            "username": "villa",
            "password": "sawers",
            "topics": {
                "temperature": "temperatura",
                "relays": "relay/#",
                "display": "display/#",
                "inputs": ["valvula", "tempHot", "tapa"],
                "commands": ["reset", "refresh"],
                "status": "esp32/status"
            }
        }

        # Variables de interfaz
        self.mqtt_broker_var = tk.StringVar(value=self.mqtt_config["broker"])
        self.mqtt_port_var = tk.IntVar(value=self.mqtt_config["port"])
        self.mqtt_username_var = tk.StringVar(value=self.mqtt_config["username"])
        self.mqtt_password_var = tk.StringVar(value=self.mqtt_config["password"])
        
        # Estado del sistema
        self.client = None
        self.esp32_connected = False
        self.last_esp32_heartbeat = None
        self.temp_history = []
        self.time_history = []
        self.max_data_points = 100
        self.system_state = {
            "temperature": 0.0,
            "relays": [False, False, False, False],
            "inputs": [False, False, False],
            "connection": False
        }

        # Configurar interfaz
        self.setup_styles()
        self.setup_ui()
        self.setup_mqtt()
        self.check_esp32_connection()

    def setup_styles(self):
        style = ttk.Style()
        self.root.configure(bg=self.colors["background"])
        style.theme_create("custom", parent="clam", settings={
            "TFrame": {"configure": {"background": self.colors["background"]}},
            "TLabelFrame": {
                "configure": {
                    "background": self.colors["background"],
                    "foreground": self.colors["text"],
                    "bordercolor": self.colors["secondary"],
                    "relief": "groove",
                    "borderwidth": 2,
                    "font": ("Helvetica", 10, "bold")
                }
            },
            "TLabel": {
                "configure": {
                    "background": self.colors["background"],
                    "foreground": self.colors["text"],
                    "font": ("Helvetica", 10)
                }
            },
            "TButton": {
                "configure": {
                    "background": self.colors["secondary"],
                    "foreground": self.colors["text"],
                    "font": ("Helvetica", 10, "bold"),
                    "borderwidth": 1,
                    "relief": "raised",
                    "padding": 8
                },
                "map": {
                    "background": [("active", self.colors["primary"])],
                    "foreground": [("active", "white")]
                }
            },
            "TEntry": {
                "configure": {
                    "padding": 5,
                    "font": ("Helvetica", 10),
                    "fieldbackground": self.colors["light"],
                    "foreground": self.colors["text"],
                    "bordercolor": self.colors["secondary"],
                    "borderwidth": 1,
                    "relief": "groove"
                }
            }
        })
        style.theme_use("custom")

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame superior
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=5)

        # Sección temperatura
        temp_frame = ttk.LabelFrame(control_frame, text="Temperatura", padding=10)
        temp_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        self.temp_label = tk.Label(temp_frame, text="--.- °C",
                                 font=('Helvetica', 36, 'bold'),
                                 fg=self.colors["primary"],
                                 bg=self.colors["background"])
        self.temp_label.pack(pady=10, padx=10)

        # Sección relés
        relays_frame = ttk.LabelFrame(control_frame, text="Control de Relés", padding=10)
        relays_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.relay_buttons = []
        relay_names = [
            "RELE 1\n(VÁLVULA)", "RELE 2\n(ENFRIAMIENTO)",
            "RELE 3\n(ALIVIO)", "RELE 4\n(FILTRACIÓN)"
        ]
        for i in range(4):
            btn = tk.Button(relays_frame, text=f"{relay_names[i]}\nOFF",
                            command=lambda idx=i: self.toggle_relay(idx + 1),
                            font=('Helvetica', 12, 'bold'),
                            bg=self.colors["light"], activebackground=self.colors["success"],
                            fg=self.colors["text"], activeforeground="white",
                            width=12, height=3, relief="flat")
            btn.grid(row=i // 2, column=i % 2, padx=10, pady=10, sticky="nsew")
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self.colors["secondary"]))
            btn.bind("<Leave>", lambda e, b=btn, i=i:
                     b.config(bg=self.colors["success"] if self.system_state["relays"][i] else self.colors["light"]))
            self.relay_buttons.append(btn)
            relays_frame.grid_columnconfigure(i % 2, weight=1)

        # Panel derecho
        right_frame = ttk.Frame(control_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)

        # Configuración MQTT
        mqtt_config_frame = ttk.LabelFrame(right_frame, text="Configuración MQTT", padding=10)
        mqtt_config_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(mqtt_config_frame, text="Broker IP:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.broker_entry = ttk.Entry(mqtt_config_frame, textvariable=self.mqtt_broker_var)
        self.broker_entry.grid(row=0, column=1, sticky=tk.EW, pady=2, padx=5)

        ttk.Label(mqtt_config_frame, text="Puerto:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.port_entry = ttk.Entry(mqtt_config_frame, textvariable=self.mqtt_port_var)
        self.port_entry.grid(row=1, column=1, sticky=tk.EW, pady=2, padx=5)

        ttk.Label(mqtt_config_frame, text="Usuario:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.user_entry = ttk.Entry(mqtt_config_frame, textvariable=self.mqtt_username_var)
        self.user_entry.grid(row=2, column=1, sticky=tk.EW, pady=2, padx=5)

        ttk.Label(mqtt_config_frame, text="Contraseña:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.pass_entry = ttk.Entry(mqtt_config_frame, textvariable=self.mqtt_password_var, show="*")
        self.pass_entry.grid(row=3, column=1, sticky=tk.EW, pady=2, padx=5)

        apply_btn = ttk.Button(mqtt_config_frame, text="Aplicar Configuración", command=self.apply_mqtt_config)
        apply_btn.grid(row=4, column=0, columnspan=2, pady=10, sticky="ew")

        # Estado de conexión
        status_frame = ttk.Frame(right_frame)
        status_frame.pack(fill=tk.X, pady=5)
        self.broker_status = tk.Label(status_frame, text="Broker: Desconectado", 
                                     fg=self.colors["danger"], bg=self.colors["background"])
        self.broker_status.pack(side=tk.LEFT, padx=5)
        self.esp32_status = tk.Label(status_frame, text="ESP32: Desconectado", 
                                    fg=self.colors["danger"], bg=self.colors["background"])
        self.esp32_status.pack(side=tk.LEFT, padx=5)

        # Entradas digitales
        inputs_frame = ttk.LabelFrame(right_frame, text="Entradas", padding=10)
        inputs_frame.pack(fill=tk.X, pady=5)
        self.input_labels = []
        for name in ["Válvula", "Temp. Alta", "Tapa"]:
            lbl = tk.Label(inputs_frame, text=f"{name}: OFF",
                          bg=self.colors["light"], fg=self.colors["text"], 
                          font=('Helvetica', 12), width=15)
            lbl.pack(pady=5, fill=tk.X)
            self.input_labels.append(lbl)

        # Comandos
        cmd_frame = ttk.LabelFrame(right_frame, text="Comandos", padding=10)
        cmd_frame.pack(fill=tk.X, pady=5)
        ttk.Button(cmd_frame, text="Reiniciar ESP32", command=self.send_reset).pack(fill=tk.X, pady=5)
        ttk.Button(cmd_frame, text="Refrescar Pantalla", command=self.send_refresh).pack(fill=tk.X, pady=5)

        # Gráfico
        graph_frame = ttk.Frame(main_frame)
        graph_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        self.setup_graph(graph_frame)

    def setup_graph(self, parent):
        self.fig = Figure(figsize=(10, 4), dpi=100, facecolor=self.colors["background"])
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor(self.colors["light"])
        self.ax.tick_params(axis='both', colors=self.colors["text"])
        self.ax.set_title('Historial de Temperatura', color=self.colors["text"])
        self.line, = self.ax.plot([], [], color=self.colors["accent2"], linewidth=2)
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def apply_mqtt_config(self):
        try:
            new_port = self.mqtt_port_var.get()
            if not (0 < new_port < 65536):
                raise ValueError("Puerto inválido")
        except Exception as e:
            messagebox.showerror("Error", f"Error en configuración:\n{str(e)}")
            return

        self.mqtt_config.update({
            "broker": self.mqtt_broker_var.get(),
            "port": new_port,
            "username": self.mqtt_username_var.get(),
            "password": self.mqtt_password_var.get()
        })

        if self.client:
            self.client.disconnect()
        self.setup_mqtt()

    def setup_mqtt(self):
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.client.username_pw_set(self.mqtt_config["username"], self.mqtt_config["password"])
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

        try:
            self.client.connect(self.mqtt_config["broker"], self.mqtt_config["port"], 60)
            self.client.loop_start()
        except Exception as e:
            messagebox.showerror("Error MQTT", f"No se pudo conectar: {str(e)}")
            self.broker_status.config(text="Broker: Error", fg=self.colors["danger"])

    def on_connect(self, client, userdata, flags, rc, properties):
        if rc == 0:
            self.system_state["connection"] = True
            self.broker_status.config(text="Broker: Conectado", fg=self.colors["success"])
            client.subscribe(self.mqtt_config["topics"]["status"])
            client.subscribe(self.mqtt_config["topics"]["temperature"])
            for t in self.mqtt_config["topics"]["inputs"]:
                client.subscribe(t)
            client.subscribe(self.mqtt_config["topics"]["relays"])
        else:
            self.broker_status.config(text=f"Broker: Error {rc}", fg=self.colors["danger"])

    def on_message(self, client, userdata, msg):
        try:
            payload = msg.payload.decode()
            if msg.topic == self.mqtt_config["topics"]["status"]:
                self.last_esp32_heartbeat = datetime.now()
                self.esp32_connected = (payload == "online")
                status = "Conectado" if self.esp32_connected else "Desconectado"
                color = self.colors["success"] if self.esp32_connected else self.colors["danger"]
                self.esp32_status.config(text=f"ESP32: {status}", fg=color)

            elif msg.topic == self.mqtt_config["topics"]["temperature"]:
                temp = float(payload)
                self.update_temperature(temp)
                self.temp_history.append(temp)
                self.time_history.append(datetime.now().timestamp())
                if len(self.temp_history) > self.max_data_points:
                    self.temp_history.pop(0)
                    self.time_history.pop(0)
                self.update_graph()

            elif msg.topic.startswith("relay/"):
                relay_num = int(msg.topic.split('/')[1])
                if 0 <= relay_num < 4:
                    state = payload == "ON"
                    self.system_state["relays"][relay_num] = state
                    self.update_relay_ui(relay_num + 1, state)

            elif msg.topic in self.mqtt_config["topics"]["inputs"]:
                idx = self.mqtt_config["topics"]["inputs"].index(msg.topic)
                state = payload == "ON"
                self.system_state["inputs"][idx] = state
                self.update_input_ui(idx, state)

        except Exception as e:
            print(f"Error procesando mensaje: {str(e)}")

    def on_disconnect(self, client, userdata, rc, properties):
        self.system_state["connection"] = False
        self.broker_status.config(text="Broker: Desconectado", fg=self.colors["danger"])

    def check_esp32_connection(self):
        if self.last_esp32_heartbeat:
            delta = (datetime.now() - self.last_esp32_heartbeat).total_seconds()
            if delta > 15:
                self.esp32_connected = False
                self.esp32_status.config(text="ESP32: Desconectado", fg=self.colors["danger"])
        self.root.after(5000, self.check_esp32_connection)

    def update_temperature(self, temp):
        self.temp_label.config(text=f"{temp:.1f} °C")
        if temp > 180:
            color = self.colors["danger"]
        elif temp > 150:
            color = self.colors["warning"]
        else:
            color = self.colors["primary"]
        self.temp_label.config(fg=color)

    def update_graph(self):
        if self.time_history:
            self.line.set_data(self.time_history, self.temp_history)
            self.ax.relim()
            self.ax.autoscale_view()
            self.ax.set_xticks([])
            self.canvas.draw()

    def toggle_relay(self, num):
        if not self.system_state["connection"]:
            messagebox.showwarning("Error", "Sin conexión MQTT")
            return
        new_state = not self.system_state["relays"][num-1]
        topic = f"relay/{num-1}"
        self.client.publish(topic, "ON" if new_state else "OFF")
    
    # Actualizar la interfaz
        btn = self.relay_buttons[num-1]
        lines = btn.cget('text').split('\n')
        new_text = f"{lines[0]}\n{'ON' if new_state else 'OFF'}"
        btn.config(
            text=new_text,
            bg=self.colors["success"] if new_state else self.colors["light"]
        )
        self.system_state["relays"][num-1] = new_state

        def update_input_ui(self, idx, state):
            lbl = self.input_labels[idx]
            name = lbl.cget('text').split(':')[0]
            lbl.config(
                text=f"{name}: {'ON' if state else 'OFF'}",
                bg=self.colors["success"] if state else self.colors["light"]
            )

    def send_reset(self):
        if self.system_state["connection"]:
            self.client.publish("reset", "ON")

    def send_refresh(self):
        if self.system_state["connection"]:
            self.client.publish("refresh", "ON")

if __name__ == "__main__":
    root = tk.Tk()
    app = ESP32ControlApp(root)
    root.mainloop()