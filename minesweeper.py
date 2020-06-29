import itertools
import random
from copy import deepcopy


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

        self.safes = set()
        self.mines = set()

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def __len__(self):
        return len(self.cells)

    def known_mines(self):
        return self.mines()

    def known_safes(self):
        return self.safes()

    def mark_mine(self, cell):
        if cell not in self.cells:
            return

        self.cells.remove(cell)
        self.count -= 1
        self.mines.add(cell)

    def mark_safe(self, cell):
        if cell not in self.cells:
            return

        self.cells.remove(cell)
        self.safes.add(cell)

class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def markAllSafe(self, sentence):
        temp = sentence.cells.copy()

        for cell in temp:
            self.mark_safe(cell)

    def markAllMines(self, sentence):
        temp = sentence.cells.copy()

        for cell in temp:
            self.mark_mine(cell)

    def allCellsAround(self,cell):
        def isValidNeighbor(cell, neighbor):
            I, J = cell
            i, j = neighbor

            if i < 0 or j < 0:
                return False
            if i == I and j == J:
                return False
            if i >= self.height or j >= self.width:
                return False
            return True

        cells = set()
        I, J = cell
        for x in range(-1,2):
            i = I + x
            for y in range(-1,2):
                j = J + y
                if isValidNeighbor(cell,(i,j)):
                    cells.add((i,j))
        return cells

    def checkNewInformation(self, sentence):
        if sentence.count == 0:
            self.markAllSafe(sentence)
        elif len(sentence) == sentence.count:
            self.markAllMines(sentence)

    def conclud(self, sentence1, sentence2):
        cells1 = sentence1.cells
        cells2 = sentence2.cells

        if len(cells2) == 0 or not cells2.issubset(cells1):
            return

        count1 = sentence1.count

        count2 = sentence2.count

        newCells = cells2 - cells1
        newCount = count2 - count1
        self.knowledge.append(Sentence(newCells, newCount))

    def concludNewInformation(self):
        self.knowledge.sort(key=lambda x: len(x), reverse=True)
        for i in range(len(self.knowledge)):
            self.checkNewInformation(self.knowledge[i])
            for j in range(i, len(self.knowledge)):
                self.conclud(self.knowledge[i], self.knowledge[j])

    def clean(self):
        """ to delete all empty sentences """
        for sentence in self.knowledge:
            if len(sentence) == 0:
                self.knowledge.remove(sentence)

    def add_knowledge(self, cell, count):
        self.moves_made.add(cell)

        self.mark_safe(cell)

        newCells = self.allCellsAround(cell)
        newSentence = Sentence(cells=newCells, count=count)
        self.knowledge.append(newSentence)

        self.concludNewInformation()
        self.clean()

    def make_safe_move(self):
        safeMove = None

        safes = self.safes - self.moves_made
        if len(safes) > 0:
            safes = list(safes)
            index = random.randrange(len(safes))
            safeMove = safes[index]

        return safeMove

    def make_random_move(self):
        if len(self.safes) + len(self.mines) == self.height * self.width:
            return None


        i = random.randrange(self.height)
        j = random.randrange(self.width)
        move = (i, j)
        while not(move not in self.mines and move not in self.moves_made):
            i = random.randrange(self.height)
            j = random.randrange(self.width)
            move = (i, j)

        return move
