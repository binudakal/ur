# start_window.py
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


from gi.repository import Gtk, Gdk, Adw, Gio
from .game_window import GameWindow
from .constants import Constants

@Gtk.Template(resource_path='/com/github/binudakal/ur/start_window.ui')
class StartWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'StartWindow'

    newGame = Gtk.Template.Child()
    pieceSelect = Gtk.Template.Child()
    orientToggle = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = self.get_application()

        self.newGame.connect("clicked", self.start_new_game)
        self.pieceSelect.connect("value-changed", self.set_num_pieces)
        self.orientToggle.connect("notify::active", self.set_orientation)

    def start_new_game(self, button):
        self.app.win = GameWindow(application=self.app)

        self.hide()
        self.app.win.present()

    def set_num_pieces(self, spinButton):
        Constants.NUM_PIECES = int(spinButton.get_adjustment().get_value())

    def set_orientation(self, toggle, state):
        Constants.ORIENTATION = toggle.get_active_name()












