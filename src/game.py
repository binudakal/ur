# game.py
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

import random
import time
from .game_elements import gameDice, halfBoard, commonBoard, Piece, Pile, Player

class UrGame:
    __gtype_name__ = 'UrGame'

    def __init__(self, win):
        self.win = win
        self.app = win.app
        self.players = [Player("Player 1", "L", self.win), Player("Player 2", "R", self.win)]
        self.currentPlayer = self.players[0]
        self.boardCommon = commonBoard()
        self.boardRosettes = (4, 8, 14)

    @property
    def otherPlayer(self):
        for player in self.players:
                if player is not self.currentPlayer:
                    return player

    @property
    def winner(self):
        return next((player for player in self.players if not player.pile), None)

    def roll_dice(self):
        return sum(random.randint(0, 1) for _ in range(4))

    def print_board(self):
        off_board = lambda x: x.position == 0

        player1Pile = "Player 1's pile:  "
        for piece1 in filter(off_board, self.players[0].pile):
            player1Pile += f"{self.players[0].side}{piece1.ID}, "

        player2Pile = "Player 2's pile:  "
        for piece2 in filter(off_board, self.players[1].pile):
            player2Pile += f"{self.players[1].side}{piece2.ID}, "

        print(f"\n{player1Pile[:-2]}\n{player2Pile[:-2]}")

        leftBoard = self.players[0].board.positions
        rightBoard = self.players[1].board.positions
        middleBoard = self.boardCommon.positions

        totalBoard = "\n"

        # Add top halfBoards and commonBoard
        for i, j in zip(range(4, 0, -1), range(5, 9)):
            middle = f"{middleBoard[j].owner.side}{middleBoard[j].ID}" if middleBoard[j] is not None else '--'
            left = f"{leftBoard[i].owner.side}{leftBoard[i].ID}" if leftBoard[i] is not None else '--'
            right = f"{rightBoard[i].owner.side}{rightBoard[i].ID}" if rightBoard[i] is not None else '--'

            totalBoard += f"                {left}  {middle}  {right}\n"
            # totalBoard += f"{leftPieces[4-i]}                {left}  {middle}  {right}\n"

        # Add middleBoard
        for j in range(9, 11):
            middle = f"{middleBoard[j].owner.side}{middleBoard[j].ID}" if middleBoard[j] is not None else '--'
            totalBoard += f"                    {middle}    \n"

        # Add bottom halfBoards and commonBoard
        for i, j in zip(range(14, 12, -1), range(11, 13)):
            middle = f"{middleBoard[j].owner.side}{middleBoard[j].ID}" if middleBoard[j] is not None else '--'
            left = f"{leftBoard[i].owner.side}{leftBoard[i].ID}" if leftBoard[i] is not None else '--'
            right = f"{rightBoard[i].owner.side}{rightBoard[i].ID}" if rightBoard[i] is not None else '--'

            totalBoard += f"                {left}  {middle}  {right}\n"

        print(totalBoard)
        print("-----------------------------------\n")


    def calculate_movable(self, player, diceroll):

        print(f"{player.name} rolled a {diceroll}.")
        # return player.pile.get_movable(diceroll)

        # If a player rolls 0, skip their turn
        if diceroll == 0:
            self.print_board()
            return

        # Flag which will be used to skip other pieces in the pile
        pilePieceConsidered = False

        for piece in player.pile:
            # Reset the piece's old next position
            piece.nextPos = None

            # Only consider the first piece in the pile encountered if there are multiple
            if piece.position == 0 and pilePieceConsidered:
                continue

            # Calculate the potential new position
            newPosition = piece.position + diceroll

            # Check if spaces are occupied
            if newPosition <= 4 or 13 <= newPosition <= 14:
                if not player.board.is_occupied(newPosition):
                    piece.nextPos = newPosition

            # With current player's pieces
            elif 5 <= newPosition <= 12:
                occupiedStatus = self.boardCommon.is_occupied(newPosition)
                if occupiedStatus:
                    # Check that the piece to replace is not one of the current player's, and that it is not on a rosette
                    if (occupiedStatus.owner != piece.owner) and (occupiedStatus.position not in self.boardRosettes):
                        piece.nextPos = newPosition
                else:
                    piece.nextPos = newPosition

            # Off the board by exactly 1
            elif newPosition == 15:
                piece.nextPos = newPosition

            if piece.position == 0:
                pilePieceConsidered = True

        movablePieces = list(filter(lambda x: x.nextPos is not None, player.pile))

        # Handle scenario with no possible moves
        if not movablePieces:
            print(f"{player.name} has no possible moves.\n")
            self.app.on_impossible(player)
            return

        # Print the piece movement options
        print("\n #  MOVE OPTIONS")
        for i, piece in enumerate(movablePieces):
            print(f"[{i + 1}] {player.side}{piece.ID}: {piece.position} --> {piece.nextPos}")

        self.win.load_movable(movablePieces)

        return movablePieces


    def make_move(self, oldTile):

        newPosition = oldTile.nextTile.location
        selectedPiece = oldTile.piece
        player = selectedPiece.owner

        # halfBoard ->
        if selectedPiece.position in player.board.positions:
            # halfBoard
            if newPosition in player.board.positions:
                player.board.move_piece(selectedPiece, newPosition)
            # commonBoard
            elif newPosition in self.boardCommon.positions:
                self.boardCommon.replace_piece(newPosition)

                player.board.return_piece(selectedPiece)
                self.boardCommon.add_piece(selectedPiece, newPosition)

            # off the board
            else:
                player.board.destroy_piece(selectedPiece)

        # commonBoard ->
        elif selectedPiece.position in self.boardCommon.positions:
            # commonBoard
            if newPosition in self.boardCommon.positions:
                self.boardCommon.move_piece(selectedPiece, newPosition)
            # halfBoard
            elif newPosition in player.board.positions:
                self.boardCommon.return_piece(selectedPiece)
                player.board.add_piece(selectedPiece, newPosition)
            # off the board
            else:
                # if newPosition in player.board.positions:
                self.boardCommon.destroy_piece(selectedPiece)

        # off the board ->
        else:
            # halfBoard
            player.board.move_piece(selectedPiece, newPosition)

        # Display the game board after moving a piece
        self.print_board()

        # Check for a winner
        if self.winner:
            print(f"{self.winner.name} has exhausted all of their pieces and won the game!\n")
            self.win.app.on_win(self.winner)
            return

        # After moving the piece, check whether it landed on a rosette
        # TODO: fix rosettes
        if selectedPiece.position in self.boardRosettes:
            print(f"{player.name} landed on a rosette at tile {selectedPiece.position} and rolls again!")
            # Skip the other player
            self.alternate_players()

    def alternate_players(self):
        # Hide the label of the other dice's button
        self.otherPlayer.dice.update_label()

        # Switch the current and other players
        self.currentPlayer = self.otherPlayer







