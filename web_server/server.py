from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)

# web_server/server.py está dentro de la carpeta del proyecto.
# Por eso subimos un nivel para llegar a la raíz: E:\Crea-J IA\
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

PATIENTS_FILE = os.path.join(DATA_DIR, "patients.json")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")


# =========================
# FUNCIONES BASE
# =========================

def load_json(path, default):
    if not os.path.exists(path):
        print(f"Archivo no encontrado: {path}")
        return default

    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        print(f"Error leyendo {path}: {e}")
        return default


def normalize_text(value):
    return str(value or "").strip().upper()


def first_value(data, keys):
    for key in keys:
        value = data.get(key)
        if value not in [None, ""]:
            return value
    return ""


@app.template_filter("json_pretty")
def json_pretty(value):
    try:
        return json.dumps(value, ensure_ascii=False, indent=4)
    except Exception:
        return str(value)


# =========================
# LECTURA FLEXIBLE DE CAMPOS
# =========================

def get_patient_expediente(patient):
    possible_keys = [
        "expediente",
        "expediente_id",
        "expediente_code",      # <- TU JSON usa este
        "codigo_expediente",
        "numero_expediente",
        "case_code",            # <- history.json usa este
        "record_id",
        "patient_id",
        "id",
        "patient_code",
        "patient_number",
        "numero_paciente",
        "paciente_id",
    ]

    value = first_value(patient, possible_keys)
    if value:
        return value

    # Búsqueda extra por si el campo cambia de nombre después
    for key, value in patient.items():
        key_lower = str(key).lower()

        if "expediente" in key_lower:
            return value

        if "case" in key_lower and "code" in key_lower:
            return value

        if "record" in key_lower:
            return value

        if "patient" in key_lower and ("id" in key_lower or "code" in key_lower):
            return value

    return ""


def get_patient_code(patient):
    possible_keys = [
        "codigo",
        "codigo_acceso",
        "codigo_verificacion",
        "verification_code",    # <- TU JSON usa este
        "access_code",
        "password",
        "code",
        "clave",
    ]

    value = first_value(patient, possible_keys)
    if value:
        return value

    for key, value in patient.items():
        key_lower = str(key).lower()

        if "codigo" in key_lower:
            return value

        if "code" in key_lower and "expediente" not in key_lower and "case" not in key_lower:
            return value

        if "clave" in key_lower:
            return value

    return ""


def get_patient_name(patient):
    return first_value(
        patient,
        [
            "patient_name",
            "patient_label",     # <- TU JSON usa este
            "paciente",
            "name",
            "nombre",
        ],
    ) or "Paciente sin nombre"


def get_risk_text(patient):
    risk = first_value(
        patient,
        [
            "risk_level",
            "general_state",     # <- TU JSON usa este
            "estado_general",
            "estado",
            "riesgo",
            "final_status",
        ],
    )

    return str(risk or "No registrado")


def get_risk_class(risk_text):
    risk = str(risk_text).lower()

    if "alto" in risk or "grave" in risk or "severo" in risk:
        return "riesgo-alto"

    if "moderado" in risk or "medio" in risk:
        return "riesgo-moderado"

    if "leve" in risk or "bajo" in risk or "estable" in risk or "normal" in risk:
        return "riesgo-bajo"

    return "riesgo-desconocido"


# =========================
# TRADUCCIÓN DE CAMPOS
# =========================

FIELD_NAMES = {
    "patient_number": "Número de paciente",
    "patient_label": "Paciente",
    "patient_name": "Paciente",
    "paciente": "Paciente",
    "name": "Paciente",
    "expediente": "Expediente",
    "expediente_code": "Expediente",
    "case_code": "Expediente",
    "created_at": "Fecha de evaluación",
    "date": "Fecha",

    "general_state": "Estado general",
    "estado_general": "Estado general",
    "risk_level": "Nivel de riesgo",

    "results": "Resultados",
    "scores": "Puntajes",
    "gad7_score": "Ansiedad GAD-7",
    "gad7": "Ansiedad GAD-7",
    "gad7_severity": "Nivel de ansiedad GAD-7",
    "cognitive_score": "Puntaje cognitivo",
    "cognitive": "Puntaje cognitivo",
    "cognitive_result": "Resultado cognitivo",
    "sleep_quality": "Calidad del sueño",
    "sleep_hours": "Horas de sueño",
    "sleep": "Sueño",
    "intake": "Intake inicial",

    "bpm": "Frecuencia cardíaca",
    "heart_rate": "Frecuencia cardíaca",
    "spo2": "Oxigenación SpO₂",
    "oxygen": "Oxigenación SpO₂",

    "alerts": "Alertas",
    "recommendations": "Recomendaciones",
    "recomendaciones": "Recomendaciones",
    "summary": "Resumen",
    "summary_text": "Resumen completo",
    "analysis": "Análisis",
    "analisis": "Análisis",
    "final_analysis": "Análisis final",
    "conclusion": "Conclusión",
    "raw_session": "Sesión completa / datos técnicos",
}


HIDDEN_FIELDS = {
    "codigo",
    "codigo_acceso",
    "codigo_verificacion",
    "access_code",
    "verification_code",
    "password",
    "code",
    "clave",
}


def nice_field_name(key):
    return FIELD_NAMES.get(str(key), str(key).replace("_", " ").capitalize())


def add_result_rows(container, data):
    """Convierte dicts como results/scores/sensor_data en filas legibles."""
    if not isinstance(data, dict):
        return

    for key, value in data.items():
        lower_key = str(key).lower()
        if lower_key in HIDDEN_FIELDS:
            continue

        # Si hay otro diccionario adentro, lo mostramos como bloque técnico.
        if isinstance(value, dict):
            container.append({
                "label": nice_field_name(key),
                "value": value,
                "kind": "dict",
            })
        else:
            container.append({
                "label": nice_field_name(key),
                "value": value if value not in [None, ""] else "No registrado",
                "kind": "normal",
            })


def build_patient_sections(patient):
    """
    Convierte el JSON crudo en secciones bonitas para HTML.
    Soporta tu formato actual:
    - expediente_code
    - verification_code
    - general_state
    - results
    - recommendations
    - analysis
    - raw_session
    """

    main_data = []
    results = []
    recommendations = []
    analysis_blocks = []
    technical_blocks = []

    for key, value in patient.items():
        lower_key = str(key).lower()

        if lower_key in HIDDEN_FIELDS:
            continue

        if lower_key in [
            "patient_number",
            "patient_label",
            "patient_name",
            "paciente",
            "name",
            "expediente",
            "expediente_code",
            "case_code",
            "record_id",
            "patient_id",
            "created_at",
            "date",
        ]:
            main_data.append({
                "label": nice_field_name(key),
                "value": value if value not in [None, ""] else "No registrado",
            })

        elif lower_key in ["general_state", "estado_general", "risk_level", "estado", "riesgo"]:
            results.append({
                "label": nice_field_name(key),
                "value": value if value not in [None, ""] else "No registrado",
                "kind": "normal",
            })

        elif lower_key in ["results", "scores", "sensor_data"]:
            if isinstance(value, dict):
                add_result_rows(results, value)
            else:
                results.append({
                    "label": nice_field_name(key),
                    "value": value,
                    "kind": "normal",
                })

        elif lower_key in ["recommendations", "recomendaciones"]:
            if isinstance(value, list):
                recommendations.extend(value)
            else:
                recommendations.append(value)

        elif lower_key in ["analysis", "analisis", "summary", "summary_text", "final_analysis", "conclusion", "alerts"]:
            analysis_blocks.append({
                "label": nice_field_name(key),
                "value": value,
            })

        elif lower_key in ["raw_session"]:
            # No lo metemos arriba porque es gigante. Lo dejamos al final como desplegable.
            technical_blocks.append({
                "label": nice_field_name(key),
                "value": value,
            })

        else:
            # Cualquier campo nuevo no se pierde.
            if isinstance(value, dict):
                technical_blocks.append({
                    "label": nice_field_name(key),
                    "value": value,
                })
            else:
                results.append({
                    "label": nice_field_name(key),
                    "value": value if value not in [None, ""] else "No registrado",
                    "kind": "normal",
                })

    return {
        "main_data": main_data,
        "results": results,
        "recommendations": recommendations,
        "analysis_blocks": analysis_blocks,
        "technical_blocks": technical_blocks,
    }


# =========================
# BÚSQUEDA DE PACIENTES
# =========================

def find_patient(expediente, codigo):
    patients = load_json(PATIENTS_FILE, [])

    expediente = normalize_text(expediente)
    codigo = str(codigo or "").strip()

    print("================================")
    print("BUSCANDO PACIENTE")
    print("Archivo:", PATIENTS_FILE)
    print("Expediente escrito:", expediente)
    print("Código escrito:", codigo)
    print("Pacientes cargados:", len(patients))

    for patient in patients:
        patient_exp = normalize_text(get_patient_expediente(patient))
        patient_code = str(get_patient_code(patient) or "").strip()

        print("----")
        print("Expediente JSON:", patient_exp)
        print("Código JSON:", patient_code)

        if patient_exp == expediente and patient_code == codigo:
            print("PACIENTE ENCONTRADO")
            return patient

    print("NO SE ENCONTRÓ PACIENTE")
    return None


def find_patient_by_expediente(expediente):
    patients = load_json(PATIENTS_FILE, [])
    expediente = normalize_text(expediente)

    for patient in patients:
        patient_exp = normalize_text(get_patient_expediente(patient))

        if patient_exp == expediente:
            return patient

    return None


def find_patient_history(expediente):
    history = load_json(HISTORY_FILE, [])
    expediente = normalize_text(expediente)
    patient_history = []

    for item in history:
        item_exp = normalize_text(get_patient_expediente(item))

        if item_exp == expediente:
            patient_history.append(item)

    return patient_history


# =========================
# RUTAS
# =========================

@app.route("/", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        expediente = request.form.get("expediente", "")

        # Acepta los dos nombres para evitar que vuelva a fallar si el HTML cambia.
        codigo = (
            request.form.get("codigo", "")
            or request.form.get("access_code", "")
            or request.form.get("verification_code", "")
        )

        patient = find_patient(expediente, codigo)

        if patient:
            real_expediente = get_patient_expediente(patient)
            return redirect(url_for("expediente", expediente=real_expediente))

        error = "Expediente o código incorrecto. Revisa ambos datos."

    return render_template("login.html", error=error)


@app.route("/expediente/<expediente>")
def expediente(expediente):
    patient = find_patient_by_expediente(expediente)

    if not patient:
        return render_template(
            "expediente.html",
            patient=None,
            expediente=expediente,
            patient_name=None,
            error="No se encontró información para este expediente.",
            sections=None,
            risk_text="No registrado",
            risk_class="riesgo-desconocido",
            history=[],
        )

    risk_text = get_risk_text(patient)
    risk_class = get_risk_class(risk_text)
    sections = build_patient_sections(patient)
    history = find_patient_history(get_patient_expediente(patient))

    return render_template(
        "expediente.html",
        patient=patient,
        expediente=get_patient_expediente(patient),
        patient_name=get_patient_name(patient),
        error=None,
        sections=sections,
        risk_text=risk_text,
        risk_class=risk_class,
        history=history,
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
            