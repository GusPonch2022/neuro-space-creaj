"""
intake.py — Preguntas iniciales del modo paciente.

Estas preguntas usan 4 opciones por pregunta:
- texto visible
- valor interno
"""


INTAKE_QUESTIONS = [
    {
        "id": "current_state",
        "question": "¿Cómo te sientes en este momento, en una escala del uno al diez?",
        "options": [
            ("1–3: Muy mal", 3),
            ("4–5: Mal / bajo", 5),
            ("6–7: Regular", 7),
            ("8–10: Bien", 10),
        ],
    },
    {
        "id": "recent_sleep_quality",
        "question": "¿Has dormido bien las últimas noches?",
        "options": [
            ("Sí, he dormido bien", 0),
            ("Más o menos", 1),
            ("He dormido poco", 2),
            ("No he dormido bien", 3),
        ],
    },
    {
        "id": "sleep_hours",
        "question": "¿Cuántas horas dormiste anoche, aproximadamente?",
        "options": [
            ("Menos de 4 horas", 3),
            ("4 a 5 horas", 2),
            ("6 a 7 horas", 1),
            ("8 horas o más", 0),
        ],
    },
    {
        "id": "stress_today",
        "question": "¿Hay algo en particular que te genere estrés o ansiedad hoy?",
        "options": [
            ("Nada en particular", 0),
            ("Algo leve", 1),
            ("Sí, bastante", 2),
            ("Sí, demasiado", 3),
        ],
    },
    {
        "id": "stimulants",
        "question": "¿Has consumido cafeína, alcohol, o algún estimulante en las últimas horas?",
        "options": [
            ("No consumí nada", 0),
            ("Cafeína", 1),
            ("Alcohol", 2),
            ("Otro estimulante", 2),
        ],
    },
    {
        "id": "body_tension",
        "question": "¿Sientes tensión física en algún lugar de tu cuerpo en este momento?",
        "options": [
            ("No siento tensión", 0),
            ("Cabeza / cuello", 1),
            ("Pecho / respiración", 3),
            ("Espalda / cuerpo", 1),
        ],
    },
    {
        "id": "weekly_mood",
        "question": "¿Cómo describirías tu estado de ánimo general esta semana?",
        "options": [
            ("Bueno / estable", 0),
            ("Cansado", 1),
            ("Triste / bajo", 2),
            ("Ansioso / irritable", 2),
        ],
    },
    {
        "id": "session_experience",
        "question": "¿Esta es tu primera sesión con Neuro Space o ya has hecho alguna antes?",
        "options": [
            ("Primera sesión", 0),
            ("Ya hice una antes", 1),
            ("He hecho varias", 2),
            ("No estoy seguro", 0),
        ],
    },
]


def run_intake(engine, voice_fn=None):
    """
    Ejecuta las preguntas iniciales.
    Devuelve:
    {
        "phase": "intake_inicial",
        "answers": [...],
        "score": total
    }
    """

    answers = []

    for i, item in enumerate(INTAKE_QUESTIONS, start=1):
        question = item["question"]
        options = item["options"]

        if voice_fn:
            voice_fn(
                engine,
                f"Pregunta {i}. {question}",
            )

        response = engine.get_button_choice(
            question,
            options,
            sub=f"Neuro Space — Intake inicial · Pregunta {i} de {len(INTAKE_QUESTIONS)}",
            cols=2,
            return_full=True,
        )

        answers.append(
            {
                "number": i,
                "id": item["id"],
                "question": question,
                "answer_text": response["text"],
                "value": response["value"],
            }
        )

    score = sum(
        answer["value"]
        for answer in answers
        if isinstance(answer["value"], int)
    )

    return {
        "phase": "intake_inicial",
        "answers": answers,
        "score": score,
    }