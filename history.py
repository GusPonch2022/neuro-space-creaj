"""
history.py — Guardado y lectura de expedientes de pacientes.
Lee history.json y patients.json para evitar números repetidos.
"""

import json
import os
from datetime import datetime

from summary import generate_patient_summary, build_summary_text


DATA_DIR = "data"
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")
PATIENTS_FILE = os.path.join(DATA_DIR, "patients.json")


def ensure_data_folder():
    """
    Crea la carpeta data si no existe.
    """
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


def _load_json_list(path):
    """
    Carga un JSON tipo lista.
    Si no existe, está vacío o está dañado, devuelve [].
    """
    ensure_data_folder()

    if not os.path.exists(path):
        return []

    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

        return []

    except Exception:
        return []


def _save_json_list(path, data):
    """
    Guarda una lista en JSON.
    """
    ensure_data_folder()

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def load_history():
    """
    Carga el historial interno.
    """
    return _load_json_list(HISTORY_FILE)


def save_history(history):
    """
    Guarda todo el historial interno.
    """
    _save_json_list(HISTORY_FILE, history)


def load_patients():
    """
    Carga patients.json, usado por el sistema de acceso/web.
    """
    return _load_json_list(PATIENTS_FILE)


def get_next_patient_number():
    """
    Calcula el siguiente número de paciente revisando:
    - history.json
    - patients.json

    Así evita repetir Paciente 3, 4, 5, etc.
    """
    history = load_history()
    patients = load_patients()

    max_number = 0

    # Revisar history.json
    for record in history:
        if not isinstance(record, dict):
            continue

        number = record.get("patient_number")

        try:
            number = int(number)
            if number > max_number:
                max_number = number
        except Exception:
            pass

    # Revisar patients.json
    for patient in patients:
        if not isinstance(patient, dict):
            continue

        number = patient.get("patient_number")

        try:
            number = int(number)
            if number > max_number:
                max_number = number
        except Exception:
            pass

    return max_number + 1


def save_patient_record(session_data):
    """
    Genera el resumen del paciente y lo guarda en history.json.
    El número de paciente ya debe venir correcto desde patient.py.
    """
    if not isinstance(session_data, dict):
        session_data = {}

    if "patient_number" not in session_data:
        session_data["patient_number"] = get_next_patient_number()

    summary = generate_patient_summary(session_data)
    summary_text = build_summary_text(summary)

    record = {
        "patient_number": summary["patient_number"],
        "case_code": summary["case_code"],
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "general_state": summary["general_state"],
        "scores": summary["scores"],
        "alerts": summary["alerts"],
        "analysis": summary["analysis"],
        "recommendations": summary["recommendations"],
        "conclusion": summary["conclusion"],
        "summary_text": summary_text,
        "raw_session": session_data,
    }

    history = load_history()

    # Evitar duplicados por si se guarda dos veces el mismo paciente
    clean_history = []
    for old_record in history:
        if not isinstance(old_record, dict):
            continue

        if int(old_record.get("patient_number", 0)) != int(record["patient_number"]):
            clean_history.append(old_record)

    clean_history.append(record)

    clean_history.sort(key=lambda x: int(x.get("patient_number", 0)))

    save_history(clean_history)

    return record


def _patient_access_to_history_record(patient):
    """
    Convierte un registro de patients.json al formato que usan Historial/Análisis.
    Así las pantallas pueden leer patients.json sin romperse.
    """
    if not isinstance(patient, dict):
        return None

    patient_number = patient.get("patient_number")
    case_code = patient.get("expediente_code")
    date = patient.get("created_at")
    general_state = patient.get("general_state")

    results = patient.get("results", {})
    raw_session = patient.get("raw_session", {})

    # Intentar sacar el historial completo si existe dentro de raw_session
    history_record = (
        raw_session
        .get("extra_data", {})
        .get("history_record")
    )

    if isinstance(history_record, dict):
        # Forzar que use los datos correctos de patients.json
        history_record["patient_number"] = patient_number
        history_record["case_code"] = case_code
        history_record["date"] = date
        history_record["general_state"] = general_state
        history_record["verification_code"] = patient.get("verification_code")

        return history_record

    # Si no existe history_record interno, crear uno básico
    record = {
        "patient_number": patient_number,
        "case_code": case_code,
        "date": date,
        "general_state": general_state,
        "scores": {
            "gad7": results.get("gad7_score"),
            "cognitive": results.get("cognitive_score"),
        },
        "alerts": [],
        "analysis": [
            patient.get("analysis", "Sin análisis registrado.")
        ],
        "recommendations": patient.get("recommendations", []),
        "conclusion": patient.get("conclusion", ""),
        "summary_text": "",
        "raw_session": raw_session,
        "verification_code": patient.get("verification_code"),
    }

    return record


def get_patient_record(patient_number):
    """
    Busca un paciente por número.
    Primero busca en patients.json.
    Si no lo encuentra, busca en history.json.
    """
    try:
        patient_number = int(patient_number)
    except Exception:
        return None

    # Buscar primero en patients.json
    patients = load_patients()

    for patient in patients:
        try:
            if int(patient.get("patient_number", 0)) == patient_number:
                return _patient_access_to_history_record(patient)
        except Exception:
            pass

    # Respaldo: buscar en history.json
    history = load_history()

    for record in history:
        try:
            if int(record.get("patient_number", 0)) == patient_number:
                return record
        except Exception:
            pass

    return None


def get_patient_by_case_code(case_code):
    """
    Busca un expediente por código NS-P0001.
    Primero busca en patients.json.
    Si no lo encuentra, busca en history.json.
    """
    # Buscar primero en patients.json
    patients = load_patients()

    for patient in patients:
        if patient.get("expediente_code") == case_code:
            return _patient_access_to_history_record(patient)

    # Respaldo: buscar en history.json
    history = load_history()

    for record in history:
        if record.get("case_code") == case_code:
            return record

    return None


def list_patient_blocks():
    """
    Devuelve una lista resumida para pantallas de análisis/historial.
    Lee primero patients.json para mostrar todos los pacientes del sistema.
    """
    patients = load_patients()
    blocks = []

    for patient in patients:
        if not isinstance(patient, dict):
            continue

        patient_number = patient.get("patient_number")
        case_code = patient.get("expediente_code")
        date = patient.get("created_at")
        general_state = patient.get("general_state")

        if patient_number is None or case_code is None:
            continue

        results = patient.get("results", {})

        blocks.append({
            "patient_number": patient_number,
            "case_code": case_code,
            "date": date,
            "general_state": general_state,
            "gad7": results.get("gad7_score"),
            "cognitive": results.get("cognitive_score"),
            "verification_code": patient.get("verification_code"),
        })

    # Si patients.json está vacío, usar history.json como respaldo
    if not blocks:
        history = load_history()

        for record in history:
            if not isinstance(record, dict):
                continue

            patient_number = record.get("patient_number")
            case_code = record.get("case_code")
            date = record.get("date")
            general_state = record.get("general_state")

            if patient_number is None or case_code is None:
                continue

            scores = record.get("scores", {})

            blocks.append({
                "patient_number": patient_number,
                "case_code": case_code,
                "date": date,
                "general_state": general_state,
                "gad7": scores.get("gad7"),
                "cognitive": scores.get("cognitive"),
                "verification_code": record.get("verification_code"),
            })

    blocks.sort(key=lambda x: int(x.get("patient_number", 0)))

    return blocks