"""
Pantalla de Inicio de CREA-J
"""

import pygame

from hud import TEXT, TEXT_DIM, CYAN


def draw(engine, surface):
    """
    Dibuja la pantalla Home sobre el HUD.
    """

    # Panel principal
    panel = pygame.Rect(320, 120, 520, 520)

    pygame.draw.rect(surface, (10, 18, 24), panel, border_radius=12)
    pygame.draw.rect(surface, CYAN, panel, 2, border_radius=12)

    # Título
    titulo = engine.font_big.render("INICIO", True, TEXT)
    surface.blit(titulo, (350, 145))

    # Información
    lineas = [
        "Bienvenido a CREA-J",
        "",
        "Estado del sistema:",
        "",
        "✓ Motor gráfico",
        "✓ HUD",
        "✓ Menú",
        "",
        "Sensores: Esperando conexión",
        "IA: Inactiva",
        "Paciente: Ninguno"
    ]

    y = 220

    for linea in lineas:
        txt = engine.font_med.render(linea, True, TEXT_DIM)
        surface.blit(txt, (350, y))
        y += 34