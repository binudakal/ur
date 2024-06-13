# window.py
#
# Copyright 2024 Binuda Kalugalage
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

from gi.repository import Gtk, Adw

@Gtk.Template(resource_path='/com/github/binudakal/gnomeur/window.ui')
class GnomeUrWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'GnomeUrWindow'

    leftTile1 = Gtk.Template.Child()
    leftTile2 = Gtk.Template.Child()
    leftTile3 = Gtk.Template.Child()
    leftTile4 = Gtk.Template.Child()
    rightTile1 = Gtk.Template.Child()
    rightTile2 = Gtk.Template.Child()
    rightTile3 = Gtk.Template.Child()
    rightTile4 = Gtk.Template.Child()
    commonTile5 = Gtk.Template.Child()
    commonTile6 = Gtk.Template.Child()
    commonTile7 = Gtk.Template.Child()
    commonTile8 = Gtk.Template.Child()
    commonTile9 = Gtk.Template.Child()
    commonTile10 = Gtk.Template.Child()
    commonTile11 = Gtk.Template.Child()
    commonTile12 = Gtk.Template.Child()
    leftTile13 = Gtk.Template.Child()
    leftTile14 = Gtk.Template.Child()
    rightTile13 = Gtk.Template.Child()
    rightTile14 = Gtk.Template.Child()

    # enableButtons = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.enableButtons.connect("clicked", self.on_clicked)

    def set_sensitivity(self, button_id, sensitivity):
        """Set the sensitivity of a button by its ID."""
        button = getattr(self, f'{button_id}')

        if button:
            button.set_sensitive(sensitivity)


    # def on_clicked(self, button):
    #     self.set_sensitivity("commonTile7", True)

