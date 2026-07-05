from patient_records import save_evaluation_as_patient, print_patient_summary


session_result = {
    "gad7_score": 11,
    "cognitive_score": 74,
    "analysis": "Paciente con signos de ansiedad moderada, pero con rendimiento cognitivo aceptable.",
    "sleep_quality": "Regular",
    "stress_level": "Alto",
    "attention_notes": "Leve dificultad para mantener concentración.",
    "sensor_data": {
        "bpm": 82,
        "spo2": 98
    }
}


record = save_evaluation_as_patient(session_result)

print()
print("Evaluación guardada como expediente.")
print_patient_summary(record)