"""
phobia.py — Exposición gradual a miedos específicos.
8 categorías x 3 niveles de intensidad, con escala SUDS (0-10) antes/después
de cada nivel y posibilidad de detenerse en cualquier momento.
"""

import time
import math
import random
import pygame

import config
from hud import CYAN, AMBER, GREEN, RED, TEXT, TEXT_DIM

PHOBIA_OPTIONS = [
    ("🕷️ Arañas", "aranas"),
    ("📦 Espacios encerrados", "espacios_cerrados"),
    ("🏔️ Alturas", "alturas"),
    ("👥 Mucha gente", "multitudes"),
    ("🌊 El mar / aguas profundas", "mar"),
    ("✈️ Aviones", "aviones"),
    ("🐕 Perros", "perros"),
    ("👁️ Ojos / miradas", "ojos"),
]


def select_phobia(engine):
    options = PHOBIA_OPTIONS + [("Ninguna de estas / omitir", None)]
    return engine.get_button_choice(
        "¿Cuál de estas situaciones te genera más miedo o incomodidad?",
        options, sub="Exposición gradual — elige una", cols=2
    )


def draw_phobia_scene(surface, w_offset, phobia_key, level, t):
    """Dibuja la escena de exposición dentro del área central de la pantalla."""
    surface_w, surface_h = surface.get_size()
    rect = pygame.Rect(w_offset, 130, surface_w-w_offset-60, surface_h-360)
    pygame.draw.rect(surface, (2, 4, 5), rect)
    clip = surface.subsurface(rect)
    w, h = rect.width, rect.height
    lv = level

    if phobia_key == "alturas":
        clip.fill((10, 24, 34))
        horizon_y = int(h*0.35)
        pygame.draw.rect(clip, (3, 7, 10), (0, horizon_y, w, h-horizon_y))
        for i in range(10+lv*8):
            speed = 40+lv*60
            x = (i*53 + t*10) % w
            y = horizon_y + ((i*37 + t*speed) % (h-horizon_y))
            alpha = min(255, int(60 + (y-horizon_y)/(h-horizon_y)*150))
            pygame.draw.line(clip, (180, 210, 230), (x, y), (x, y+10+lv*4), 1)
    elif phobia_key == "aranas":
        clip.fill((12, 10, 8))
        count = 2*lv
        for i in range(count):
            x = w*0.15 + (i*97 % int(w*0.7)) + math.sin(t*0.7+i)*10
            y = h*0.2 + (i*61 % int(h*0.6)) + math.cos(t*0.6+i)*10
            size = 10+lv*4
            for leg in range(8):
                ang = (leg/8)*2*math.pi + math.sin(t*2+i)*0.1
                pygame.draw.line(clip, (220, 190, 160), (x, y), (x+math.cos(ang)*size, y+math.sin(ang)*size), 2)
            pygame.draw.circle(clip, (26, 20, 16), (int(x), int(y)), int(size*0.4))
    elif phobia_key == "espacios_cerrados":
        clip.fill((5, 5, 5))
        margin = int(20 + lv*(min(w, h)*0.14))
        pygame.draw.rect(clip, (150, 150, 150), (margin, margin, w-margin*2, h-margin*2), width=4)
        dark = pygame.Surface((w, h), pygame.SRCALPHA)
        alpha = min(255, int(60+lv*40))
        dark.fill((0, 0, 0, alpha))
        pygame.draw.rect(dark, (0, 0, 0, 0), (margin, margin, w-margin*2, h-margin*2))
        clip.blit(dark, (0, 0))
    elif phobia_key == "multitudes":
        clip.fill((16, 20, 26))
        count = 25*lv
        for i in range(count):
            x = (i*43 + t*(10+lv*5)) % w
            y = h*0.4 + ((i*29) % int(h*0.55))
            pygame.draw.circle(clip, (180, 200, 220), (int(x), int(y)), 5)
            pygame.draw.rect(clip, (180, 200, 220), (int(x)-3, int(y)+5, 6, 12))
    elif phobia_key == "mar":
        depth = lv
        top_color = (10, 74, 92) if depth == 1 else (6, 47, 60) if depth == 2 else (2, 14, 20)
        bottom_color = (2, 35, 44) if depth < 3 else (1, 10, 14)
        for yy in range(0, h, 4):
            frac = yy/h
            color = tuple(int(top_color[i]+(bottom_color[i]-top_color[i])*frac) for i in range(3))
            pygame.draw.line(clip, color, (0, yy), (w, yy))
        for i in range(20):
            x = (i*61 + t*5) % w
            y = h - ((i*40 + t*(20+lv*15)) % h)
            pygame.draw.circle(clip, (200, 230, 240), (int(x), int(y)), 2+(i % 3))
    elif phobia_key == "aviones":
        shake = lv*3
        ox, oy = math.sin(t*9)*shake, math.cos(t*11)*shake*0.6
        clip.fill((10, 19, 32))
        for i in range(6):
            y = h*0.3 + i*20
            pygame.draw.line(clip, (255, 255, 255), (ox, y+oy), (w+ox, y+math.sin(t*4+i)*shake*2+oy), 1)
        px, py = w//2+ox, h//2+oy
        pygame.draw.polygon(clip, (200, 220, 230), [(px-40, py), (px+40, py), (px+15, py-6), (px-15, py-6)])
        pygame.draw.polygon(clip, (200, 220, 230), [(px-5, py-3), (px-25, py-26), (px-15, py-3)])
        pygame.draw.polygon(clip, (200, 220, 230), [(px-5, py+3), (px-25, py+26), (px-15, py+3)])

    elif phobia_key == "perros":
        clip.fill((21, 17, 13))
        size = 30+lv*30
        x, y = w//2, h//2 + (3-lv)*10
        pygame.draw.ellipse(clip, (58, 44, 30), (x-size, y-int(size*0.7), size*2, int(size*1.4)))
        pygame.draw.ellipse(clip, (58, 44, 30), (x-int(size*1.05), y-int(size*1.0), int(size*0.7), size))
        pygame.draw.ellipse(clip, (58, 44, 30), (x+int(size*0.35), y-int(size*1.0), int(size*0.7), size))
        pygame.draw.circle(clip, (255, 255, 255), (x-int(size*0.3), y-int(size*0.1)), max(2, int(size*0.08)))
        pygame.draw.circle(clip, (255, 255, 255), (x+int(size*0.3), y-int(size*0.1)), max(2, int(size*0.08)))
    elif phobia_key == "ojos":
        clip.fill((12, 12, 16))
        count = lv
        for i in range(count):
            x = w*(0.3+i*0.2)
            y = h/2
            r = 30+lv*8
            pygame.draw.ellipse(clip, (232, 232, 224), (x-r, y-r*0.6, r*2, r*1.2))
            blink = (math.sin(t*0.5+i)+1)/2
            iris_x = x + math.sin(t*0.3+i)*r*0.3
            pygame.draw.circle(clip, (58, 90, 106), (int(iris_x), int(y)), max(2, int(r*0.35*blink+2)))
            pygame.draw.circle(clip, (0, 0, 0), (int(iris_x), int(y)), max(1, int(r*0.15*blink+1)))
    else:
        clip.fill((10, 10, 10))

    pygame.draw.rect(surface, CYAN, rect, width=1)


engine_font_cache = {}


def run_phobia_exposure(engine, phobia_key, levels=3, level_seconds=None):
    global engine_font_cache
    engine_font_cache["big"] = engine.font_big
    level_seconds = level_seconds or config.PHOBIA_LEVEL_SECONDS
    label = config.PHOBIA_LABELS.get(phobia_key, phobia_key)
    results = []
    stopped_at_level = None

    for level in range(1, levels+1):
        before = engine.get_suds(f"Antes del nivel {level} de {levels} ({label}), ¿qué tan ansioso/a te sientes ahora?")
        if before == "STOP":
            stopped_at_level = level
            break

        snaps = []
        t0 = time.time()
        w_offset = 60

        def render(surface):
            t = time.time()-t0
            draw_phobia_scene(surface, w_offset, phobia_key, level, t)
            title = engine.font_med.render(f"{label} — Nivel {level}/{levels}", True, CYAN)
            surface.blit(title, (w_offset, 90))
            pct = min(1.0, (time.time()-t0)/level_seconds)
            bar_rect = pygame.Rect(w_offset, engine.height-90, engine.width-w_offset-600, 8)
            pygame.draw.rect(surface, (40, 50, 55), bar_rect, border_radius=4)
            pygame.draw.rect(surface, CYAN, (bar_rect.x, bar_rect.y, int(bar_rect.width*pct), bar_rect.height), border_radius=4)

        last_snap_time = [time.time()]

        def on_tick(event):
            pass

        def condition():
            now = time.time()
            if now - last_snap_time[0] >= 1.0:
                snap = engine.bio.snapshot()
                snaps.append(snap)
                engine.update_gauges_with_snapshot(snap)
                last_snap_time[0] = now
            return (now - t0) >= level_seconds

        engine.run_until(condition, None, render, with_console=False)

        after = engine.get_suds("¿Qué tan ansioso/a te sientes después de este nivel?")
        anx_avg = sum(s["anxiety"]["score"] for s in snaps)/len(snaps) if snaps else 0
        results.append({
            "level": level, "sudsBefore": before,
            "sudsAfter": None if after == "STOP" else after,
            "anxAvgSensor": anx_avg,
        })
        if after == "STOP":
            stopped_at_level = level
            break

    return {
        "phobia": phobia_key, "results": results,
        "stoppedAtLevel": stopped_at_level,
        "completedAllLevels": stopped_at_level is None,
    }