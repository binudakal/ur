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
    def __init__(self, button, var, num, sensitivity, icon):
        self.button = button
        self.var = var
        self.num = num
        self.defaultIcon = icon
        self.currentIcon = None
        self.currentImage = None

class gameDice():
    def __init__(self, button, label):
        self.button = button
        self.label = label
        self.image = ""

    def update_dice(self, diceroll):
        self.label.set_text(str(diceroll))

    def dice_click(self, button, game):
        game.get_other_player().dice.label.set_text("")
        game.currentPlayer.dice.button.set_sensitive(False)

        game.play_turn(game.roll_dice())




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


    whiteButton = Gtk.Template.Child()
    whiteLabel = Gtk.Template.Child()
    blackButton = Gtk.Template.Child()
    blackLabel = Gtk.Template.Child()

    # diceButton = Gtk.Template.Child()
    # diceText = Gtk.Template.Child()
    # titleText = Gtk.Template.Child()
    # pileText = Gtk.Template.Child()
    # boardText = Gtk.Template.Child()

    # TODO: Dynamically store tile widgets
    # ....


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("Ur")
        self.app = self.get_application()
        self.button_manager = ButtonManager(self)

        self.dice = [gameDice(self.whiteButton, self.whiteLabel), gameDice(self.blackButton, self.blackLabel)]
        self.activeTile = None
        self.activeDice = None

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

        # Create tiles
        self.allTiles = []
        for attr in dir(UrWindow):
            if "Tile" in attr:
                position = int(attr[1:].replace("Tile", ""))
                icon = "starred-symbolic" if position in [4, 8, 14] else ""
                self.allTiles.append(gameTile(getattr(self, attr), attr, int(position), False, icon))

        # Set CSS for tiles
        for tile in filter(lambda x: "Tile0" not in x.var and "Tile15" not in x.var, self.allTiles):
            tile.button.set_icon_name(tile.defaultIcon)
            tile.button.set_css_classes(['tile'])

        # Create a game instance
        self.game = Game(self.app, self)

        # Connect button handlers
        for tile in self.allTiles:
            tile.button.connect("clicked", self.tile_click, tile)
        self.whiteButton.connect("clicked", self.dice[0].dice_click, self.game)
        self.blackButton.connect("clicked", self.dice[1].dice_click, self.game)


    def set_sensitivity(self, button_id, sensitivity):
        button = getattr(self, f'{button_id}')
        button.set_sensitive(sensitivity)


    # def update_dice(self, player, diceroll):
        # self.titleText.set_text(f"{player.name}'s turn")
        # self.diceText.set_text(f"{player.name} rolled a {diceroll}")
    #     player.dice.label.set_text(str(diceroll))


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


        # Set the movable tile's image to either black or white tile depending on the side of the owner of the piece on it
        for piece, tile in zip(self.movablePieces, self.movableTiles):
            pieceSide = piece.owner.side
            if pieceSide == "L":
                counterImage = Gtk.Image.new_from_file("/app/share/icons/hicolor/symbolic/apps/white_counter.svg")
            elif pieceSide == "R":
                counterImage = Gtk.Image.new_from_file("/app/share/icons/hicolor/symbolic/apps/black_counter.svg")
            tile.currentImage = counterImage


    def show_potential(self):
        if self.activeTile.var in self.movableTileMap.keys():
            self.set_sensitivity(self.movableTileMap[self.activeTile.var], True)


    def hide_potential(self):
        self.set_sensitivity(self.movableTileMap[self.activeTile.var], False)


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

        if self.previousTile.num != 0:
            self.previousTile.button.set_child(None)
            self.previousTile.button.set_icon_name(self.previousTile.defaultIcon)

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
            self.game.currentPlayer.dice.button.set_sensitive(True)
            self.clean_board()
            self.game.make_move(self.activeTile.num)
            self.update_icons()









