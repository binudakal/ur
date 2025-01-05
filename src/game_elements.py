from abc import ABC, abstractmethod
from .constants import Constants

class gameDice:
    def __init__(self, win, owner):
        self.win = win
        self.owner = owner

        if self.owner.side == "L":
            self.button = self.win.whiteButton
            self.label = self.win.whiteLabel
        else:
            self.button = self.win.blackButton
            self.label = self.win.blackLabel

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

class Node:
    def __init__(self, item=None):
        self.item = item
        self.link = None

class Pile:
    """ Pile class for holding player pieces """

    def __init__(self, pieces):
        self.length = 0
        self.top = None

        for piece in pieces:
            self.push(piece)

    def push(self, item):
        new_node = Node(item)
        new_node.link = self.top
        self.top = new_node
        self.length += 1

    def pop(self):
        if self.is_empty():
            raise Exception('Stack is empty')

        item = self.top.item
        self.top = self.top.link
        self.length -= 1
        return item

    def __len__(self) -> int:
        return self.length

    def is_empty(self) -> bool:
        return self.top is None

    def find_movable(diceroll) -> list:
        # If a player rolls 0, they cannot move any pieces
        if diceroll == 0:
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
                    if (occupiedStatus.owner != piece.owner) and (occupiedStatus.position not in self.boardRosettes):
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



class Player:
    def __init__(self, name, side, win):
        self.name = name
        self.side = side
        self.pieces = [Piece(self, _ + 1) for _ in range(Constants.NUM_PIECES)]
        self.board = halfBoard()
        self.dice = gameDice(win, self)
        self.pile = Pile(self.pieces)

    def __str__(self):
        # return f"{self.name} on the {self.side} side."
        a = f"{self.name}:\n"
        for piece in self.pieces:
            a += str(piece) + "\n"
        return a

