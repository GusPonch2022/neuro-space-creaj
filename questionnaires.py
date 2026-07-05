"""
questionnaires.py — Cuestionarios validados.

Incluye:
- GAD-7: escala de ansiedad con 7 preguntas y 4 opciones.
"""


GAD7_QUESTIONS = [
    {
        "id": "nervous",
        "question": "Sentirte nervioso, ansioso o con los nervios de punta.",
    },
    {
        "id": "worry_control",
        "question": "No poder dejar de preocuparte o controlar tus preocupaciones.",
    },
    {
        "id": "too_much_worry",
        "question": "Preocuparte demasiado por diferentes cosas.",
    },
    {
        "id": "relaxing",
        "question": "Tener dificultad para relajarte.",
    },
    {
        "id": "restless",
        "question": "Estar tan inquieto que te resulta difícil quedarte quieto.",
    },
    {
        "id": "irritable",
        "question": "Irritarte o enojarte con facilidad.",
    },
    {
        "id": "afraid",
        "question": "Sentir miedo, como si algo terrible pudiera pasar.",
    },
]


GAD7_OPTIONS = [
    ("Nunca", 0),
    ("Varios días", 1),
    ("Más de la mitad de los días", 2),
    ("Casi todos los días", 3),
]


def interpret_gad7_score(score):
    """
    Interpreta el puntaje total del GAD-7.
    """

    if score >= 15:
        return "Ansiedad severa"

    if score >= 10:
        return "Ansiedad moderada"

    if score >= 5:
        return "Ansiedad leve"

    return "Ansiedad mínima"


def run_gad7(engine, voice_fn=None):
    """
    Ejecuta el GAD-7 con botones.

    Devuelve:
    {
        "phase": "gad7",
        "answers": [...],
        "score": total,
        "level": nivel
    }
    """

    answers = []

    for i, item in enumerate(GAD7_QUESTIONS, start=1):
        question = item["question"]

        if voice_fn:
            voice_fn(
                engine,
                f"Pregunta {i} del GAD siete. {question}",
            )

        response = engine.get_button_choice(
            question,
            GAD7_OPTIONS,
            sub=f"Neuro Space — GAD-7 · Pregunta {i} de {len(GAD7_QUESTIONS)}",
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

    level = interpret_gad7_score(score)

    return {
        "phase": "gad7",
        "answers": answers,
        "score": score,
        "level": level,
    }