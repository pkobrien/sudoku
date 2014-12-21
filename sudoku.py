# -*- coding: utf-8 -*-
"""
@author: Patrick K. O'Brien

An object-oriented treatment of Peter Norvig's paper and
function-based code from http://norvig.com/sudoku.html.
"""

import random

__version__ = '0.7.0'


DIGITS = ('1', '2', '3', '4', '5', '6', '7', '8', '9')
VALID_GRID_CHARS = DIGITS + ('0', '.')


def display_grid(grid):
    """Print grid in a readable format."""
    print(format_grid(grid))


def format_grid(grid):
    """Return formatted grid."""
    grid = normalize_grid(grid)
    width = 2
    border = '+'.join(['-' * (1 + (width * 3))] * 3)
    lines = []
    rows = [grid[n+0:n+9] for n in range(0, 81, 9)]
    for n, row in enumerate(rows):
        line = ' ' + ''.join(
            row[n2].center(width) + ('| ' if n2 in (2, 5) else '')
            for n2 in range(9))
        lines.append(line)
        if n in (2, 5):
            lines.append(border)
    return '\n' + '\n'.join(lines) + '\n'


def normalize_grid(grid):
    """Return 81 character string of digits (with dots for missing values)."""
    normalized = ''.join([c for c in grid if c in VALID_GRID_CHARS])
    normalized = normalized.replace('0', '.')
    if len(normalized) != 81:
        raise ValueError('Grid is not a proper text representation.')
    return normalized


def shuffled(iterable):
    """Return shuffled copy of iterable as a list."""
    l = list(iterable)
    random.shuffle(l)
    return l


class Puzzle(object):
    """Puzzle class."""

    def __init__(self):
        """Create a Puzzle instance."""
        self.rows = []
        self.columns = []
        self.blocks = []
        self.squares = []
        self.mirror = {}
        self.reset()

    def reset(self):
        """Reset the puzzle back to a clean slate."""
        self.rows = []
        self.columns = []
        self.blocks = []
        self.squares = []
        self.mirror = {}
        size = range(9)
        for n in size:
            num = n + 1
            self.rows.append(Row(num))
            self.columns.append(Column(num))
            self.blocks.append(Block(num))
        triples = [size[0:3], size[3:6], size[6:9]]
        block_finder = {}
        blocking = [(rs, cs) for rs in triples for cs in triples]
        for nb, (rs, cs) in enumerate(blocking):
            block_finder.update({(nr, nc): nb for nr in rs for nc in cs})
        num = 0
        for nr in size:
            row = self.rows[nr]
            for nc in size:
                column = self.columns[nc]
                block = self.blocks[block_finder[(nr, nc)]]
                num += 1
                self.squares.append(Square(num, row, column, block))
        self.mirror = dict(zip(self.squares, reversed(self.squares)))
        for square in self.squares:
            square._setup_peers()

    @property
    def assigned_digits(self):
        """Return set of digits that have been successfully assigned."""
        return {square.current_value for square in self.squares
                if square.was_assigned}

    @property
    def assigned_squares(self):
        """Return list of squares with assigned values."""
        return [square for square in self.squares if square.was_assigned]

    @property
    def current_grid(self):
        """Return the current grid as an 81 character string."""
        return ''.join(square.current_value
                       if square.current_value else '.'
                       for square in self.squares)

    @property
    def solved_grid(self):
        """Return the solved grid as an 81 character string."""
        return ''.join(square.solved_value
                       if square.solved_value else '.'
                       for square in self.squares)

    @property
    def is_solved(self):
        """Return True if all squares have been solved."""
        return all(square.is_solved for square in self.squares)

    def setup_random_grid(self, min_assigned_squares=17, symmetrical=True):
        """Setup random grid with min of 17 to max of 80 squares assigned."""
        self.reset()
        min_assigned_squares = max(min_assigned_squares, 17)
        min_assigned_squares = min(min_assigned_squares, 80)
        min_unique_digits = 8
        for square in shuffled(self.squares):
            if square in self.assigned_squares:
                # Already assigned as a mirror for symmetry.
                continue
            if not square._assign_random_digit():
                break
#            self.assigned_squares.append(square)
            if symmetrical:
                other = self.mirror[square]
                if other is not square:
                    if not other._assign_random_digit():
                        break
#                    self.assigned_squares.append(other)
            if (len(self.assigned_squares) >= min_assigned_squares and
                    len(self.assigned_digits) >= min_unique_digits):
                self._attempt_brute_force(True)
                if self.is_solved:
                    self._update_squares()
                    return
                else:
                    break
        # Failed to setup a solveable grid so try again.
        self.setup_random_grid(min_assigned_squares, symmetrical)

    def _attempt_brute_force(self, result):
        if result is False:
            return False
        if self.is_solved:
            return True
        square = min((len(square.possible_digits), square)
                     for square in self.squares
                     if len(square.possible_digits) > 1)[1]
        for digit in square.possible_digits:
            self._save_possible_digits()
            result = self._attempt_brute_force(square._apply(digit))
            if not result:
                self._restore_possible_digits()
            else:
                break
        return result

    def _save_possible_digits(self):
        """Save the state of possible digits to support backtracking."""
        for square in self.squares:
            square._save_possible_digits()

    def _restore_possible_digits(self):
        """Restore possible digits from an earlier saved state."""
        for square in self.squares:
            square._restore_possible_digits()

    def _update_squares(self):
        for square in self.squares:
            square.solved_value = square.possible_digits[0]


class Region(object):
    """Parent class for Row, Column and Block."""

    def __init__(self, number):
        self.number = number
        self.name = str(number)
        self.squares = []

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.number)


class Row(Region):
    pass


class Column(Region):
    pass


class Block(Region):
    pass


class Square(object):
    """Square class."""

    def __init__(self, number, row, column, block):
        """Create a Square instance."""
        self.number = number
        self.name = str(number)
        self.row = row
        self.column = column
        self.block = block
        row.squares.append(self)
        column.squares.append(self)
        block.squares.append(self)
        self.peers = set()
        self.possible_digits = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
        self._possible_digits_state = ()
        self.current_value = None
        self.solved_value = None
        self.was_assigned = False

    def __repr__(self):
        return '<Square %s @ Row:%s Col:%s Digit(s):%s>' % (
            self.name, self.row.number, self.column.number,
            ''.join(self.possible_digits))

    @property
    def is_solved(self):
        """Return True if square has been solved."""
        return len(self.possible_digits) == 1

    def _assign(self, digit):
        """Assign digit to square. Return False if conflict detected."""
        self.current_value = digit
        self.was_assigned = True
        return self._apply(digit)

    def _assign_random_digit(self):
        """Assign random digit from possible digits for the square."""
        return self._assign(random.choice(self.possible_digits))

    def _apply(self, digit):
        """Apply digit to square by eliminating all other digits."""
        digits_to_eliminate = [other for other in self.possible_digits
                               if other != digit]
        if all(self._eliminate(other) for other in digits_to_eliminate):
            return True
        else:
            return False

    def _eliminate(self, digit):
        """Eliminate digit from possible digits for square."""
        if digit not in self.possible_digits:
            return True
        self.possible_digits.remove(digit)
        if len(self.possible_digits) == 0:
            return False
        elif len(self.possible_digits) == 1:
            if not all(peer._eliminate(self.possible_digits[0])
                       for peer in self.peers):
                return False
        # Check each region to see if digit can now only appear in one place.
        # If so, assign it to the square in that place.
        for squares in (self.row.squares, self.column.squares,
                        self.block.squares):
            places = [square for square in squares
                      if digit in square.possible_digits]
            if len(places) == 0:
                return False
            elif len(places) == 1:
                if not places[0]._apply(digit):
                    return False
        return True

    def _save_possible_digits(self):
        """Save the state of possible digits to support backtracking."""
        self._possible_digits_state = tuple(self.possible_digits)

    def _restore_possible_digits(self):
        """Restore possible digits from an earlier saved state."""
        self.possible_digits = list(self._possible_digits_state)

    def _setup_peers(self):
        """Determine the set of squares that are peers of this square."""
        others = self.row.squares + self.column.squares + self.block.squares
        self.peers = {square for square in others if square is not self}


class Game(object):
    """Game class."""
    # .player, .puzzle, start(), stop()
    pass


class Player(object):
    """Player class."""
    pass
