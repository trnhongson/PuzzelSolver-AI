from __future__ import annotations


def goal_state(size: int) -> tuple:
    """Trả về trạng thái đích cho bàn cờ *size x size*.

    Ví dụ:
        >>> goal_state(3)
        (1, 2, 3, 4, 5, 6, 7, 8, 0)
        >>> goal_state(4)
        (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0)
    """
    n = size * size
    return tuple(list(range(1, n)) + [0])


def _count_inversions(state: tuple) -> int:
    """Đếm số cặp đảo nghịch thế (inversions) trong *state*.

    Một cặp (a, b) được gọi là đảo nghịch thế nếu a xuất hiện trước b
    trong state nhưng a > b, bỏ qua ô trống (0).
    """
    tiles = [t for t in state if t != 0]
    inversions = 0
    for i in range(len(tiles)):
        for j in range(i + 1, len(tiles)):
            if tiles[i] > tiles[j]:
                inversions += 1
    return inversions


def is_solvable(state: tuple, size: int) -> bool:
    """Kiểm tra bàn cờ *state* (kích thước *size x size*) có giải được không.

    Quy tắc:
      - **size lẻ (ví dụ 3×3):** giải được khi số đảo nghịch thế là **chẵn**.
      - **size chẵn (ví dụ 4×4):** xét thêm vị trí hàng (tính từ dưới lên)
        của ô trống:
          + Nếu ô trống ở hàng chẵn (tính từ dưới lên, bắt đầu từ 1)
            → giải được khi số đảo nghịch thế là **lẻ**.
          + Nếu ô trống ở hàng lẻ (tính từ dưới lên)
            → giải được khi số đảo nghịch thế là **chẵn**.
    """
    inversions = _count_inversions(state)

    if size % 2 == 1:
        # Lưới lẻ: giải được khi inversions chẵn
        return inversions % 2 == 0
    else:
        # Lưới chẵn: cần xét vị trí hàng ô trống (tính từ dưới lên, bắt đầu từ 1)
        blank_index = state.index(0)
        blank_row_from_top = blank_index // size       # hàng tính từ trên xuống (0-indexed)
        blank_row_from_bottom = size - blank_row_from_top  # hàng tính từ dưới lên (1-indexed)

        if blank_row_from_bottom % 2 == 0:
            # Ô trống ở hàng chẵn (tính từ dưới) → inversions phải lẻ
            return inversions % 2 == 1
        else:
            # Ô trống ở hàng lẻ (tính từ dưới) → inversions phải chẵn
            return inversions % 2 == 0


def get_neighbors(state: tuple, size: int) -> list[tuple]:
    """Trả về danh sách các trạng thái kề có thể đi tới từ *state*.

    Di chuyển ô trống theo 4 hướng (lên, xuống, trái, phải).
    Bỏ qua các hướng đi ra ngoài bàn cờ.
    """
    neighbors: list[tuple] = []
    n = size * size
    blank = state.index(0)
    row, col = divmod(blank, size)

    # (delta_row, delta_col)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for dr, dc in directions:
        new_row, new_col = row + dr, col + dc
        if 0 <= new_row < size and 0 <= new_col < size:
            new_blank = new_row * size + new_col
            # Tạo trạng thái mới bằng cách hoán đổi ô trống và ô đích
            lst = list(state)
            lst[blank], lst[new_blank] = lst[new_blank], lst[blank]
            neighbors.append(tuple(lst))

    return neighbors
