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

from gi.repository import Gtk, Gdk, Adw, Gio
from .game import *

class gameTile():
    def __init__(self, button, var, sensitivity, icon):
        self.button = button
        self.var = var
        self.sensitive = sensitivity
        self.defaultIcon = icon
        self.currentIcon = None
        self.toggled = False
        self.currentImage = None


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
    LTile15 = Gtk.Template.Child()
    RTile13 = Gtk.Template.Child()
    RTile14 = Gtk.Template.Child()
    RTile15 = Gtk.Template.Child()

    diceText = Gtk.Template.Child()
    diceButton = Gtk.Template.Child()
    titleText = Gtk.Template.Child()
    pileText = Gtk.Template.Child()


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("Ur")


        self.app = self.get_application()
        self.button_manager = ButtonManager(self)

        self.activeTile = None
        self.clickedTiles = []

        self.movableTileMap = {}
        self.movableTiles = None

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

        for tile in filter(lambda x: "Tile0" not in x.var and "Tile15" not in x.var, self.allTiles):
            tile.button.set_icon_name(tile.defaultIcon)
            tile.button.set_css_classes(['tile'])

        for tile in self.allTiles:
            tile.button.connect("clicked", self.tile_click, tile)

        self.diceButton.connect("clicked", self.dice_click)


        self.game = Game(self.app, self)


    def set_sensitivity(self, button_id, sensitivity):
        button = getattr(self, f'{button_id}')
        button.set_sensitive(sensitivity)


    def update_text(self, playerName, diceroll):
        self.titleText.set_text(f"{playerName}'s turn")
        self.diceText.set_text(f"{playerName} rolled a {diceroll}.")
        # self.pileText.set_text(f"Player 1's pile:  L1, L2, L3, L4, L5\nPlayer 2's pile:  R1, R2, R3, R4, R5")


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
        self.movableTiles = list(filter(find_movable, self.allTiles))

        for key, value in self.movablePieces.items():

            # if the movable piece is on one half of the board
            if key.position <= 4 or 13 <= key.position <= 14:
                self.set_sensitivity(f"{key.side}Tile{key.position}", True)

            # if in common board
            elif 5 <= key.position <= 12:
                self.set_sensitivity(f"CTile{key.position}", True)

            # TODO: make movableTileMap have actual tiles, not their vars
            # create map of movable tiles and the potential new tiles
            if value <= 4 or 13 <= value <= 14:
                self.movableTileMap[f"{key.side}Tile{key.position}"] = f"{key.owner.side}Tile{value}"
            elif 5 <= value <= 12:
                self.movableTileMap[f"{key.side}Tile{key.position}"] = f"CTile{value}"
            elif value == 15:
                self.movableTileMap[f"{key.side}Tile{key.position}"] = f"{key.owner.side}Tile15"



        for piece, tile in zip(self.movablePieces, self.movableTiles):
            pieceSide = piece.owner.side
            if pieceSide == "L":
                counterImage = Gtk.Image.new_from_file("./Documents/Github Repos/ur/data/icons/hicolor/symbolic/white_counter.svg")
            elif pieceSide == "R":
                counterImage = Gtk.Image.new_from_file("./Documents/Github Repos/ur/data/icons/hicolor/symbolic/black_counter.svg")
            tile.currentImage = counterImage
            # tile.button.set_child(tile.currentImage)





    def show_potential(self):
        if self.activeTile.var in self.movableTileMap.keys():
            self.set_sensitivity(self.movableTileMap[self.activeTile.var], True)


    def hide_potential(self):
        self.set_sensitivity(self.movableTileMap[self.activeTile.var], False)
        # self.activeTile.button.set_icon_name('')


    def dice_click(self, clickedButton):
        self.game.play_game(self.game.roll_dice())


    def clean_board(self):
        for tile in self.allTiles:
            tile.button.set_active(False)
        self.button_manager.disable_all_buttons()


    def reset_icon(self, tile):
        if tile.currentIcon:
            tile.button.set_icon_name(tile.currentIcon)
        else:
            tile.button.set_icon_name(tile.defaultIcon)

    def update_icons(self):
        print(f"{self.previousTile.var} --> {self.activeTile.var}")
        # for tile in self.movableTiles:
        #     if tile.var == a or tile.var == b:
        #         print(tile)

        for tile in self.movableTiles:
            print(tile.currentImage)

        if self.previousTile.var[-1] != "0":
            self.previousTile.button.set_child(None)

        self.activeTile.button.set_child(self.previousTile.currentImage)






    def tile_click(self, clickedButton, clickedTile):
        if self.activeTile:
            self.previousTile = self.activeTile

        self.activeTile = clickedTile

        # for clicking a movable tile
        if self.activeTile in self.movableTiles:
            if clickedButton.get_active():
                self.show_potential()
            else:
                self.hide_potential()

        # for clicking a tile to move to
        elif self.activeTile.var in self.movableTileMap.values():
            # print(self.movableTileMap)
            # self.update_icons(list(self.movableTileMap.keys())[list(self.movableTileMap.values()).index(self.activeTile.var)], self.activeTile.var)



            self.game.make_move(int(self.activeTile.var[5:]))
            self.update_icons()
            self.clean_board()







