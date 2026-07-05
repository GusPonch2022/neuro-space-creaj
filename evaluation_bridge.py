"""
evaluation_bridge.py
Puente entre la evaluación del paciente y el sistema de expedientes.
"""

from patient_records import save_evaluation_as_patient


def build_session_result(
    patient_number=None,
    case_code=None,
    gad7_score=0,
    cognitive_score=100,
    analysis="Evaluación registrada.",
    sensor_data=None,
    extra_data=None
):
    """
    Construye el paquete final de evaluación.
    Este paquete luego se guarda como expediente de acceso web.
    """

    session_result = {
        "patient_number": patient_number,
        "case_code": case_code,
        "gad7_score": gad7_score,
        "cognitive_score": cognitive_score,
        "analysis": analysis,
        "sensor_data": sensor_data or {},
        "extra_data": extra_data or {}
    }

    return session_result


def finish_patient_evaluation(
    patient_number=None,
    case_code=None,
    gad7_score=0,
    cognitive_score=100,
    analysis="Evaluación registrada.",
    sensor_data=None,
    extra_data=None
):
    """
    Finaliza la evaluación y crea el expediente del paciente.
    Usa el mismo número y expediente que history.py.
    """

    session_result = build_session_result(
        patient_number=patient_number,
        case_code=case_code,
        gad7_score=gad7_score,
        cognitive_score=cognitive_score,
        analysis=analysis,
        sensor_data=sensor_data,
        extra_data=extra_data
    )

    record = save_evaluation_as_patient(session_result)

    return record