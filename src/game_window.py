# game_window.py
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
from .constants import Constants


class gameTile():
    def __init__(self, button, var, location):

        self.button = button
        self.var = var
        self.location = location

        self.side = var[:1]

        self.defaultImage = None
        self.currentImage = None

        self.images = {
            self.location in (4, 8, 14): "/app/share/icons/hicolor/symbolic/tiles/rosette.svg",
            self.location in (1, 3, 11): "/app/share/icons/hicolor/symbolic/tiles/1-3-11.svg",
            self.location in (2, 6, 9, 12): "/app/share/icons/hicolor/symbolic/tiles/2-6-9-12.svg",
            self.location in (7, 10): "/app/share/icons/hicolor/symbolic/tiles/7-10.svg",
            self.location == 5: "/app/share/icons/hicolor/symbolic/tiles/5.svg",
            self.location == 13: "/app/share/icons/hicolor/symbolic/tiles/13.svg",
            self.location == 15: "/app/share/icons/hicolor/symbolic/tiles/15.svg",
            self.location == 0: None
        }

        # Set image to button's child
        if self.images[True]:
            self.defaultImage = Gtk.Image.new_from_file(self.images[True])
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
            if not image:
                self.button.set_icon_name("")
            else:
                self.button.set_child(image)

    def __str__(self):
        return (f"GameTile(var={self.var}, location={self.location}, "
                f"side={self.side}, nextTile={self.nextTile})")


@Gtk.Template(resource_path='/com/github/binudakal/ur/game_window.ui')
class GameWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'GameWindow'

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

    returnMenu = Gtk.Template.Child()
    resetGame = Gtk.Template.Child()

    # TODO: Dynamically store tile widgets
    # ....


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = self.get_application()

        self.activeTile = None
        self.inactiveTile = None

        # Create a game instance
        self.game = Game(self)

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
        for attr in dir(GameWindow):
            if "Tile" in attr:
                position = int(attr[1:].replace("Tile", ""))

                # Create the current tile
                currentTile = gameTile(getattr(self, attr), attr, int(position))
                # Connect button handlers
                currentTile.button.connect("clicked", self.tile_click, currentTile)
                self.allTiles.append(currentTile) # append to list of allTiles

                # currentTile.button.set_sensitive(True)


        #
        self.returnMenu.connect("clicked", self.return_menu)
        self.resetGame.connect("clicked", self.reset_game)

    def return_menu(self, button):
        print("return")
        self.app.menuWin.present()

        self.hide()
        self.destroy()

    def reset_game(self, button):
        print("game reset")



    def set_sensitivity(self, button_id, sensitivity):
        button = getattr(self, f'{button_id}')
        button.set_sensitive(sensitivity)


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

                    if piece.owner.side == "L":
                        tile.currentImage = Gtk.Image.new_from_file("/app/share/icons/hicolor/symbolic/white_counter.svg")
                    elif piece.owner.side == "R":
                        tile.currentImage = Gtk.Image.new_from_file("/app/share/icons/hicolor/symbolic/black_counter.svg")

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

        # elif self.activeTile.nextTile:
            # self.inactiveTile.nextTile.button.set_sensitive(False)
        #     print("uhh...")













