from patient_records import create_patient_record

record = create_patient_record(
    gad7_score=14,
    cognitive_score=62,
    analysis_text="Paciente con ansiedad moderada y atención reducida. Se recomienda seguimiento."
)

print("EXPEDIENTE CREADO:")
print("Paciente:", record["patient_label"])
print("Expediente:", record["expediente_code"])
print("Código verificación:", record["verification_code"])
print("Fecha:", record["created_at"])
print("Estado:", record["general_state"])
print("GAD-7:", record["results"]["gad7_score"])
print("Cognitivo:", str(record["results"]["cognitive_score"]) + "%")
print("Recomendaciones:")

for rec in record["recommendations"]:
    print("-", rec)
    