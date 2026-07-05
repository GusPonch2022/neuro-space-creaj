"""
screen_manager.py
Administrador de pantallas de CREA-J.
"""

HOME = "HOME"
PATIENT = "PATIENT"
SENSORS = "SENSORS"
ANALYSIS = "ANALYSIS"
HISTORY = "HISTORY"
SETTINGS = "SETTINGS"
DOCTOR = "DOCTOR"   


class ScreenManager:

    def __init__(self):
        self.current_screen = HOME

    def set_screen(self, screen):

        if screen in (
            HOME,
            PATIENT,
            SENSORS,
            ANALYSIS,
            HISTORY,
            SETTINGS,
            DOCTOR,
        ):
            self.current_screen = screen

    def get_screen(self):
        return self.current_screen