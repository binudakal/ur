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
    def __init__(self, button, var, location):


        self.side = var[:1]

        self.button = button
        self.var = var
        self.location = location

        self.defaultImage = None
        self.currentImage = None
        self.defaultIcon = ""

        self.nextTile = None

        self.piece = None
        self.images = {
            self.location in (4, 8, 14): "/app/share/icons/hicolor/symbolic/apps/rosette.svg",
            self.location in (1, 3, 11): "/app/share/icons/hicolor/symbolic/apps/1-3-11.svg",
            self.location in (2, 6, 9, 12): "/app/share/icons/hicolor/symbolic/apps/2-6-9-12.svg",
            self.location in (7, 10): "/app/share/icons/hicolor/symbolic/apps/7-10.svg",
            self.location == 5: "/app/share/icons/hicolor/symbolic/apps/5.svg",
            self.location == 13: "/app/share/icons/hicolor/symbolic/apps/13.svg",
            self.location in (0, 15): None
        }

        if self.images[True]:
            self.defaultImage = Gtk.Image.new_from_file(self.images[True])

    def update_tile(self, tile, piece):
        tile.button.set_sensitive(True)
        tile.update_image(piece.owner.side)
        tile.nextTile = self.get_tile_by_position(piece.position)

    def update_image(self, image):
        if self.location != 0:
            if not image:
                self.button.set_icon_name("")
            else:
                self.button.set_child(image)

    def __str__(self):
        return (f"GameTile(var={self.var}, location={self.location}, "
                f"side={self.side}, nextTile={self.nextTile})")


class gameDice():
    def __init__(self, num, button, label):
        self.num = num
        self.button = button
        self.label = label
        self.button.set_child(Gtk.Image.new_from_file("/app/share/icons/hicolor/symbolic/apps/dice.svg"))

        self.nextDice = None

    def update_label(self, diceroll=None):
        if diceroll:
            self.label.set_visible(True)
            self.label.set_text(diceroll)
        else:
            self.label.set_visible(False)

    def dice_click(self, button, win):
        if win.activeDice:
            win.inactiveDice = win.activeDice
        win.activeDice = self


        win.game.otherPlayer.dice.update_label()
        win.game.currentPlayer.dice.update_label()
        win.game.currentPlayer.dice.button.set_sensitive(False)

        win.game.play_turn(win.game.roll_dice())



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

    # TODO: Dynamically store tile widgets
    # ....


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("Ur")
        self.app = self.get_application()

        self.dice = [gameDice(1, self.whiteButton, self.whiteLabel), gameDice(2, self.blackButton, self.blackLabel)]
        self.activeTile = None
        self.activeDice = self.dice[0]


        # Create a game instance
        self.game = Game(self.app, self)

        # Create a toast overlay
        # self.toast_overlay = Adw.ToastOverlay()
        # self.set_child(self.toast_overlay)

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
                self.allTiles.append(gameTile(getattr(self, attr), attr, int(position)))

        # Set CSS for tiles
        regularTiles = filter(lambda x: x.location not in [0, 15], self.allTiles)
        for tile in regularTiles:
            tile.button.set_css_classes(['tile'])
            tile.button.set_icon_name(tile.defaultIcon)
            if tile.defaultImage:
                tile.button.set_child(tile.defaultImage)

        # Connect button handlers
        for tile in self.allTiles:
            tile.button.connect("clicked", self.tile_click, tile)
        self.whiteButton.connect("clicked", self.dice[0].dice_click, self)
        self.blackButton.connect("clicked", self.dice[1].dice_click, self)

    @property
    def inactiveDice(self):
        for dice in self.dice:
                if dice is not self.activeDice:
                    return dice

    @inactiveDice.setter
    def inactiveDice(self, dice):
        self._inactiveDice = dice


    def set_sensitivity(self, button_id, sensitivity):
        button = getattr(self, f'{button_id}')
        button.set_sensitive(sensitivity)


    def load_movable(self, movablePieces):

        def get_tile_by_var(var_value):
            return next((tile for tile in self.allTiles if tile.var == var_value), None)

        # Make the nextTile pieces a property of the tile they are on
        for tile in self.allTiles:
            # Reset the nextTile property
            tile.nextTile = None

            for piece in movablePieces:
                if tile.side == piece.side and tile.location == piece.position:
                    tile.button.set_sensitive(True)
                    tile.piece = piece

                    if piece.nextPos <= 4 or 13 <= piece.nextPos <= 15:
                        tile.nextTile = get_tile_by_var(f"{piece.owner.side}Tile{piece.nextPos}")
                    elif 5 <= piece.nextPos <= 12:
                        tile.nextTile = get_tile_by_var(f"CTile{piece.nextPos}")

                    if piece.owner.side == "L":
                        tile.currentImage = Gtk.Image.new_from_file("/app/share/icons/hicolor/symbolic/apps/white_counter.svg")
                    elif piece.owner.side == "R":
                        tile.currentImage = Gtk.Image.new_from_file("/app/share/icons/hicolor/symbolic/apps/black_counter.svg")


    def disable_board(self):
        # Disable and deactivate all buttons
        for tile in self.allTiles:
            tile.button.set_active(False)
            tile.button.set_sensitive(False)

    def update_icons(self):
        # Restore the inactive tile's default image/set empty icon
        self.inactiveTile.update_image(self.inactiveTile.defaultImage)

        # Update the current tile's button image
        self.activeTile.update_image(self.inactiveTile.currentImage)


    def tile_click(self, clickedButton, clickedTile):
        # Set active and inactive tiles
        if self.activeTile:
            self.inactiveTile = self.activeTile
        self.activeTile = clickedTile

        # Clicking a tile from which a piece can be moved
        if self.activeTile.nextTile:
            if clickedButton.get_active():
                self.activeTile.nextTile.button.set_sensitive(True)
            else:
                self.activeTile.nextTile.button.set_sensitive(False)

        # Clicking a tile which a piece can be moved to
        elif self.activeTile == self.inactiveTile.nextTile:

            # Enable the other player's dice
            self.game.currentPlayer.dice.button.set_sensitive(True)

            # Update the icons and then disable the board for the next diceroll
            self.update_icons()
            self.disable_board()

            # Make the next move
            self.game.make_move(self.inactiveTile)












