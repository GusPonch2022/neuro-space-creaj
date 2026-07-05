from engine import Engine
from menu import show_main_menu

from screens.welcome import show_welcome_screen
from screens.jarvis_intro import show_jarvis_intro_screen
from screens.patient import show_patient_screen
from screens.sensors import show_sensors_screen
from screens.analysis import show_analysis_screen
from screens.history import show_history_screen
from screens.settings import show_settings_screen

from doctor import prompt_password, run_doctor_config

from screen_manager import (
    ScreenManager,
    HOME,
    PATIENT,
    SENSORS,
    ANALYSIS,
    HISTORY,
    SETTINGS,
    DOCTOR,
)


class App:

    def __init__(self):
        self.engine = Engine()
        self.manager = ScreenManager()

    def run(self):
        show_welcome_screen(self.engine)

        while True:

            screen = self.manager.get_screen()

            if screen == HOME:
                opcion = show_main_menu(self.engine)
                self.manager.set_screen(opcion)

            elif screen == PATIENT:
                result = show_jarvis_intro_screen(self.engine)

                if result == "START_EVALUATION":
                    show_patient_screen(self.engine)

                self.manager.set_screen(HOME)

            elif screen == SENSORS:
                show_sensors_screen(self.engine)
                self.manager.set_screen(HOME)

            elif screen == ANALYSIS:
                show_analysis_screen(self.engine)
                self.manager.set_screen(HOME)

            elif screen == HISTORY:
                show_history_screen(self.engine)
                self.manager.set_screen(HOME)

            elif screen == SETTINGS:
                show_settings_screen(self.engine)
                self.manager.set_screen(HOME)

            elif screen == DOCTOR:
                acceso_correcto = prompt_password(self.engine)

                if acceso_correcto:
                    run_doctor_config(self.engine)

                self.manager.set_screen(HOME)