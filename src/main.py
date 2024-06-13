# main.py
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

import sys
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Gio, Adw
from .window import GnomeUrWindow

# ur-cli imports
import random
import time

from abc import ABC, abstractmethod


def roll_dice():
    return sum(random.randint(0, 1) for _ in range(4))

pauseTime = 0

boardRosettes = [4, 8, 14]

class Board(ABC):
    def is_occupied(self, position):
        # Return the (occupied status, occupying piece)
        return (self.positions[position] is not None, self.positions[position])

    def add_piece(self, piece, position):
        self.positions[position] = piece
        piece.position = position

    def return_piece(self, piece):
        self.positions[piece.position] = None
        piece.position = 0

    def remove_piece(self, piece):
        self.positions[piece.position] = None
        piece.position = None # to prevent double rosette bug
        piece.owner.pieces.remove(piece)


    @abstractmethod
    def move_piece(self, position, piece):
        pass

class halfBoard(Board):
    def __init__(self):
        self.positions = {i: None for i in range(1, 5)}
        self.positions.update({13: None, 14: None})

    def move_piece(self, piece, position):
        # Update the position dictionaries
        self.return_piece(piece) # remove current piece from its old spot
        self.add_piece(piece, position) # add it to its new spot

class commonBoard(Board):
    def __init__(self):
        self.positions = {i: None for i in range(5, 13)}

    def move_piece(self, piece, position):
        # If the other player's piece is already there,
        if self.is_occupied(position)[0]:
        # Return it to their pile (position = 0)
            print(f"{self.positions[position].owner.side}{self.positions[position].ID} was returned to {self.positions[position].owner.name}'s pile.")
            self.return_piece(self.positions[position])

        # Move the piece to the new spot (after removing old piece above if applicable)
        self.return_piece(piece)
        self.add_piece(piece, position)



class Piece:
    def __init__(self, player, pieceNumber):
        self.owner = player
        self.position = 0
        self.ID = pieceNumber
        self.onCommon = False


class Player:
    def __init__(self, name, side):
        self.name = name
        self.side = side
        self.pieces = [Piece(self, _ + 1) for _ in range(5)]
        self.halfBoard = halfBoard()


class Game:
    def __init__(self):
        self.boardCommon = commonBoard()
        self.players = [Player("Player 1", "L"), Player("Player 2", "R")]


    def print_board(self):
        print("this is where the buttons should be updated")
        time.sleep(pauseTime)


    def move_pieces(self, player, diceroll):
        print(f"{player.name} rolled a {diceroll}.")
        time.sleep(pauseTime/2)

        # If a player rolls 0, skip their turn
        if diceroll == 0:
            self.print_board()
            return

        # Create an empty dictionary which
        movablePieces = {}

        # Flag which will be used to skip other pieces in the pile
        pilePieceConsidered = False

        for piece in player.pieces:

            # Only consider the first piece in the pile encountered if there are multiple
            if piece.position == 0 and pilePieceConsidered:
                continue

            # Calculate the potential new position
            newPosition = piece.position + diceroll

            # Check if spaces are occupied
            if newPosition <= 4 or 13 <= newPosition <= 14:
                if not player.halfBoard.is_occupied(newPosition)[0]:
                    movablePieces[piece] = newPosition

            # With current player's pieces
            elif 5 <= newPosition <= 12:
                occupiedStatus = self.boardCommon.is_occupied(newPosition)
                if occupiedStatus[0]:
                    # Check that the piece to replace is not one of the current player's, and that it is not on a rosette
                    if (occupiedStatus[1].owner != piece.owner) and (occupiedStatus[1].position not in boardRosettes):
                        movablePieces[piece] = newPosition
                else:
                    movablePieces[piece] = newPosition

            # Off the board by exactly 1
            elif newPosition == 15:
                movablePieces[piece] = newPosition

            if piece.position == 0:
                pilePieceConsidered = True

        # Handle scenario with no possible moves
        if not movablePieces:
            print(f"{player.name} has no possible moves.\n")
            return

        # Display the piece movement options
        print("\n #  MOVE OPTIONS")
        for i, pair in enumerate(movablePieces.items()):
            print(f"[{i + 1}] {player.side}{pair[0].ID}: {pair[0].position} --> {pair[1]}")

        moveChoice = int(input("\nSelect an option: ")) - 1
        # moveChoice = 0 # for debugging (chooses the first option each time)

        selectedPiece = list(movablePieces.keys())[moveChoice]
        newPosition = movablePieces[selectedPiece]

        # halfBoard ->
        if selectedPiece.position in player.halfBoard.positions:
            # halfBoard
            if newPosition in player.halfBoard.positions:
                player.halfBoard.move_piece(selectedPiece, newPosition)
            # commonBoard
            elif newPosition in self.boardCommon.positions:
                player.halfBoard.return_piece(selectedPiece)
                self.boardCommon.add_piece(selectedPiece, newPosition)
            # off the board
            else:
                player.halfBoard.remove_piece(selectedPiece)

        # commonBoard ->
        elif selectedPiece.position in self.boardCommon.positions:
            # commonBoard
            if newPosition in self.boardCommon.positions:
                self.boardCommon.move_piece(selectedPiece, newPosition)
            # halfBoard
            elif newPosition in player.halfBoard.positions:
                self.boardCommon.return_piece(selectedPiece)
                player.halfBoard.add_piece(selectedPiece, newPosition)
            # off the board
            else:
                self.boardCommon.remove_piece(selectedPiece)

        # off the board ->
        else:
            # halfBoard
            player.halfBoard.move_piece(selectedPiece, diceroll)

        # Display the game board after moving a piece
        self.print_board()

        # After moving the piece, check whether it landed on a rosette
        if selectedPiece.position in boardRosettes:
            print(f"{player.name} landed on a rosette at tile {selectedPiece.position} and rolls again!")
            self.move_pieces(player, roll_dice())


    def check_winner(self, player):
        return not player.pieces


    def play_game(self):
        # Display the empty board at the start of gameplay
        self.print_board()

        while True:
            for player in self.players:
                diceroll = roll_dice()

                self.move_pieces(player, diceroll)

                if self.check_winner(player):
                    print(f"{player.name} has exhausted all of their pieces and won the game!\n")
                    return














class ButtonManager:
    def __init__(self, window):
        self.window = window

    def set_sensitivity(self, button_id, sensitivity):
        """Set the sensitivity of a button."""
        self.window.set_sensitivity(button_id, sensitivity)

    def disable_all_buttons(self):
        """Disable all buttons."""
        button_ids = [
            "leftTile1", "leftTile2", "leftTile3", "leftTile4", "commonTile5", "commonTile6",
            "commonTile7", "commonTile8", "commonTile9", "commonTile10", "commonTile11",
            "commonTile12", "leftTile13", "leftTile14"
        ]
        for button_id in button_ids:
            self.set_sensitivity(button_id, False)


class GnomeUrApplication(Adw.Application):
    """The main application singleton class."""

    def __init__(self):
        super().__init__(application_id='com.github.binudakal.gnomeur',
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)
        self.create_action('quit', lambda *_: self.quit(), ['<primary>q'])
        self.create_action('about', self.on_about_action)
        self.create_action('preferences', self.on_preferences_action)

    def do_activate(self):
        """Called when the application is activated.

        We raise the application's main window, creating it if
        necessary.
        """
        win = self.props.active_window
        if not win:
            win = GnomeUrWindow(application=self)
            # self.button_manager = ButtonManager(win)
            # self.button_manager.disable_all_buttons()
        win.present()

    def on_about_action(self, widget, _):
        """Callback for the app.about action."""
        about = Adw.AboutWindow(transient_for=self.props.active_window,
                                application_name='Ur',
                                application_icon='com.github.binudakal.gnomeur',
                                developer_name='Binuda Kalugalage',
                                version='0.1.0',
                                developers=['Binuda Kalugalage'],
                                copyright='© 2024 Binuda Kalugalage')
        about.present()

    def on_preferences_action(self, widget, _):
        """Callback for the app.preferences action."""
        print('app.preferences action activated')

    def create_action(self, name, callback, shortcuts=None):
        """Add an application action.

        Args:
            name: the name of the action
            callback: the function to be called when the action is
              activated
            shortcuts: an optional list of accelerators
        """
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)


def main(version):
    """The application's entry point."""
    app = GnomeUrApplication()

    # urGame = Game()
    # urGame.play_game()

    return app.run(sys.argv)




if __name__ == "__main__":
    main(None)

