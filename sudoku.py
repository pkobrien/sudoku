# -*- coding: utf-8 -*-
"""
@author: Patrick K. O'Brien

An object-oriented treatment of Peter Norvig's paper and
function-based code from http://norvig.com/sudoku.html.
"""

import random

__version__ = '0.8.0'


DIGITS = {'1', '2', '3', '4', '5', '6', '7', '8', '9'}

VALID_GRID_CHARS = DIGITS.union({'0', '.'})

ROWS = [range(i, i + 9) for i in range(0, 81, 9)]

COLUMNS = [range(i, i + 81, 9) for i in range(9)]

BLOCKS = [sum([range(i + 9*x, i + 9*x + 3) for x in range(3)], [])
          for i in sum([range(z*27, z*27 + 9, 3) for z in range(3)], [])]


def row_indices(i):
    """Return list of grid index values for squares in the same row as i.

    So if i is 3 its row indices are [0, 1, 2, 3, 4, 5, 6, 7, 8].
    """
    start = i - i % 9
    return range(start, start + 9)


def column_indices(i):
    """Return list of grid index values for squares in the same column as i.

    So if i is 3 its column indices are [3, 12, 21, 30, 39, 48, 57, 66, 75].
    """
    start = i % 9
    return range(start, start + 81, 9)


def block_indices(i):
    """Return list of grid index values for squares in the same block as i.

    So if i is 3 its block indices are [3, 4, 5, 12, 13, 14, 21, 22, 23].
    """
    start = 27 * (i // 27) + 3 * ((i % 9) // 3)
    return sum([range(start + 9*y, start + 9*y + 3) for y in range(3)], [])


def peer_indices(i):
    """Return set of grid index values for peers of the square at i.

    Every square has 20 peers.
    So if i is 3 its peers are {0, 1, 2, 4, 5, 6, 7, 8, 12, 13, 14,
                                21, 22, 23, 30, 39, 48, 57, 66, 75}.
    """
    return (set.union(set(row_indices(i)),
                      set(column_indices(i)),
                      set(block_indices(i))
                      ) - {i})


def unit_indices(i):
    """Return (row_indices, column_indices, block_indices) for square at i."""
    return row_indices(i), column_indices(i), block_indices(i)


PEERS = [peer_indices(i) for i in range(81)]

UNITS = [unit_indices(i) for i in range(81)]


def display(grid):
    """Print grid in a readable format."""
    print(formatted(grid))


def formatted(grid):
    """Return grid in a readable format."""
    grid = normalize(grid)
    width = 2
    border = '+'.join(['-' * (1 + (width * 3))] * 3)
    lines = []
    rows = [grid[n:n+9] for n in range(0, 81, 9)]
    for n, row in enumerate(rows):
        line = ' ' + ''.join(
            row[n2].center(width) + ('| ' if n2 in (2, 5) else '')
            for n2 in range(9))
        lines.append(line)
        if n in (2, 5):
            lines.append(border)
    return '\n' + '\n'.join(lines) + '\n'


def grid_map_all_digits():
    """Return dictionary of {i: string_of_all_digits} pairs."""
    string_of_all_digits = ''.join(DIGITS)
    return {i: string_of_all_digits for i in range(81)}


def is_valid(grid):
    """Return true if grid has no duplicate values within a unit.

    Does not guarantee that an unsolved grid can be solved."""
    grid = normalize(grid)
    units = ROWS + COLUMNS + BLOCKS
    for unit in units:
        values = [grid[i] for i in unit if grid[i] != '.']
        if len(values) != len(set(values)):
            return False
    return True


def normalize(grid):
    """Return 81 character string of digits (with dots for missing values)."""
    normalized = ''.join([c for c in grid if c in VALID_GRID_CHARS])
    normalized = normalized.replace('0', '.')
    if len(normalized) != 81:
        raise ValueError('Grid is not a proper text representation.')
    return normalized


def random_grid(min_assigned_squares=26, symmetrical=True):
    """Return random (grid, solution).

    Assign a minimum of 26 to a maximum of 80 squares.
    Assigning less than 26 squares takes too long."""
    min_assigned_squares = max(min_assigned_squares, 26)
    min_assigned_squares = min(min_assigned_squares, 80)
    min_unique_digits = 8
    grid_map = grid_map_all_digits()
    mirror = list(reversed(range(81)))
    assigned_squares = []
    for i in shuffled(range(81)):
        if i in assigned_squares:
            # Already assigned earlier as a mirror for symmetry.
            continue
        if not assign(grid_map, i, random.choice(grid_map[i])):
            break
        assigned_squares.append(i)
        if symmetrical:
            # Assign a value to the mirror square as well.
            other_i = mirror[i]
            if other_i != i:
                if not assign(grid_map, other_i,
                              random.choice(grid_map[other_i])):
                    break
                assigned_squares.append(i)
        unique_digits = {grid_map[i] for i in assigned_squares}
        if (len(assigned_squares) >= min_assigned_squares and
                len(unique_digits) >= min_unique_digits):
            # Sudoku requires a grid with one and only one solution.
            count = 0
            for solution in solve(to_grid(grid_map)):
                count += 1
                if count > 1:
                    break
            if not count == 1:
                # No solution or more than one solution.
                break
            unassigned_squares = set(range(81)) - set(assigned_squares)
            grid = to_grid(grid_map, unassigned_squares)
            return grid, solution
    # Failed to setup a single-solution grid, so try again.
    return random_grid(min_assigned_squares, symmetrical)


def assign(grid_map, i, digit):
    """Assign digit to grid_map[i] and eliminate from peers."""
    digits_to_eliminate = grid_map[i].replace(digit, '')
    if all(eliminate(grid_map, i, d2) for d2 in digits_to_eliminate):
        return grid_map
    else:
        return False


def eliminate(grid_map, i, digit):
    """Eliminate digit from potential digits for square at grid_map[i]."""
    if digit not in grid_map[i]:
        return grid_map
    grid_map[i] = grid_map[i].replace(digit, '')
    d2 = grid_map[i]
    if len(d2) == 0:
        return False
    elif len(d2) == 1:
        if not all(eliminate(grid_map, peer, d2) for peer in PEERS[i]):
            return False
    for unit in UNITS[i]:
        places = [i2 for i2 in unit if digit in grid_map[i2]]
        if len(places) == 0:
            return False
        elif len(places) == 1:
            if not assign(grid_map, places[0], digit):
                return False
    return grid_map


def to_grid(grid_map, unassigned_squares=[]):
    """Return grid string from a grid_map dictionary."""
    return ''.join(grid_map[i]
                   if len(grid_map[i]) == 1
                   and i not in unassigned_squares else '.'
                   for i in range(81))


def replace_value(grid, i, new_value):
    """Return grid with grid[i] replaced by new_value."""
    return grid[:i] + new_value + grid[i+1:]


def shuffled(iterable):
    """Return shuffled copy of iterable as a list."""
    l = list(iterable)
    random.shuffle(l)
    return l


def solve(grid):
    """Generate all possible solutions for a solveable grid."""
    grid = normalize(grid)
    if not is_valid(grid):
        return
    for solution in _solve(grid):
        yield solution


def _possible_values(grid, index):
    """Return list of available digit values for grid[index]."""
    return list(DIGITS - set(grid[n] for n in PEERS[index]))


def _solve(grid):
    """Generate all possible solutions for a solveable grid."""
    if '.' not in grid:
        yield grid
        return
    unsolved = []
    for i in [i for i, value in enumerate(grid) if value == '.']:
        values = _possible_values(grid, i)
        if not values:
            # Grid cannot be solved.
            return
        unsolved.append((len(values), i, values))
    i, values = min(unsolved)[1:]
    for new_value in values:
        for solution in _solve(replace_value(grid, i, new_value)):
            yield solution


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
    def assigned_grid(self):
        """Return the assigned grid as an 81 character string."""
        return ''.join(square.current_value
                       if square.current_value and square.was_assigned else '.'
                       for square in self.squares)

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

    def setup_random_grid(self, min_assigned_squares=26, symmetrical=True):
        """Setup random grid with a min of 26 to a max of 80 squares assigned.

        Processing a grid with less than 26 squares assigned takes too long."""
        self.reset()
        min_assigned_squares = max(min_assigned_squares, 26)
        min_assigned_squares = min(min_assigned_squares, 80)
        min_unique_digits = 8
        for square in shuffled(self.squares):
            if square.was_assigned:
                # Already assigned as a mirror for symmetry.
                continue
            if not square._assign_random_digit():
                break
            if symmetrical:
                other = self.mirror[square]
                if other is not square:
                    if not other._assign_random_digit():
                        break
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
        # Check each region to see if digit can now only appear in
        # one place.  If so, assign it to the square in that place.
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
        self.peers = set(others) - {self}


class Game(object):
    """Game class."""
    # .player, .puzzle, start(), stop()
    pass


class Player(object):
    """Player class."""
    pass
