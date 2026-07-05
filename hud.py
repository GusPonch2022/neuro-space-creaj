"""
hud.py — Elementos visuales reutilizables del HUD de Jarvis (pygame).
"""

import math
import random
import pygame

CYAN = (76, 242, 255)
CYAN_DIM = (28, 94, 107)
AMBER = (255, 180, 84)
RED = (255, 84, 112)
GREEN = (89, 255, 176)
BG = (4, 7, 10)
TEXT = (207, 233, 238)
TEXT_DIM = (111, 147, 160)


class Particles:
    def __init__(self, width, height, count=80):
        self.w, self.h = width, height
        self.points = [
            {"x": random.uniform(0, width), "y": random.uniform(0, height),
             "vx": random.uniform(-0.4, 0.4), "vy": random.uniform(-0.4, 0.4),
             "r": random.uniform(1, 2.4)}
            for _ in range(count)
        ]

    def update_and_draw(self, surface):
        for p in self.points:
            p["x"] += p["vx"]; p["y"] += p["vy"]
            if p["x"] < 0: p["x"] = self.w
            if p["x"] > self.w: p["x"] = 0
            if p["y"] < 0: p["y"] = self.h
            if p["y"] > self.h: p["y"] = 0
        for i, a in enumerate(self.points):
            for b in self.points[i+1:]:
                d = math.hypot(a["x"]-b["x"], a["y"]-b["y"])
                if d < 110:
                    pygame.draw.line(surface, (20, 50, 60), (a["x"], a["y"]), (b["x"], b["y"]), 1)
        for p in self.points:
            pygame.draw.circle(surface, CYAN, (int(p["x"]), int(p["y"])), int(p["r"]))


class Core:
    def __init__(self, center, base_radius=80):
        self.center = center
        self.base_radius = base_radius
        self.t = 0.0

    def update_and_draw(self, surface, speaking, dt):
        self.t += dt
        pulse = 1.0 + (0.12 * math.sin(self.t * 10) if speaking else 0.0)
        radius = int(self.base_radius * pulse)

        glow = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        for i in range(6, 0, -1):
            alpha = 14 if speaking else 7
            pygame.draw.circle(glow, (*CYAN, alpha), self.center, radius + i * 10)
        surface.blit(glow, (0, 0))

        pygame.draw.circle(surface, (10, 30, 38), self.center, radius)
        pygame.draw.circle(surface, CYAN, self.center, radius, width=2)
        for ring_r, speed, dashed in ((radius+35, 0.6, True), (radius+60, -0.4, False)):
            self._draw_ring(surface, ring_r, self.t*speed, dashed)

        amp = 14 if speaking else 3
        points = []
        for x in range(-radius+10, radius-10, 4):
            y = int(math.sin(x/8 + self.t*6) * amp * (1 if speaking else 0.4))
            points.append((self.center[0]+x, self.center[1]+y))
        if len(points) > 1:
            pygame.draw.lines(surface, CYAN, False, points, 2)

    def _draw_ring(self, surface, radius, angle_offset, dashed):
        segments = 40
        for i in range(segments):
            if dashed and i % 2 == 0:
                continue
            a0 = (i/segments)*2*math.pi + angle_offset
            a1 = ((i+0.7)/segments)*2*math.pi + angle_offset
            p0 = (self.center[0]+radius*math.cos(a0), self.center[1]+radius*math.sin(a0))
            p1 = (self.center[0]+radius*math.cos(a1), self.center[1]+radius*math.sin(a1))
            pygame.draw.line(surface, CYAN_DIM, p0, p1, 2)


class Gauge:
    def __init__(self, pos, radius, color, title, suffix=""):
        self.pos = pos; self.radius = radius; self.color = color
        self.title = title; self.suffix = suffix
        self.percent = 0.0; self.target_percent = 0.0
        self.value_text = "--"; self.sub_text = "esperando lectura"

    def set_value(self, percent, value_text, sub_text):
        self.target_percent = max(0, min(100, percent))
        self.value_text = value_text; self.sub_text = sub_text

    def update(self, dt):
        self.percent += (self.target_percent - self.percent) * min(1.0, dt*4)

    def draw(self, surface, font_title, font_value, font_sub):
        cx, cy = self.pos
        pygame.draw.circle(surface, (40, 50, 55), (cx, cy), self.radius, width=6)
        start_angle = -math.pi/2
        end_angle = start_angle + (self.percent/100)*2*math.pi
        rect = pygame.Rect(cx-self.radius, cy-self.radius, self.radius*2, self.radius*2)
        if self.percent > 1:
            pygame.draw.arc(surface, self.color, rect, -end_angle, -start_angle, 6)
        surface.blit(font_title.render(self.title, True, TEXT_DIM), (cx+self.radius+18, cy-26))
        surface.blit(font_value.render(self.value_text+" "+self.suffix, True, self.color), (cx+self.radius+18, cy-6))
        surface.blit(font_sub.render(self.sub_text, True, TEXT_DIM), (cx+self.radius+18, cy+18))


class Console:
    def __init__(self, rect, font, font_small):
        self.rect = rect; self.font = font; self.font_small = font_small
        self.lines = []
        self.input_text = ""; self.input_active = False

    def add_line(self, who, text, color=TEXT):
        self.lines.append((who, text, color))
        if len(self.lines) > 9:
            self.lines = self.lines[-9:]

    def draw(self, surface):
        pygame.draw.rect(surface, (10, 18, 22), self.rect, border_radius=10)
        pygame.draw.rect(surface, CYAN_DIM, self.rect, width=1, border_radius=10)
        y = self.rect.top + 14
        for who, text, color in self.lines:
            wrapped = wrap_text(text, self.font_small, self.rect.width-30)
            x_offset = 0
            if who:
                who_surf = self.font_small.render(f"{who}:", True, color)
                surface.blit(who_surf, (self.rect.left+16, y))
                x_offset = who_surf.get_width()+6
            for j, wline in enumerate(wrapped):
                txt_surf = self.font_small.render(wline, True, TEXT if who else TEXT_DIM)
                x = self.rect.left+16+(x_offset if j == 0 else 0)
                surface.blit(txt_surf, (x, y)); y += 20

        box_rect = pygame.Rect(self.rect.left+14, self.rect.bottom-46, self.rect.width-28, 34)
        border_color = CYAN if self.input_active else CYAN_DIM
        pygame.draw.rect(surface, border_color, box_rect, width=1, border_radius=6)
        display_text = self.input_text if self.input_text else ("Escribe tu respuesta y presiona Enter..." if self.input_active else "")
        color = TEXT if self.input_text else TEXT_DIM
        surface.blit(self.font_small.render(display_text, True, color), (box_rect.left+10, box_rect.top+8))


def wrap_text(text, font, max_width):
    words = text.split(" ")
    lines = []; current = ""
    for w in words:
        test = (current+" "+w).strip()
        if font.size(test)[0] <= max_width:
            current = test
        else:
            if current: lines.append(current)
            current = w
    if current: lines.append(current)
    return lines or [""]


def draw_button(surface, rect, text, font, active=False, color=CYAN, bg_hover=False):
    border_color = color if (active or bg_hover) else CYAN_DIM
    bg_color = (20, 40, 46) if bg_hover else (12, 24, 28)
    pygame.draw.rect(surface, bg_color, rect, border_radius=8)
    pygame.draw.rect(surface, border_color, rect, width=1, border_radius=8)
    txt_surf = font.render(text, True, TEXT)
    surface.blit(txt_surf, (rect.centerx - txt_surf.get_width()//2, rect.centery - txt_surf.get_height()//2))
