"""
patient.py — Pantalla y flujo principal del modo paciente.

Flujo:
1. Intake inicial.
2. GAD-7.
3. Prueba cognitiva de atención por colores.
4. Guardado automático del expediente.
5. Resultado final.
"""

from datetime import datetime

import pygame

from hud import TEXT, TEXT_DIM, CYAN
from intake import run_intake
from questionnaires import run_gad7
from tests_cognitive import run_color_attention_test
from history import get_next_patient_number, save_patient_record
from evaluation_bridge import finish_patient_evaluation


def _voice_stop(engine):
    """
    Limpia solo la cola de voz pendiente.
    No detiene el motor de voz.
    """

    if hasattr(engine, "voice") and engine.voice:
        if hasattr(engine.voice, "_clear_queue"):
            engine.voice._clear_queue()


def _voice_say(engine, text, interrupt=False):
    """
    Habla de forma segura.
    """

    if hasattr(engine, "voice") and engine.voice:
        try:
            engine.voice.say(text, interrupt=interrupt)
        except TypeError:
            engine.voice.say(text)


def _make_patient_voice_interruptible(engine):
    """
    Durante las preguntas, hace que la voz sea urgente.
    """

    if not hasattr(engine, "voice") or not engine.voice:
        return None

    original_say = engine.voice.say
    original_say_async = getattr(engine.voice, "say_async", None)

    def say_interruptible(text, *args, **kwargs):
        kwargs.setdefault("urgent", True)
        kwargs.pop("interrupt", None)
        return original_say(text, *args, **kwargs)

    def say_async_interruptible(text, *args, **kwargs):
        kwargs.setdefault("urgent", True)
        kwargs.pop("interrupt", None)

        if original_say_async:
            return original_say_async(text, *args, **kwargs)

        return original_say(text, *args, **kwargs)

    engine.voice.say = say_interruptible
    engine.voice.say_async = say_async_interruptible

    return original_say, original_say_async


def _restore_patient_voice(engine, originals):
    """
    Restaura la voz normal después de las preguntas.
    """

    if originals is None:
        return

    if not hasattr(engine, "voice") or not engine.voice:
        return

    original_say, original_say_async = originals

    engine.voice.say = original_say

    if original_say_async:
        engine.voice.say_async = original_say_async


def draw_patient_button(screen, rect, text, font, mouse_pos):
    """
    Botón simple para pantallas del modo paciente.
    """

    hovered = rect.collidepoint(mouse_pos)

    if hovered:
        fill = (0, 80, 110)
    else:
        fill = (8, 25, 40)

    pygame.draw.rect(screen, fill, rect, border_radius=14)
    pygame.draw.rect(screen, CYAN, rect, 2, border_radius=14)

    txt = font.render(text, True, TEXT)
    txt_rect = txt.get_rect(center=rect.center)
    screen.blit(txt, txt_rect)
def wrap_text(text, font, max_width):
    """
    Divide un texto largo en varias líneas para que no se salga del panel.
    """

    words = str(text).split(" ")
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + word + " "

        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line.strip())
            current_line = word + " "

    if current_line:
        lines.append(current_line.strip())

    return lines

def show_patient_message(engine, title, lines, button_text="CONTINUAR"):
    """
    Muestra una pantalla de mensaje con botón continuar.
    """

    button = pygame.Rect(
        engine.width // 2 - 170,
        engine.height - 130,
        340,
        65,
    )

    while True:
        engine.screen.fill((5, 10, 18))

        mouse_pos = pygame.mouse.get_pos()

        title_surf = engine.font_big.render(title, True, CYAN)
        title_rect = title_surf.get_rect(center=(engine.width // 2, 80))
        engine.screen.blit(title_surf, title_rect)

        box = pygame.Rect(
            engine.width // 2 - 470,
            160,
            940,
            330,
        )

        pygame.draw.rect(engine.screen, (8, 18, 32), box, border_radius=20)
        pygame.draw.rect(engine.screen, CYAN, box, 2, border_radius=20)

        y = box.y + 55

        for line in lines:
            text = engine.font_medium.render(line, True, TEXT)
            text_rect = text.get_rect(center=(engine.width // 2, y))
            engine.screen.blit(text, text_rect)
            y += 45

        draw_patient_button(
            engine.screen,
            button,
            button_text,
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
                if button.collidepoint(event.pos):
                    return

def show_generated_access_record(engine, patient_access_record):
    """
    Pantalla intermedia que muestra el expediente y código de acceso generado.
    """

    button = pygame.Rect(
        engine.width // 2 - 180,
        engine.height - 115,
        360,
        65,
    )

    patient_label = patient_access_record.get("patient_label", "Paciente")
    expediente_code = patient_access_record.get("expediente_code", "N/A")
    verification_code = patient_access_record.get("verification_code", "N/A")
    general_state = patient_access_record.get("general_state", "Sin estado")

    results = patient_access_record.get("results", {})
    gad7_score = results.get("gad7_score", "N/A")
    cognitive_score = results.get("cognitive_score", "N/A")

    _voice_say(
        engine,
        f"Expediente generado. {patient_label}. Código de expediente {expediente_code}. "
        f"Código de verificación {verification_code}.",
        interrupt=True,
    )

    while True:
        engine.screen.fill((5, 10, 18))

        mouse_pos = pygame.mouse.get_pos()

        title = engine.font_big.render("EXPEDIENTE GENERADO", True, CYAN)
        title_rect = title.get_rect(center=(engine.width // 2, 75))
        engine.screen.blit(title, title_rect)

        subtitle = engine.font_medium.render(
            "Guarda estos datos para consultar el expediente después",
            True,
            TEXT_DIM,
        )
        subtitle_rect = subtitle.get_rect(center=(engine.width // 2, 125))
        engine.screen.blit(subtitle, subtitle_rect)

        box = pygame.Rect(
            engine.width // 2 - 470,
            175,
            940,
            360,
        )

        pygame.draw.rect(engine.screen, (8, 18, 32), box, border_radius=22)
        pygame.draw.rect(engine.screen, CYAN, box, 2, border_radius=22)

        info_lines = [
            ("Paciente", patient_label),
            ("Expediente", expediente_code),
            ("Código de verificación", verification_code),
            ("Estado general", general_state),
            ("GAD-7", gad7_score),
            ("Cognitivo", f"{cognitive_score}%"),
        ]

        y = box.y + 45

        for label, value in info_lines:
            label_surf = engine.font_medium.render(f"{label}:", True, TEXT_DIM)
            value_surf = engine.font_medium.render(str(value), True, TEXT)

            engine.screen.blit(label_surf, (box.x + 70, y))
            engine.screen.blit(value_surf, (box.x + 390, y))

            y += 48

        warning = engine.font_small.render(
            "El expediente y el código serán necesarios para acceder al registro del paciente.",
            True,
            TEXT_DIM,
        )

        engine.screen.blit(
            warning,
            (
                engine.width // 2 - warning.get_width() // 2,
                box.y + box.height - 45,
            ),
        )

        draw_patient_button(
            engine.screen,
            button,
            "VER RESULTADO FINAL",
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
                if button.collidepoint(event.pos):
                    return
def show_final_patient_result(engine, record):
    """
    Pantalla final del modo paciente con análisis, recomendaciones y scroll.
    Recibe el expediente ya guardado desde history.py.
    """

    scores = record.get("scores", {})

    cognitive = scores.get("cognitive")
    sleep = scores.get("sleep")

    cognitive_text = "Sin datos" if cognitive is None else f"{cognitive}%"
    sleep_text = "Sin datos" if sleep is None else str(sleep)

    lines = [
        ("Paciente", f"Número {record.get('patient_number', 'N/A')}"),
        ("Expediente", record.get("case_code", "N/A")),
        ("Fecha", record.get("date", "N/A")),
        ("Estado general", record.get("general_state", "N/A")),
        ("", ""),
        ("PUNTAJES", ""),
        ("Intake inicial", f"{scores.get('intake', 0)} puntos"),
        ("GAD-7", f"{scores.get('gad7', 0)} puntos"),
        ("Cognitivo", cognitive_text),
        ("Sueño", sleep_text),
        ("", ""),
        ("ALERTAS", ""),
    ]

    for item in record.get("alerts", []):
        lines.append(("", f"• {item}"))

    lines.append(("", ""))
    lines.append(("ANÁLISIS", ""))

    for item in record.get("analysis", []):
        lines.append(("", f"• {item}"))

    lines.append(("", ""))
    lines.append(("RECOMENDACIONES", ""))

    for item in record.get("recommendations", []):
        lines.append(("", f"• {item}"))

    lines.append(("", ""))
    lines.append(("CONCLUSIÓN", ""))
    lines.append(("", record.get("conclusion", "")))

    _voice_say(
        engine,
        f"Evaluación finalizada. Estado general: {record.get('general_state', 'sin datos')}. "
        f"{record.get('conclusion', '')}"
    )

    button = pygame.Rect(
        engine.width // 2 - 180,
        engine.height - 90,
        360,
        60,
    )

    box = pygame.Rect(
        engine.width // 2 - 520,
        145,
        1040,
        engine.height - 270,
    )

    scroll = 0

    while True:
        engine.screen.fill((5, 10, 18))

        mouse_pos = pygame.mouse.get_pos()

        title_surf = engine.font_big.render("RESULTADO FINAL", True, CYAN)
        title_rect = title_surf.get_rect(center=(engine.width // 2, 70))
        engine.screen.blit(title_surf, title_rect)

        pygame.draw.rect(engine.screen, (8, 18, 32), box, border_radius=20)
        pygame.draw.rect(engine.screen, CYAN, box, 2, border_radius=20)

        content_surface = engine.screen.subsurface(box)
        content_surface.fill((8, 18, 32))

        y = 30 - scroll

        for label, value in lines:
            if label == "" and value == "":
                y += 24
                continue

            if label in [
                "PUNTAJES",
                "ALERTAS",
                "ANÁLISIS",
                "RECOMENDACIONES",
                "CONCLUSIÓN",
            ]:
                text_surf = engine.font_medium.render(label, True, CYAN)

                if -40 < y < box.height:
                    content_surface.blit(text_surf, (40, y))

                y += 42
                continue
            
            if label:
                text = f"{label}: {value}"
            else:
                text = value

            color = TEXT if label else TEXT_DIM

            wrapped_lines = wrap_text(
                text,
                engine.font_small,
                box.width - 90,
            )

            for wrapped_line in wrapped_lines:
                text_surf = engine.font_small.render(wrapped_line, True, color)

                if -40 < y < box.height:
                    content_surface.blit(text_surf, (45, y))

                y += 32
        hint = engine.font_small.render("Usa la rueda del mouse para ver más", True, TEXT_DIM)
        engine.screen.blit(
            hint,
            (
                engine.width // 2 - hint.get_width() // 2,
                engine.height - 130,
            ),
        )

        draw_patient_button(
            engine.screen,
            button,
            "VOLVER AL MENÚ",
            engine.font_medium,
            mouse_pos,
        )

        pygame.display.flip()
        engine.clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.MOUSEWHEEL:
                scroll -= event.y * 35

                if scroll < 0:
                    scroll = 0

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if button.collidepoint(event.pos):
                    return


def show_patient_screen(engine):
    """
    Ejecuta la evaluación completa del paciente.
    """

    _voice_stop(engine)

    patient_number = get_next_patient_number()

    print(f"✅ Evaluación del Paciente {patient_number} iniciada.")

    _voice_say(
        engine,
        f"Modo paciente seleccionado. Iniciando evaluación del paciente número {patient_number}.",
        interrupt=True,
    )

    show_patient_message(
        engine,
        f"EVALUACIÓN DEL PACIENTE {patient_number}",
        [
            f"Paciente número {patient_number}.",
            "La evaluación comenzará ahora.",
            "Responde cada pregunta con calma.",
        "JARVIS hablará solo en botones, accesos y resultado final.",        ],
        "COMENZAR",
    )

    session_result = {
        "patient_number": patient_number,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "intake": None,
        "gad7": None,
        "cognitive": None,
    }

    # Durante preguntas NO se usa voz.
    # Las preguntas solo se muestran en pantalla.

    session_result["intake"] = run_intake(engine)

    _voice_stop(engine)

    session_result["gad7"] = run_gad7(engine)

    _voice_stop(engine) 

    session_result["cognitive"] = run_color_attention_test(engine, rounds=8)

    _voice_stop(engine)

    record = save_patient_record(session_result)

    scores = record.get("scores", {})

    gad7_score = scores.get("gad7", 0)
    cognitive_score = scores.get("cognitive", 100)

    analysis_list = record.get("analysis", [])

    if isinstance(analysis_list, list):
        analysis_text = " ".join(analysis_list)
    else:
        analysis_text = str(analysis_list)

    patient_access_record = finish_patient_evaluation(
    patient_number=record.get("patient_number"),
    case_code=record.get("case_code"),
    gad7_score=gad7_score,
    cognitive_score=cognitive_score,
    analysis=analysis_text,
    sensor_data={
        "bpm": None,
        "spo2": None
    },
    extra_data={
        "source": "screens/patient.py",
        "history_record": record
    }
)

    print("Resultado completo de sesión:")
    print(record)

    print()
    print("Paciente guardado automáticamente en sistema de acceso:")
    print("Paciente:", patient_access_record["patient_label"])
    print("Expediente:", patient_access_record["expediente_code"])
    print("Código:", patient_access_record["verification_code"])

    show_generated_access_record(engine, patient_access_record)

    show_final_patient_result(engine, record)
    