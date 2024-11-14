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
    def __init__(self, button, var, location, sensitivity, image):
        self.var = var
        self.location = location
        self.side = var[:1]

        self.button = button
        self.defaultImage = image
        self.currentImage = None
        self.defaultIcon = ""

        self.movable = None


    def update_image(self, image):
        if not image:
            self.button.set_icon_name(self.defaultIcon)
        else:
            self.button.set_child(image)

    def __str__(self):
        return (f"GameTile(var={self.var}, location={self.location}, "
                f"side={self.side}, movable={self.movable})")


class gameDice():
    def __init__(self, button, label):
        self.button = button
        self.label = label
        self.image = ""

    def update_dice(self, diceroll):
        self.label.set_visible(True)
        self.label.set_text(str(diceroll))

    def dice_click(self, button, dice, win):
        if win.activeDice:
            win.previousDice = win.activeDice

        win.activeDice = dice
        win.game.get_other_player().dice.label.set_text("")
        win.game.get_other_player().dice.label.set_visible(False)
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

        self.dice = [gameDice(self.whiteButton, self.whiteLabel), gameDice(self.blackButton, self.blackLabel)]
        self.activeTile = None
        self.activeDice = None

        # Create a game instance
        self.game = Game(self.app, self)

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
                rosetteImage = Gtk.Image.new_from_file("/app/share/icons/hicolor/symbolic/apps/rosette.svg")
                image = rosetteImage if position in [4, 8, 14] else None
                self.allTiles.append(gameTile(getattr(self, attr), attr, int(position), False, image))

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
        self.whiteButton.connect("clicked", self.dice[0].dice_click, self.dice[0], self)
        self.blackButton.connect("clicked", self.dice[1].dice_click, self.dice[1], self)


    def set_sensitivity(self, button_id, sensitivity):
        button = getattr(self, f'{button_id}')
        button.set_sensitive(sensitivity)


    def load_movable(self, movablePieces):

        def get_tile_by_var(var_value):
            return next((tile for tile in self.allTiles if tile.var == var_value), None)

        # Make the movable pieces a property of the tile they are on
        for tile in self.allTiles:
            # Reset the movable property
            tile.movable = None

            for piece, pos in movablePieces.items():
                if tile.side == piece.side and tile.location == piece.position:
                    tile.button.set_sensitive(True)

                    if pos <= 4 or 13 <= pos <= 15:
                        tile.movable = get_tile_by_var(f"{piece.owner.side}Tile{pos}")
                    elif 5 <= pos <= 12:
                        tile.movable = get_tile_by_var(f"CTile{pos}")

                    if piece.owner.side == "L":
                        tile.currentImage = Gtk.Image.new_from_file("/app/share/icons/hicolor/symbolic/apps/white_counter.svg")
                    elif piece.owner.side == "R":
                        tile.currentImage = Gtk.Image.new_from_file("/app/share/icons/hicolor/symbolic/apps/black_counter.svg")


    def show_potential(self):
        self.activeTile.movable.button.set_sensitive(True)

    def hide_potential(self):
        self.activeTile.movable.button.set_sensitive(False)

    def disable_board(self):
        # Disable and deactivate all buttons
        for tile in self.allTiles:
            tile.button.set_active(False)
            tile.button.set_sensitive(False)

    def update_icons(self):
        if self.previousTile.location != 0:
            # Restore the previous tile's default image/set empty icon
            self.previousTile.update_image(self.previousTile.defaultImage)

        # Update the current tile's button image
        self.activeTile.update_image(self.previousTile.currentImage)


    def tile_click(self, clickedButton, clickedTile):

        if self.activeTile:
            self.previousTile = self.activeTile

        self.activeTile = clickedTile

        # Clicking a tile from which a piece can be moved
        if self.activeTile.movable:
            if clickedButton.get_active():
                self.show_potential()
            else:
                self.hide_potential()

        # Clicking a tile which a piece can be moved to
        elif self.activeTile == self.previousTile.movable:

            # Enable the other player's dice
            self.game.currentPlayer.dice.button.set_sensitive(True)

            # Update the icons and then disable the board for the next diceroll
            self.update_icons()
            self.disable_board()

            # Make the next move
            self.game.make_move(self.activeTile.location)










