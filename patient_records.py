"""
patient_records.py
Sistema base de expedientes de pacientes para Neuro Space / CREA-J.

Crea:
- Número de paciente
- Código de expediente: NS-P0001
- Código de verificación de 8 dígitos
- Fecha/hora
- Estado general
- Resultado GAD-7
- Resultado cognitivo
- Recomendaciones
- Análisis final
"""

import os
import json
import random
from datetime import datetime


DATA_DIR = "data"
PATIENTS_FILE = os.path.join(DATA_DIR, "patients.json")


def ensure_data_folder():
    """
    Crea la carpeta data si no existe.
    """
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


def load_patients():
    """
    Carga todos los pacientes guardados.
    """
    ensure_data_folder()

    if not os.path.exists(PATIENTS_FILE):
        return []

    try:
        with open(PATIENTS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return []


def save_patients(patients):
    """
    Guarda la lista completa de pacientes.
    """
    ensure_data_folder()

    with open(PATIENTS_FILE, "w", encoding="utf-8") as file:
        json.dump(patients, file, indent=4, ensure_ascii=False)


def generate_patient_number():
    """
    Genera el siguiente número de paciente.
    """
    patients = load_patients()
    return len(patients) + 1


def generate_expediente_code(patient_number):
    """
    Genera código tipo NS-P0001.
    """
    return f"NS-P{patient_number:04d}"


def generate_verification_code():
    """
    Genera código de verificación de 8 dígitos.
    """
    patients = load_patients()
    used_codes = {str(p.get("verification_code")) for p in patients}

    while True:
        code = str(random.randint(10000000, 99999999))

        if code not in used_codes:
            return code


def classify_general_state(gad7_score, cognitive_score):
    """
    Clasificación básica del estado general.
    Esto después lo podemos mejorar con sensores y más lógica de IA.
    """

    if gad7_score >= 15 or cognitive_score < 50:
        return "Riesgo alto"

    elif gad7_score >= 10 or cognitive_score < 70:
        return "Riesgo moderado"

    elif gad7_score >= 5:
        return "Riesgo leve"

    else:
        return "Estable"


def generate_recommendations(general_state, gad7_score, cognitive_score):
    """
    Genera recomendaciones básicas según el resultado.
    Después esto lo conectamos con la IA.
    """

    recommendations = []

    if general_state == "Riesgo alto":
        recommendations.append("Recomendar evaluación profesional lo antes posible.")
        recommendations.append("Evitar que el paciente permanezca sin acompañamiento si presenta malestar fuerte.")
        recommendations.append("Registrar síntomas principales y cambios recientes.")

    elif general_state == "Riesgo moderado":
        recommendations.append("Recomendar seguimiento y nueva evaluación.")
        recommendations.append("Aplicar técnicas de respiración y control de ansiedad.")
        recommendations.append("Observar sueño, estrés y concentración durante los próximos días.")

    elif general_state == "Riesgo leve":
        recommendations.append("Recomendar descanso adecuado y monitoreo preventivo.")
        recommendations.append("Mantener hábitos saludables y repetir evaluación si los síntomas aumentan.")

    else:
        recommendations.append("Estado estable. Mantener hábitos saludables.")
        recommendations.append("Repetir evaluación de forma preventiva si es necesario.")

    if cognitive_score < 70:
        recommendations.append("Realizar ejercicios de atención y memoria.")

    if gad7_score >= 10:
        recommendations.append("Registrar posibles detonantes de ansiedad.")

    return recommendations


def create_patient_record(
    gad7_score=0,
    cognitive_score=100,
    analysis_text="Evaluación inicial registrada.",
    raw_session=None,
    patient_number=None,
    expediente_code=None
):
    """
    Crea y guarda un expediente completo de paciente.
    Si viene desde history.py, usa el mismo número y expediente.
    """

    if patient_number is None:
        patient_number = generate_patient_number()

    try:
        patient_number = int(patient_number)
    except Exception:
        patient_number = generate_patient_number()

    if not expediente_code:
        expediente_code = generate_expediente_code(patient_number)

    verification_code = generate_verification_code()

    general_state = classify_general_state(gad7_score, cognitive_score)
    recommendations = generate_recommendations(
        general_state,
        gad7_score,
        cognitive_score
    )

    record = {
        "patient_number": patient_number,
        "patient_label": f"Paciente {patient_number}",
        "expediente_code": expediente_code,
        "verification_code": verification_code,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

        "general_state": general_state,

        "results": {
            "gad7_score": gad7_score,
            "cognitive_score": cognitive_score
        },

        "recommendations": recommendations,

        "analysis": analysis_text,

        "raw_session": raw_session or {}
    }

    patients = load_patients()

    # Evita duplicar el mismo expediente si se guarda otra vez.
    updated = False

    for index, patient in enumerate(patients):
        if patient.get("expediente_code") == expediente_code:
            old_code = patient.get("verification_code")

            if old_code:
                record["verification_code"] = old_code

            patients[index] = record
            updated = True
            break

    if not updated:
        patients.append(record)

    save_patients(patients)

    return record

def get_patient_by_expediente(expediente_code):
    """
    Busca paciente por código de expediente.
    """
    patients = load_patients()

    for patient in patients:
        if patient.get("expediente_code") == expediente_code:
            return patient

    return None


def verify_patient_access(expediente_code, verification_code):
    """
    Verifica acceso usando expediente + código de 8 dígitos.
    """
    patient = get_patient_by_expediente(expediente_code)

    if not patient:
        return None

    if str(patient.get("verification_code")) == str(verification_code):
        return patient

    return None
def get_all_patients():
    """
    Devuelve todos los pacientes guardados.
    """
    return load_patients()


def get_patient_by_number(patient_number):
    """
    Busca paciente por número.
    Ejemplo: 1, 2, 3...
    """
    patients = load_patients()

    for patient in patients:
        if patient.get("patient_number") == patient_number:
            return patient

    return None


def print_patient_summary(patient):
    """
    Muestra un resumen bonito del paciente en terminal.
    """

    if not patient:
        print("Paciente no encontrado.")
        return

    print("===================================")
    print("EXPEDIENTE DEL PACIENTE")
    print("===================================")
    print("Paciente:", patient.get("patient_label"))
    print("Expediente:", patient.get("expediente_code"))
    print("Código verificación:", patient.get("verification_code"))
    print("Fecha:", patient.get("created_at"))
    print("Estado general:", patient.get("general_state"))

    results = patient.get("results", {})
    print("GAD-7:", results.get("gad7_score"))
    print("Cognitivo:", str(results.get("cognitive_score")) + "%")

    print()
    print("Análisis:")
    print(patient.get("analysis"))

    print()
    print("Recomendaciones:")

    for rec in patient.get("recommendations", []):
        print("-", rec)

    print("===================================")
def save_evaluation_as_patient(session_result):
    """
    Convierte el resultado completo de una evaluación en un expediente de paciente.

    Usa el mismo paciente, expediente, estado, análisis y recomendaciones que history.py
    cuando vienen incluidos.
    """

    gad7_score = session_result.get("gad7_score", 0)
    cognitive_score = session_result.get("cognitive_score", 100)

    analysis_text = session_result.get(
        "analysis",
        "Evaluación registrada sin análisis detallado."
    )

    patient_number = session_result.get("patient_number")
    expediente_code = session_result.get("case_code")

    extra_data = session_result.get("extra_data", {})
    history_record = extra_data.get("history_record", {})

    record = create_patient_record(
        gad7_score=gad7_score,
        cognitive_score=cognitive_score,
        analysis_text=analysis_text,
        raw_session=session_result,
        patient_number=patient_number,
        expediente_code=expediente_code
    )

    # Copia los datos finales reales del historial
    if history_record:
        if history_record.get("general_state"):
            record["general_state"] = history_record.get("general_state")

        if history_record.get("recommendations"):
            record["recommendations"] = history_record.get("recommendations")

        if history_record.get("conclusion"):
            record["conclusion"] = history_record.get("conclusion")

        if history_record.get("analysis"):
            analysis_data = history_record.get("analysis")

            if isinstance(analysis_data, list):
                record["analysis"] = " ".join(analysis_data)
            else:
                record["analysis"] = str(analysis_data)

        patients = load_patients()

        for index, patient in enumerate(patients):
            if patient.get("expediente_code") == expediente_code:
                patients[index] = record
                break

        save_patients(patients)

    return record