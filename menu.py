import pygame

from hud import draw_button, CYAN

from screen_manager import (
    HOME,
    PATIENT,
    SENSORS,
    ANALYSIS,
    HISTORY,
    SETTINGS,
    DOCTOR,
)


def show_main_menu(engine):
    """
    Menú principal de NeuroSpace.
    Devuelve la pantalla seleccionada.
    """

    botones = {
        HOME: pygame.Rect(
            engine.width // 2 - 150,
            100,
            300,
            65,
        ),

        PATIENT: pygame.Rect(60, 220, 300, 75),
        SENSORS: pygame.Rect(60, 340, 300, 75),
        DOCTOR: pygame.Rect(60, 460, 300, 75),

        ANALYSIS: pygame.Rect(
            engine.width - 360,
            220,
            300,
            75,
        ),
        HISTORY: pygame.Rect(
            engine.width - 360,
            340,
            300,
            75,
        ),
        SETTINGS: pygame.Rect(
            engine.width - 360,
            460,
            300,
            75,
        ),
    }

    etiquetas = {
        HOME: "INICIO",
        PATIENT: "PACIENTE",
        SENSORS: "SENSORES",
        DOCTOR: "DOCTOR",
        ANALYSIS: "ANÁLISIS",
        HISTORY: "HISTORIAL",
        SETTINGS: "CONFIGURACIÓN",
    }

    mensajes_voz = {
        HOME: "Pantalla de inicio seleccionada.",
        PATIENT: None,
        SENSORS: "Modo sensores activado.",
        DOCTOR: "Modo doctor seleccionado. Ingrese la contraseña.",
        ANALYSIS: "Abriendo módulo de análisis.",
        HISTORY: "Abriendo historial clínico.",
        SETTINGS: "Abriendo configuración del sistema.",
    }

    resultado = {"valor": None}

    def hablar_opcion(pantalla):
        """
        Hace que JARVIS hable cuando se presiona un botón.
        """

        if hasattr(engine, "voice") and engine.voice is not None:
            mensaje = mensajes_voz.get(
                pantalla,
                "Opción seleccionada."
            )
        if mensaje: 
            engine.voice.say(mensaje)

    def eventos(event):
        if (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
        ):
            for pantalla, rect in botones.items():
                if rect.collidepoint(event.pos):

                    hablar_opcion(pantalla)

                    resultado["valor"] = pantalla
                    return

    def dibujar(surface):
        mouse = pygame.mouse.get_pos()

        for pantalla, rect in botones.items():
            draw_button(
                surface,
                rect,
                etiquetas[pantalla],
                engine.font_med,
                color=CYAN,
                bg_hover=rect.collidepoint(mouse),
            )

    engine.run_until(
        lambda: resultado["valor"] is not None,
        eventos,
        dibujar,
        with_console=False,
        with_gauges=False,
    )

    return resultado["valor"]