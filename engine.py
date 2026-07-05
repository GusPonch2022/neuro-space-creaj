"""
engine.py — Motor central de la app.

Maneja:
- Ventana pygame
- Fondo HUD
- Núcleo JARVIS
- Medidores
- Consola
- Voz
- Botones genéricos
- Preguntas con 4 opciones
"""

import sys
import time
import pygame

import config
from sensors import BioState
from voice_system.voice_manager import VoiceManager

from hud import (
    Particles,
    Core,
    Gauge,
    Console,
    draw_button,
    CYAN,
    AMBER,
    GREEN,
    RED,
    TEXT,
    TEXT_DIM,
)


class Engine:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption(
            f"{config.PROJECT_NAME} — {config.ASSISTANT_NAME}"
        )

        if config.FULLSCREEN:
            self.screen = pygame.display.set_mode(
                (0, 0),
                pygame.FULLSCREEN,
            )
        else:
            self.screen = pygame.display.set_mode(
                config.WINDOW_SIZE
            )

        self.width, self.height = self.screen.get_size()
        self.clock = pygame.time.Clock()

        # Fuentes
        self.font_title = pygame.font.SysFont(
            "Arial",
            30,
            bold=True,
        )

        self.font_status = pygame.font.SysFont(
            "Consolas",
            16,
        )

        self.font_gtitle = pygame.font.SysFont(
            "Consolas",
            14,
        )

        self.font_gvalue = pygame.font.SysFont(
            "Arial",
            22,
            bold=True,
        )

        self.font_gsub = pygame.font.SysFont(
            "Consolas",
            13,
        )

        self.font_big = pygame.font.SysFont(
            "Arial",
            46,
            bold=True,
        )

        self.font_med = pygame.font.SysFont(
            "Arial",
            20,
        )

        self.font_small_btn = pygame.font.SysFont(
            "Arial",
            15,
        )

        self.font_log = pygame.font.SysFont(
            "Consolas",
            15,
        )

        # Alias por si algún archivo usa estos nombres
        self.font_medium = self.font_med
        self.font_small = self.font_status

        # Sistemas internos
        self.bio = BioState()
        self.voice = VoiceManager()

        self.particles = Particles(
            self.width,
            self.height,
            count=90,
        )

        self.core = Core(
            center=(
                self.width // 2,
                self.height // 2,
            ),
            base_radius=90,
        )

        self.console_rect = pygame.Rect(
            self.width - 560,
            self.height - 320,
            520,
            290,
        )

        self.console = Console(
            self.console_rect,
            self.font_med,
            self.font_log,
        )

        gauge_x = self.width - 560

        self.gauges = {
            "eeg": Gauge(
                (gauge_x, 110),
                28,
                CYAN,
                "EEG · ONDAS ALFA",
            ),
            "hr": Gauge(
                (gauge_x, 190),
                28,
                AMBER,
                "RITMO CARDIACO",
                "BPM",
            ),
            "spo2": Gauge(
                (gauge_x, 270),
                28,
                GREEN,
                "OXIGENACIÓN",
                "%",
            ),
            "anx": Gauge(
                (gauge_x, 350),
                28,
                RED,
                "ANSIEDAD",
                "/100",
            ),
        }

        self.status_text = "SISTEMA EN ESPERA"
        self.status_color = AMBER

    # -------------------------------------------------
    # BÁSICOS
    # -------------------------------------------------
    def quit_app(self):
        pygame.quit()
        sys.exit()

    def handle_global_events(self, event):
        if event.type == pygame.QUIT:
            self.quit_app()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.quit_app()

    def set_status(self, text, color):
        self.status_text = text
        self.status_color = color

    # -------------------------------------------------
    # TEXTO
    # -------------------------------------------------
    def wrap_text(self, text, font, max_width):
        """
        Divide un texto largo en varias líneas para que no se salga de pantalla.
        """

        words = text.split(" ")
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + word + " "

            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line.strip():
                    lines.append(current_line.strip())
                current_line = word + " "

        if current_line.strip():
            lines.append(current_line.strip())

        return lines

    def draw_centered_wrapped_text(
        self,
        surface,
        text,
        font,
        color,
        center_x,
        start_y,
        max_width,
        line_gap=8,
    ):
        """
        Dibuja texto centrado en varias líneas.
        """

        lines = self.wrap_text(
            text,
            font,
            max_width,
        )

        y = start_y

        for line in lines:
            surf = font.render(
                line,
                True,
                color,
            )

            rect = surf.get_rect(
                center=(
                    center_x,
                    y,
                )
            )

            surface.blit(
                surf,
                rect,
            )

            y += font.get_height() + line_gap

        return y

    # -------------------------------------------------
    # FONDO GENERAL
    # -------------------------------------------------
    def render_background(
        self,
        dt,
        with_console=True,
        with_gauges=True,
    ):
        self.screen.fill((4, 7, 10))

        # Partículas
        self.particles.update_and_draw(self.screen)

        # Título principal
        title_surf = self.font_title.render(
            config.PROJECT_NAME,
            True,
            TEXT,
        )

        self.screen.blit(
            title_surf,
            (
                self.width // 2 - title_surf.get_width() // 2,
                30,
            ),
        )

        # Núcleo central
        self.core.update_and_draw(
            self.screen,
            self.voice.speaking,
            dt,
        )

        label = self.font_status.render(
            "J A R V I S",
            True,
            TEXT_DIM,
        )

        self.screen.blit(
            label,
            (
                self.core.center[0] - label.get_width() // 2,
                self.core.center[1] + self.core.base_radius + 25,
            ),
        )

        # Medidores
        if with_gauges:
            for gauge in self.gauges.values():
                gauge.update(dt)

                gauge.draw(
                    self.screen,
                    self.font_gtitle,
                    self.font_gvalue,
                    self.font_gsub,
                )

        # Consola
        if with_console:
            self.console.draw(self.screen)

        # Barra de estado permanente
        self.draw_status_bar()

    def draw_status_bar(self):
        barra_rect = pygame.Rect(
            0,
            self.height - 34,
            self.width,
            34,
        )

        pygame.draw.rect(
            self.screen,
            (8, 16, 20),
            barra_rect,
        )

        pygame.draw.line(
            self.screen,
            CYAN,
            (0, barra_rect.top),
            (self.width, barra_rect.top),
            1,
        )

        if self.bio.arduino is not None:
            sensor_estado = "MAX30102 CONECTADO"
            sensor_color = GREEN
        else:
            sensor_estado = "MODO SIMULADO"
            sensor_color = AMBER

        paciente_estado = "PACIENTE: NINGUNO"
        modo_estado = "MODO: SISTEMA"
        hora_actual = time.strftime("%H:%M:%S")

        texto_izquierda = self.font_status.render(
            paciente_estado,
            True,
            TEXT_DIM,
        )

        texto_centro = self.font_status.render(
            f"{sensor_estado}   |   {modo_estado}",
            True,
            sensor_color,
        )

        texto_derecha = self.font_status.render(
            hora_actual,
            True,
            TEXT_DIM,
        )

        self.screen.blit(
            texto_izquierda,
            (
                20,
                barra_rect.centery - texto_izquierda.get_height() // 2,
            ),
        )

        self.screen.blit(
            texto_centro,
            (
                self.width // 2 - texto_centro.get_width() // 2,
                barra_rect.centery - texto_centro.get_height() // 2,
            ),
        )

        self.screen.blit(
            texto_derecha,
            (
                self.width - texto_derecha.get_width() - 20,
                barra_rect.centery - texto_derecha.get_height() // 2,
            ),
        )

    # -------------------------------------------------
    # MEDIDORES
    # -------------------------------------------------
    def update_gauges_with_snapshot(self, snap):
        self.gauges["eeg"].set_value(
            snap["eeg"]["alpha"] * 100,
            str(round(snap["eeg"]["alpha"] * 100)),
            f"beta {round(snap['eeg']['beta'] * 100)}%",
        )

        self.gauges["hr"].set_value(
            (snap["bpm"] - 50) / (110 - 50) * 100,
            str(snap["bpm"]),
            f"HRV {snap['hrv']} ms",
        )

        self.gauges["spo2"].set_value(
            (snap["spo2"] - 90) / (100 - 90) * 100,
            str(snap["spo2"]),
            "normal",
        )

        anx_pct = snap["anxiety"]["score"] * 100

        self.gauges["anx"].set_value(
            anx_pct,
            str(round(anx_pct)),
            snap["anxiety"]["level"].replace("_", " "),
        )

        level = snap["anxiety"]["level"]

        if level == "ansiedad_alta":
            self.set_status(
                "ANSIEDAD ALTA DETECTADA",
                RED,
            )
        elif level == "ansiedad_moderada":
            self.set_status(
                "MONITOREANDO · ANSIEDAD MODERADA",
                AMBER,
            )
        else:
            self.set_status(
                "MONITOREANDO · ESTADO ESTABLE",
                GREEN,
            )

    # -------------------------------------------------
    # BUCLE GENÉRICO
    # -------------------------------------------------
    def run_until(
        self,
        condition_fn,
        extra_event_handler=None,
        render_extra=None,
        with_console=True,
        with_gauges=True,
    ):
        """
        Renderiza continuamente hasta que condition_fn() sea True.
        """

        last_time = time.time()

        while not condition_fn():
            now = time.time()
            dt = now - last_time
            last_time = now

            for event in pygame.event.get():
                self.handle_global_events(event)

                if extra_event_handler:
                    extra_event_handler(event)

            self.render_background(
                dt,
                with_console=with_console,
                with_gauges=with_gauges,
            )

            if render_extra:
                render_extra(self.screen)

            pygame.display.flip()
            self.clock.tick(config.FPS)

    # -------------------------------------------------
    # VOZ + CONSOLA
    # -------------------------------------------------
    def jarvis_say(self, text, color=CYAN):
        self.console.add_line(
            config.ASSISTANT_NAME,
            text,
            color,
        )

        self.voice.say_async(text)

        self.run_until(
            lambda: not self.voice.speaking
        )

    def get_text_answer(self):
        self.console.input_active = True
        self.console.input_text = ""

        answer = {
            "value": None
        }

        def on_event(event):
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if self.console.input_text.strip():
                        answer["value"] = self.console.input_text.strip()

                elif event.key == pygame.K_BACKSPACE:
                    self.console.input_text = self.console.input_text[:-1]

                else:
                    if event.unicode and event.unicode.isprintable():
                        self.console.input_text += event.unicode

        self.run_until(
            lambda: answer["value"] is not None,
            on_event,
        )

        self.console.input_active = False

        user_text = answer["value"]

        self.console.add_line(
            "TÚ",
            user_text,
            AMBER,
        )

        return user_text

    # -------------------------------------------------
    # BOTONES GENÉRICOS / PREGUNTAS
    # -------------------------------------------------
    def get_button_choice(
        self,
        title,
        options,
        sub="",
        cols=2,
        extra_buttons=None,
        btn_w=None,
        return_full=False,
    ):
        """
        Muestra botones y devuelve la opción seleccionada.

        options:
            [
                ("Texto visible", valor_interno),
                ...
            ]

        return_full=False:
            devuelve solo el valor interno.

        return_full=True:
            devuelve:
            {
                "text": texto visible,
                "value": valor interno
            }
        """

        result = {
            "text": None,
            "value": None,
        }

        gap = 20
        btn_h = 76

        max_grid_w = self.width - 160

        if btn_w is None:
            btn_w = min(
                430,
                (max_grid_w - (cols - 1) * gap) // cols,
            )

        rows = (len(options) + cols - 1) // cols

        grid_w = cols * btn_w + (cols - 1) * gap
        grid_h = rows * btn_h + (rows - 1) * gap

        start_x = self.width // 2 - grid_w // 2
        start_y = 330

        rects = []

        for i, (label, value) in enumerate(options):
            col = i % cols
            row = i // cols

            rect = pygame.Rect(
                start_x + col * (btn_w + gap),
                start_y + row * (btn_h + gap),
                btn_w,
                btn_h,
            )

            rects.append(
                (
                    rect,
                    label,
                    value,
                )
            )

        extra_rects = []

        if extra_buttons:
            extra_btn_w = 320
            extra_y = start_y + grid_h + 35

            total_extra_w = (
                len(extra_buttons) * extra_btn_w
                + (len(extra_buttons) - 1) * gap
            )

            extra_x = self.width // 2 - total_extra_w // 2

            for j, (label, value) in enumerate(extra_buttons):
                rect = pygame.Rect(
                    extra_x + j * (extra_btn_w + gap),
                    extra_y,
                    extra_btn_w,
                    btn_h,
                )

                extra_rects.append(
                    (
                        rect,
                        label,
                        value,
                    )
                )

        def choose(label, value):
            result["text"] = label
            result["value"] = value

        def on_event(event):
            if event.type == pygame.KEYDOWN:
                if event.key in [
                    pygame.K_1,
                    pygame.K_2,
                    pygame.K_3,
                    pygame.K_4,
                ]:
                    index = event.key - pygame.K_1

                    if index < len(options):
                        label, value = options[index]
                        choose(label, value)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for rect, label, value in rects + extra_rects:
                    if rect.collidepoint(event.pos):
                        choose(label, value)

        def render_extra(surface):
            overlay = pygame.Surface(
                surface.get_size(),
                pygame.SRCALPHA,
            )

            overlay.fill(
                (2, 4, 6, 235)
            )

            surface.blit(
                overlay,
                (0, 0),
            )

            # Subtítulo arriba
            if sub:
                sub_surf = self.font_med.render(
                    sub,
                    True,
                    CYAN,
                )

                surface.blit(
                    sub_surf,
                    (
                        self.width // 2 - sub_surf.get_width() // 2,
                        55,
                    ),
                )

            # Pregunta arriba
            self.draw_centered_wrapped_text(
                surface=surface,
                text=title,
                font=self.font_big,
                color=TEXT,
                center_x=self.width // 2,
                start_y=120,
                max_width=self.width - 160,
                line_gap=8,
            )

            mouse_pos = pygame.mouse.get_pos()

            # Botones principales
            for rect, label, value in rects:
                draw_button(
                    surface,
                    rect,
                    label,
                    self.font_med,
                    bg_hover=rect.collidepoint(mouse_pos),
                )

            # Botones extra
            for rect, label, value in extra_rects:
                draw_button(
                    surface,
                    rect,
                    label,
                    self.font_med,
                    color=RED,
                    bg_hover=rect.collidepoint(mouse_pos),
                )

            # Instrucción inferior
            info = self.font_status.render(
                "Selecciona una opción para continuar · también puedes usar 1, 2, 3 o 4",
                True,
                TEXT_DIM,
            )

            surface.blit(
                info,
                (
                    self.width // 2 - info.get_width() // 2,
                    self.height - 70,
                ),
            )

        self.run_until(
            lambda: result["value"] is not None,
            on_event,
            render_extra,
            with_console=False,
            with_gauges=False,
        )

        if return_full:
            return {
                "text": result["text"],
                "value": result["value"],
            }

        return result["value"]

    def get_suds(self, title_text):
        """
        Escala SUDS 0-10 + botón de detener.
        Devuelve int 0-10 o 'STOP'.
        """

        options = [
            (str(i), i)
            for i in range(11)
        ]

        return self.get_button_choice(
            title_text,
            options,
            sub="0 = nada de ansiedad · 10 = ansiedad máxima",
            cols=11,
            extra_buttons=[
                (
                    "⏹ DETENER LA EXPOSICIÓN",
                    "STOP",
                )
            ],
        )