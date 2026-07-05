"""
voice_manager.py
Administrador fuerte de voz para JARVIS.

Ventajas:
- No bloquea pygame.
- Usa cola de mensajes.
- Habla en un hilo separado.
- Evita mensajes duplicados.
- Permite mensajes normales, urgentes e interrumpibles.
- Tiene compatibilidad con el sistema viejo: say_async().
"""

import queue
import threading
import time

from voice_system.voice_engine import VoiceEngine


class VoiceManager:
    def __init__(self):
        self.engine = VoiceEngine()

        self.queue = queue.Queue()
        self.running = True
        self.speaking = False

        self.last_text = ""
        self.last_time = 0
        self.duplicate_delay = 3.0

        self.worker = threading.Thread(
            target=self._voice_loop,
            daemon=True
        )
        self.worker.start()

        print("✅ VoiceManager iniciado.")

    def say(self, text, urgent=False, interrupt=False):
        """
        Envía texto a JARVIS.

        Modo normal:
            engine.voice.say("Hola")

        Modo interrumpible:
            engine.voice.say("Pregunta nueva", interrupt=True)

        Modo urgente:
            engine.voice.say("Alerta", urgent=True)
        """

        if not text:
            return

        clean_text = str(text).strip()

        if not clean_text:
            return

        now = time.time()

        if not interrupt:
            if (
                clean_text == self.last_text
                and now - self.last_time < self.duplicate_delay
            ):
                print("⚠️ Voz duplicada ignorada:", clean_text)
                return

        self.last_text = clean_text
        self.last_time = now

        message = {
            "text": clean_text,
            "urgent": urgent,
            "interrupt": interrupt,
            "time": now,
        }

        if interrupt:
            self._clear_queue()

            try:
                self.engine.stop()
            except Exception:
                pass

            self.queue.put(message)
            return

        if urgent:
            self._clear_queue()
            self.queue.put(message)
            return

        self.queue.put(message)

    def say_async(self, text, urgent=False, interrupt=False):
        """
        Compatibilidad con el sistema viejo.
        """

        self.say(
            text,
            urgent=urgent,
            interrupt=interrupt,
        )

    def _voice_loop(self):
        while self.running:
            message = None

            try:
                message = self.queue.get(timeout=0.2)

                text = message.get("text", "")
                urgent = message.get("urgent", False)
                interrupt = message.get("interrupt", False)

                self.speaking = True

                if interrupt:
                    print("⏩ Voz interrumpible:", text)
                elif urgent:
                    print("🚨 Voz urgente:", text)
                else:
                    print("🗣️ JARVIS:", text)

                try:
                    self.engine.speak_blocking(text)
                except Exception as error:
                    print("❌ Error al hablar en speak_blocking.")
                    print("Error:", error)

            except queue.Empty:
                pass

            except Exception as error:
                print("❌ Error en VoiceManager.")
                print("Error:", error)

            finally:
                self.speaking = False

                if message is not None:
                    try:
                        self.queue.task_done()
                    except Exception:
                        pass

    def _clear_queue(self):
        """
        Limpia todos los mensajes pendientes.
        """

        try:
            while not self.queue.empty():
                self.queue.get_nowait()
                self.queue.task_done()
        except Exception:
            pass

    def stop_current_voice(self):
        """
        Corta la voz actual y limpia la cola.
        """

        self._clear_queue()

        try:
            self.engine.stop()
        except Exception:
            pass

        self.speaking = False

    def is_speaking(self):
        return self.speaking

    def has_pending_messages(self):
        return not self.queue.empty()

    def stop(self):
        self.running = False
        self._clear_queue()

        try:
            self.engine.stop()
        except Exception:
            pass

        print("🛑 VoiceManager detenido.")