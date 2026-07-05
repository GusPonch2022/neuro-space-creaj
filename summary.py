"""
summary.py — Cerebro evaluador de JARVIS para NEURO SPACE.

Este módulo toma los resultados del paciente y genera:
- Estado general
- Puntajes
- Alertas
- Análisis
- Recomendaciones
- Conclusión
- Código de expediente
"""


def safe_get(data, key, default=None):
    """
    Obtiene un valor de un diccionario sin romper el programa.
    """
    if not isinstance(data, dict):
        return default
    return data.get(key, default)


def get_patient_number(session_data):
    """
    Obtiene el número del paciente.
    Si no existe, usa 1.
    """
    number = safe_get(session_data, "patient_number", 1)

    try:
        return int(number)
    except Exception:
        return 1


def generate_case_code(patient_number):
    """
    Genera un código formal de expediente.
    Ejemplo:
    Paciente 8 -> NS-P0008
    """
    return f"NS-P{patient_number:04d}"


def extract_intake_score(session_data):
    """
    Extrae el puntaje del intake inicial.
    Puede venir como total_score o calculado desde answers.
    """
    intake = safe_get(session_data, "intake", {})

    total = safe_get(intake, "total_score", None)
    if total is not None:
        return int(total)

    answers = safe_get(intake, "answers", [])
    score = 0

    if isinstance(answers, list):
        for answer in answers:
            value = safe_get(answer, "value", 0)
            try:
                score += int(value)
            except Exception:
                pass

    return score


def extract_gad7_score(session_data):
    """
    Extrae puntaje GAD-7.
    """
    gad7 = safe_get(session_data, "gad7", {})
    questionnaires = safe_get(session_data, "questionnaires", {})

    possible_sources = [
        gad7,
        safe_get(questionnaires, "gad7", {}),
        safe_get(session_data, "GAD7", {}),
    ]

    for source in possible_sources:
        total = safe_get(source, "total", None)
        if total is None:
            total = safe_get(source, "score", None)
        if total is None:
            total = safe_get(source, "total_score", None)

        if total is not None:
            try:
                return int(total)
            except Exception:
                pass

    return 0


def extract_cognitive_score(session_data):
    """
    Extrae porcentaje cognitivo o de atención.
    Si no existe, devuelve None.
    """
    cognitive = safe_get(session_data, "cognitive", {})
    test_cognitive = safe_get(session_data, "test_cognitive", {})

    possible_sources = [
        cognitive,
        test_cognitive,
        safe_get(session_data, "tests_cognitive", {}),
    ]

    for source in possible_sources:
        for key in ["percentage", "percent", "score_percent", "accuracy"]:
            value = safe_get(source, key, None)
            if value is not None:
                try:
                    return int(value)
                except Exception:
                    pass

        score = safe_get(source, "score", None)
        total = safe_get(source, "total", None)

        if score is not None and total:
            try:
                return int((float(score) / float(total)) * 100)
            except Exception:
                pass

    return None


def extract_sleep_value(session_data):
    """
    Busca datos relacionados al sueño dentro del intake.
    """
    intake = safe_get(session_data, "intake", {})
    answers = safe_get(intake, "answers", [])

    if not isinstance(answers, list):
        return None

    for answer in answers:
        answer_id = str(safe_get(answer, "id", "")).lower()
        question = str(safe_get(answer, "question", "")).lower()

        if "sleep" in answer_id or "sueño" in question or "dorm" in question:
            value = safe_get(answer, "value", None)
            try:
                return int(value)
            except Exception:
                return None

    return None


def classify_gad7(score):
    """
    Clasificación orientativa del GAD-7.
    """
    if score >= 15:
        return "ansiedad severa"
    elif score >= 10:
        return "ansiedad moderada"
    elif score >= 5:
        return "ansiedad leve"
    else:
        return "ansiedad mínima"


def classify_cognitive(score):
    """
    Clasificación simple de atención/cognición.
    """
    if score is None:
        return "sin datos cognitivos"

    if score >= 85:
        return "rendimiento cognitivo adecuado"
    elif score >= 65:
        return "rendimiento cognitivo moderadamente conservado"
    elif score >= 45:
        return "rendimiento cognitivo bajo"
    else:
        return "rendimiento cognitivo muy bajo"


def determine_general_state(intake_score, gad7_score, cognitive_score, sleep_value):
    """
    Determina el estado general del paciente.
    """
    risk_points = 0

    if intake_score >= 25:
        risk_points += 3
    elif intake_score >= 15:
        risk_points += 2
    elif intake_score >= 8:
        risk_points += 1

    if gad7_score >= 15:
        risk_points += 3
    elif gad7_score >= 10:
        risk_points += 2
    elif gad7_score >= 5:
        risk_points += 1

    if cognitive_score is not None:
        if cognitive_score < 45:
            risk_points += 3
        elif cognitive_score < 65:
            risk_points += 2
        elif cognitive_score < 85:
            risk_points += 1

    if sleep_value is not None:
        if sleep_value <= 3:
            risk_points += 2
        elif sleep_value <= 5:
            risk_points += 1

    if risk_points >= 8:
        return "Riesgo alto"
    elif risk_points >= 5:
        return "Riesgo moderado"
    elif risk_points >= 2:
        return "Riesgo leve"
    else:
        return "Estable"


def generate_alerts(intake_score, gad7_score, cognitive_score, sleep_value):
    """
    Genera alertas importantes.
    """
    alerts = []

    if gad7_score >= 15:
        alerts.append("Ansiedad elevada detectada.")
    elif gad7_score >= 10:
        alerts.append("Ansiedad moderada detectada.")

    if intake_score >= 25:
        alerts.append("Carga emocional alta en la evaluación inicial.")
    elif intake_score >= 15:
        alerts.append("Carga emocional moderada en la evaluación inicial.")

    if cognitive_score is not None:
        if cognitive_score < 45:
            alerts.append("Rendimiento cognitivo muy bajo.")
        elif cognitive_score < 65:
            alerts.append("Rendimiento cognitivo bajo.")

    if sleep_value is not None and sleep_value <= 3:
        alerts.append("Sueño deficiente reportado.")

    if not alerts:
        alerts.append("No se detectan alertas críticas en esta evaluación.")

    return alerts


def generate_analysis(intake_score, gad7_score, cognitive_score, sleep_value):
    """
    Genera análisis en lenguaje humano.
    """
    analysis = []

    gad7_classification = classify_gad7(gad7_score)
    cognitive_classification = classify_cognitive(cognitive_score)

    analysis.append(f"El paciente presenta {gad7_classification} según los datos registrados.")

    if intake_score >= 25:
        analysis.append("La evaluación inicial muestra una carga emocional elevada.")
    elif intake_score >= 15:
        analysis.append("La evaluación inicial muestra señales de carga emocional moderada.")
    elif intake_score >= 8:
        analysis.append("La evaluación inicial muestra señales leves de malestar.")
    else:
        analysis.append("La evaluación inicial no muestra una carga emocional significativa.")

    if sleep_value is not None:
        if sleep_value <= 3:
            analysis.append("El sueño deficiente puede estar afectando el estado emocional y la atención.")
        elif sleep_value <= 5:
            analysis.append("La calidad del sueño parece irregular y podría influir en el rendimiento general.")
        else:
            analysis.append("El sueño reportado no parece ser un factor crítico en esta evaluación.")

    analysis.append(f"En el área cognitiva, el resultado indica {cognitive_classification}.")

    return analysis


def generate_recommendations(general_state, gad7_score, cognitive_score, sleep_value):
    """
    Genera recomendaciones claras, simples y útiles según el estado del paciente.
    """

    recommendations = []

    # Recomendaciones según estado general
    if general_state == "Riesgo alto":
        recommendations.append("Buscar apoyo de un profesional de salud mental lo antes posible.")
        recommendations.append("No ignorar los síntomas si el malestar emocional es intenso.")
        recommendations.append("Evitar que el paciente se quede sin acompañamiento si se siente muy alterado.")
        recommendations.append("Realizar una nueva evaluación más adelante para comparar el cambio del estado.")
        recommendations.append("Reducir actividades que aumenten el estrés durante las próximas horas.")

    elif general_state == "Riesgo moderado":
        recommendations.append("Tomar un descanso breve en un lugar tranquilo.")
        recommendations.append("Repetir la evaluación después de un tiempo para ver si el estado mejora o empeora.")
        recommendations.append("Considerar apoyo profesional si los síntomas continúan por varios días.")
        recommendations.append("Evitar sobrecargarse con demasiadas tareas el mismo día.")
        recommendations.append("Hablar con una persona de confianza sobre cómo se siente.")

    elif general_state == "Riesgo leve":
        recommendations.append("Mantener observación del estado emocional durante el día.")
        recommendations.append("Descansar unos minutos si aparece tensión, ansiedad o cansancio mental.")
        recommendations.append("Repetir la evaluación si los síntomas aumentan.")
        recommendations.append("Mantener una rutina básica de sueño, comida e hidratación.")
        recommendations.append("Evitar acumular estrés sin pausas.")

    else:
        recommendations.append("Mantener hábitos saludables y seguimiento preventivo.")
        recommendations.append("Dormir bien, hidratarse y mantener descansos durante el día.")
        recommendations.append("Repetir la evaluación en otro momento para comparar resultados.")
        recommendations.append("Continuar con actividades normales si el paciente se siente estable.")

    # Recomendaciones por ansiedad
    if gad7_score >= 15:
        recommendations.append("Practicar respiración lenta: inhalar 4 segundos, sostener 2 y exhalar 6 segundos.")
        recommendations.append("Alejarse temporalmente de ruido, pantallas o situaciones que aumenten la ansiedad.")
        recommendations.append("Evitar tomar decisiones importantes mientras el nivel de ansiedad esté alto.")
        recommendations.append("Buscar ayuda si la ansiedad impide estudiar, trabajar, dormir o convivir normalmente.")

    elif gad7_score >= 10:
        recommendations.append("Realizar respiración lenta durante 3 a 5 minutos.")
        recommendations.append("Identificar qué situación pudo aumentar la ansiedad.")
        recommendations.append("Hacer una pausa corta antes de continuar con actividades exigentes.")
        recommendations.append("Evitar cafeína o bebidas energéticas si el paciente se siente nervioso.")

    elif gad7_score >= 5:
        recommendations.append("Usar pausas breves para evitar que la ansiedad aumente.")
        recommendations.append("Realizar una actividad relajante como caminar, escuchar música tranquila o estirarse.")
        recommendations.append("Observar si la ansiedad aparece en momentos específicos del día.")

    # Recomendaciones por sueño
    if sleep_value is not None:
        if sleep_value <= 3:
            recommendations.append("Priorizar dormir mejor durante la noche siguiente.")
            recommendations.append("Evitar pantallas, café o bebidas energéticas antes de dormir.")
            recommendations.append("Intentar acostarse a una hora más estable.")
            recommendations.append("Reducir ruido, luz fuerte o distracciones al momento de dormir.")
            recommendations.append("Si el mal sueño continúa, registrarlo y comentarlo con un profesional.")

        elif sleep_value <= 5:
            recommendations.append("Mejorar la higiene del sueño con horarios más constantes.")
            recommendations.append("Evitar usar el celular justo antes de dormir.")
            recommendations.append("Tomar una pausa de relajación antes de acostarse.")

    # Recomendaciones por cognición / atención
    if cognitive_score is not None:
        if cognitive_score < 45:
            recommendations.append("Repetir la prueba cognitiva en un ambiente silencioso y sin distracciones.")
            recommendations.append("Evitar tareas que requieran mucha concentración hasta descansar.")
            recommendations.append("Revisar si el bajo rendimiento puede estar relacionado con cansancio, estrés o mal sueño.")
            recommendations.append("Considerar evaluación profesional si el bajo rendimiento se repite.")

        elif cognitive_score < 65:
            recommendations.append("Realizar actividades de concentración cortas, con descansos entre ellas.")
            recommendations.append("Evitar hacer muchas tareas al mismo tiempo.")
            recommendations.append("Repetir la prueba cognitiva después de descansar.")

        elif cognitive_score < 85:
            recommendations.append("La atención está aceptable, pero puede mejorar con descanso y menos distracciones.")
            recommendations.append("Mantener pausas breves si se realizarán tareas largas.")

        else:
            recommendations.append("El rendimiento cognitivo fue adecuado; mantener buenos hábitos de descanso y concentración.")

    # Recomendaciones generales para todo expediente
    recommendations.append("Registrar cualquier cambio importante en el historial del paciente.")
    recommendations.append("Comparar este resultado con futuras evaluaciones para observar evolución.")
    recommendations.append("Recordar que esta evaluación es orientativa y no reemplaza una valoración profesional.")

    return recommendations      


def generate_conclusion(general_state, gad7_score, cognitive_score):
    """
    Genera conclusión final del expediente.
    """
    if general_state == "Riesgo alto":
        return (
            "El paciente muestra señales importantes de alteración emocional o cognitiva. "
            "Se recomienda seguimiento cuidadoso y valoración profesional."
        )

    if general_state == "Riesgo moderado":
        return (
            "El paciente presenta señales emocionales activas, principalmente relacionadas "
            "con ansiedad, estrés o descanso insuficiente. No se descarta necesidad de seguimiento."
        )

    if general_state == "Riesgo leve":
        return (
            "El paciente muestra señales leves de malestar. Se recomienda observación, "
            "autocuidado y repetir la evaluación si los síntomas aumentan."
        )

    return (
        "El paciente se encuentra estable según los datos registrados en esta evaluación. "
        "No se observan señales críticas en el resultado actual."
    )


def generate_patient_summary(session_data):
    """
    Función principal.
    Recibe los datos de sesión y devuelve el expediente evaluado.
    """
    patient_number = get_patient_number(session_data)
    case_code = generate_case_code(patient_number)

    intake_score = extract_intake_score(session_data)
    gad7_score = extract_gad7_score(session_data)
    cognitive_score = extract_cognitive_score(session_data)
    sleep_value = extract_sleep_value(session_data)

    general_state = determine_general_state(
        intake_score,
        gad7_score,
        cognitive_score,
        sleep_value,
    )

    alerts = generate_alerts(
        intake_score,
        gad7_score,
        cognitive_score,
        sleep_value,
    )

    analysis = generate_analysis(
        intake_score,
        gad7_score,
        cognitive_score,
        sleep_value,
    )

    recommendations = generate_recommendations(
        general_state,
        gad7_score,
        cognitive_score,
        sleep_value,
    )

    conclusion = generate_conclusion(
        general_state,
        gad7_score,
        cognitive_score,
    )

    return {
        "patient_number": patient_number,
        "case_code": case_code,
        "general_state": general_state,
        "scores": {
            "intake": intake_score,
            "gad7": gad7_score,
            "cognitive": cognitive_score,
            "sleep": sleep_value,
        },
        "alerts": alerts,
        "analysis": analysis,
        "recommendations": recommendations,
        "conclusion": conclusion,
        "saved_message": "Expediente guardado correctamente",
    }


def build_summary_text(summary):
    """
    Convierte el expediente en texto para mostrarlo en pantalla o guardarlo.
    """
    lines = []

    lines.append(f"Paciente número {summary['patient_number']}")
    lines.append(f"Código de expediente: {summary['case_code']}")
    lines.append("")
    lines.append(f"Estado general: {summary['general_state']}")
    lines.append("")

    lines.append("Puntajes:")
    lines.append(f"- Intake inicial: {summary['scores']['intake']}")
    lines.append(f"- GAD-7: {summary['scores']['gad7']}")

    cognitive = summary["scores"]["cognitive"]
    if cognitive is None:
        lines.append("- Cognitivo: Sin datos")
    else:
        lines.append(f"- Cognitivo: {cognitive}%")

    sleep = summary["scores"]["sleep"]
    if sleep is None:
        lines.append("- Sueño: Sin datos")
    else:
        lines.append(f"- Sueño: {sleep}")

    lines.append("")
    lines.append("Alertas:")
    for item in summary["alerts"]:
        lines.append(f"- {item}")

    lines.append("")
    lines.append("Análisis:")
    for item in summary["analysis"]:
        lines.append(f"- {item}")

    lines.append("")
    lines.append("Recomendaciones:")
    for item in summary["recommendations"]:
        lines.append(f"- {item}")

    lines.append("")
    lines.append("Conclusión:")
    lines.append(summary["conclusion"])

    lines.append("")
    lines.append(summary["saved_message"])

    return "\n".join(lines)