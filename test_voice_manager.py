import time

from voice_system.voice_manager import VoiceManager


voice = VoiceManager()

voice.say("Bienvenido al sistema de monitoreo Neuro Space.")
voice.say("Soy JARVIS. Sistema de asistencia médica inicializado.")
voice.say("Modo de prueba de voz femenina activado.")
voice.say("Prueba número cuatro. Si escuchas esto, la cola de voz funciona correctamente.")

time.sleep(20)

voice.stop()