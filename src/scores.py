# scores.py
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

UI_PATH = '/com/github/binudakal/ur/'
SETTINGS_SCHEMA = 'com.github.binudakal.ur'


@Gtk.Template(resource_path=UI_PATH + 'scores.ui')
class UrScoresDialog(Adw.Dialog):
    __gtype_name__ = 'UrScoresDialog'

    def __init__(self, parent, **kwargs):
        super().__init__(**kwargs)

        self.parent = parent

        # Load CSS
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path('/app/share/ur/ur/main.css')
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

