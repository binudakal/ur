import random
import time
from abc import ABC, abstractmethod

# from .window import UrWindow

pauseTime = 0

boardRosettes = [4, 8, 14]

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

    def remove_piece(self, piece):
        """
        Completely destroy a piece, after having reached the end
        """
        piece.position = None  # to prevent double rosette bug
        self.positions[piece.position] = None
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
        self.side = self.owner.side

    def __str__(self):
        return f"Player {self.owner.name}'s piece {self.side}{self.ID} at position {self.position}"

class Player:
    def __init__(self, name, side):
        self.name = name
        self.side = side
        self.pieces = [Piece(self, _ + 1) for _ in range(5)]
        self.boardHalf = halfBoard()

class Game:
    __gtype_name__ = 'UrGame'

    def __init__(self, app, win):
        self.boardCommon = commonBoard()
        self.players = [Player("Player 1", "L"), Player("Player 2", "R")]
        self.app = app
        self.win = win
        self.button_manager = win.button_manager

        self.currentPlayer = self.players[0]
        self.movablePieces = {}


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
        self.win.pileText.set_text(f"\n{player1Pile[:-2]}\n{player2Pile[:-2]}")

        leftBoard = self.players[0].boardHalf.positions
        rightBoard = self.players[1].boardHalf.positions
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

        # self.win.boardText.set_text(totalBoard)


    def calculate_movable(self, player, diceroll):

        for piece in player.pieces:
            if 5 <= piece.position <= 12:
                piece.side = "C"
            else:
                piece.side = piece.owner.side

        self.win.clean_board()

        print(f"{player.name} rolled a {diceroll}.")

        # If a player rolls 0, skip their turn
        if diceroll == 0:
            self.print_board()
            return

        # Reset movablePieces
        self.movablePieces = {}

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
                if not player.boardHalf.is_occupied(newPosition):
                    self.movablePieces[piece] = newPosition

            # With current player's pieces
            elif 5 <= newPosition <= 12:
                occupiedStatus = self.boardCommon.is_occupied(newPosition)
                if occupiedStatus:
                    # Check that the piece to replace is not one of the current player's, and that it is not on a rosette
                    if (occupiedStatus.owner != piece.owner) and (occupiedStatus.position not in boardRosettes):
                        self.movablePieces[piece] = newPosition
                else:
                    self.movablePieces[piece] = newPosition

            # Off the board by exactly 1
            elif newPosition == 15:
                self.movablePieces[piece] = newPosition

            if piece.position == 0:
                pilePieceConsidered = True

        # Handle scenario with no possible moves
        if not self.movablePieces:
            print(f"{player.name} has no possible moves.\n")
            self.win.diceText.set_text(f"{player.name} has no possible moves.")
            return

        # Display the piece movement options
        print("\n #  MOVE OPTIONS")
        for i, pair in enumerate(self.movablePieces.items()):
            print(f"[{i + 1}] {player.side}{pair[0].ID}: {pair[0].position} --> {pair[1]}")

        self.win.load_movable(self.movablePieces)


    def make_move(self, newPosition):

        # print(list(self.movablePieces.values()), "---", newPosition)

        player = list(x.owner for x in self.movablePieces.keys())[list(self.movablePieces.values()).index(newPosition)]

        selectedPiece = list(self.movablePieces)[list(self.movablePieces.values()).index(newPosition)]

        # halfBoard ->
        if selectedPiece.position in player.boardHalf.positions:
            # halfBoard
            if newPosition in player.boardHalf.positions:
                player.boardHalf.move_piece(selectedPiece, newPosition)
            # commonBoard
            elif newPosition in self.boardCommon.positions:
                self.boardCommon.replace_piece(newPosition)

                player.boardHalf.return_piece(selectedPiece)
                self.boardCommon.add_piece(selectedPiece, newPosition)

            # off the board
            else:
                player.boardHalf.remove_piece(selectedPiece)

        # commonBoard ->
        elif selectedPiece.position in self.boardCommon.positions:
            # commonBoard
            if newPosition in self.boardCommon.positions:
                self.boardCommon.move_piece(selectedPiece, newPosition)
            # halfBoard
            elif newPosition in player.boardHalf.positions:
                self.boardCommon.return_piece(selectedPiece)
                player.boardHalf.add_piece(selectedPiece, newPosition)
            # off the board
            else:
                self.boardCommon.remove_piece(selectedPiece)

        # off the board ->
        else:
            # halfBoard
            player.boardHalf.move_piece(selectedPiece, newPosition)

        # Display the game board after moving a piece
        self.print_board()



        # After moving the piece, check whether it landed on a rosette
        # TODO: fix rosettes
        if selectedPiece.position in boardRosettes:
            print(f"{player.name} landed on a rosette at tile {selectedPiece.position} and rolls again!")
            self.play_turn(self.roll_dice(), True)
            # self.calculate_movable(player, self.roll_dice())

        # -----------------------------------------------


    def check_winner(self, player):
        return not player.pieces

    def get_other_player(self):
        for player in self.players:
            if player is not self.currentPlayer:
                return player


    def play_turn(self, diceroll, rosette):
        # Display the empty board at the start of gameplay
        self.print_board()

        otherPlayer = self.get_other_player()

        # move the current player
        if not rosette:
            self.win.update_text(self.currentPlayer.name, diceroll)
        else:
            self.win.titleText.set_text(f"{otherPlayer.name} landed on a rosette!")
            self.win.update_text(otherPlayer.name, diceroll)

        self.calculate_movable(self.currentPlayer, diceroll)

        if self.check_winner(self.currentPlayer):
            print(f"{self.currentPlayer.name} has exhausted all of their pieces and won the game!\n")
            self.win.diceButton.set_sensitive(False)
            self.win.clean_board()
            self.win.titleText.set_text(f"{self.currentPlayer.name} wins!")
            return

        # set currentPlayer/next player
        self.currentPlayer = otherPlayer




