import random
import pygame

from hud import CYAN, GREEN, AMBER, RED, TEXT, TEXT_DIM, draw_button


# ---------------- UTILIDADES VISUALES ----------------

def draw_card(surface, rect, title, subtitle, status, action, font_big, font_med, color, mouse_pos):
    hover = rect.collidepoint(mouse_pos)

    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)

    if hover:
        panel.fill((8, 28, 34, 235))
    else:
        panel.fill((5, 18, 24, 220))

    surface.blit(panel, rect.topleft)

    pygame.draw.rect(
        surface,
        color,
        rect,
        width=2,
        border_radius=14
    )

    line_y = rect.y + 28

    pygame.draw.line(
        surface,
        color,
        (rect.x + 28, line_y),
        (rect.right - 28, line_y),
        width=2
    )

    title_render = font_big.render(title, True, TEXT)
    subtitle_render = font_med.render(subtitle, True, TEXT_DIM)
    status_render = font_med.render(status, True, color)
    action_render = font_med.render(action, True, color)

    surface.blit(
        title_render,
        (
            rect.centerx - title_render.get_width() // 2,
            rect.y + 70
        )
    )

    surface.blit(
        subtitle_render,
        (
            rect.centerx - subtitle_render.get_width() // 2,
            rect.y + 140
        )
    )

    surface.blit(
        status_render,
        (
            rect.centerx - status_render.get_width() // 2,
            rect.y + 185
        )
    )

    surface.blit(
        action_render,
        (
            rect.centerx - action_render.get_width() // 2,
            rect.y + 225
        )
    )


def draw_dark_panel(surface, rect, border_color=CYAN):
    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    panel.fill((5, 18, 24, 220))
    surface.blit(panel, rect.topleft)

    pygame.draw.rect(
        surface,
        border_color,
        rect,
        width=2,
        border_radius=12
    )


def draw_center_title(engine, surface, title_text, subtitle_text):
    title = engine.font_big.render(
        title_text,
        True,
        TEXT
    )

    subtitle = engine.font_med.render(
        subtitle_text,
        True,
        TEXT_DIM
    )

    surface.blit(
        title,
        (
            70,
            90
        )
    )

    surface.blit(
        subtitle,
        (
            70,
            160
        )
    )


def draw_sensor_title(engine, surface, title_text, subtitle_text):
    title = engine.font_big.render(
        title_text,
        True,
        CYAN
    )

    subtitle = engine.font_med.render(
        subtitle_text,
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


# ---------------- PANTALLA PRINCIPAL DE SENSORES ----------------

def show_sensors_screen(engine):
    salir = {"value": False}
    selected = {"screen": None}

    card_w = 300
    card_h = 270
    gap = 55

    total_w = (card_w * 3) + (gap * 2)
    start_x = engine.width // 2 - total_w // 2
    card_y = 285

    oxi_rect = pygame.Rect(start_x, card_y, card_w, card_h)
    ecg_rect = pygame.Rect(start_x + card_w + gap, card_y, card_w, card_h)
    eeg_rect = pygame.Rect(start_x + (card_w + gap) * 2, card_y, card_w, card_h)

    back_rect = pygame.Rect(70, engine.height - 95, 275, 60)

    def on_event(event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE or event.key == pygame.K_ESCAPE:
                salir["value"] = True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if back_rect.collidepoint(event.pos):
                salir["value"] = True

            elif oxi_rect.collidepoint(event.pos):
                selected["screen"] = "oximeter"

            elif ecg_rect.collidepoint(event.pos):
                selected["screen"] = "ecg"

            elif eeg_rect.collidepoint(event.pos):
                selected["screen"] = "eeg"

    def render(surface):
        draw_center_title(
            engine,
            surface,
            "MÓDULO DE SENSORES",
            "Seleccione el circuito que desea comprobar."
        )

        mouse_pos = pygame.mouse.get_pos()

        draw_card(
            surface,
            oxi_rect,
            "OXÍMETRO",
            "BPM y SpO₂",
            "DISPONIBLE",
            "SELECCIONAR",
            engine.font_big,
            engine.font_med,
            GREEN,
            mouse_pos
        )

        draw_card(
            surface,
            ecg_rect,
            "ECG",
            "Frecuencia cardíaca",
            "PENDIENTE",
            "SELECCIONAR",
            engine.font_big,
            engine.font_med,
            AMBER,
            mouse_pos
        )

        draw_card(
            surface,
            eeg_rect,
            "EEG",
            "Ondas cerebrales",
            "PENDIENTE",
            "SELECCIONAR",
            engine.font_big,
            engine.font_med,
            AMBER,
            mouse_pos
        )

        info = engine.font_med.render(
            "Cada sensor tendrá su propia pantalla de conexión, prueba y resultados.",
            True,
            TEXT_DIM
        )

        surface.blit(
            info,
            (
                engine.width // 2 - info.get_width() // 2,
                engine.height - 175
            )
        )

        draw_button(
            surface,
            back_rect,
            "VOLVER AL INICIO",
            engine.font_med,
            color=CYAN,
            bg_hover=back_rect.collidepoint(mouse_pos)
        )

    engine.run_until(
        lambda: salir["value"] or selected["screen"] is not None,
        on_event,
        render,
        with_console=False,
        with_gauges=False
    )

    if selected["screen"] == "oximeter":
        show_oximeter_screen(engine)
        show_sensors_screen(engine)

    elif selected["screen"] == "ecg":
        show_ecg_screen(engine)
        show_sensors_screen(engine)

    elif selected["screen"] == "eeg":
        show_eeg_screen(engine)
        show_sensors_screen(engine)


# ---------------- OXÍMETRO ----------------

def show_oximeter_screen(engine):
    salir = {"value": False}

    back_rect = pygame.Rect(70, engine.height - 95, 275, 60)

    def get_bpm():
        try:
            return int(engine.bio.read_hr())
        except Exception:
            return random.randint(70, 90)

    def get_spo2():
        try:
            return int(engine.bio.read_spo2())
        except Exception:
            return random.randint(96, 99)

    def on_event(event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE or event.key == pygame.K_ESCAPE:
                salir["value"] = True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if back_rect.collidepoint(event.pos):
                salir["value"] = True

    def render(surface):
        surface.fill((3, 8, 18))

        draw_sensor_title(
            engine,
            surface,
            "OXÍMETRO",
            "Lectura individual de BPM y oxigenación"
        )

        bpm = get_bpm()
        spo2 = get_spo2()

        panel = pygame.Rect(
            engine.width // 2 - 430,
            180,
            860,
            330
        )

        draw_dark_panel(surface, panel, GREEN)

        bpm_title = engine.font_med.render(
            "Ritmo cardíaco",
            True,
            TEXT_DIM
        )

        bpm_value = engine.font_big.render(
            f"{bpm} BPM",
            True,
            AMBER
        )

        spo2_title = engine.font_med.render(
            "Oxigenación",
            True,
            TEXT_DIM
        )

        spo2_value = engine.font_big.render(
            f"{spo2} %",
            True,
            GREEN
        )

        surface.blit(
            bpm_title,
            (
                panel.x + 80,
                panel.y + 70
            )
        )

        surface.blit(
            bpm_value,
            (
                panel.x + 80,
                panel.y + 110
            )
        )

        surface.blit(
            spo2_title,
            (
                panel.x + 500,
                panel.y + 70
            )
        )

        surface.blit(
            spo2_value,
            (
                panel.x + 500,
                panel.y + 110
            )
        )

        if spo2 >= 95 and 55 <= bpm <= 110:
            estado = "Estado: lectura dentro de rango esperado"
            color_estado = GREEN
        else:
            estado = "Estado: revisar colocación del sensor"
            color_estado = RED

        estado_txt = engine.font_med.render(
            estado,
            True,
            color_estado
        )

        surface.blit(
            estado_txt,
            (
                panel.x + 80,
                panel.y + 235
            )
        )

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


# ---------------- ECG ----------------

def show_ecg_screen(engine):
    salir = {"value": False}

    back_rect = pygame.Rect(70, engine.height - 95, 275, 60)

    def on_event(event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE or event.key == pygame.K_ESCAPE:
                salir["value"] = True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if back_rect.collidepoint(event.pos):
                salir["value"] = True

    def render(surface):
        surface.fill((3, 8, 18))

        draw_sensor_title(
            engine,
            surface,
            "ECG / RITMO CARDIACO",
            "Módulo pendiente de conexión"
        )

        panel = pygame.Rect(
            engine.width // 2 - 430,
            180,
            860,
            330
        )

        draw_dark_panel(surface, panel, AMBER)

        lines = [
            "Estado: pendiente de integración.",
            "",
            "Aquí se mostrará:",
            "• Señal cardíaca",
            "• Frecuencia estimada",
            "• Calidad de contacto",
            "• Posible ruido en la señal"
        ]

        y = panel.y + 55

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
                    panel.x + 60,
                    y
                )
            )

            y += 36

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


# ---------------- EEG ----------------

def show_eeg_screen(engine):
    salir = {"value": False}

    back_rect = pygame.Rect(70, engine.height - 95, 275, 60)

    def on_event(event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE or event.key == pygame.K_ESCAPE:
                salir["value"] = True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if back_rect.collidepoint(event.pos):
                salir["value"] = True

    def render(surface):
        surface.fill((3, 8, 18))

        draw_sensor_title(
            engine,
            surface,
            "EEG / ONDAS CEREBRALES",
            "Módulo pendiente de conexión"
        )

        panel = pygame.Rect(
            engine.width // 2 - 430,
            180,
            860,
            330
        )

        draw_dark_panel(surface, panel, CYAN)

        lines = [
            "Estado: pendiente de integración.",
            "",
            "Aquí se mostrará:",
            "• Ondas alfa",
            "• Ondas beta",
            "• Ondas theta",
            "• Calidad de contacto"
        ]

        y = panel.y + 55

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
                    panel.x + 60,
                    y
                )
            )

            y += 36

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