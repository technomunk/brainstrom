# A solution for https://www.codewars.com/kata/5b2c2c95b6989da552000120/python

from typing import Tuple

# The keyboard is a collection of symbols in a regular grid.
KEYBOARD = [
    ["a", "b", "c", "d", "e", "1", "2", "3"],
    ["f", "g", "h", "i", "j", "4", "5", "6"],
    ["k", "l", "m", "n", "o", "7", "8", "9"],
    ["p", "q", "r", "s", "t", ".", "@", "0"],
    ["u", "v", "w", "x", "y", "z", "_", "/"],
    ["", " ", "", "", "", "", "", ""],
]

START_INDEX = (0, 0)
SHIFT_INDEX = (0, 5)

Index = Tuple[int, int]


def find(sym: str) -> Tuple[int, int]:
    """
    Get the index of the provided character in the keyboard.

    Returns (x, y) indices of the symbol or None.
    """
    sym = sym.lower()
    for (y, row) in enumerate(KEYBOARD):
        for (x, char) in enumerate(row):
            if char == sym:
                return (x, y)
    return None


def index_dist(a: Tuple[int, int], b: Tuple[int, int]) -> int:
    """
    Get the minimum number of button presses required to go from a to b.
    """
    (ax, ay) = a
    (bx, by) = b
    dx = abs(ax - bx)
    # wrap horizontally
    if dx > 4:
        dx = 8 - dx

    dy = abs(ay - by)
    # wrap vertically
    if dy > 3:
        dy = 6 - dy
    return dx + dy


class State:
    """
    Current state of the keyboard.
    Contains the selected key index and the currently selected case.
    """

    def __init__(self) -> None:
        self.index = (0, 0)
        self.upper = False

    def walkTo(self, index: Index) -> int:
        """
        Perform all the necessary button clicks to get to provided index.
        Returns the minimum number of button presses required to get to provided character index.
        """
        steps = index_dist(self.index, index)
        self.index = index
        return steps

    def press(self, char: str) -> int:
        """
        Perform all the necessary button clicks to get to provided character.
        Returns the minimum number of button presses required to achieve the press.
        """
        steps = 0
        if char.isalpha() and (self.upper != char.isupper()):
            # Press SHIFT
            steps = self.walkTo(SHIFT_INDEX) + 1
            self.upper = not self.upper
        steps += self.walkTo(find(char)) + 1
        return steps


def tv_remote(str: str) -> int:
    """
    Get the minimum number of button presses required to type in the provided string.
    """
    # If the first character is upper case, we need to shift first
    state = State()
    count = 0
    for char in str:
        count += state.press(char)
    return count
