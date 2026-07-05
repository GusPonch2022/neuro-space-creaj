import pygame

from hud import CYAN, RED, TEXT, TEXT_DIM, draw_button
from history import load_history
from patient_records import get_all_patients


def get_med_font(engine):
    return getattr(engine, "font_med", getattr(engine, "font_medium", engine.font_small))


def draw_panel(surface, rect, border_color=CYAN):
    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    panel.fill((5, 18, 24, 210))
    surface.blit(panel, rect.topleft)

    pygame.draw.rect(
        surface,
        border_color,
        rect,
        width=2,
        border_radius=12,
    )


def wrap_text(text, font, max_width):
    words = str(text).split(" ")
    lines = []
    current = ""

    for word in words:
        test = current + word + " "

        if font.size(test)[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current.strip())
            current = word + " "

    if current:
        lines.append(current.strip())

    return lines


def draw_analysis_card(surface, rect, title, subtitle, font_title, font_sub, mouse_pos):
    hovered = rect.collidepoint(mouse_pos)

    if hovered:
        fill = (0, 75, 95)
    else:
        fill = (7, 24, 35)

    pygame.draw.rect(surface, fill, rect, border_radius=14)
    pygame.draw.rect(surface, CYAN, rect, 2, border_radius=14)

    title_surf = font_title.render(title, True, TEXT)
    sub_surf = font_sub.render(subtitle, True, TEXT_DIM)

    surface.blit(title_surf, (rect.x + 25, rect.y + 12))
    surface.blit(sub_surf, (rect.x + 25, rect.y + 45))


def clean_history_records(history):
    records = []

    for record in history:
        if not isinstance(record, dict):
            continue

        patient_number = record.get("patient_number")
        case_code = record.get("case_code")

        if patient_number is None or case_code is None:
            continue

        records.append(record)

    return records


def _to_list(value):
    """
    Convierte texto/listas en lista para que las pantallas puedan dibujar viñetas.
    """

    if value is None:
        return []

    if isinstance(value, list):
        return value

    return [str(value)]


def _build_alerts_from_patient(patient):
    """
    Crea alertas simples cuando el expediente viene desde patients.json.
    """

    alerts = []
    state = str(patient.get("general_state", "")).lower()

    results = patient.get("results", {})
    if not isinstance(results, dict):
        results = {}

    gad7 = results.get("gad7_score", 0)
    cognitive = results.get("cognitive_score", 100)

    try:
        gad7 = int(gad7)
    except Exception:
        gad7 = 0

    try:
        cognitive = int(cognitive)
    except Exception:
        cognitive = 100

    if "alto" in state:
        alerts.append("Estado general marcado como riesgo alto.")

    if gad7 >= 10:
        alerts.append("Puntaje GAD-7 con señales de ansiedad que requieren seguimiento.")

    if cognitive < 70:
        alerts.append("Resultado cognitivo por debajo del nivel esperado.")

    if not alerts:
        alerts.append("Sin alertas críticas registradas.")

    return alerts


def _build_conclusion_from_patient(patient):
    state = patient.get("general_state", "Sin estado")
    code = patient.get("expediente_code", "Sin expediente")

    return f"Expediente {code} registrado en sistema de acceso. Estado general: {state}."


def normalize_patient_record(patient):
    """
    Convierte un registro de data/patients.json al formato que usan
    las pantallas de Historial y Análisis.
    """

    if not isinstance(patient, dict):
        return None

    raw_session = patient.get("raw_session", {})
    history_record = None

    if isinstance(raw_session, dict):
        extra_data = raw_session.get("extra_data", {})

        if isinstance(extra_data, dict):
            possible_history = extra_data.get("history_record")

            if isinstance(possible_history, dict):
                history_record = possible_history

    if history_record:
        record = dict(history_record)

        scores = record.get("scores", {})
        if not isinstance(scores, dict):
            scores = {}

        results = patient.get("results", {})
        if not isinstance(results, dict):
            results = {}

        scores.setdefault("gad7", results.get("gad7_score", 0))
        scores.setdefault("cognitive", results.get("cognitive_score", 100))

        record["scores"] = scores
        record["patient_number"] = patient.get("patient_number", record.get("patient_number", "N/A"))
        record["case_code"] = patient.get("expediente_code", record.get("case_code", "N/A"))
        record["date"] = patient.get("created_at", record.get("date", "Sin fecha"))
        record["general_state"] = patient.get("general_state", record.get("general_state", "Sin estado"))
        record["verification_code"] = patient.get("verification_code", "N/A")
        record["raw_session"] = raw_session

        if not record.get("analysis"):
            record["analysis"] = _to_list(patient.get("analysis"))

        if not record.get("recommendations"):
            record["recommendations"] = _to_list(patient.get("recommendations"))

        if not record.get("alerts"):
            record["alerts"] = _build_alerts_from_patient(patient)

        if not record.get("conclusion"):
            record["conclusion"] = _build_conclusion_from_patient(patient)

        return record

    results = patient.get("results", {})
    if not isinstance(results, dict):
        results = {}

    record = {
        "patient_number": patient.get("patient_number", "N/A"),
        "case_code": patient.get("expediente_code", "N/A"),
        "verification_code": patient.get("verification_code", "N/A"),
        "date": patient.get("created_at", "Sin fecha"),
        "general_state": patient.get("general_state", "Sin estado"),
        "scores": {
            "intake": 0,
            "gad7": results.get("gad7_score", 0),
            "cognitive": results.get("cognitive_score", 100),
            "sleep": None,
        },
        "alerts": _build_alerts_from_patient(patient),
        "analysis": _to_list(patient.get("analysis")),
        "recommendations": _to_list(patient.get("recommendations")),
        "conclusion": _build_conclusion_from_patient(patient),
        "raw_session": raw_session,
    }

    return record


def load_patient_records_for_screen():
    """
    Fuente principal: data/patients.json.
    Si todavía no existe, usa data/history.json como respaldo.
    """

    records = []

    try:
        patients = get_all_patients()
    except Exception as error:
        print("⚠️ No se pudo cargar patients.json:", error)
        patients = []

    for patient in patients:
        record = normalize_patient_record(patient)

        if record:
            records.append(record)

    if records:
        return records

    return clean_history_records(load_history())


def get_scores(record):
    scores = record.get("scores", {})

    if not isinstance(scores, dict):
        scores = {}

    return scores


def get_cognitive_text(record):
    scores = get_scores(record)
    cognitive = scores.get("cognitive")

    if cognitive is None:
        return "Sin cognitivo"

    return f"Cognitivo: {cognitive}%"


def get_gad7_text(record):
    scores = get_scores(record)
    gad7 = scores.get("gad7")

    if gad7 is None:
        return "GAD-7: Sin datos"

    return f"GAD-7: {gad7}"


def build_analysis_lines(record):
    scores = get_scores(record)

    cognitive = scores.get("cognitive")
    sleep = scores.get("sleep")

    cognitive_text = "Sin datos" if cognitive is None else f"{cognitive}%"
    sleep_text = "Sin datos" if sleep is None else str(sleep)

    lines = [
        ("Paciente", f"Número {record.get('patient_number', 'N/A')}"),
        ("Expediente", record.get("case_code", "N/A")),
        ("Código verificación", record.get("verification_code", "N/A")),
        ("Fecha", record.get("date", "Sin fecha")),
        ("Estado general", record.get("general_state", "Sin estado")),
        ("", ""),

        ("INDICADORES PRINCIPALES", ""),
        ("Intake inicial", f"{scores.get('intake', 0)} puntos"),
        ("GAD-7", f"{scores.get('gad7', 0)} puntos"),
        ("Cognitivo", cognitive_text),
        ("Sueño", sleep_text),
        ("", ""),

        ("LECTURA IA", ""),
    ]

    for item in record.get("analysis", []):
        lines.append(("", f"• {item}"))

    lines.append(("", ""))
    lines.append(("ALERTAS", ""))

    for item in record.get("alerts", []):
        lines.append(("", f"• {item}"))

    lines.append(("", ""))
    lines.append(("RECOMENDACIONES", ""))

    for item in record.get("recommendations", []):
        lines.append(("", f"• {item}"))

    lines.append(("", ""))
    lines.append(("CONCLUSIÓN", ""))
    lines.append(("", record.get("conclusion", "Sin conclusión disponible.")))

    return lines


def draw_text_lines(content_surface, engine, lines, scroll):
    y = 30 - scroll
    font_med = get_med_font(engine)

    section_titles = [
        "INDICADORES PRINCIPALES",
        "LECTURA IA",
        "ALERTAS",
        "RECOMENDACIONES",
        "CONCLUSIÓN",
        "INFORMACIÓN",
    ]

    for label, value in lines:
        if label == "" and value == "":
            y += 24
            continue

        if label in section_titles:
            txt = font_med.render(label, True, CYAN)

            if -40 < y < content_surface.get_height():
                content_surface.blit(txt, (40, y))

            y += 42
            continue

        if label:
            text = f"{label}: {value}"
            color = TEXT
        else:
            text = value
            color = TEXT_DIM

        wrapped = wrap_text(text, engine.font_small, content_surface.get_width() - 90)

        for line in wrapped:
            txt = engine.font_small.render(line, True, color)

            if -40 < y < content_surface.get_height():
                content_surface.blit(txt, (45, y))

            y += 32


def get_priority_action(record):
    state = str(record.get("general_state", "")).lower()
    scores = get_scores(record)

    gad7 = scores.get("gad7", 0)
    cognitive = scores.get("cognitive", 100)
    sleep = scores.get("sleep", 10)

    try:
        gad7 = int(gad7)
    except Exception:
        gad7 = 0

    try:
        cognitive = int(cognitive)
    except Exception:
        cognitive = 100

    try:
        sleep = int(sleep)
    except Exception:
        sleep = 10

    if "alto" in state:
        return "Priorizar seguimiento cercano y recomendar apoyo profesional."

    if gad7 >= 15:
        return "Recomendar apoyo profesional y reducir estímulos de estrés."

    if gad7 >= 10:
        return "Aplicar respiración lenta, observar evolución y repetir evaluación."

    if cognitive < 65:
        return "Repetir prueba cognitiva en un ambiente tranquilo."

    if sleep <= 3:
        return "Priorizar descanso, higiene del sueño y seguimiento posterior."

    return "Mantener seguimiento preventivo y comparar con próximas evaluaciones."


def draw_metric_box(surface, rect, title, value, detail, engine):
    font_med = get_med_font(engine)

    pygame.draw.rect(surface, (7, 24, 35), rect, border_radius=16)
    pygame.draw.rect(surface, CYAN, rect, 2, border_radius=16)

    title_surf = engine.font_small.render(title, True, TEXT_DIM)
    value_surf = font_med.render(str(value), True, TEXT)
    detail_surf = engine.font_small.render(str(detail), True, TEXT_DIM)

    surface.blit(title_surf, (rect.x + 20, rect.y + 16))
    surface.blit(value_surf, (rect.x + 20, rect.y + 48))
    surface.blit(detail_surf, (rect.x + 20, rect.y + 88))


def show_patient_analysis_detail(engine, record):
    salir = {"value": False}
    scroll = {"value": 0}

    font_med = get_med_font(engine)

    patient_number = record.get("patient_number", "N/A")
    case_code = record.get("case_code", "N/A")
    date = record.get("date", "Sin fecha")
    state = record.get("general_state", "Sin estado")
    scores = get_scores(record)

    back_rect = pygame.Rect(
        40,
        engine.height - 80,
        220,
        50,
    )

    main_panel = pygame.Rect(
        engine.width // 2 - 610,
        150,
        1220,
        engine.height - 265,
    )

    def on_event(event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE or event.key == pygame.K_ESCAPE:
                salir["value"] = True

        if event.type == pygame.MOUSEWHEEL:
            scroll["value"] -= event.y * 35

            if scroll["value"] < 0:
                scroll["value"] = 0

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if back_rect.collidepoint(event.pos):
                salir["value"] = True

    def render(surface):
        surface.fill((3, 8, 18))

        title = engine.font_big.render(
            f"ANÁLISIS IA DEL PACIENTE {patient_number}",
            True,
            CYAN,
        )

        subtitle = font_med.render(
            f"{case_code} | Código: {record.get('verification_code', 'N/A')} | {date}",
            True,
            TEXT_DIM,
        )

        surface.blit(
            title,
            (
                engine.width // 2 - title.get_width() // 2,
                42,
            ),
        )

        surface.blit(
            subtitle,
            (
                engine.width // 2 - subtitle.get_width() // 2,
                100,
            ),
        )

        draw_panel(surface, main_panel)

        content = surface.subsurface(main_panel)
        content.fill((5, 18, 24))

        y = 25 - scroll["value"]

        state_rect = pygame.Rect(35, y, main_panel.width - 70, 130)

        if -130 < y < main_panel.height:
            pygame.draw.rect(content, (8, 28, 40), state_rect, border_radius=18)
            pygame.draw.rect(content, CYAN, state_rect, 2, border_radius=18)

            label = engine.font_small.render("ESTADO GENERAL", True, TEXT_DIM)
            value = engine.font_big.render(state, True, CYAN)
            note = engine.font_small.render(
                "Lectura principal generada por Neuro Space",
                True,
                TEXT_DIM,
            )

            content.blit(label, (state_rect.x + 25, state_rect.y + 16))
            content.blit(value, (state_rect.x + 25, state_rect.y + 48))
            content.blit(note, (state_rect.x + 25, state_rect.y + 105))

        y += 160

        section = font_med.render("INDICADORES PRINCIPALES", True, CYAN)

        if -50 < y < main_panel.height:
            content.blit(section, (35, y))

        y += 45

        box_w = (main_panel.width - 100) // 3
        box_h = 125

        metric_y = y

        box1 = pygame.Rect(35, metric_y, box_w, box_h)
        box2 = pygame.Rect(50 + box_w, metric_y, box_w, box_h)
        box3 = pygame.Rect(65 + box_w * 2, metric_y, box_w, box_h)

        if -160 < metric_y < main_panel.height:
            draw_metric_box(
                content,
                box1,
                "INTAKE INICIAL",
                f"{scores.get('intake', 0)} puntos",
                "Carga emocional inicial",
                engine,
            )

            draw_metric_box(
                content,
                box2,
                "GAD-7",
                f"{scores.get('gad7', 0)} puntos",
                "Ansiedad registrada",
                engine,
            )

            cognitive = scores.get("cognitive")
            cognitive_text = "Sin datos" if cognitive is None else f"{cognitive}%"

            draw_metric_box(
                content,
                box3,
                "COGNITIVO",
                cognitive_text,
                "Atención / precisión",
                engine,
            )

        y += 165

        section = font_med.render("ALERTAS DETECTADAS", True, CYAN)

        if -50 < y < main_panel.height:
            content.blit(section, (35, y))

        y += 40

        for alert in record.get("alerts", []):
            for line in wrap_text(f"• {alert}", engine.font_small, main_panel.width - 120):
                txt = engine.font_small.render(line, True, TEXT_DIM)

                if -40 < y < main_panel.height:
                    content.blit(txt, (50, y))

                y += 32

        y += 22

        section = font_med.render("LECTURA IA", True, CYAN)

        if -50 < y < main_panel.height:
            content.blit(section, (35, y))

        y += 40

        for item in record.get("analysis", []):
            for line in wrap_text(f"• {item}", engine.font_small, main_panel.width - 120):
                txt = engine.font_small.render(line, True, TEXT_DIM)

                if -40 < y < main_panel.height:
                    content.blit(txt, (50, y))

                y += 32

        y += 22

        section = font_med.render("ACCIÓN PRIORITARIA", True, CYAN)

        if -50 < y < main_panel.height:
            content.blit(section, (35, y))

        y += 42

        priority_rect = pygame.Rect(35, y, main_panel.width - 70, 105)

        if -140 < y < main_panel.height:
            pygame.draw.rect(content, (7, 24, 35), priority_rect, border_radius=16)
            pygame.draw.rect(content, CYAN, priority_rect, 2, border_radius=16)

            priority_action = get_priority_action(record)

            line_y = priority_rect.y + 25

            for line in wrap_text(f"• {priority_action}", engine.font_small, priority_rect.width - 50):
                txt = engine.font_small.render(line, True, TEXT)
                content.blit(txt, (priority_rect.x + 25, line_y))
                line_y += 30

        y += 135

        section = font_med.render("RECOMENDACIONES", True, CYAN)

        if -50 < y < main_panel.height:
            content.blit(section, (35, y))

        y += 40

        for item in record.get("recommendations", []):
            for line in wrap_text(f"• {item}", engine.font_small, main_panel.width - 120):
                txt = engine.font_small.render(line, True, TEXT_DIM)

                if -40 < y < main_panel.height:
                    content.blit(txt, (50, y))

                y += 32

        y += 22

        section = font_med.render("CONCLUSIÓN", True, CYAN)

        if -50 < y < main_panel.height:
            content.blit(section, (35, y))

        y += 40

        conclusion = record.get("conclusion", "Sin conclusión disponible.")

        for line in wrap_text(f"• {conclusion}", engine.font_small, main_panel.width - 120):
            txt = engine.font_small.render(line, True, TEXT_DIM)

            if -40 < y < main_panel.height:
                content.blit(txt, (50, y))

            y += 32

        hint = engine.font_small.render(
            "Usa la rueda del mouse para ver más análisis",
            True,
            TEXT_DIM,
        )

        surface.blit(
            hint,
            (
                engine.width // 2 - hint.get_width() // 2,
                engine.height - 118,
            ),
        )

        mouse_pos = pygame.mouse.get_pos()

        draw_button(
            surface,
            back_rect,
            "REGRESAR",
            font_med,
            color=RED,
            bg_hover=back_rect.collidepoint(mouse_pos),
        )

    engine.run_until(
        lambda: salir["value"],
        on_event,
        render,
        with_console=False,
        with_gauges=False,
    )


def show_analysis_screen(engine):
    salir = {"value": False}
    scroll = {"value": 0}

    font_med = get_med_font(engine)

    history = load_patient_records_for_screen()

    history_to_show = sorted(
        history,
        key=lambda item: item.get("patient_number", 0),
        reverse=True,
    )

    back_rect = pygame.Rect(
        40,
        engine.height - 80,
        220,
        50,
    )

    panel = pygame.Rect(
        engine.width // 2 - 610,
        170,
        1220,
        engine.height - 285,
    )

    card_rects = []

    def on_event(event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE or event.key == pygame.K_ESCAPE:
                salir["value"] = True

        if event.type == pygame.MOUSEWHEEL:
            scroll["value"] -= event.y * 45

            if scroll["value"] < 0:
                scroll["value"] = 0

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if back_rect.collidepoint(event.pos):
                salir["value"] = True
                return

            mouse_x, mouse_y = event.pos

            for rect, record in card_rects:
                real_rect = pygame.Rect(
                    panel.x + rect.x,
                    panel.y + rect.y,
                    rect.width,
                    rect.height,
                )

                if real_rect.collidepoint(mouse_x, mouse_y):
                    show_patient_analysis_detail(engine, record)
                    return

    def render(surface):
        surface.fill((3, 8, 18))

        title = engine.font_big.render(
            "ANÁLISIS",
            True,
            CYAN,
        )

        subtitle = font_med.render(
            "Selecciona un paciente para generar interpretación IA",
            True,
            TEXT_DIM,
        )

        surface.blit(
            title,
            (
                engine.width // 2 - title.get_width() // 2,
                55,
            ),
        )

        surface.blit(
            subtitle,
            (
                engine.width // 2 - subtitle.get_width() // 2,
                110,
            ),
        )

        draw_panel(surface, panel)

        content_surface = surface.subsurface(panel)
        content_surface.fill((5, 18, 24))

        card_rects.clear()

        if not history_to_show:
            msg = font_med.render(
                "Todavía no hay evaluaciones guardadas.",
                True,
                TEXT_DIM,
            )

            content_surface.blit(
                msg,
                (
                    panel.width // 2 - msg.get_width() // 2,
                    panel.height // 2 - msg.get_height() // 2,
                ),
            )

        else:
            mouse_pos = pygame.mouse.get_pos()
            local_mouse = (
                mouse_pos[0] - panel.x,
                mouse_pos[1] - panel.y,
            )

            y = 25 - scroll["value"]

            for record in history_to_show:
                patient_number = record.get("patient_number", "N/A")
                case_code = record.get("case_code", "N/A")
                date = record.get("date", "Sin fecha")
                state = record.get("general_state", "Sin estado")

                title_text = f"Analizar Paciente {patient_number} | {case_code}"
                subtitle_text = (
                    f"{date}  |  {state}  |  "
                    f"{get_gad7_text(record)}  |  "
                    f"{get_cognitive_text(record)}"
                )

                card = pygame.Rect(
                    35,
                    y,
                    panel.width - 70,
                    78,
                )

                if -90 < y < panel.height:
                    draw_analysis_card(
                        content_surface,
                        card,
                        title_text,
                        subtitle_text,
                        font_med,
                        engine.font_small,
                        local_mouse,
                    )

                    card_rects.append((card, record))

                y += 95

            hint = engine.font_small.render(
                "Usa la rueda del mouse para ver más pacientes",
                True,
                TEXT_DIM,
            )

            surface.blit(
                hint,
                (
                    engine.width // 2 - hint.get_width() // 2,
                    engine.height - 118,
                ),
            )

        mouse_pos = pygame.mouse.get_pos()

        draw_button(
            surface,
            back_rect,
            "REGRESAR",
            font_med,
            color=RED,
            bg_hover=back_rect.collidepoint(mouse_pos),
        )

    engine.run_until(
        lambda: salir["value"],
        on_event,
        render,
        with_console=False,
        with_gauges=False,
    )