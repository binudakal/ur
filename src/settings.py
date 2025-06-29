from gi.repository import Gio

SETTINGS_SCHEMA = "io.github.binudakal.ur"

class Settings:
    _settings = Gio.Settings.new(SETTINGS_SCHEMA)

    @classmethod
    def is_horizontal(cls) -> bool:
        return cls._settings.get_boolean("horizontal")

    @classmethod
    def set_orientation(cls, orientation):
        cls._settings.set_boolean("horizontal", orientation == "horizontal")

    @classmethod
    def get_num_pieces(cls) -> int:
        return cls._settings.get_int("num-pieces")

    @classmethod
    def set_num_pieces(cls, val: int):
        cls._settings.set_int("num-pieces", val)



