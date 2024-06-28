import random
import time
from abc import ABC, abstractmethod

# from .window import UrWindow

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
        piece.position = None
        # piece.position = None  # to prevent double rosette bug
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
        self.return_piece(piece)  # remove current piece from its old spot
        self.add_piece(piece, position)  # add it to its new spot

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
        self.side = self.owner.side

        # check if piece moved to commonboard after each move
        # if self.position <= 4 or 13 <= self.position <= 14:
        #     self.side = self.owner.side
        # elif 5 <= newPosition <= 12:
        #     self.side = "C"

class Player:
    def __init__(self, name, side):
        self.name = name
        self.side = side
        self.pieces = [Piece(self, _ + 1) for _ in range(5)]
        self.halfBoard = halfBoard()

class Game:
    __gtype_name__ = 'UrGame'

    def __init__(self, app, win):
        self.boardCommon = commonBoard()
        self.players = [Player("Player 1", "L"), Player("Player 2", "R")]
        self.app = app
        self.win = win
        self.button_manager = win.button_manager

        self.currentPlayer = self.players[0]

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

        leftBoard = self.players[0].halfBoard.positions
        rightBoard = self.players[1].halfBoard.positions
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
        time.sleep(pauseTime)

    def move_pieces(self, player, diceroll):

        # this doesn't update at the correct time
        for piece in player.pieces:
            if 5 <= piece.position <= 12:
                piece.side = "C"
            else:
                piece.side = piece.owner.side



        self.win.clean_board()

        print(f"{player.name} rolled a {diceroll}.")
        self.win.update_text(player.name, diceroll)
        time.sleep(pauseTime / 2)

        # If a player rolls 0, skip their turn
        if diceroll == 0:
            self.print_board()
            return

        # Create an empty dictionary which will hold movable pieces and where they can move to
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

        # self.win.show_movable()

        # Display the piece movement options
        print("\n #  MOVE OPTIONS")
        for i, pair in enumerate(movablePieces.items()):
            print(f"[{i + 1}] {player.side}{pair[0].ID}: {pair[0].position} --> {pair[1]}")

        self.win.load_movable(movablePieces)


        # moveChoice = int(input("\nSelect an option: ")) - 1
        moveChoice = 0  # for debugging (chooses the first option each time)



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
            self.move_pieces(player, self.roll_dice())


    def check_winner(self, player):
        return not player.pieces

    def play_game(self, diceroll):
        # Display the empty board at the start of gameplay
        self.print_board()

        # move the current player
        self.move_pieces(self.currentPlayer, diceroll)

        if self.check_winner(self.currentPlayer):
            print(f"{self.currentPlayer.name} has exhausted all of their pieces and won the game!\n")
            self.win.diceButton.set_sensitive(False)
            self.win.titleText.set_text(f"{self.currentPlayer.name} wins!")
            return

        # set currentPlayer/next player
        for player in self.players:
            if player is not self.currentPlayer:
                self.currentPlayer = player
                break




