# game_window.py
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
from .game import *
from .settings import Settings

class GameTile():
    def __init__(self, button, var, location):

        self.button = button
        self.var = var
        self.location = location

        self.side = var[0]

        self.defaultImage = None
        self.currentImage = None

        self.images = {
            self.location in (4, 8, 14): "4-8-14",
            self.location in (1, 3, 11): "1-3-11",
            self.location in (2, 6, 9, 12): "2-6-9-12",
            self.location in (7, 10): "7-10",
            self.location == 5: "5",
            self.location == 13: "13",
            self.location == 15: "15",
            self.location == 0: None
        }

        # Set image to button's child
        if self.images[True]:
            self.defaultImage = Gtk.Image.new_from_file(f"/app/share/icons/hicolor/symbolic/tiles/{self.images[True]}.svg")
            self.button.set_child(self.defaultImage)

        # Set CSS to tile's button
        if self.location not in (0, 15):
            self.button.set_css_classes(['tile'])

    def update_tile(self, tile, piece):
        tile.button.set_sensitive(True)
        tile.set_image(piece.owner.side)
        tile.nextTile = self.get_tile_by_position(piece.position)

    def set_image(self, image):
        if self.location not in (0, 15):
            self.button.set_child(image)


    def __str__(self):
        return (f"GameTile(var={self.var}, location={self.location}, "
                f"side={self.side}, nextTile={self.nextTile})")


class GameWindow(Adw.ApplicationWindow):
    __gtype_name__ = "GameWindow"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = self.get_application()

        self.load_ui()

        self.connect("close-request", self.on_game_close)

        # Get dice buttons and labels
        self.whiteButton = self.builder.get_object("whiteButton")
        self.whiteRoll = self.builder.get_object("whiteRoll")
        self.whitePieces = self.builder.get_object("whitePieces")
        self.blackButton = self.builder.get_object("blackButton")
        self.blackRoll = self.builder.get_object("blackRoll")
        self.blackPieces = self.builder.get_object("blackPieces")

        # Connect return and reset buttons
        self.builder.get_object("returnMenu").connect("clicked", self.app.on_return)

        # Create a game instance
        self.game = UrGame(self)

        # Create tiles
        self.allTiles = []
        for i in list(range(0, 5)) + list(range(5, 13)) + list(range(13, 16)):
            for side in ("C") if i in range(5, 13) else ("L", "R"):
                # Create the current tile
                currentTile = GameTile(self.builder.get_object(f"{side}Tile{i}"), f"{side}Tile{i}", i)
                # Connect button handlers
                currentTile.button.connect("clicked", self.tile_click, currentTile)
                self.allTiles.append(currentTile)  # Append to list of allTiles

        self.activeTile = None
        self.inactiveTile = None

    def on_game_close(self, window):
        self.app.quit()
        return False

    def load_ui(self):
        # Initialise builder
        self.builder = Gtk.Builder()
        # Load horizontal/vertical UI file
        self.builder.add_from_resource(f"/com/github/binudakal/ur/{"horizontal" if Settings.is_horizontal() else "vertical"}_game.ui")

        # Get game window's content from builder
        builderWindow = self.builder.get_object(self.__gtype_name__)

        # Transfer content to this window
        windowContent = builderWindow.get_content()
        builderWindow.set_content(None)
        self.set_content(windowContent)

        # Load CSS
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path('/app/share/ur/ur/main.css')
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )


    def load_movable(self, movablePieces):

        def get_tile_by_var(var):
            return next((tile for tile in self.allTiles if tile.var == var), None)

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

                    tile.currentImage = Gtk.Image.new_from_file(f"/app/share/icons/hicolor/symbolic/{"white" if piece.owner.side == "L" else "black" }_counter.svg")

    def update_images(self):
        # Restore the inactive tile's default image
        self.inactiveTile.set_image(self.inactiveTile.defaultImage)

        # Update the current tile's button image
        self.activeTile.set_image(self.inactiveTile.currentImage)

    def disable_board(self):
        # Disable and deactivate all buttons
        for tile in self.allTiles:
            tile.button.set_active(False)
            tile.button.set_sensitive(False)

    def tile_click(self, clickedButton, clickedTile):
        # Set active and inactive tiles
        if self.activeTile:
            self.inactiveTile = self.activeTile
        self.activeTile = clickedTile

        # Clicking a tile from which a piece can be moved
        if self.activeTile.nextTile:

            # Automatically hide other sensitive buttons if already active
            if self.inactiveTile:
                if self.inactiveTile != self.activeTile:
                    if self.inactiveTile.button.get_active():
                        self.inactiveTile.button.set_active(False)
                        self.inactiveTile.nextTile.button.set_sensitive(False)

            if clickedButton.get_active():
                self.activeTile.nextTile.button.set_sensitive(True)
            else:
                self.activeTile.nextTile.button.set_sensitive(False)

        # Clicking a tile which a piece can be moved to
        elif self.activeTile == self.inactiveTile.nextTile:

            # Make the move
            self.game.make_move(self.inactiveTile)

            # Enable the next player's dice
            self.game.currentPlayer.dice.button.set_sensitive(True)

            # Update the icons and then disable the board for the next diceroll
            self.update_images()
            self.disable_board()















