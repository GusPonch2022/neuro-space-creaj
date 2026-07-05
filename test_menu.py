print("1")

import pygame

print("2")

from engine import Engine

print("3")

import menu
from screen_manager import (
    ScreenManager,
    HOME,
    PATIENT,
    SENSORS,
    ANALYSIS,
    HISTORY,
    SETTINGS,
)

print("4")


def main():
    print("5")

    engine = Engine()

    manager = ScreenManager()

    print(manager.get_screen())

    print("6")

    while True:

        opcion = menu.show_main_menu(engine)

        if opcion == "INICIO":
            manager.set_screen(HOME)

        elif opcion == "PACIENTE":
            manager.set_screen(PATIENT)

        elif opcion == "SENSORES":
            manager.set_screen(SENSORS)

        elif opcion == "ANÁLISIS":
            manager.set_screen(ANALYSIS)

        elif opcion == "HISTORIAL":
            manager.set_screen(HISTORY)

        elif opcion == "CONFIGURACIÓN":
            manager.set_screen(SETTINGS)

        print("Pantalla actual:", manager.get_screen())


if __name__ == "__main__":
    print("7")
    main()