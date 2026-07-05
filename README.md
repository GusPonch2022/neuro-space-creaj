# Neuro Space — Jarvis (Python, escritorio, Modo Doctor/Paciente)

Versión de escritorio en Python (pygame), con la misma estructura de la
versión web más reciente: pantalla de inicio con **Modo Paciente** /
**Modo Doctor** (contraseña **1035**), secciones repartidas en varias
visitas, categorías de edad, exposición gradual a miedos específicos,
resumen dual paciente/doctor, e historial guardado en JSON.

## Instalación

```bash
pip install pygame pyttsx3
# Linux también necesita: sudo apt-get install espeak-ng
python3 main.py
```

Se abre en pantalla completa. ESC para salir en cualquier momento.

## Qué incluye esta versión

- Modo Doctor (contraseña `1035`): arma una o varias **secciones** de
  pruebas (el paciente avanza de sección en cada visita y vuelve a la
  primera al terminar todas), elige la **categoría de edad** (ajusta
  automáticamente cantidad de intentos y niveles), y configura el
  módulo de **exposición a miedos** (el paciente elige o el doctor
  preselecciona uno de los 8: arañas, espacios encerrados, alturas,
  multitudes, mar, aviones, perros, ojos).
- Entrevista inicial con **respuestas variadas** de Jarvis (ya no repite
  siempre lo mismo).
- Pruebas: **GAD-7**, **atención/tiempo de reacción**, **Stroop**,
  **N-Back**, **toma de decisiones** (apuestas variables por ronda),
  **respiración guiada y coherencia cardiaca**.
- **Exposición gradual a fobias** por niveles (2 a 4 según edad), con
  escala SUDS (0-10) antes/después de cada nivel y botón para detenerse.
- **Escena final generada** (océano calmo / bosque con lluvia /
  respiración guiada) elegida según el sensor simulado COMBINADO con
  las respuestas reales de la entrevista (sueño reportado, estrés
  mencionado, estimulantes).
- **Resumen dual**: pestaña para el paciente (lenguaje simple +
  recomendaciones) y pestaña de reporte clínico avanzado (protegida con
  la misma contraseña `1035`).
- **Historial en JSON** (`data/history.json`) con fecha, sección, edad,
  y métricas de cada sesión.
- Al terminar: despedida personalizada y **vuelta automática al inicio**.

## Qué NO incluye todavía (sí están en la versión web)

PSS, PANAS, CPT, Trail Making Test, memoria visual, flexibilidad
cognitiva, orientación espacial, reconocimiento emocional, y video/música
reales (esta versión usa solo escenas generadas). Se pueden agregar
siguiendo el mismo patrón de `tests_cognitive.py` — avísame si quieres
que continúe con esa siguiente tanda.

## Estructura

```
neuro_space_py2/
├── main.py              # Punto de entrada y flujo principal
├── engine.py            # Motor: ventana, render, helpers de botones/texto
├── config.py            # Parámetros, contraseña, rutas, edad
├── hud.py               # Elementos visuales (núcleo, medidores, partículas)
├── sensors.py           # Biométricos simulados
├── voice.py             # Voz offline (pyttsx3)
├── intake.py            # Entrevista inicial con respuestas variadas
├── questionnaires.py    # GAD-7
├── tests_cognitive.py   # Atención, Stroop, N-Back, decisión, respiración
├── phobia.py            # Exposición gradual a 8 miedos x niveles
├── scene.py             # Escena final generada según respuestas
├── summary.py           # Interpretaciones + resumen dual paciente/doctor
├── doctor.py            # Contraseña + configuración por secciones/edad
├── history.py           # Historial en JSON
└── data/                # session_config.json, section_progress.json, history.json
```

## Nota de seguridad

No pude ejecutar pygame en el entorno donde construí este proyecto (sin
acceso a internet para instalarlo), así que todo fue validado a nivel de
sintaxis y lógica con cuidado, pero te recomiendo que en cuanto lo corras
me digas si algo falla, para ajustarlo de inmediato.
