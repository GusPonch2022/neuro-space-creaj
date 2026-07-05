"""
main.py — NEURO SPACE / JARVIS (Python, escritorio, modo Doctor/Paciente)

Ejecuta:  python3 main.py

Incluye en esta versión: modo Doctor (contraseña 1035) con secciones
repartidas en varias visitas y categorías de edad, GAD-7, atención/reacción,
Stroop, N-Back, toma de decisiones (apuestas variables), respiración guiada,
exposición gradual a 8 miedos específicos por niveles, escena final generada
según las respuestas reales, resumen dual paciente/doctor, historial en
JSON, y vuelta automática al inicio con despedida.

NOTA: esta versión de escritorio todavía no incluye PSS, PANAS, CPT, Trail
Making, memoria visual, flexibilidad cognitiva, orientación espacial ni
reconocimiento emocional (sí están en la versión web). Se pueden agregar
después siguiendo el mismo patrón de tests_cognitive.py.
"""

import sys
import time
import random
import pygame

import config
from engine import Engine
from hud import CYAN, AMBER, GREEN, RED, TEXT, TEXT_DIM, draw_button
import doctor
import intake
import questionnaires
import tests_cognitive as tc
import phobia
import scene
import summary
import history
import menu


def show_start_screen(engine):
    """Pantalla inicial con dos botones: Modo Paciente / Modo Doctor.
    Devuelve 'patient' o 'doctor'."""
    btn_w, btn_h = 360, 64
    patient_rect = pygame.Rect(engine.width//2-btn_w//2, engine.height//2-20, btn_w, btn_h)
    doctor_rect = pygame.Rect(engine.width//2-btn_w//2, engine.height//2+60, btn_w, btn_h)
    result = {"mode": None}

    def on_event(event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if patient_rect.collidepoint(event.pos):
                result["mode"] = "patient"
            elif doctor_rect.collidepoint(event.pos):
                result["mode"] = "doctor"

    def render(surface):
        title = engine.font_big.render("NEURO SPACE", True, TEXT)
        surface.blit(title, (engine.width//2-title.get_width()//2, engine.height//2-160))
        sub = engine.font_med.render("ASISTENTE JARVIS — MONITOREO NEUROCOGNITIVO Y BIOMÉTRICO", True, TEXT_DIM)
        surface.blit(sub, (engine.width//2-sub.get_width()//2, engine.height//2-110))
        mouse_pos = pygame.mouse.get_pos()
        draw_button(surface, patient_rect, "▶ MODO PACIENTE", engine.font_med, color=GREEN,
                    bg_hover=patient_rect.collidepoint(mouse_pos))
        draw_button(surface, doctor_rect, "🩺 MODO DOCTOR", engine.font_med, color=AMBER,
                    bg_hover=doctor_rect.collidepoint(mouse_pos))
        hint = engine.font_gsub.render("(ESC en cualquier momento para salir)", True, TEXT_DIM)
        surface.blit(hint, (engine.width//2-hint.get_width()//2, engine.height//2+150))

    engine.run_until(lambda: result["mode"] is not None, on_event, render, with_console=False)
    return result["mode"]


def show_farewell(engine, nombre, section_index, total_sections):
    next_section = (section_index + 1) % total_sections
    msg = (f"Gracias por tu confianza, {nombre}. Nos vemos en la próxima sesión "
           f"de Neuro Space (Sección {next_section+1} de {total_sections}).")
    continue_rect = pygame.Rect(engine.width//2-200, engine.height//2+60, 400, 56)
    done = {"value": False}

    def on_event(event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if continue_rect.collidepoint(event.pos):
                done["value"] = True

    def render(surface):
        title = engine.font_big.render("SESIÓN FINALIZADA", True, TEXT)
        surface.blit(title, (engine.width//2-title.get_width()//2, engine.height//2-100))
        from hud import wrap_text
        y = engine.height//2-30
        for line in wrap_text(msg, engine.font_med, engine.width-300):
            surf = engine.font_med.render(line, True, TEXT_DIM)
            surface.blit(surf, (engine.width//2-surf.get_width()//2, y))
            y += 28
        mouse_pos = pygame.mouse.get_pos()
        draw_button(surface, continue_rect, "⟲ VOLVER AL INICIO", engine.font_med, color=CYAN,
                    bg_hover=continue_rect.collidepoint(mouse_pos))

    engine.run_until(lambda: done["value"], on_event, render, with_console=False)
    return next_section


def run_session(engine, section, age_category, section_index=None):
    """Ejecuta una sesión completa según la sección/edad configuradas por el doctor."""
    selected = section["selectedTests"]
    phobia_cfg = section["phobia"]
    age_params = config.get_age_params(age_category)

    engine.console.lines = []
    engine.set_status("INICIANDO SISTEMA", AMBER)
    engine.jarvis_say("Hola, bienvenido. Soy Jarvis, el asistente del proyecto Neuro Space.")
    engine.jarvis_say("Voy a acompañarte durante esta sesión con distintas pruebas y una experiencia visual diseñada para ayudarte.")
    engine.jarvis_say("Antes de comenzar, quiero hacerte algunas preguntas.")

    answers = intake.run_intake(engine)

    gad7 = attention_stats = stroop_stats = nback_stats = decision_stats = breathing_stats = phobia_stats = None

    if selected.get("gad7") and age_params["allow_gad7"]:
        engine.jarvis_say("Vamos a hacer un cuestionario breve y validado de ansiedad.")
        gad7 = questionnaires.run_gad7(engine)

    if selected.get("attention"):
        engine.jarvis_say("Ahora una prueba de atención y tiempo de reacción, similar a las que se usan para evaluar el estado de alerta en pilotos. Presiona la barra espaciadora cuando el círculo se encienda en verde.")
        attention_stats = tc.run_attention_test(engine, age_params["attention"])

    if selected.get("stroop"):
        engine.jarvis_say("Ahora la prueba de Stroop: haz click en el color de la TINTA, no en lo que dice la palabra.")
        stroop_stats = tc.run_stroop_test(engine, age_params["stroop"])

    if selected.get("nback"):
        engine.jarvis_say("Ahora una prueba de memoria de trabajo. Indica si la letra actual coincide con la de dos lugares atrás.")
        nback_stats = tc.run_nback_test(engine, 2, age_params["nback"])

    if selected.get("decision"):
        engine.jarvis_say("Ahora toma de decisiones: elige la opción que prefieras en cada ronda.")
        decision_stats = tc.run_decision_test(engine, age_params["decision"])

    if selected.get("breathing"):
        engine.jarvis_say("Ahora un breve ejercicio de respiración guiada y coherencia cardiaca.")
        breathing_stats = tc.run_breathing_test(engine, 6)

    if selected.get("phobia"):
        phobia_key = None
        if phobia_cfg.get("mode") == "doctor_pick" and phobia_cfg.get("doctorPhobia"):
            phobia_key = phobia_cfg["doctorPhobia"]
            label = config.PHOBIA_LABELS[phobia_key]
            engine.jarvis_say(f"Tu doctor preparó un ejercicio de exposición gradual sobre: {label}. Vamos a hacerlo con calma, en niveles, y puedes detenerte cuando quieras.")
        else:
            engine.jarvis_say("Ahora un ejercicio de exposición gradual. Elige qué situación te genera más miedo o incomodidad.")
            phobia_key = phobia.select_phobia(engine)
            if phobia_key:
                label = config.PHOBIA_LABELS[phobia_key]
                engine.jarvis_say(f"Entendido, vamos a trabajar con {label}, en niveles crecientes, y puedes detenerte cuando quieras.")
        if phobia_key:
            phobia_stats = phobia.run_phobia_exposure(engine, phobia_key, age_params["phobia_levels"])
            if phobia_stats["stoppedAtLevel"]:
                engine.jarvis_say("Está bien, detuvimos el ejercicio donde lo necesitabas. Eso también es información valiosa.")
            else:
                engine.jarvis_say(f"Completaste los {age_params['phobia_levels']} niveles del ejercicio. Buen trabajo.")

    snapshots = []
    initial_snap = engine.bio.snapshot()
    engine.update_gauges_with_snapshot(initial_snap)
    profile = scene.derive_scene_profile(initial_snap, answers, gad7)

    if selected.get("experience"):
        engine.jarvis_say("Excelente, gracias por completar las pruebas. Ahora voy a colocar la experiencia visual. Respira con calma.")
        time.sleep(0.4)
        level = profile["level"]
        engine.console.add_line("SISTEMA", f"Escena elegida según tu estado combinado ({round(profile['combinedScore']*100)}/100): {level.replace('_',' ')}", TEXT_DIM)
        snapshots = scene.run_experience(engine, level, profile)
        engine.jarvis_say("La experiencia ha terminado.")
    else:
        snapshots = [initial_snap, engine.bio.snapshot(), engine.bio.snapshot()]

    nombre = (answers.get(intake.QUESTIONS[0]) or "").strip() or "paciente"
    bpm_prom = round(sum(s["bpm"] for s in snapshots)/len(snapshots))
    spo2_prom = round(sum(s["spo2"] for s in snapshots)/len(snapshots))
    anx_prom = sum(s["anxiety"]["score"] for s in snapshots)/len(snapshots)
    anx_max = max(s["anxiety"]["score"] for s in snapshots)

    if anx_prom >= 0.66:
        interpretacion = "Hoy tu cuerpo mostró señales de ansiedad alta durante buena parte de la sesión. Te recomendamos descansar y, si es posible, hablarlo con un profesional pronto."
    elif anx_prom >= 0.35:
        interpretacion = "Hoy mostraste niveles de ansiedad moderados, con algunos momentos de mayor activación."
    else:
        interpretacion = "Hoy te mostraste tranquilo y estable durante la mayor parte de la sesión. ¡Buen trabajo cuidando de ti!"

    summary_data = {
        "nombre": nombre, "answers": answers, "bpmProm": bpm_prom, "spo2Prom": spo2_prom,
        "anxProm": anx_prom, "anxMax": anx_max, "interpretacionSimple": interpretacion,
        "ageCategory": age_category,
        "gad7": gad7, "attentionStats": attention_stats, "stroopStats": stroop_stats,
        "nbackStats": nback_stats, "decisionStats": decision_stats, "breathingStats": breathing_stats,
        "phobiaStats": phobia_stats,
    }

    engine.console.add_line("DIAGNÓSTICO", interpretacion, GREEN)
    engine.voice.say(interpretacion)
    summary.show_dual_summary(engine, summary_data)

    record = history.build_session_record(
        nombre, snapshots, attention_stats, interpretacion, gad7, stroop_stats, nback_stats,
        breathing_stats, section_index=section_index, age_category=age_category,
    )
    history.add_session_to_history(record)

    engine.jarvis_say(f"Gracias por tu confianza, {nombre}. Que tengas un excelente día, nos vemos en la próxima sesión de Neuro Space.")
    engine.set_status("SESIÓN FINALIZADA", GREEN)
    return nombre


def main():
    engine = Engine()

    while True:
        mode = show_start_screen(engine)
        if mode == "doctor":
            ok = doctor.prompt_password(engine)
            if ok:
                doctor.run_doctor_config(engine)
            continue

        # Modo paciente: cargar configuración guardada por el doctor (o default)
        saved = doctor.load_session_config() or doctor.default_session_config()
        sections = saved.get("sections") or doctor.default_session_config()["sections"]
        progress = doctor.load_section_progress()
        section_index = progress % len(sections)
        section = sections[section_index]
        age_category = saved.get("ageCategory", "adultos_16mas")

        engine.console.add_line(
            "SISTEMA",
            f"Sección {section_index+1} de {len(sections)} · {config.AGE_LABELS.get(age_category, age_category)}",
            TEXT_DIM,
        )

        nombre = run_session(engine, section, age_category, section_index)

        doctor.save_section_progress((section_index + 1) % len(sections))
        time.sleep(0.5)
        show_farewell(engine, nombre, section_index, len(sections))