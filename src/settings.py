# settings.py
#
# Copyright 2025 Binuda Kalugalage
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

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

    @classmethod
    def get_scores(cls, name: str) -> int:
        return cls._settings.get_int(f"{name.lower()}-wins")

    @classmethod
    def increment_score(cls, name: str) -> None:
        tag = f"{name.lower()}-wins"
        current = cls._settings.get_int(tag)
        cls._settings.set_int(tag, current + 1)

