"""
jarvis_intro.py — Pantalla de presentación de JARVIS antes de iniciar la evaluación.
"""

import pygame

from hud import TEXT, TEXT_DIM, CYAN
from screen_manager import HOME


def draw_intro_button(screen, rect, text, font, mouse_pos):
    hovered = rect.collidepoint(mouse_pos)

    if hovered:
        fill_color = (0, 80, 110)
        border_color = (0, 220, 255)
    else:
        fill_color = (8, 25, 40)
        border_color = CYAN

    pygame.draw.rect(screen, fill_color, rect, border_radius=14)
    pygame.draw.rect(screen, border_color, rect, 2, border_radius=14)

    txt_surf = font.render(text, True, TEXT)
    txt_rect = txt_surf.get_rect(center=rect.center)
    screen.blit(txt_surf, txt_rect)


def show_jarvis_intro_screen(engine):
    """
    Pantalla inicial del modo paciente.
    JARVIS se presenta y espera a que el usuario presione INICIAR EVALUACIÓN.
    """

    start_button = pygame.Rect(
        engine.width // 2 - 210,
        engine.height - 170,
        420,
        75,
    )

    back_button = pygame.Rect(
        40,
        engine.height - 90,
        220,
        55,
    )

    # Para que JARVIS no repita la presentación mil veces
    if not hasattr(engine, "jarvis_patient_intro_done"):
        engine.jarvis_patient_intro_done = False

    if not engine.jarvis_patient_intro_done:
        engine.jarvis_patient_intro_done = True

        if hasattr(engine, "voice") and engine.voice:
            engine.voice.say(
                "Soy JARVIS, asistente del sistema Neuro Space. "
                "Te guiaré durante la evaluación del paciente. "
                "Cuando estés listo, presiona iniciar evaluación."
            )

    while True:
        engine.screen.fill((5, 10, 18))

        mouse_pos = pygame.mouse.get_pos()

        # Título principal
        title = engine.font_big.render("MODO PACIENTE", True, CYAN)
        title_rect = title.get_rect(center=(engine.width // 2, 75))
        engine.screen.blit(title, title_rect)

        # Subtítulo
        subtitle = engine.font_medium.render(
            "Presentación de JARVIS",
            True,
            TEXT_DIM,
        )
        subtitle_rect = subtitle.get_rect(center=(engine.width // 2, 130))
        engine.screen.blit(subtitle, subtitle_rect)

        # Caja central más estética
        box = pygame.Rect(
            engine.width // 2 - 500,
            180,
            1000,
            300,
        )

        pygame.draw.rect(engine.screen, (8, 18, 32), box, border_radius=22)
        pygame.draw.rect(engine.screen, CYAN, box, 2, border_radius=22)

        lines = [
            "Soy JARVIS, asistente del sistema Neuro Space.",
            "Te guiaré durante la evaluación del paciente.",
            "Primero responderás algunas preguntas.",
            "Luego se analizarán los resultados obtenidos.",
            "Cuando estés listo, presiona INICIAR EVALUACIÓN.",
        ]

        # Texto centrado y más grande
        y = box.y + 45

        for line in lines:
            text = engine.font_medium.render(line, True, TEXT)
            text_rect = text.get_rect(center=(engine.width // 2, y))
            engine.screen.blit(text, text_rect)
            y += 48

        # Botón iniciar
        draw_intro_button(
            engine.screen,
            start_button,
            "INICIAR EVALUACIÓN",
            engine.font_medium,
            mouse_pos,
        )

        # Botón volver
        draw_intro_button(
            engine.screen,
            back_button,
            "VOLVER",
            engine.font_small,
            mouse_pos,
        )

        pygame.display.flip()
        engine.clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if start_button.collidepoint(event.pos):
                    return "START_EVALUATION"

                if back_button.collidepoint(event.pos):
                    return HOME