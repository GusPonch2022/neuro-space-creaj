"""
config.py — Neuro Space / Jarvis (Python, escritorio, modo Doctor/Paciente)
"""

import os

PROJECT_NAME = "NEURO SPACE"
ASSISTANT_NAME = "JARVIS"
ADMIN_PASSWORD = "1035"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
DATA_DIR = os.path.join(BASE_DIR, "data")
SESSION_CONFIG_PATH = os.path.join(DATA_DIR, "session_config.json")
SECTION_PROGRESS_PATH = os.path.join(DATA_DIR, "section_progress.json")
HISTORY_PATH = os.path.join(DATA_DIR, "history.json")
LOGO_PATH = os.path.join(ASSETS_DIR, "logo.png")

VIDEO_LIBRARY = {
    "calma": os.path.join(ASSETS_DIR, "videos", "calma.mp4"),
    "ansiedad_moderada": os.path.join(ASSETS_DIR, "videos", "ansiedad_moderada.mp4"),
    "ansiedad_alta": os.path.join(ASSETS_DIR, "videos", "ansiedad_alta.mp4"),
}
MUSIC_LIBRARY = {
    "calma": os.path.join(ASSETS_DIR, "music", "calma.mp3"),
    "ansiedad_moderada": os.path.join(ASSETS_DIR, "music", "ansiedad_moderada.mp3"),
    "ansiedad_alta": os.path.join(ASSETS_DIR, "music", "ansiedad_alta.mp3"),
}
SCENE_TITLES = {
    "calma": "OCÉANO CALMO",
    "ansiedad_moderada": "BOSQUE CON LLUVIA",
    "ansiedad_alta": "RESPIRACIÓN GUIADA",
}

USE_REAL_MUSE = False
USE_REAL_POLAR = False
POLAR_MAC_ADDRESS = "XX:XX:XX:XX:XX:XX"
USE_REAL_MAX30102 = False

FULLSCREEN = True #False   
WINDOW_SIZE = (1280, 720)
FPS = 30

TTS_RATE = 145

FALLBACK_SCENE_SECONDS = 16
PHOBIA_LEVEL_SECONDS = 13

PHOBIA_LABELS = {
    "aranas": "Arañas",
    "espacios_cerrados": "Espacios encerrados",
    "alturas": "Alturas",
    "multitudes": "Mucha gente",
    "mar": "El mar / aguas profundas",
    "aviones": "Aviones",
    "perros": "Perros",
    "ojos": "Ojos / miradas",
}

ALL_TEST_KEYS = [
    "gad7", "attention", "stroop", "nback", "decision", "breathing",
    "phobia", "experience",
]
TEST_LABELS = {
    "gad7": "GAD-7 (ansiedad)",
    "attention": "Atención y tiempo de reacción",
    "stroop": "Test de Stroop",
    "nback": "Memoria de trabajo (N-Back)",
    "decision": "Toma de decisiones",
    "breathing": "Respiración y coherencia cardiaca",
    "phobia": "Exposición gradual a un miedo específico",
    "experience": "Experiencia inmersiva (escena generada)",
}
DEFAULT_SELECTED_TESTS = {k: True for k in ALL_TEST_KEYS}
DEFAULT_SELECTED_TESTS["phobia"] = False

AGE_CATEGORIES = ["ninos_5_8", "ninos_8_12", "adolescentes_12_16", "adultos_16mas"]
AGE_LABELS = {
    "ninos_5_8": "5 a 8 años",
    "ninos_8_12": "8 a 12 años",
    "adolescentes_12_16": "12 a 16 años",
    "adultos_16mas": "16+ / adultos",
}
AGE_PARAMS = {
    "ninos_5_8": {"attention": 5, "stroop": 6, "nback": 8, "decision": 6, "phobia_levels": 2, "allow_gad7": False},
    "ninos_8_12": {"attention": 6, "stroop": 8, "nback": 10, "decision": 8, "phobia_levels": 3, "allow_gad7": False},
    "adolescentes_12_16": {"attention": 8, "stroop": 10, "nback": 12, "decision": 9, "phobia_levels": 3, "allow_gad7": True},
    "adultos_16mas": {"attention": 8, "stroop": 12, "nback": 14, "decision": 10, "phobia_levels": 4, "allow_gad7": True},
}


def get_age_params(age_category):
    return AGE_PARAMS.get(age_category, AGE_PARAMS["adultos_16mas"])
