# -*- coding: utf-8 -*-

import pytest
import sudoku as su


def test_module_constants():
    assert len(su.DIGITS) == 9
    assert len(su.VALID_GRID_CHARS) == 11
    assert len(su.ROWS) == 9
    for row in su.ROWS:
        assert len(row) == 9
    assert len(su.COLUMNS) == 9
    for column in su.COLUMNS:
        assert len(column) == 9
    assert len(su.BLOCKS) == 9
    for block in su.BLOCKS:
        assert len(block) == 9
    assert len(su.UNITS) == 27
    for unit in su.UNITS:
        assert len(unit) == 9
    assert len(su.PEERS) == 81


def test_normalize_ValueError():
    with pytest.raises(ValueError):
        su.normalize('')
    with pytest.raises(ValueError):
        su.normalize('.' * 82)


normalized = '4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......'

rows_and_zeros = """
400000805
030000000
000700000
020000060
000080400
000010000
000603070
500200000
104000000
"""

formatted = """
 4 . . | . . . | 8 . 5 
 . 3 . | . . . | . . . 
 . . . | 7 . . | . . . 
-------+-------+-------
 . 2 . | . . . | . 6 . 
 . . . | . 8 . | 4 . . 
 . . . | . 1 . | . . . 
-------+-------+-------
 . . . | 6 . 3 | . 7 . 
 5 . . | 2 . . | . . . 
 1 . 4 | . . . | . . . 
"""


def test_normalize():
    assert su.normalize(normalized) == normalized
    assert su.normalize(rows_and_zeros) == normalized
    assert su.normalize(formatted) == normalized


def test_formatted():
    assert su.formatted(normalized) == formatted


def test_row_indices():
    assert su.row_indices(0) == [0, 1, 2, 3, 4, 5, 6, 7, 8]
    assert su.row_indices(40) == [36, 37, 38, 39, 40, 41, 42, 43, 44]
    assert su.row_indices(80) == [72, 73, 74, 75, 76, 77, 78, 79, 80]


def test_column_indices():
    assert su.column_indices(0) == [0, 9, 18, 27, 36, 45, 54, 63, 72]
    assert su.column_indices(40) == [4, 13, 22, 31, 40, 49, 58, 67, 76]
    assert su.column_indices(80) == [8, 17, 26, 35, 44, 53, 62, 71, 80]


def test_block_indices():
    assert su.block_indices(0) == [0, 1, 2, 9, 10, 11, 18, 19, 20]
    assert su.block_indices(40) == [30, 31, 32, 39, 40, 41, 48, 49, 50]
    assert su.block_indices(80) == [60, 61, 62, 69, 70, 71, 78, 79, 80]


def test_peer_indices():
    assert su.peer_indices(0) == {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,
                                  18, 19, 20, 27, 36, 45, 54, 63, 72}
    assert su.peer_indices(40) == {4, 13, 22, 30, 31, 32, 36, 37, 38, 39,
                                   41, 42, 43, 44, 48, 49, 50, 58, 67, 76}
    assert su.peer_indices(80) == {8, 17, 26, 35, 44, 53, 60, 61, 62, 69,
                                   70, 71, 72, 73, 74, 75, 76, 77, 78, 79}


def test_is_valid():
    grid = '4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......'
    assert su.is_valid(grid)


def test_is_valid_not():
    grid = '747' + '.' * 78
    assert not su.is_valid(grid)


def test_is_valid_empty_grid():
    grid = '.' * 81
    assert su.is_valid(grid)


def test_is_valid_solved_grid():
    grid = '417369825632158947958724316825437169791586432346912758289643571573291684164875293'
    assert su.is_valid(grid)


def test_solve_already_solved():
    grid = '417369825632158947958724316825437169791586432346912758289643571573291684164875293'
    solution = grid
    all_solutions = list(su.solve(grid))
    assert len(all_solutions) == 1
    assert all_solutions[0] == solution


def test_solve_one_solution():
    grid = '4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......'
    solution = '417369825632158947958724316825437169791586432346912758289643571573291684164875293'
    all_solutions = list(su.solve(grid))
    assert len(all_solutions) == 1
    assert all_solutions[0] == solution


def test_solve_four_solutions():
    grid = '027800061000030008910005420500016030000970200070000096700000080006027000030480007'
    assert len(list(su.solve(grid))) == 4


def test_solve_infinite_solutions():
    # Okay, well... almost infinite. :-)
    grid = '.' * 81
    for count, solution in enumerate(su.solve(grid)):
        assert len(solution) == 81
        if count > 10:
            break
    assert count > 10


def test_solve_invalid_grid():
    grid = '747' + '.' * 78
    assert len(list(su.solve(grid))) == 0


def test_solve_hard_grid_1():
    hard_grid = """
        ... ... ..3
        78. 1.. .5.
        3.. ..5 2..
        .12 .6. .8.
        ..7 .2. 9..
        .3. .4. 51.
        ..4 6.. ..9
        .9. ..7 .45
        5.. ... ...
        """
    solution = '245986173789132654361475298912563487457821936836749512174658329693217845528394761'
    all_solutions = list(su.solve(hard_grid))
    assert len(all_solutions) == 1
    assert all_solutions[0] == solution


def test_solve_hard_grid_2():
    hard_grid = """
        ..3 6.4 9..
        ... .5. ...
        9.. ... ..7
        2.. ... ..6
        .4. ... .5.
        8.. ... ..1
        1.. ... ..5
        ... ... ...
        .92 736 41.
        """
    solution = '753614982628957134914382567275193846341268759869475321136849275487521693592736418'
    all_solutions = list(su.solve(hard_grid))
    assert len(all_solutions) == 1
    assert all_solutions[0] == solution


def test_solve_hard_grid_3():
    hard_grid = """
        ... 6.. 2..
        8.4 .3. ...
        ... ..9 ...
        4.5 ... ..7
        71. ... ...
        ..3 .5. ..8
        3.. .7. ..4
        ... ..1 9..
        ... 2.. .6.
        """
    solution = '971684235864532791532719486485963127716428359293157648329876514658341972147295863'
    all_solutions = list(su.solve(hard_grid))
    assert len(all_solutions) == 1
    assert all_solutions[0] == solution


def test_Puzzle_setup_random_grid():
    p = su.Puzzle()
    p.setup_random_grid()
    assert p.is_solved
    assert len(p.current_grid) == 81
    assert len(p.solved_grid) == 81
