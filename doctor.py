"""
doctor.py — Pantallas de modo Doctor: contraseña, selección de pruebas por
secciones, categoría de edad del paciente y configuración del módulo doctor.
"""

import json
import os
import pygame

import config
from hud import CYAN, GREEN, RED, TEXT, TEXT_DIM, draw_button
from phobia import PHOBIA_OPTIONS


# ---------------- PERSISTENCIA ----------------

def _ensure_data_dir():
    os.makedirs(config.DATA_DIR, exist_ok=True)


def load_session_config():
    _ensure_data_dir()

    if not os.path.exists(config.SESSION_CONFIG_PATH):
        return None

    try:
        with open(config.SESSION_CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def save_session_config(cfg):
    _ensure_data_dir()

    with open(config.SESSION_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


def load_section_progress():
    if not os.path.exists(config.SECTION_PROGRESS_PATH):
        return 0

    try:
        with open(config.SECTION_PROGRESS_PATH, "r", encoding="utf-8") as f:
            return json.load(f).get("index", 0)
    except Exception:
        return 0


def save_section_progress(idx):
    _ensure_data_dir()

    with open(config.SECTION_PROGRESS_PATH, "w", encoding="utf-8") as f:
        json.dump({"index": idx}, f)


def default_session_config():
    return {
        "sections": [
            {
                "selectedTests": dict(config.DEFAULT_SELECTED_TESTS),
                "phobia": {
                    "mode": "patient_pick",
                    "doctorPhobia": None
                }
            }
        ],
        "ageCategory": "adultos_16mas",
    }


# ---------------- VOZ SEGURA ----------------

def jarvis_say(engine, mensaje):
    """
    Intenta hacer hablar a JARVIS sin romper el programa.
    Sirve si tu voz usa say(), speak() o si todavía no está conectada.
    """

    print(f"JARVIS: {mensaje}")

    if not hasattr(engine, "voice"):
        return

    try:
        engine.voice.say(mensaje)
        return
    except Exception:
        pass

    try:
        engine.voice.speak(mensaje)
        return
    except Exception:
        pass


# ---------------- CONTRASEÑA ----------------

def prompt_password(engine):
    """
    Muestra un campo de contraseña centrado.
    Devuelve True si la contraseña es correcta.
    Devuelve False si es incorrecta o si se cancela.
    """

    typed = {"value": ""}
    result = {"done": None}

    box_rect = pygame.Rect(
        engine.width // 2 - 180,
        engine.height // 2 - 20,
        360,
        50
    )

    ok_rect = pygame.Rect(
        engine.width // 2 - 160,
        engine.height // 2 + 50,
        150,
        46
    )

    cancel_rect = pygame.Rect(
        engine.width // 2 + 10,
        engine.height // 2 + 50,
        150,
        46
    )

    def on_event(event):
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_RETURN:
                result["done"] = (
                    typed["value"] == str(config.ADMIN_PASSWORD)
                )

            elif event.key == pygame.K_BACKSPACE:
                typed["value"] = typed["value"][:-1]

            elif event.key == pygame.K_ESCAPE:
                result["done"] = False

            elif event.unicode and event.unicode.isprintable():
                typed["value"] += event.unicode

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            if ok_rect.collidepoint(event.pos):
                result["done"] = (
                    typed["value"] == str(config.ADMIN_PASSWORD)
                )

            elif cancel_rect.collidepoint(event.pos):
                result["done"] = False

    def render(surface):
        overlay = pygame.Surface(
            surface.get_size(),
            pygame.SRCALPHA
        )

        overlay.fill((2, 4, 6, 235))
        surface.blit(overlay, (0, 0))

        title = engine.font_big.render(
            "ACCESO RESTRINGIDO",
            True,
            TEXT
        )

        surface.blit(
            title,
            (
                engine.width // 2 - title.get_width() // 2,
                engine.height // 2 - 130
            )
        )

        sub = engine.font_med.render(
            "Ingresa la contraseña de doctor/administrador",
            True,
            TEXT_DIM
        )

        surface.blit(
            sub,
            (
                engine.width // 2 - sub.get_width() // 2,
                engine.height // 2 - 80
            )
        )

        pygame.draw.rect(
            surface,
            (255, 255, 255, 10),
            box_rect,
            border_radius=8
        )

        pygame.draw.rect(
            surface,
            CYAN,
            box_rect,
            width=2,
            border_radius=8
        )

        masked = "•" * len(typed["value"])

        txt = engine.font_med.render(
            masked,
            True,
            TEXT
        )

        surface.blit(
            txt,
            (
                box_rect.centerx - txt.get_width() // 2,
                box_rect.centery - txt.get_height() // 2
            )
        )

        mouse_pos = pygame.mouse.get_pos()

        draw_button(
            surface,
            ok_rect,
            "Entrar",
            engine.font_med,
            bg_hover=ok_rect.collidepoint(mouse_pos)
        )

        draw_button(
            surface,
            cancel_rect,
            "Cancelar",
            engine.font_med,
            color=RED,
            bg_hover=cancel_rect.collidepoint(mouse_pos)
        )

    engine.run_until(
        lambda: result["done"] is not None,
        on_event,
        render,
        with_console=False
    )

    acceso_correcto = result["done"] is True

    if acceso_correcto:
        jarvis_say(engine, "Acceso concedido.")
    else:
        jarvis_say(engine, "Acceso denegado.")

    return acceso_correcto


# ---------------- PANTALLA DE CONFIGURACIÓN DEL DOCTOR ----------------

def run_doctor_config(engine):
    salir = {"value": False}

    def on_event(event):
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_BACKSPACE:
                salir["value"] = True

            elif event.key == pygame.K_ESCAPE:
                salir["value"] = True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pass

    def render(surface):
        titulo = engine.font_big.render(
            "MODO DOCTOR",
            True,
            GREEN
        )

        mensaje = engine.font_med.render(
            "Acceso concedido — presiona Backspace para regresar",
            True,
            TEXT
        )

        surface.blit(
            titulo,
            (
                engine.width // 2 - titulo.get_width() // 2,
                engine.height // 2 - 60
            )
        )

        surface.blit(
            mensaje,
            (
                engine.width // 2 - mensaje.get_width() // 2,
                engine.height // 2 + 10
            )
        )

    engine.run_until(
        lambda: salir["value"],
        on_event,
        render,
        with_console=False,
        with_gauges=False
    )