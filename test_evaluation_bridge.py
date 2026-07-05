from evaluation_bridge import finish_patient_evaluation
from patient_records import print_patient_summary


record = finish_patient_evaluation(
    gad7_score=8,
    cognitive_score=86,
    analysis="Paciente con síntomas leves. Rendimiento cognitivo adecuado.",
    sensor_data={
        "bpm": 79,
        "spo2": 99
    },
    extra_data={
        "sleep": "Regular",
        "stress": "Medio"
    }
)

print()
print("Evaluación final conectada correctamente.")
print_patient_summary(record)