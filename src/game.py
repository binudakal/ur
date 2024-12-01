import random
import time
from abc import ABC, abstractmethod

from .constants import Constants
from gi.repository import Gtk, Gdk, Adw, Gio

class gameDice():
    def __init__(self, win, owner):
        self.win = win
        self.owner = owner

        if self.owner.side == "L":
            self.button = self.win.whiteButton
            self.label = self.win.whiteLabel
        else:
            self.button = self.win.blackButton
            self.label = self.win.blackLabel

        self.button.connect("clicked", self.dice_click)
        self.button.set_child(Gtk.Image.new_from_file("/app/share/icons/hicolor/symbolic/dice.svg"))

    def update_label(self, diceroll=None):
        if diceroll:
            self.label.set_visible(True)
            self.label.set_text(diceroll)
        else:
            self.label.set_visible(False)

    def dice_click(self, button):
        diceRoll = self.win.game.roll_dice()
        movable = self.win.game.calculate_movable(self.owner, diceRoll)

        # Update the label and sensitivity of this dice's button
        self.update_label(str(diceRoll))
        self.button.set_sensitive(False)

        # Hide the label of the other dice's button
        self.win.game.otherPlayer.dice.update_label()

        # If no pieces can be moved, let the other player roll their dice
        if not movable:
            # Enable the other player's dice
            self.win.game.otherPlayer.dice.button.set_sensitive(True)

        self.win.game.alternate_players()


boardRosettes = (4, 8, 14)

# Create the dictionary which will hold movable pieces and where they can move to

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

    def return_piece(self, piece):
        """
        Remove a piece from the board, moving it back to the pile
        """
        self.positions[piece.position] = None
        piece.position = 0

    def destroy_piece(self, piece):
        """
        Completely remove a piece, after having reached the end
        """
        self.positions[piece.position] = None
        piece.position = None  # to prevent double rosette bug
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
            print(f"{occupyingPiece.owner.side}{occupyingPiece.ID} was returned to {occupyingPiece.owner.name}'s pile.")

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
        return f"{self.owner.name}'s piece {self.owner.side}{self.ID} at position {self.position}"

class Player:
    def __init__(self, name, side, win):
        self.name = name
        self.side = side
        self.pieces = [Piece(self, _ + 1) for _ in range(Constants.NUM_PIECES)]
        self.board = halfBoard()
        self.dice = gameDice(win, self)

    def __str__(self):
        # return f"{self.name} on the {self.side} side."
        a = ""
        for piece in self.pieces:
            a += str(piece) + "\n"
        return a


class Game:
    __gtype_name__ = 'UrGame'

    def __init__(self, win):
        self.win = win
        self.app = win.app
        self.players = [Player("Player 1", "L", self.win), Player("Player 2", "R", self.win)]
        self.currentPlayer = self.players[0]
        self.boardCommon = commonBoard()

    @property
    def otherPlayer(self):
        for player in self.players:
                if player is not self.currentPlayer:
                    return player

    @property
    def winner(self):
        # for player in self.players:
        #     if not player.pieces:
        #         return player

        return next((player for player in self.players if not player.pieces), None)

    def roll_dice(self):
        return sum(random.randint(0, 1) for _ in range(4))

    def print_board(self):
        off_board = lambda x: x.position == 0

        player1Pile = "Player 1's pile:  "
        for piece1 in filter(off_board, self.players[0].pieces):
            player1Pile += f"{self.players[0].side}{piece1.ID}, "

        player2Pile = "Player 2's pile:  "
        for piece2 in filter(off_board, self.players[1].pieces):
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
        print("-----------------------------------")


    def format_tile(self, side, pos):
        if pos <= 4 or 13 <= pos <= 15:
            tile.nextTile = get_tile_by_var(f"{piece.owner.side}Tile{pos}")
        elif 5 <= pos <= 12:
            tile.nextTile = get_tile_by_var(f"CTile{pos}")


    def calculate_movable(self, player, diceroll):

        print(f"{player.name} rolled a {diceroll}.")

        # If a player rolls 0, skip their turn
        if diceroll == 0:
            self.print_board()
            return

        # Flag which will be used to skip other pieces in the pile
        pilePieceConsidered = False

        for piece in player.pieces:
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
                    if (occupiedStatus.owner != piece.owner) and (occupiedStatus.position not in boardRosettes):
                        piece.nextPos = newPosition
                else:
                    piece.nextPos = newPosition

            # Off the board by exactly 1
            elif newPosition == 15:
                piece.nextPos = newPosition

            if piece.position == 0:
                pilePieceConsidered = True

        movablePieces = list(filter(lambda x: x.nextPos is not None, player.pieces))

        # Handle scenario with no possible moves
        if not movablePieces:
            print(f"{player.name} has no possible moves.\n")
            # self.app.on_impossible(player)
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
            self.win.app.on_win_action(self.winner)
            return

        # After moving the piece, check whether it landed on a rosette
        # TODO: fix rosettes
        if selectedPiece.position in boardRosettes:
            print(f"{player.name} landed on a rosette at tile {selectedPiece.position} and rolls again!")
            # Skip the other player
            self.alternate_players()

        # -----------------------------------------------

    def alternate_players(self):
        self.currentPlayer = self.otherPlayer

    # def check_winner(self, player):
    #     return not player.pieces

    # def play_turn(self, diceroll):
        ## Display the empty board at the start of gameplay
    #     self.print_board()

    #     self.currentPlayer.dice.update_label(str(diceroll))

        ## Move the current player
    #     self.calculate_movable(self.currentPlayer, diceroll)

        ## Set the other player as the new currentPlayer (next player)
    #     self.currentPlayer = self.otherPlayer





