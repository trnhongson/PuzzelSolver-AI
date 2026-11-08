from __future__ import annotations

import heapq
import time
from typing import Callable

from src.core.puzzle_state import goal_state, get_neighbors, is_solvable


def solve(
    start_state: tuple,
    size: int,
    heuristic_fn: Callable[[tuple, int], int],
    node_limit: int = 200_000,
    timeout_seconds: float = 10.0,
) -> dict:
    """Giải bài toán puzzle bằng thuật toán A*.

    Parameters
    ----------
    start_state : tuple
        Trạng thái bắt đầu, ví dụ ``(1, 2, 3, 4, 0, 5, 7, 8, 6)`` cho 8-puzzle.
    size : int
        Kích thước bàn cờ (3 cho 8-puzzle, 4 cho 15-puzzle).
    heuristic_fn : Callable[[tuple, int], int]
        Hàm heuristic dạng ``heuristic_fn(state, size) -> int``
        (ví dụ: ``manhattan_distance`` hoặc ``misplaced_tiles``).
    node_limit : int
        Giới hạn số node được mở rộng (expand). Nếu vượt quá, dừng sớm.
    timeout_seconds : float
        Giới hạn thời gian chạy (giây). Nếu vượt quá, dừng sớm.

    Returns
    -------
    dict
        ``path``            – list các trạng thái từ start đến goal (hoặc None).
        ``nodes_expanded``  – số node đã được mở rộng.
        ``time_taken``      – thời gian chạy (giây).
        ``solved``          – True nếu tìm được lời giải.
        ``stopped_reason``  – ``"solved"`` | ``"node_limit"`` | ``"timeout"``
                              | ``"unsolvable"``
    """
    goal = goal_state(size)

    # ── Kiểm tra nhanh: trạng thái không giải được ─────────────────────
    if not is_solvable(start_state, size):
        return {
            "path": None,
            "nodes_expanded": 0,
            "time_taken": 0.0,
            "solved": False,
            "stopped_reason": "unsolvable",
        }

    # ── Trường hợp đặc biệt: đã ở trạng thái đích ────────────────────
    if start_state == goal:
        return {
            "path": [start_state],
            "nodes_expanded": 0,
            "time_taken": 0.0,
            "solved": True,
            "stopped_reason": "solved",
        }

    # ── Khởi tạo A* ───────────────────────────────────────────────────
    start_time = time.perf_counter()

    # g_score: chi phí thực tế từ start đến node hiện tại
    g_score: dict[tuple, int] = {start_state: 0}

    # came_from: truy vết đường đi
    came_from: dict[tuple, tuple | None] = {start_state: None}

    # Priority queue: (f_score, tie_breaker, state)
    # tie_breaker dùng để đảm bảo thứ tự ổn định khi f bằng nhau
    counter = 0
    h_start = heuristic_fn(start_state, size)
    open_set: list[tuple[int, int, tuple]] = [(h_start, counter, start_state)]

    # Tập đóng (closed set) — các node đã được mở rộng
    closed_set: set[tuple] = set()

    nodes_expanded = 0

    # ── Vòng lặp chính A* ─────────────────────────────────────────────
    while open_set:
        # Kiểm tra timeout
        elapsed = time.perf_counter() - start_time
        if elapsed >= timeout_seconds:
            return {
                "path": None,
                "nodes_expanded": nodes_expanded,
                "time_taken": elapsed,
                "solved": False,
                "stopped_reason": "timeout",
            }

        # Kiểm tra node_limit
        if nodes_expanded >= node_limit:
            return {
                "path": None,
                "nodes_expanded": nodes_expanded,
                "time_taken": time.perf_counter() - start_time,
                "solved": False,
                "stopped_reason": "node_limit",
            }

        # Lấy node có f nhỏ nhất
        f_current, _, current = heapq.heappop(open_set)

        # Bỏ qua nếu đã mở rộng trước đó (có thể bị thêm nhiều lần vào heap)
        if current in closed_set:
            continue

        # Đánh dấu đã mở rộng
        closed_set.add(current)
        nodes_expanded += 1

        # Kiểm tra đích
        if current == goal:
            path = _reconstruct_path(came_from, current)
            return {
                "path": path,
                "nodes_expanded": nodes_expanded,
                "time_taken": time.perf_counter() - start_time,
                "solved": True,
                "stopped_reason": "solved",
            }

        # Mở rộng các neighbor
        current_g = g_score[current]
        for neighbor in get_neighbors(current, size):
            if neighbor in closed_set:
                continue

            tentative_g = current_g + 1  # chi phí mỗi bước = 1

            if tentative_g < g_score.get(neighbor, float("inf")):
                # Tìm được đường tốt hơn đến neighbor
                g_score[neighbor] = tentative_g
                came_from[neighbor] = current
                f_score = tentative_g + heuristic_fn(neighbor, size)
                counter += 1
                heapq.heappush(open_set, (f_score, counter, neighbor))

    # ── Hết open_set mà không tìm được lời giải (không nên xảy ra
    #    nếu is_solvable đã lọc đúng) ──────────────────────────────────
    return {
        "path": None,
        "nodes_expanded": nodes_expanded,
        "time_taken": time.perf_counter() - start_time,
        "solved": False,
        "stopped_reason": "no_solution",
    }


def _reconstruct_path(
    came_from: dict[tuple, tuple | None], current: tuple
) -> list[tuple]:
    """Truy vết đường đi từ ``came_from`` map, trả về list trạng thái
    từ start → goal."""
    path: list[tuple] = [current]
    while came_from[current] is not None:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path
