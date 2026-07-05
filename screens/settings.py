import pygame

from hud import CYAN, RED, TEXT, TEXT_DIM, draw_button


def draw_panel(surface, rect, border_color=CYAN):
    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    panel.fill((5, 18, 24, 210))
    surface.blit(panel, rect.topleft)

    pygame.draw.rect(
        surface,
        border_color,
        rect,
        width=2,
        border_radius=12
    )


def show_settings_screen(engine):
    salir = {"value": False}

    back_rect = pygame.Rect(40, engine.height - 80, 220, 50)

    def on_event(event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE or event.key == pygame.K_ESCAPE:
                salir["value"] = True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if back_rect.collidepoint(event.pos):
                salir["value"] = True

    def render(surface):
        surface.fill((3, 8, 18))

        title = engine.font_big.render(
            "CONFIGURACIÓN",
            True,
            CYAN
        )

        subtitle = engine.font_med.render(
            "Ajustes generales del sistema Neuro Space",
            True,
            TEXT_DIM
        )

        surface.blit(
            title,
            (
                engine.width // 2 - title.get_width() // 2,
                55
            )
        )

        surface.blit(
            subtitle,
            (
                engine.width // 2 - subtitle.get_width() // 2,
                110
            )
        )

        panel = pygame.Rect(
            engine.width // 2 - 430,
            175,
            860,
            360
        )

        draw_panel(surface, panel)

        lines = [
            "Opciones pendientes:",
            "",
            "• Activar / desactivar voz de JARVIS",
            "• Ajustar volumen",
            "• Cambiar modo de pantalla",
            "• Configurar puerto COM de sensores",
            "• Reiniciar datos de sesión",
            "• Configurar pruebas del paciente"
        ]

        y = panel.y + 35

        for line in lines:
            color = TEXT if line and not line.startswith("•") else TEXT_DIM

            txt = engine.font_med.render(
                line,
                True,
                color
            )

            surface.blit(
                txt,
                (
                    panel.x + 40,
                    y
                )
            )

            y += 35

        mouse_pos = pygame.mouse.get_pos()

        draw_button(
            surface,
            back_rect,
            "REGRESAR",
            engine.font_med,
            color=RED,
            bg_hover=back_rect.collidepoint(mouse_pos)
        )

    engine.run_until(
        lambda: salir["value"],
        on_event,
        render,
        with_console=False,
        with_gauges=False
    )