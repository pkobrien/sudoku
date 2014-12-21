# -*- coding: utf-8 -*-

import pytest
import sudoku as su


def test_module_constants():
    assert len(su.DIGITS) == 9

with pytest.raises(ValueError):
    su.normalize_grid('')

with pytest.raises(ValueError):
    su.normalize_grid('0' * 82)

normalized = '4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......'

solution = '417369825632158947958724316825437169791586432346912758289643571573291684164875293'

rows_and_columns_with_zeros = """
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

assert su.format_grid(normalized) == formatted

assert su.normalize_grid(normalized) == normalized
assert su.normalize_grid(rows_and_columns_with_zeros) == normalized
assert su.normalize_grid(formatted) == normalized


def test_puzzle_with_random_grid():
    p = su.Puzzle()
    p.setup_random_grid()
    assert p.is_solved
    assert len(p.current_grid) == 81
    assert len(p.solved_grid) == 81

#==============================================================================
# assert su.solve_grid(normalized) == solution
# 
# # TODO assert su.solve_grid('.' * 81) is False
# 
# hard_grid = """
# ... ... ..3
# 78. 1.. .5.
# 3.. ..5 2..
# .12 .6. .8.
# ..7 .2. 9..
# .3. .4. 51.
# ..4 6.. ..9
# .9. ..7 .45
# 5.. ... ...
# """
# solution = '245986173789132654361475298912563487457821936836749512174658329693217845528394761'
# assert su.solve_grid(hard_grid) == solution
# 
# hard_grid = """
# ... 6.. 2..
# 8.4 .3. ...
# ... ..9 ...
# 4.5 ... ..7
# 71. ... ...
# ..3 .5. ..8
# 3.. .7. ..4
# ... ..1 9..
# ... 2.. .6.
# """
# solution = '971684235864532791532719486485963127716428359293157648329876514658341972147295863'
# assert su.solve_grid(hard_grid) == solution
# 
# hard_grid = """
# ..3 6.4 9..
# ... .5. ...
# 9.. ... ..7
# 2.. ... ..6
# .4. ... .5.
# 8.. ... ..1
# 1.. ... ..5
# ... ... ...
# .92 736 41.
# """
# solution = '753614982628957134914382567275193846341268759869475321136849275487521693592736418'
# assert su.solve_grid(hard_grid) == solution
#==============================================================================
