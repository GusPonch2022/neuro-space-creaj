"""
voice.py — Voz de Jarvis, 100% offline (pyttsx3). No requiere internet ni API.
"""

import threading
import pyttsx3
import config


class Voice:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", config.TTS_RATE)
        self._pick_spanish_voice()
        self.speaking = False
        self._lock = threading.Lock()

    def _pick_spanish_voice(self):
        try:
            voices = self.engine.getProperty("voices")
            for v in voices:
                name = (v.name or "").lower()
                vid = (v.id or "").lower()
                if "spanish" in name or "es" in vid or "es_" in vid or "es-" in vid:
                    self.engine.setProperty("voice", v.id)
                    return
        except Exception:
            pass

    def say(self, text):
        with self._lock:
            self.speaking = True
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            finally:
                self.speaking = False

    def say_async(self, text):
        t = threading.Thread(target=self.say, args=(text,), daemon=True)
        t.start()
        return t