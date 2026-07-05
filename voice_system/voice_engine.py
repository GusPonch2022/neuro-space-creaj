"""
voice_engine.py
Motor seguro de voz usando pyttsx3.

Versión reforzada:
- Selecciona voz femenina en español.
- Reinicia el motor en cada frase para evitar que pyttsx3 se quede trabado.
- Es más lento, pero mucho más estable para pygame.
"""

import pyttsx3

from voice_system.voice_constants import (
    VOICE_RATE,
    VOICE_VOLUME,
    LANGUAGE_PRIORITY,
    FEMALE_PRIORITY,
)


class VoiceEngine:
    def __init__(self):
        self.selected_voice_id = None
        self.selected_voice_name = None
        self.ready = False

        self._detect_best_voice()

    def _detect_best_voice(self):
        """
        Detecta la mejor voz disponible.
        Solo se usa para guardar el ID de la voz.
        """

        try:
            engine = pyttsx3.init()
            voices = engine.getProperty("voices")

            if not voices:
                print("⚠️ No se encontraron voces instaladas.")
                self.ready = False
                return

            best_voice = None
            best_score = -1

            print("\n🎙️ Voces encontradas:")

            for voice in voices:
                name = (voice.name or "").lower()
                voice_id = (voice.id or "").lower()
                text = f"{name} {voice_id}"

                score = 0

                for word in LANGUAGE_PRIORITY:
                    if word in text:
                        score += 10

                for word in FEMALE_PRIORITY:
                    if word in text:
                        score += 5

                print(f"   • {voice.name} | score: {score}")

                if score > best_score:
                    best_score = score
                    best_voice = voice

            if best_voice:
                self.selected_voice_id = best_voice.id
                self.selected_voice_name = best_voice.name
                self.ready = True

                print(f"\n🎙️ Voz seleccionada: {best_voice.name}\n")
                print("✅ Motor de voz preparado correctamente.")

            else:
                self.ready = False
                print("⚠️ No se pudo seleccionar una voz.")

            try:
                engine.stop()
            except Exception:
                pass

        except Exception as error:
            self.ready = False
            print("❌ No se pudo preparar el motor de voz.")
            print("Error:", error)

    def speak_blocking(self, text):
        """
        Habla una frase.
        Se crea un motor nuevo por cada frase para evitar bloqueos.
        """

        if not self.ready:
            print("⚠️ Voz no disponible:", text)
            return

        if not text:
            return

        engine = None

        try:
            engine = pyttsx3.init()

            engine.setProperty("rate", VOICE_RATE)
            engine.setProperty("volume", VOICE_VOLUME)

            if self.selected_voice_id:
                engine.setProperty("voice", self.selected_voice_id)

            engine.say(text)
            engine.runAndWait()

        except Exception as error:
            print("❌ Error hablando.")
            print("Texto:", text)
            print("Error:", error)

        finally:
            try:
                if engine:
                    engine.stop()
            except Exception:
                pass

    def stop(self):
        """
        Compatibilidad con VoiceManager.
        """
        pass