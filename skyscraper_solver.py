# A programatic solver for skyscrapers puzzle (see https://brainbashers.com/skyscrapers.asp )
#
# Given an N*N board and clues that give the number of skyscrapers seen in a row or a column
# from the size figure out where each of the skyscraper lies.
# Each row and column should contain all possible heights of skyscrapers. Skyscrapers come
# in N different heights and taller (larger) skyscrapers hide lower ones behind them.

from typing import Callable, Iterable, List, MutableSequence, Optional, Tuple

# (clue, solution) pairs
EXAMPLE_PUZZLES = (
    (
        (2, 2, 1, 3, 2, 2, 3, 1, 1, 2, 2, 3, 3, 2, 1, 3),
        (
            (1, 3, 4, 2),
            (4, 2, 1, 3),
            (3, 4, 2, 1),
            (2, 1, 3, 4),
        ),
    ),
    (
        (0, 0, 1, 2, 0, 2, 0, 0, 0, 3, 0, 0, 0, 1, 0, 0),
        (
            (2, 1, 4, 3),
            (3, 4, 1, 2),
            (4, 2, 3, 1),
            (1, 3, 2, 4),
        ),
    ),
)


def vals_to_str(vals: List[int], padding=0) -> str:
    """
    Convert a list of values into a string of provided length.
    """
    prefix = " " * max(0, padding - len(vals))
    return prefix + "".join(str(v) for v in vals)


def row_to_str(row: Iterable[List[int]], padding=0) -> str:
    """
    Convert a row of possible values to a string.
    """
    return ", ".join(vals_to_str(vals, padding) for vals in row)


def filter_mut(seq: MutableSequence, pred: Optional[Callable] = None):
    """
    Filter a sequence in-place removing any elements that pass provided predicate.
    If no predicate is provided removes all truthy elements.
    Returns number of elements removed.
    """
    if pred is None:
        pred = lambda x: bool(x)

    count = 0
    for i in reversed(range(len(seq))):
        if pred(seq[i]):
            seq.pop(i)
            count += 1

    return count


class State:
    """
    State stores possible values for each of the skyscraper at a given position
    and provides a convenient way to retreive said values with 2 indices.
    """

    def __init__(self, n: int) -> None:
        self.n = n
        self._vals = [[i + 1 for i in range(n)] for x in range(n ** 2)]

    def _index(self, indices: Tuple[int, int]) -> int:
        """
        Get the flat index from combined indices.
        """
        if not isinstance(indices, tuple):
            raise TypeError
        if len(indices) != 2:
            raise KeyError
        if any(
            (
                indices[0] < 0,
                indices[0] >= self.n,
                indices[1] < 0,
                indices[1] >= self.n,
            )
        ):
            raise IndexError
        return indices[1] * self.n + indices[0]

    def __getitem__(self, indices: Tuple[int, int]) -> List[int]:
        return self._vals[self._index(indices)]

    def __setitem__(self, indices: Tuple[int, int], value: List[int]) -> None:
        if not isinstance(value, list):
            raise TypeError
        self._vals[self._index(indices)] = value

    def __str__(self) -> str:
        padding = max(len(vals) for vals in self._vals)
        return "\n".join(row_to_str(row, padding) for row in self.rows())

    def row(self, y: int):
        for x in range(self.n):
            yield self[x, y]

    def col(self, x: int):
        for y in range(self.n):
            yield self[x, y]

    def rows(self):
        for y in range(self.n):
            yield self.row(y)

    def cols(self):
        for x in range(self.n):
            yield self.col(x)

    def eliminate_row(self, val: int, y: int) -> int:
        """
        Eliminate provided value from the provided row in the state.
        Returns number of elements eliminated from the row.
        """
        count = 0
        for vals in self.row(y):
            count += filter_mut(vals, lambda x: x == val)
        return count

    def eliminate_col(self, val: int, x: int) -> int:
        """
        Eliminate provided value from the provided column in the state.
        Returns number of elements eliminated from the row.
        """
        count = 0
        for vals in self.col(x):
            count += filter_mut(vals, lambda x: x == val)
        return count

    def count_in_row(self, val: int, y: int) -> int:
        """
        Count the number of occurrences of provided value in the given row.
        """
        count = 0
        for vals in self.row(y):
            count += int(val in vals)
        return count

    def count_in_col(self, val: int, x: int) -> int:
        """
        Count the number of occurrences of provided value in the given column.
        """
        count = 0
        for vals in self.col(x):
            count += int(val in vals)
        return count

    def pin(self, val: int, x: int, y: int) -> int:
        """
        Fix a given value at provided index.
        Eliminates the value from the column and row.
        Returns the number of cells the value was eliminated from.
        """
        assert val in self[x, y]
        count = self.eliminate_col(val, x) + self.eliminate_row(val, y)
        self[x, y].append(val)
        # The value was re-introduced after elimination
        return count - 1

    def pin_singles(self) -> int:
        """
        Pin any values that occur once in a row or a column.
        Returns number of values pinned.
        """
        count = 0
        for y in range(self.n):
            for x in range(self.n):
                if len(self[x, y]) > 1:
                    for val in self[x, y]:
                        if (
                            self.count_in_col(val, x) == 1
                            or self.count_in_row(val, y) == 1
                        ):
                            self.pin(val, x, y)
                            count += 1
        return count

    def prune(self) -> int:
        """
        Eliminate any values that contradict pinned ones.
        """
        count = 0
        for y in range(self.n):
            for x in range(self.n):
                if len(self[x, y]) == 1:
                    val = self[x, y][0]
                    # take 1 as the value will have been eliminated from the allowed cell
                    count += self.eliminate_col(val, x) + self.eliminate_row(val, y) - 1
                    self[x, y].append(val)
        return count

    def apply_clue_edges(self, clues: List[int]) -> None:
        """
        Eliminate values that vialate the following constraint:
        (value + clue <= N + 2 + distance)
        where distance is number cells between the clue and a cell.
        """
        assert len(clues) == self.n * 4

        # top->bottom clues
        for i, clue in enumerate(clues[self.n * 0 : self.n * 1]):
            if clue == 0:
                continue
            for values in self.col(i):
                dist = i
                filter_mut(values, lambda x: x + clue > self.n + 2 + dist)

        # right->left
        for i, clue in enumerate(clues[self.n * 1 : self.n * 2]):
            if clue == 0:
                continue
            for values in self.row(i):
                dist = self.n - i - 1
                filter_mut(values, lambda x: x + clue > self.n + 2 + dist)

        # bottom->top
        for i, clue in enumerate(clues[self.n * 2 : self.n * 3]):
            if clue == 0:
                continue
            for values in self.col(self.n - i - 1):
                dist = self.n - i - 1
                filter_mut(values, lambda x: x + clue > self.n + 2 + dist)

        # left->right
        for i, clue in enumerate(clues[self.n * 3 : self.n * 4]):
            if clue == 0:
                continue
            for values in self.row(self.n - i - 1):
                dist = i
                filter_mut(values, lambda x: x + clue > self.n + 2 + dist)

    def collapse(self) -> Tuple[Tuple[int]]:
        """
        Convert a solution state into a tuple grid of result values.
        """
        return (tuple(row) for row in self.rows())


if __name__ == "__main__":
    for clues, expected_result in EXAMPLE_PUZZLES:
        state = State(4)
        state.apply_clue_edges(clues)
        print(state)
        # assert state.collapse() == expected_result
