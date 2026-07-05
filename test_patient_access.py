from patient_records import verify_patient_access, print_patient_summary


expediente = input("Ingrese expediente: ")
codigo = input("Ingrese código de verificación: ")

patient = verify_patient_access(expediente, codigo)

if patient:
    print()
    print("Acceso concedido.")
    print_patient_summary(patient)
else:
    print()
    print("Acceso denegado. Expediente o código incorrecto.")
