"""
screens/sensors.py — Pantalla de comprobación de sensores.

Actualmente permite:
- Probar el oxímetro MAX30102.
- Mostrar BPM y SpO2.
- Mostrar estado de conexión.
- Mostrar el puerto COM detectado.
- Actualizar manual o automáticamente.
- Reconectar el sensor.
- Guardar una medición en el historial.
"""

import pygame

import history
from hud import (
    CYAN,
    GREEN,
    AMBER,
    RED,
    TEXT,
    TEXT_DIM,
    draw_button,
)


def show_oximeter_screen(engine):
    resultado = {
        "salir": False,
    }

    datos = {
        "snapshot": engine.bio.snapshot(),
    }

    mensaje = {
        "texto": "",
        "color": GREEN,
        "tiempo": 0,
    }

    ultimo_update = pygame.time.get_ticks()

    # Actualización automática cada 2 segundos
    intervalo_actualizacion = 2000

    # Botones
    volver_rect = pygame.Rect(
        60,
        engine.height - 90,
        220,
        50,
    )

    actualizar_rect = pygame.Rect(
        310,
        engine.height - 90,
        220,
        50,
    )

    reconectar_rect = pygame.Rect(
        560,
        engine.height - 90,
        220,
        50,
    )

    guardar_rect = pygame.Rect(
        810,
        engine.height - 90,
        240,
        50,
    )

    def mostrar_mensaje(
        texto,
        color=GREEN,
    ):
        mensaje["texto"] = texto
        mensaje["color"] = color
        mensaje["tiempo"] = pygame.time.get_ticks()

    def actualizar_medicion():
        datos["snapshot"] = engine.bio.snapshot()

    def guardar_medicion():
        snapshot = datos["snapshot"]

        try:
            history.add_sensor_measurement(
                "Paciente",
                snapshot,
            )

            mostrar_mensaje(
                "MEDICIÓN GUARDADA CORRECTAMENTE",
                GREEN,
            )

            print(
                "✅ Medición del oxímetro "
                "guardada en el historial."
            )

        except Exception as error:
            mostrar_mensaje(
                "ERROR AL GUARDAR LA MEDICIÓN",
                RED,
            )

            print(
                "⚠️ Error guardando la medición:",
                error,
            )

    def reconectar_sensor():
        conectado = engine.bio.reconectar()

        actualizar_medicion()

        if conectado:
            mostrar_mensaje(
                "MAX30102 CONECTADO CORRECTAMENTE",
                GREEN,
            )

        else:
            mostrar_mensaje(
                "NO SE ENCONTRÓ EL MAX30102",
                AMBER,
            )

    def eventos(event):
        if (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
        ):
            if volver_rect.collidepoint(event.pos):
                resultado["salir"] = True

            elif actualizar_rect.collidepoint(event.pos):
                actualizar_medicion()

                mostrar_mensaje(
                    "MEDICIÓN ACTUALIZADA",
                    CYAN,
                )

            elif reconectar_rect.collidepoint(event.pos):
                reconectar_sensor()

            elif guardar_rect.collidepoint(event.pos):
                guardar_medicion()

    def dibujar_panel(
        surface,
        rect,
        titulo,
        valor,
        unidad,
        color,
        descripcion,
    ):
        pygame.draw.rect(
            surface,
            (10, 18, 22),
            rect,
            border_radius=12,
        )

        pygame.draw.rect(
            surface,
            CYAN,
            rect,
            width=1,
            border_radius=12,
        )

        titulo_text = engine.font_med.render(
            titulo,
            True,
            TEXT_DIM,
        )

        valor_completo = (
            f"{valor} {unidad}"
            if unidad
            else str(valor)
        )

        valor_text = engine.font_big.render(
            valor_completo,
            True,
            color,
        )

        descripcion_text = engine.font_med.render(
            descripcion,
            True,
            color,
        )

        surface.blit(
            titulo_text,
            (
                rect.centerx
                - titulo_text.get_width() // 2,
                rect.top + 25,
            ),
        )

        surface.blit(
            valor_text,
            (
                rect.centerx
                - valor_text.get_width() // 2,
                rect.top + 75,
            ),
        )

        surface.blit(
            descripcion_text,
            (
                rect.centerx
                - descripcion_text.get_width() // 2,
                rect.bottom - 40,
            ),
        )

    def color_segun_estado(level):
        if level == "normal":
            return GREEN

        if level == "warning":
            return AMBER

        return RED

    def dibujar(surface):
        nonlocal ultimo_update

        ahora = pygame.time.get_ticks()

        # Actualización automática
        if (
            ahora - ultimo_update
            >= intervalo_actualizacion
        ):
            actualizar_medicion()
            ultimo_update = ahora

        snapshot = datos["snapshot"]

        bpm = snapshot.get("bpm", "--")
        spo2 = snapshot.get("spo2", "--")

        conectado = snapshot.get(
            "oximeter_connected",
            False,
        )

        simulado = snapshot.get(
            "simulated",
            True,
        )

        puerto = snapshot.get(
            "port",
            None,
        )

        bpm_status = snapshot.get(
            "bpm_status",
            {
                "text": "SIN DATOS",
                "level": "warning",
            },
        )

        spo2_status = snapshot.get(
            "spo2_status",
            {
                "text": "SIN DATOS",
                "level": "warning",
            },
        )

        # Título
        titulo = engine.font_big.render(
            "MÓDULO DE SENSORES",
            True,
            TEXT,
        )

        surface.blit(
            titulo,
            (60, 45),
        )

        subtitulo = engine.font_med.render(
            "Prueba individual del oxímetro MAX30102",
            True,
            TEXT_DIM,
        )

        surface.blit(
            subtitulo,
            (60, 100),
        )

        # Estado de conexión
        conexion_panel = pygame.Rect(
            60,
            145,
            engine.width - 120,
            90,
        )

        pygame.draw.rect(
            surface,
            (10, 18, 22),
            conexion_panel,
            border_radius=12,
        )

        pygame.draw.rect(
            surface,
            GREEN if conectado else AMBER,
            conexion_panel,
            width=2,
            border_radius=12,
        )

        if conectado:
            conexion_texto = (
                "MAX30102 CONECTADO"
            )

            conexion_color = GREEN

            detalle_conexion = (
                f"Puerto activo: {puerto}"
            )

        else:
            conexion_texto = (
                "MAX30102 NO CONECTADO"
            )

            conexion_color = AMBER

            detalle_conexion = (
                "El sistema está utilizando datos simulados"
            )

        conexion_label = engine.font_med.render(
            conexion_texto,
            True,
            conexion_color,
        )

        detalle_label = engine.font_med.render(
            detalle_conexion,
            True,
            TEXT_DIM,
        )

        surface.blit(
            conexion_label,
            (
                conexion_panel.left + 25,
                conexion_panel.top + 18,
            ),
        )

        surface.blit(
            detalle_label,
            (
                conexion_panel.left + 25,
                conexion_panel.top + 52,
            ),
        )

        # Indicador de modo
        modo_texto = (
            "DATOS REALES"
            if conectado and not simulado
            else "MODO SIMULADO"
        )

        modo_color = (
            GREEN
            if conectado and not simulado
            else AMBER
        )

        modo_label = engine.font_med.render(
            modo_texto,
            True,
            modo_color,
        )

        surface.blit(
            modo_label,
            (
                conexion_panel.right
                - modo_label.get_width()
                - 25,
                conexion_panel.centery
                - modo_label.get_height() // 2,
            ),
        )

        # Paneles principales
        panel_bpm = pygame.Rect(
            60,
            275,
            470,
            230,
        )

        panel_spo2 = pygame.Rect(
            570,
            275,
            470,
            230,
        )

        dibujar_panel(
            surface=surface,
            rect=panel_bpm,
            titulo="RITMO CARDÍACO",
            valor=bpm,
            unidad="BPM",
            color=color_segun_estado(
                bpm_status["level"]
            ),
            descripcion=bpm_status["text"],
        )

        dibujar_panel(
            surface=surface,
            rect=panel_spo2,
            titulo="SATURACIÓN DE OXÍGENO",
            valor=spo2,
            unidad="%",
            color=color_segun_estado(
                spo2_status["level"]
            ),
            descripcion=spo2_status["text"],
        )

        # Información adicional
        info_y = 535

        actualizacion_text = engine.font_med.render(
            "Actualización automática: cada 2 segundos",
            True,
            TEXT_DIM,
        )

        surface.blit(
            actualizacion_text,
            (60, info_y),
        )

        fecha_medicion = snapshot.get(
            "timestamp",
            "Sin registro",
        )

        fecha_text = engine.font_med.render(
            f"Última medición: {fecha_medicion}",
            True,
            TEXT_DIM,
        )

        surface.blit(
            fecha_text,
            (60, info_y + 30),
        )

        advertencia = engine.font_med.render(
            (
                "Resultados orientativos. "
                "Este sistema no sustituye una evaluación médica."
            ),
            True,
            AMBER,
        )

        surface.blit(
            advertencia,
            (60, info_y + 65),
        )

        # Mensaje temporal
        if mensaje["texto"]:
            tiempo_transcurrido = (
                ahora - mensaje["tiempo"]
            )

            if tiempo_transcurrido <= 2500:
                mensaje_text = engine.font_med.render(
                    mensaje["texto"],
                    True,
                    mensaje["color"],
                )

                surface.blit(
                    mensaje_text,
                    (
                        60,
                        engine.height - 135,
                    ),
                )

            else:
                mensaje["texto"] = ""

        # Botones
        mouse = pygame.mouse.get_pos()

        draw_button(
            surface,
            volver_rect,
            "VOLVER AL INICIO",
            engine.font_med,
            color=CYAN,
            bg_hover=volver_rect.collidepoint(
                mouse
            ),
        )

        draw_button(
            surface,
            actualizar_rect,
            "PROBAR SENSOR",
            engine.font_med,
            color=CYAN,
            bg_hover=actualizar_rect.collidepoint(
                mouse
            ),
        )

        draw_button(
            surface,
            reconectar_rect,
            "RECONECTAR",
            engine.font_med,
            color=AMBER,
            bg_hover=reconectar_rect.collidepoint(
                mouse
            ),
        )

        draw_button(
            surface,
            guardar_rect,
            "GUARDAR MEDICIÓN",
            engine.font_med,
            color=GREEN,
            bg_hover=guardar_rect.collidepoint(
                mouse
            ),
        )

    engine.run_until(
        lambda: resultado["salir"],
        eventos,
        dibujar,
        with_console=False,
        with_gauges=False,
    
    )