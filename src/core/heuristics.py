from __future__ import annotations


def manhattan_distance(state: tuple, size: int) -> int:
    """Tính tổng khoảng cách Manhattan của các ô số tới vị trí đích.

    Parameters
    ----------
    state : tuple
        Trạng thái bàn cờ hiện tại (dạng tuple 1D, số 0 là ô trống).
    size : int
        Kích thước cạnh bàn cờ (3 cho 8-puzzle, 4 cho 15-puzzle).

    Returns
    -------
    int
        Tổng khoảng cách Manhattan (không tính ô trống 0).
    """
    distance = 0
    for idx, tile in enumerate(state):
        if tile == 0:
            continue
        current_row, current_col = divmod(idx, size)
        goal_row, goal_col = divmod(tile - 1, size)
        distance += abs(current_row - goal_row) + abs(current_col - goal_col)
    return distance


def misplaced_tiles(state: tuple, size: int) -> int:
    """Đếm số ô nằm sai vị trí so với trạng thái đích (không tính ô trống 0).

    Parameters
    ----------
    state : tuple
        Trạng thái bàn cờ hiện tại (dạng tuple 1D, số 0 là ô trống).
    size : int
        Kích thước cạnh bàn cờ (3 cho 8-puzzle, 4 cho 15-puzzle).

    Returns
    -------
    int
        Số lượng ô số bị đặt sai vị trí.
    """
    count = 0
    for idx, tile in enumerate(state):
        if tile != 0 and tile != idx + 1:
            count += 1
    return count
