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
from .game import *

class gameTile():
    def __init__(self, button, var, sensitivity, icon):
        self.button = button
        self.var = var
        self.sensitive = sensitivity
        self.defaultIcon = icon
        self.currentIcon = None
        self.toggled = False

class ButtonManager:
    def __init__(self, win):
        self.win = win

    def disable_all_buttons(self):
        """Disable all buttons."""
        button_ids = [
            "LTile1", "LTile2", "LTile3", "LTile4", "LTile13", "LTile14",
            "CTile5", "CTile6", "CTile7", "CTile8", "CTile9", "CTile10", "CTile11", "CTile12",
            "RTile1", "RTile2", "RTile3", "RTile4", "RTile13", "RTile14"
        ]
        for button_id in button_ids:
            self.win.set_sensitivity(button_id, False)


@Gtk.Template(resource_path='/com/github/binudakal/gnomeur/window.ui')
class GnomeUrWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'GnomeUrWindow'

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

    diceText = Gtk.Template.Child()
    diceButton = Gtk.Template.Child()
    titleText = Gtk.Template.Child()
    pileText = Gtk.Template.Child()



    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.app = self.get_application()
        self.button_manager = ButtonManager(self)

        self.activeTile = None

        css_provider = Gtk.CssProvider()

        css_provider.load_from_path('/app/share/gnome-ur/gnome_ur/main.css')
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        self.allTiles = []

        for attr in dir(GnomeUrWindow):
            if "Tile" in attr:
                position = int(attr[1:].replace("Tile", ""))
                icon = "view-grid-symbolic" if position in [4, 8, 14] else ""
                self.allTiles.append(gameTile(getattr(self, attr), attr, False, icon))

        for tile in self.allTiles:
            tile.button.set_icon_name(tile.defaultIcon)
            tile.button.set_css_classes(['tile'])
            tile.button.connect("clicked", self.tile_click, tile)

        self.diceButton.connect("clicked", self.dice_click)


        self.game = Game(self.app, self)
        # self.game.play_game()




    def set_sensitivity(self, button_id, sensitivity):
        button = getattr(self, f'{button_id}')
        button.set_sensitive(sensitivity)

    def show_movable(self):
        pass

    def update_text(self, playerName, diceroll):
        self.titleText.set_text(f"{playerName}'s turn")
        self.diceText.set_text(f"{playerName} rolled a {diceroll}.")
        self.pileText.set_text(f"Player 1's pile:  L1, L2, L3, L4, L5\nPlayer 2's pile:  R1, R2, R3, R4, R5")

    def load_movable(self, movablePieces):

        def find_movable(x):
            tilePos = int(x.var[1:].replace("Tile", ""))
            tileSide = x.var[:1]

            pieceSides = [piece.side for piece in list(movablePieces.keys())]
            piecePositions = [piece.position for piece in list(movablePieces.keys())]

            return tileSide in pieceSides and tilePos in piecePositions

        # filter all the tiles on the board to find the movable ones
        self.movableTiles = filter(find_movable, self.allTiles)

        # for tile in self.movableTiles:
        #     print(tile.var)

    def await_move(self):
        # while not self.activeTile:
        #     print("1")
        pass

    def dice_click(self, clickedButton):
        # print(self.game.roll_dice())
        self.game.play_game(self.game.roll_dice())

    def tile_click(self, clickedButton, clickedTile):
        print(clickedButton.get_active())
        # focusIcon = "audio-volume-muted-symbolic"
        # clickedTile.button.set_icon_name(focusIcon)

        # if the button has not already been clicked:
        if clickedButton.get_active():
            self.activeTile = clickedTile # toggle

            print("toggled")
            # go through each other unfocused tile and reset their icons + disable them
            for tile in self.allTiles:
                if tile.button != self.activeTile.button:

                        if tile.currentIcon != None:
                            tile.button.set_icon_name(tile.currentIcon)
                        else:
                            tile.button.set_icon_name(tile.defaultIcon)

                        tile.button.set_active(False)
                        self.set_sensitivity(tile.var, False)


        else:
            print("untoggled")

            for tile in self.allTiles:
                # reset icons
                if tile.currentIcon != None:
                    tile.button.set_icon_name(tile.currentIcon)
                else:
                    tile.button.set_icon_name(tile.defaultIcon)

                # enable the button once again if it is a movable one
                if tile in self.movableTiles:
                    print(tile)
                    self.set_sensitivity(tile.var, True)

            self.activeTile = None # untoggle






