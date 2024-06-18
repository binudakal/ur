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

from gi.repository import Gtk, Gdk, Adw

class gameTile():
    def __init__(self, button, var, sensitivity, icon):
        self.button = button
        self.var = var
        self.sensitive = sensitivity
        self.defaultIcon = icon
        self.currentIcon = None
        self.clicked = False


@Gtk.Template(resource_path='/com/github/binudakal/gnomeur/window.ui')
class GnomeUrWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'GnomeUrWindow'

    css_provider = Gtk.CssProvider()
    css_provider.load_from_path('main.css')
    Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    LTile0 = Gtk.Template.Child()
    LTile1 = Gtk.Template.Child()
    LTile2 = Gtk.Template.Child()
    LTile3 = Gtk.Template.Child()
    LTile4 = Gtk.Template.Child()
    RTile0 = Gtk.Template.Child()
    RTile1 = Gtk.Template.Child()
    RTile2 = Gtk.Template.Child()
    RTile3 = Gtk.Template.Child()
    RTile4 = Gtk.Template.Child()
    CTile5 = Gtk.Template.Child()
    CTile6 = Gtk.Template.Child()
    CTile7 = Gtk.Template.Child()
    CTile8 = Gtk.Template.Child()
    CTile9 = Gtk.Template.Child()
    CTile10 = Gtk.Template.Child()
    CTile11 = Gtk.Template.Child()
    CTile12 = Gtk.Template.Child()
    LTile13 = Gtk.Template.Child()
    LTile14 = Gtk.Template.Child()
    RTile13 = Gtk.Template.Child()
    RTile14 = Gtk.Template.Child()



    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.allTiles = []

        for attr in dir(GnomeUrWindow):
            if "Tile" in attr:
                position = int(attr[1:].replace("Tile", ""))
                icon = "view-grid-symbolic" if position in [4, 8, 14] else ""
                self.allTiles.append(gameTile(getattr(self, attr), attr, False, icon))

        for tile in self.allTiles:
            tile.button.set_icon_name(tile.defaultIcon)
            tile.button.connect("clicked", self.on_click, tile)

    def set_sensitivity(self, button_id, sensitivity):
        button = getattr(self, f'{button_id}')

        button.set_sensitive(sensitivity)

    def load_movable(self, movablePieces):

        def movable(x):
            tilePos = int(x.var[1:].replace("Tile", ""))
            tileSide = x.var[:1]
            temp = [piece.side for piece in list(movablePieces.keys())]

            return tilePos in list(movablePieces.values()) and tileSide in temp

        # movable = lambda x: int(x.var[1:].replace("Tile", "")) in list(movablePieces.values()) and x.var[:1] in list(movablePieces.keys())
        self.movableTiles = filter(movable, self.allTiles)

        for tile in self.movableTiles:
            print("eigwg", tile.var)


    def on_click(self, clickedButton, clickedTile):
        print(self.movableTiles)

        self.activeTile = clickedTile
        self.activeButton = self.activeTile.button

        focusIcon = "audio-volume-muted-symbolic"
        clickedTile.button.set_icon_name(focusIcon)

        # if the button has not already been clicked:
        if not self.activeTile.clicked:
            print("toggled")
            # go through each other unfocused tile and reset their icons + disable them
            for tile in self.allTiles:
                if tile.button != self.activeButton:

                        if tile.currentIcon != None:
                            tile.button.set_icon_name(tile.currentIcon)
                        else:
                            tile.button.set_icon_name(tile.defaultIcon)

                        self.set_sensitivity(tile.var, False)

            # toggle
            self.activeTile.clicked = True
        else:
            print("untoggled")
            for tile in self.movableTiles:
                print(tile)

        # go through each other unfocused tile and reset their icons + disable them
            for tile in self.allTiles:

                # reset icons
                if tile.currentIcon != None:
                    tile.button.set_icon_name(tile.currentIcon)
                else:
                    tile.button.set_icon_name(tile.defaultIcon)

                # enable the button once again if it is a movable one
                if tile in self.movableTiles:
                    self.set_sensitivity(tile.var, True)

            # untoggle
            self.activeTile.clicked = False




        # movablePlaces = []
        # if self.activeButton.position in movablePlaces:

        # self.show_moves()



