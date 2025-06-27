# game_elements.py
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

from abc import ABC, abstractmethod
from .settings import Settings

class gameDice:
    def __init__(self, win, owner):
        self.win = win
        self.owner = owner

        if self.owner.side == "L":
            self.button = self.win.whiteButton
            self.label = self.win.whiteRoll
        else:
            self.button = self.win.blackButton
            self.label = self.win.blackRoll

        # Connect the dice's button to the click function
        self.button.connect("clicked", self.dice_click)

    def update_label(self, diceroll=None):
        if diceroll:
            self.label.set_visible(True)
            self.label.set_text(diceroll)
        else:
            self.label.set_visible(False)

    def dice_click(self, button):
        diceRoll = self.win.game.roll_dice()
        movable = self.win.game.calculate_movable(self.owner, diceRoll)

        # Update the label and sensitivity of the dice's button
        self.update_label(str(diceRoll))
        self.button.set_sensitive(False)

        # If no pieces can be moved, let the other player roll their dice
        if not movable:
            # Enable the other player's dice
            self.win.game.otherPlayer.dice.button.set_sensitive(True)

        # Switch the current player
        self.win.game.alternate_players()


class Board(ABC):
    def is_occupied(self, position):
        """"
        Return the occupying piece if occupied, None otherwise
        """
        return self.positions[position]

    def add_piece(self, piece, position):
        """
        Add a piece to the board
        """
        self.positions[position] = piece
        piece.position = position

        piece.owner.pile.update_label()

    def return_piece(self, piece):
        """
        Remove a piece from the board, moving it back to the pile
        """
        self.positions[piece.position] = None
        piece.position = 0

        piece.owner.pile.update_label()

    def destroy_piece(self, piece):
        """
        Completely remove a piece, after having reached the end
        """
        self.positions[piece.position] = None
        piece.position = None  # to prevent double rosette bug

        piece.owner.pile.remove(piece)
        piece.owner.pile.update_label()

    @abstractmethod
    def move_piece(self, position, piece):
        pass

class halfBoard(Board):
    def __init__(self):
        self.positions = {i: None for i in range(1, 5)}
        self.positions.update({13: None, 14: None})

    def move_piece(self, piece, position):
        # Update the position dictionaries
        self.return_piece(piece)  # remove piece from its current/old spot
        self.add_piece(piece, position)  # add it to its new spot


class commonBoard(Board):
    def __init__(self):
        self.positions = {i: None for i in range(5, 13)}

    def replace_piece(self, position):
        # If the other player's piece is already there,
        occupyingPiece = self.is_occupied(position)
        if occupyingPiece:
            # Return it to their pile (position = 0)
            self.return_piece(occupyingPiece)
            print(f"\n{occupyingPiece.owner.side}{occupyingPiece.ID} was returned to {occupyingPiece.owner.name}'s pile.")

    def move_piece(self, piece, position):
        self.replace_piece(position)

        # Move the piece to the new spot (after removing old piece above if applicable)
        self.return_piece(piece)
        self.add_piece(piece, position)

class Piece:
    def __init__(self, player, pieceNumber):
        self.owner = player
        self.position = 0
        self.ID = pieceNumber

    @property
    def side(self):
        if 5 <= self.position <= 12:
            return "C"
        else:
            return self.owner.side

    @property
    def board(self):
        if self.position <= 4 or 13 <= self.position <= 15:
            return self.owner.board

    def __str__(self):
        return f"Piece {self.owner.side}{self.ID} at position {self.position}"


class Pile(list):
    """ Pile class for holding player pieces """

    def __init__(self, win, owner, pieces):
        super().__init__(pieces)

        self.win = win
        self.owner = owner

        self.pieces = pieces

        if self.owner.side == "L":
            self.label = self.win.whitePieces
        else:
            self.label = self.win.blackPieces

    def is_empty(self) -> bool:
        return self.top is None

    def update_label(self):
        self.label.set_text(str(sum(1 for p in self if p.position == 0)))

class Player:
    def __init__(self, name, side, win):
        self.name = name
        self.side = side
        self.board = halfBoard()
        self.dice = gameDice(win, self)
        self.pile = Pile(win, self, [Piece(self, _ + 1) for _ in range(Settings.get_num_pieces())])

        self.pile.update_label()

    def __str__(self):
        # return f"{self.name} on the {self.side} side."
        a = f"{self.name}:\n"
        for piece in self.pile:
            a += str(piece) + "\n"
        return a


