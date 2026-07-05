"""
sensors.py — Control de sensores biomédicos de CREA-J.

Actualmente:
- Detecta automáticamente Arduino, ESP32 o adaptadores USB serial.
- Lee BPM y SpO2 desde el MAX30102.
- Usa datos simulados si no existe conexión.
- Detecta desconexiones durante la ejecución.

Formato esperado desde Arduino:

BPM: 80   SpO2: 98%
"""

import random
import re
import time

import serial
from serial.tools import list_ports


class BioState:
    def __init__(self):
        # Últimos valores válidos registrados
        self.bpm = random.randint(65, 85)
        self.spo2 = random.randint(95, 99)

        # Estado del sensor
        self.arduino = None
        self.puerto = None
        self.modo_simulado = True
        self.ultima_linea = ""
        self.ultimo_error = ""

        # Intenta conectarse automáticamente
        self.conectar()

    def detectar_puerto(self):
        """
        Busca automáticamente un Arduino, ESP32
        o adaptador USB serial.

        Los puertos Bluetooth son ignorados.
        """

        puertos = list(list_ports.comports())

        if not puertos:
            print("⚠️ No hay puertos COM disponibles.")
            return None

        palabras_clave = [
            "arduino",
            "ch340",
            "ch341",
            "cp210",
            "usb serial",
            "usb-serial",
            "silicon labs",
            "ftdi",
            "esp32",
        ]

        print("🔍 Buscando puerto COM...")

        for puerto in puertos:
            descripcion = (
                f"{puerto.description} "
                f"{puerto.manufacturer or ''} "
                f"{puerto.hwid}"
            ).lower()

            print(
                f"   • {puerto.device}: "
                f"{puerto.description}"
            )

            if "bluetooth" in descripcion:
                continue

            if any(
                palabra in descripcion
                for palabra in palabras_clave
            ):
                print(
                    f"✅ Dispositivo compatible encontrado "
                    f"en {puerto.device}."
                )

                return puerto.device

        print(
            "⚠️ No se encontró Arduino, ESP32 "
            "ni adaptador USB serial."
        )

        return None

    def conectar(self):
        """
        Intenta detectar y abrir el puerto del sensor.
        """

        # Evita abrir dos veces el mismo puerto
        if self.arduino is not None:
            return True

        self.puerto = self.detectar_puerto()

        if self.puerto is None:
            self.modo_simulado = True
            self.ultimo_error = (
                "No se encontró ningún sensor conectado."
            )

            print(
                "⚠️ Se utilizarán datos simulados."
            )

            return False

        try:
            self.arduino = serial.Serial(
                port=self.puerto,
                baudrate=115200,
                timeout=1,
            )

            # Arduino normalmente se reinicia al abrir el puerto
            time.sleep(2)

            # Limpia datos anteriores del búfer
            self.arduino.reset_input_buffer()

            self.modo_simulado = False
            self.ultimo_error = ""

            print(
                f"✅ MAX30102 conectado automáticamente "
                f"en {self.puerto}."
            )

            return True

        except Exception as error:
            self.arduino = None
            self.modo_simulado = True
            self.ultimo_error = str(error)

            print(
                f"⚠️ No se pudo abrir el puerto "
                f"{self.puerto}: {error}"
            )

            return False

    def desconectar(self):
        """
        Cierra correctamente la conexión serial.
        """

        if self.arduino is not None:
            try:
                self.arduino.close()

            except Exception:
                pass

        self.arduino = None
        self.modo_simulado = True

    def reconectar(self):
        """
        Cierra la conexión anterior y vuelve
        a buscar automáticamente el sensor.
        """

        print("🔄 Intentando reconectar el MAX30102...")

        self.desconectar()
        self.puerto = None

        return self.conectar()

    def procesar_linea(self, linea):
        """
        Extrae BPM y SpO2 desde una línea del Arduino.

        Formato esperado:

        BPM: 80   SpO2: 98%
        """

        patron = re.search(
            r"BPM\s*:\s*(\d+).*?"
            r"SpO2\s*:\s*(\d+)",
            linea,
            re.IGNORECASE,
        )

        if patron is None:
            return False

        bpm_leido = int(patron.group(1))
        spo2_leido = int(patron.group(2))

        datos_validos = False

        # Rangos amplios para evitar aceptar errores evidentes
        if 35 <= bpm_leido <= 220:
            self.bpm = bpm_leido
            datos_validos = True

        if 70 <= spo2_leido <= 100:
            self.spo2 = spo2_leido
            datos_validos = True

        return datos_validos

    def leer_oximetro(self):
        """
        Lee BPM y SpO2.

        Si el sensor no está conectado,
        genera valores simulados.
        """

        if self.arduino is not None:
            try:
                linea = self.arduino.readline().decode(
                    "utf-8",
                    errors="ignore",
                ).strip()

                if linea:
                    self.ultima_linea = linea
                    print("Arduino:", linea)

                    self.procesar_linea(linea)

                return {
                    "bpm": self.bpm,
                    "spo2": self.spo2,
                    "connected": True,
                    "simulated": False,
                    "port": self.puerto,
                    "raw_line": self.ultima_linea,
                    "error": "",
                }

            except (
                serial.SerialException,
                OSError,
            ) as error:
                self.ultimo_error = str(error)

                print(
                    "⚠️ El MAX30102 fue desconectado:",
                    error,
                )

                self.desconectar()

            except Exception as error:
                self.ultimo_error = str(error)

                print(
                    "⚠️ Error leyendo el MAX30102:",
                    error,
                )

        # Datos simulados
        self.bpm = max(
            55,
            min(
                110,
                self.bpm + random.randint(-3, 3),
            ),
        )

        self.spo2 = random.randint(95, 99)

        return {
            "bpm": self.bpm,
            "spo2": self.spo2,
            "connected": False,
            "simulated": True,
            "port": None,
            "raw_line": "",
            "error": self.ultimo_error,
        }

    def estado_bpm(self, bpm):
        """
        Clasifica el ritmo cardíaco de manera básica.
        No representa un diagnóstico médico.
        """

        if bpm < 50:
            return {
                "text": "PULSO BAJO",
                "level": "warning",
            }

        if bpm <= 100:
            return {
                "text": "RANGO ESTABLE",
                "level": "normal",
            }

        if bpm <= 120:
            return {
                "text": "PULSO ELEVADO",
                "level": "warning",
            }

        return {
            "text": "PULSO MUY ELEVADO",
            "level": "danger",
        }

    def estado_spo2(self, spo2):
        """
        Clasifica la saturación de oxígeno.
        No representa un diagnóstico médico.
        """

        if spo2 >= 95:
            return {
                "text": "OXIGENACIÓN ESTABLE",
                "level": "normal",
            }

        if spo2 >= 90:
            return {
                "text": "OXIGENACIÓN BAJA",
                "level": "warning",
            }

        return {
            "text": "OXIGENACIÓN MUY BAJA",
            "level": "danger",
        }

    def read_hr(self):
        """
        Método conservado para mantener compatibilidad
        con otras partes del programa.

        HRV todavía no se calcula de manera real.
        """

        datos = self.leer_oximetro()

        return datos["bpm"], None

    def read_spo2(self):
        """
        Método conservado para mantener compatibilidad.
        """

        return self.spo2

    def read_eeg(self):
        """
        Datos provisionales para evitar romper otros módulos.

        El EEG real será implementado posteriormente.
        """

        return {
            "delta": None,
            "theta": None,
            "alpha": None,
            "beta": None,
            "gamma": None,
            "connected": False,
            "simulated": True,
        }

    def snapshot(self):
        """
        Obtiene una medición completa del estado actual.

        Actualmente solo BPM y SpO2 pueden ser reales.
        """

        datos_oximetro = self.leer_oximetro()

        bpm = datos_oximetro["bpm"]
        spo2 = datos_oximetro["spo2"]

        estado_bpm = self.estado_bpm(bpm)
        estado_spo2 = self.estado_spo2(spo2)

        return {
            "bpm": bpm,
            "spo2": spo2,

            # Todavía no existen mediciones reales
            "hrv": None,
            "eeg": self.read_eeg(),
            "anxiety": {
                "score": None,
                "level": "no_disponible",
            },

            # Estado del oxímetro
            "oximeter_connected": datos_oximetro[
                "connected"
            ],
            "simulated": datos_oximetro[
                "simulated"
            ],
            "port": datos_oximetro["port"],
            "raw_line": datos_oximetro[
                "raw_line"
            ],
            "error": datos_oximetro["error"],

            # Clasificación visual
            "bpm_status": estado_bpm,
            "spo2_status": estado_spo2,

            # Identifica el tipo de medición guardada
            "sensor": "MAX30102",
            "measurement_type": "oximeter_test",
            "timestamp": time.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        }