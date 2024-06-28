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
        for tile in self.win.allTiles:
            self.win.set_sensitivity(tile.var, False)

    def deactivate_all_buttons(self):
        for tile in win.allTiles:
            self.win.set_active(tile.var, False)


@Gtk.Template(resource_path='/com/github/binudakal/ur/window.ui')
class UrWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'UrWindow'

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

        self.movablePieces = None
        self.movableTileMap = {}

        # Load CSS
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path('/app/share/ur/ur/main.css')
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        self.allTiles = []

        for attr in dir(UrWindow):
            if "Tile" in attr:
                position = int(attr[1:].replace("Tile", ""))
                icon = "starred-symbolic" if position in [4, 8, 14] else ""
                self.allTiles.append(gameTile(getattr(self, attr), attr, False, icon))

        for tile in filter(lambda x: "Tile0" not in x.var, self.allTiles):
            tile.button.set_icon_name(tile.defaultIcon)
            tile.button.set_css_classes(['tile'])

        for tile in self.allTiles:
            tile.button.connect("clicked", self.tile_click, tile)

        self.diceButton.connect("clicked", self.dice_click)


        self.game = Game(self.app, self)
        # self.game.play_game()




    def set_sensitivity(self, button_id, sensitivity):
        button = getattr(self, f'{button_id}')
        button.set_sensitive(sensitivity)

    def update_text(self, playerName, diceroll):
        self.titleText.set_text(f"{playerName}'s turn")
        self.diceText.set_text(f"{playerName} rolled a {diceroll}.")
        self.pileText.set_text(f"Player 1's pile:  L1, L2, L3, L4, L5\nPlayer 2's pile:  R1, R2, R3, R4, R5")

    def load_movable(self, movablePieces):
        self.movablePieces = movablePieces
        self.movableTileMap = {}

        def find_movable(x):
            tilePos = int(x.var[1:].replace("Tile", ""))
            tileSide = x.var[:1]

            pieceSides = [piece.side for piece in list(movablePieces.keys())]
            piecePositions = [piece.position for piece in list(movablePieces.keys())]

            return tileSide in pieceSides and tilePos in piecePositions

        # filter all the tiles on the board to find the movable ones
        self.movableTiles = filter(find_movable, self.allTiles)

        for pair in movablePieces.items():
            print(f"{pair[0].side}Tile{pair[0].position}", pair[1])

            if pair[0].position <= 4 or 13 <= pair[0].position <= 14:
                self.set_sensitivity(f"{pair[0].side}Tile{pair[0].position}", True)
            elif 5 <= pair[0].position <= 12:
                self.set_sensitivity(f"CTile{pair[0].position}", True)

            if pair[1] <= 4 or 13 <= pair[1] <= 14:
                if pair[0].position is not None:
                    self.movableTileMap[f"{pair[0].side}Tile{pair[0].position}"] = f"{pair[0].side}Tile{pair[1]}"
                else:
                    self.movableTileMap[f"{pair[0].side}Tile14"] = f"{pair[0].side}Tile{pair[1]}"
            else:
                self.movableTileMap[f"{pair[0].side}Tile{pair[0].position}"] = f"CTile{pair[1]}"

            # create dictionary of movabletiles
            # for tile in self.allTiles:
            #     if f"Tile{}" in tile.var:

            # (lambda x: f"Tile{}" in x.var, self.allTiles)


    def show_potential(self, clickedTile):
        # for pos in self.movablePieces.values():
        #     for tile in self.allTiles:
        #         if str(pos) in tile.var:
        #             tile.button.set_sensitive(True)

        potentialTile = None

        # find the potential tile for the clickedTile
        # (piece, pos)
        # for pair in self.movablePieces.items():
        #     for tile in self.allTiles:
        #         if tile.var == f"{pair[0].side}Tile{pair[1]}":
        #             print(f"{pair[0].side}Tile{pair[0].position}")
                    # if str(pair[1]) in clickedTile.var:
        #             tile.button.set_sensitive(True)

        # for pair in self.movablePieces.items():
        #     print(f"{pair[0].side}Tile{pair[0].position}")



        # create list of movable tile vars
        # for pair in movablePieces.items():
            # print(f"{pair[0].side}Tile{pair[0].position}", pair[1])
        #     print(f"{pair[0].side}Tile{pair[0].position}", pair[1])


        #     if pair[0].position is not None:
        #         movableTileMap[f"{pair[0].side}Tile{pair[0].position}"] = f"{pair[0].side}Tile{pair[1]}"
        #     else:
        #         movableTileMap[f"{pair[0].side}Tile14"] = f"{pair[0].side}Tile{pair[1]}"

        print(self.movableTileMap)

        # for tile in self.allTiles:
        #     if tile.var in movableTileMap.keys():
        #         self.set_sensitivity(movableTileMap[tile.var], True)

        if clickedTile.var in self.movableTileMap.keys():
            self.set_sensitivity(self.movableTileMap[clickedTile.var], True)

        # for tile in self.allTiles:
        #     for pair in self.movablePieces.items():

        #         print(f"{pair[0].side}Tile{pair[0].position}")
                # if the looped tile is the same as one in the movablePieces using new pos (pair[1])
        #         if tile.var == f"{pair[0].side}Tile{pair[1]}":
                    # if the clicked tile is the same as the original piece
        #             print(clickedTile.var, f"{pair[0].side}Tile{pair[0].position}")

        #             if clickedTile.var == f"{pair[0].side}Tile{pair[0].position}":
        #                 print(tile.var)
        #                 tile.button.set_sensitive(True)


        # for pair in self.movablePieces.items():
        #     for tile in self.allTiles:
        #         if tile.var == f"{pair[0].side}Tile{pair[1]}":
        #             tile.button.set_sensitive(True)


    def hide_potential(self):
        # for tile in filter(lambda x: x not in self.movableTiles, self.allTiles):
        #     tile.button.set_active(False)

        for tile in self.allTiles:
            tile.button.set_active(False)



    # def enable_tiles(movablePieces):

    def dice_click(self, clickedButton):
        # print(self.game.roll_dice())
        self.game.play_game(self.game.roll_dice())
        # clickedButton.set_sensitive(False)

    def clean_board(self):
        for tile in self.allTiles:
            tile.button.set_active(False)
        self.button_manager.disable_all_buttons()

    def reset_icon(self, tile):
        if tile.currentIcon != None:
            tile.button.set_icon_name(tile.currentIcon)
        else:
            tile.button.set_icon_name(tile.defaultIcon)

    def tile_click(self, clickedButton, clickedTile):
        # focusIcon = "audio-volume-muted-symbolic"
        # clickedTile.button.set_icon_name(focusIcon)

        # for showing potential tiles
        # if clickedTile == self.activeTile:
        #     if clickedButton.get_active():
        #         self.activeTile = clickedTile # toggle

        # movable piece selected
        # else:














        # if the button has not already been clicked:
        if clickedButton.get_active():
            self.activeTile = clickedTile # toggle

            print("toggled")
            # go through each other unfocused tile and reset their icons + disable them
            # for tile in self.allTiles:
            #     if tile.button != self.activeTile.button:

            #             self.reset_icon(tile)

            #             tile.button.set_active(False)
            #             self.set_sensitivity(tile.var, False)

            self.show_potential(clickedTile)


        else:
            print("untoggled")

            self.hide_potential()

            for tile in self.allTiles:

                self.reset_icon(tile)

                # enable the button once again if it is a movable one
                if tile in self.movableTiles:
                    self.set_sensitivity(tile.var, True)

            # self.activeTile = None # untoggle






