"""
scene.py — Escena visual generada al final de la sesión (océano calmo,
bosque con lluvia, respiración guiada), elegida según el sensor simulado
COMBINADO con las respuestas reales de la entrevista (igual que la web).
"""

import re
import math
import time
import random
import pygame

import config
from hud import CYAN, TEXT, TEXT_DIM

SCENE_TITLES = {
    "calma": "OCÉANO CALMO",
    "ansiedad_moderada": "BOSQUE CON LLUVIA",
    "ansiedad_alta": "RESPIRACIÓN GUIADA",
}

STRESS_KEYWORDS = ["estres", "estrés", "ansiedad", "nervios", "preocup", "agobi", "presion", "presión", "examen", "problema"]
STIMULANT_KEYWORDS = ["cafe", "café", "cafeina", "cafeína", "energizante", "alcohol", "redbull", "monster"]


def parse_sleep_hours(text):
    if not text:
        return None
    m = re.search(r"(\d+(?:[.,]\d+)?)", text)
    if not m:
        return None
    try:
        return float(m.group(1).replace(",", "."))
    except ValueError:
        return None


def derive_scene_profile(initial_snap, answers, gad7):
    from intake import QUESTIONS
    sleep_answer = answers.get(QUESTIONS[3], "")
    stress_answer = (answers.get(QUESTIONS[4], "") + " " + answers.get(QUESTIONS[7], "")).lower()
    stimulant_answer = answers.get(QUESTIONS[5], "").lower()

    sleep_hours = parse_sleep_hours(sleep_answer)
    stress_flag = any(k in stress_answer for k in STRESS_KEYWORDS)
    stimulant_flag = any(k in stimulant_answer for k in STIMULANT_KEYWORDS)

    componentes = [initial_snap["anxiety"]["score"]]
    if gad7:
        componentes.append(gad7["total"] / 21)
    combined = sum(componentes) / len(componentes)
    if stress_flag: combined += 0.12
    if stimulant_flag: combined += 0.04
    combined = min(1.0, combined)

    if combined >= 0.62:
        level = "ansiedad_alta"
    elif combined >= 0.32:
        level = "ansiedad_moderada"
    else:
        level = "calma"

    intensity = 0.2 + combined*0.9
    if stress_flag: intensity += 0.25
    if stimulant_flag: intensity += 0.15
    intensity = min(1.5, intensity)

    fatigue = 0.0
    if sleep_hours is not None:
        if sleep_hours < 5: fatigue = 0.8
        elif sleep_hours < 6.5: fatigue = 0.4

    return {
        "level": level, "intensity": intensity, "fatigue": fatigue,
        "combinedScore": combined, "sleepHours": sleep_hours,
        "stressFlag": stress_flag, "stimulantFlag": stimulant_flag,
    }


def draw_scene(surface, rect, level, t, intensity, fatigue):
    clip = surface.subsurface(rect)
    w, h = rect.width, rect.height
    turb = intensity * 0.5

    if level == "calma":
        clip.fill((6, 35, 48))
        for i in range(6):
            points = []
            for x in range(0, w, 8):
                y = h*0.5 + i*18 + math.sin(x*0.02 + t*(1.2+intensity*0.6) + i) * (10+turb*30)
                points.append((x, y))
            if len(points) > 1:
                pygame.draw.lines(clip, CYAN, False, points, 2)
    elif level == "ansiedad_moderada":
        clip.fill((4, 26, 18))
        drop_count = int(60 + intensity*40)
        for i in range(drop_count):
            x = (i*47 + t*(60+intensity*30)) % w
            y = (i*71 + t*(220+turb*260)) % h
            pygame.draw.line(clip, (120, 220, 180), (x, y), (x-4, y+14), 2)
    else:  # ansiedad_alta
        clip.fill((26, 10, 20))
        cx, cy = w//2, h//2
        r = int(40 + 30*math.sin(t*(0.8+intensity*0.3)) + 30 + turb*40)
        r = max(10, r)
        pygame.draw.circle(clip, (255, 140, 170), (cx, cy), r, width=3)

    if fatigue > 0.2:
        dark = pygame.Surface((w, h), pygame.SRCALPHA)
        dark.fill((0, 0, 0, int(fatigue*90)))
        clip.blit(dark, (0, 0))

    pygame.draw.rect(surface, CYAN, rect, width=1)


def run_experience(engine, level, profile, duration_seconds=None):
    duration_seconds = duration_seconds or config.FALLBACK_SCENE_SECONDS
    rect = pygame.Rect(60, 130, engine.width-660, engine.height-360)
    t0 = time.time()
    snapshots = []
    last_snap_time = [time.time()]

    def render(surface):
        t = time.time()-t0
        draw_scene(surface, rect, level, t, profile["intensity"], profile["fatigue"])
        title = engine.font_med.render(SCENE_TITLES.get(level, ""), True, CYAN)
        surface.blit(title, (rect.left, rect.top-36))
        pct = min(1.0, (time.time()-t0)/duration_seconds)
        bar_rect = pygame.Rect(rect.left, engine.height-50, rect.width, 8)
        pygame.draw.rect(surface, (40, 50, 55), bar_rect, border_radius=4)
        pygame.draw.rect(surface, CYAN, (bar_rect.x, bar_rect.y, int(bar_rect.width*pct), bar_rect.height), border_radius=4)

    def condition():
        now = time.time()
        if now - last_snap_time[0] >= 1.0:
            snap = engine.bio.snapshot()
            snapshots.append(snap)
            engine.update_gauges_with_snapshot(snap)
            last_snap_time[0] = now
        return (now - t0) >= duration_seconds

    engine.run_until(condition, None, render, with_console=False)
    return snapshots
