"""
tests_cognitive.py — Pruebas cognitivas para NeuroSpace.
Incluye prueba de atención por colores.
"""

import pygame
import random
import time

from hud import TEXT, TEXT_DIM, CYAN


COLOR_OPTIONS = {
    "ROJO": (220, 50, 50),
    "AZUL": (50, 130, 240),
    "VERDE": (50, 200, 100),
    "AMARILLO": (240, 210, 50),
}


def draw_color_button(screen, rect, label, color, font, mouse_pos):
    """
    Dibuja un botón de color para la prueba cognitiva.
    """

    hovered = rect.collidepoint(mouse_pos)

    if hovered:
        border_color = (255, 255, 255)
        border_width = 4
    else:
        border_color = CYAN
        border_width = 2

    pygame.draw.rect(screen, color, rect, border_radius=18)
    pygame.draw.rect(screen, border_color, rect, border_width, border_radius=18)

    txt = font.render(label, True, (255, 255, 255))
    txt_rect = txt.get_rect(center=rect.center)
    screen.blit(txt, txt_rect)


def show_message(engine, title, message, seconds=1.2):
    """
    Muestra un mensaje temporal en pantalla.
    """

    start = time.time()

    while time.time() - start < seconds:
        engine.screen.fill((5, 10, 18))

        title_surf = engine.font_big.render(title, True, CYAN)
        title_rect = title_surf.get_rect(center=(engine.width // 2, 190))
        engine.screen.blit(title_surf, title_rect)

        msg_surf = engine.font_medium.render(message, True, TEXT)
        msg_rect = msg_surf.get_rect(center=(engine.width // 2, 290))
        engine.screen.blit(msg_surf, msg_rect)

        pygame.display.flip()
        engine.clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit


def run_color_attention_test(engine, rounds=8):
    """
    Prueba cognitiva de atención por colores.
    """

    if hasattr(engine, "voice") and engine.voice:
        engine.voice.say(
            "Iniciando prueba cognitiva de atención. "
            "Selecciona el color que se indique en pantalla."
        )

    show_message(
        engine,
        "PRUEBA DE ATENCIÓN",
        "Selecciona el color indicado en la pantalla.",
        2,
    )

    button_w = 260
    button_h = 110
    gap_x = 80
    gap_y = 55

    start_x = engine.width // 2 - button_w - gap_x // 2
    start_y = 330

    buttons = {
        "ROJO": pygame.Rect(start_x, start_y, button_w, button_h),
        "AZUL": pygame.Rect(start_x + button_w + gap_x, start_y, button_w, button_h),
        "VERDE": pygame.Rect(start_x, start_y + button_h + gap_y, button_w, button_h),
        "AMARILLO": pygame.Rect(
            start_x + button_w + gap_x,
            start_y + button_h + gap_y,
            button_w,
            button_h,
        ),
    }

    correct = 0
    errors = 0
    reaction_times = []

    color_names = list(COLOR_OPTIONS.keys())

    for round_index in range(rounds):
        target = random.choice(color_names)
        selected = None


        round_start = time.time()

        while selected is None:
            engine.screen.fill((5, 10, 18))

            mouse_pos = pygame.mouse.get_pos()

            title = engine.font_big.render("ATENCIÓN COGNITIVA", True, CYAN)
            title_rect = title.get_rect(center=(engine.width // 2, 70))
            engine.screen.blit(title, title_rect)

            progress_text = f"Ronda {round_index + 1} de {rounds}"
            progress = engine.font_small.render(progress_text, True, TEXT_DIM)
            progress_rect = progress.get_rect(center=(engine.width // 2, 125))
            engine.screen.blit(progress, progress_rect)

            instruction = engine.font_big.render(
                f"Selecciona: {target}",
                True,
                TEXT,
            )
            instruction_rect = instruction.get_rect(center=(engine.width // 2, 210))
            engine.screen.blit(instruction, instruction_rect)

            for name, rect in buttons.items():
                draw_color_button(
                    engine.screen,
                    rect,
                    name,
                    COLOR_OPTIONS[name],
                    engine.font_medium,
                    mouse_pos,
                )

            pygame.display.flip()
            engine.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for name, rect in buttons.items():
                        if rect.collidepoint(event.pos):
                            selected = name
                            break

        reaction_time = round(time.time() - round_start, 2)
        reaction_times.append(reaction_time)

        if selected == target:
            correct += 1

           # if hasattr(engine, "voice") and engine.voice:
          #      engine.voice.say(
          #          "Correcto.",
             #       urgent=True,
            #    )

            show_message(
                engine,
                "CORRECTO",
                f"Tiempo: {reaction_time} segundos",
                0.7,
            )

        else:
            errors += 1

          #  if hasattr(engine, "voice") and engine.voice:
           #     engine.voice.say(
           #         "Incorrecto.",
          #          urgent=True,
           #     )

            show_message(
                engine,
                "INCORRECTO",
                f"Era {target}. Seleccionaste {selected}.",
                0.9,
            )

    total = rounds
    accuracy = round((correct / total) * 100, 1)

    if reaction_times:
        avg_reaction_time = round(sum(reaction_times) / len(reaction_times), 2)
    else:
        avg_reaction_time = 0

    if accuracy >= 85 and avg_reaction_time <= 2.0:
        level = "Atención estable"
    elif accuracy >= 65:
        level = "Atención moderada"
    else:
        level = "Atención baja"

    results = {
        "test": "Atención por colores",
        "total": total,
        "correct": correct,
        "errors": errors,
        "accuracy": accuracy,
        "avg_reaction_time": avg_reaction_time,
        "level": level,
    }

   #  if hasattr(engine, "voice") and engine.voice:
   #      engine.voice.say(
   #          f"Prueba de atención finalizada. "
   #          f"Aciertos: {correct} de {total}. "
   #          f"Resultado: {level}."
   #      )

    show_cognitive_results(engine, results)

    return results


def show_cognitive_results(engine, results):
    """
    Pantalla final de resultados cognitivos.
    """

    continue_button = pygame.Rect(
        engine.width // 2 - 170,
        engine.height - 130,
        340,
        65,
    )

    while True:
        engine.screen.fill((5, 10, 18))

        mouse_pos = pygame.mouse.get_pos()

        title = engine.font_big.render("RESULTADO COGNITIVO", True, CYAN)
        title_rect = title.get_rect(center=(engine.width // 2, 80))
        engine.screen.blit(title, title_rect)

        box = pygame.Rect(
            engine.width // 2 - 430,
            160,
            860,
            330,
        )

        pygame.draw.rect(engine.screen, (8, 18, 32), box, border_radius=20)
        pygame.draw.rect(engine.screen, CYAN, box, 2, border_radius=20)

        lines = [
            f"Prueba: {results['test']}",
            f"Total de rondas: {results['total']}",
            f"Aciertos: {results['correct']}",
            f"Errores: {results['errors']}",
            f"Precisión: {results['accuracy']}%",
            f"Tiempo promedio de reacción: {results['avg_reaction_time']} segundos",
            f"Resultado: {results['level']}",
        ]

        y = box.y + 40

        for line in lines:
            text = engine.font_medium.render(line, True, TEXT)
            text_rect = text.get_rect(center=(engine.width // 2, y))
            engine.screen.blit(text, text_rect)
            y += 40

        hovered = continue_button.collidepoint(mouse_pos)

        if hovered:
            fill = (0, 80, 110)
        else:
            fill = (8, 25, 40)

        pygame.draw.rect(engine.screen, fill, continue_button, border_radius=14)
        pygame.draw.rect(engine.screen, CYAN, continue_button, 2, border_radius=14)

        btn_text = engine.font_medium.render("CONTINUAR", True, TEXT)
        btn_rect = btn_text.get_rect(center=continue_button.center)
        engine.screen.blit(btn_text, btn_rect)

        pygame.display.flip()
        engine.clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if continue_button.collidepoint(event.pos):
                    return