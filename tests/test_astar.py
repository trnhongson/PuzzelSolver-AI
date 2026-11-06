import sys
import os
import unittest

# Đảm bảo đường dẫn gốc của project luôn nằm trong sys.path để không lỗi import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.puzzle_state import goal_state, is_solvable, get_neighbors
from src.core.astar import solve


# ── Heuristic mẫu để test A* độc lập ──────────────────────────────────

def _manhattan_distance(state: tuple, size: int) -> int:
    """Manhattan Distance."""
    goal = goal_state(size)
    distance = 0
    for i, tile in enumerate(state):
        if tile == 0:
            continue
        goal_idx = goal.index(tile)
        current_row, current_col = divmod(i, size)
        goal_row, goal_col = divmod(goal_idx, size)
        distance += abs(current_row - goal_row) + abs(current_col - goal_col)
    return distance


def _misplaced_tiles(state: tuple, size: int) -> int:
    """Misplaced Tiles."""
    goal = goal_state(size)
    return sum(1 for i in range(len(state)) if state[i] != 0 and state[i] != goal[i])


# ═══════════════════════════════════════════════════════════════════════
#  Test solve() — trường hợp cơ bản
# ═══════════════════════════════════════════════════════════════════════

class TestAStarBasic(unittest.TestCase):
    def test_already_solved(self):
        """Trạng thái đích → path chỉ gồm 1 phần tử."""
        result = solve(goal_state(3), 3, _manhattan_distance)
        self.assertTrue(result["solved"])
        self.assertEqual(result["stopped_reason"], "solved")
        self.assertEqual(result["path"], [goal_state(3)])
        self.assertEqual(result["nodes_expanded"], 0)

    def test_one_move(self):
        """Cần đúng 1 bước → path có 2 phần tử."""
        state = (1, 2, 3, 4, 5, 6, 7, 0, 8)
        result = solve(state, 3, _manhattan_distance)
        self.assertTrue(result["solved"])
        self.assertEqual(len(result["path"]), 2)
        self.assertEqual(result["path"][0], state)
        self.assertEqual(result["path"][-1], goal_state(3))

    def test_unsolvable_state(self):
        """Trạng thái không giải được → solved = False."""
        state = (2, 1, 3, 4, 5, 6, 7, 8, 0)
        self.assertFalse(is_solvable(state, 3))
        result = solve(state, 3, _manhattan_distance)
        self.assertFalse(result["solved"])
        self.assertEqual(result["stopped_reason"], "unsolvable")
        self.assertIsNone(result["path"])


# ═══════════════════════════════════════════════════════════════════════
#  Test solve() — tính tối ưu
# ═══════════════════════════════════════════════════════════════════════

class TestAStarOptimal(unittest.TestCase):
    def test_optimal_path_length_known_case(self):
        """Trạng thái có lời giải tối ưu đã biết trước (2 bước)."""
        state = (1, 2, 3, 4, 0, 5, 7, 8, 6)
        result = solve(state, 3, _manhattan_distance)
        self.assertTrue(result["solved"])
        self.assertEqual(len(result["path"]), 3)

    def test_path_starts_and_ends_correctly(self):
        state = (1, 2, 3, 4, 0, 5, 7, 8, 6)
        result = solve(state, 3, _manhattan_distance)
        self.assertEqual(result["path"][0], state)
        self.assertEqual(result["path"][-1], goal_state(3))

    def test_each_step_is_valid_neighbor(self):
        state = (1, 2, 3, 0, 4, 5, 7, 8, 6)
        result = solve(state, 3, _manhattan_distance)
        self.assertTrue(result["solved"])

        path = result["path"]
        for i in range(len(path) - 1):
            neighbors = get_neighbors(path[i], 3)
            self.assertIn(
                path[i + 1],
                neighbors,
                f"Bước {i} -> {i+1} không phải neighbor hợp lệ: {path[i]} -> {path[i+1]}",
            )


# ═══════════════════════════════════════════════════════════════════════
#  Test solve() — cả 2 heuristic
# ═══════════════════════════════════════════════════════════════════════

class TestAStarBothHeuristics(unittest.TestCase):
    def test_both_heuristics_find_same_optimal_length(self):
        """Cả Manhattan và Misplaced Tiles đều tìm được lời giải có cùng độ dài tối ưu."""
        state = (1, 2, 3, 4, 0, 5, 7, 8, 6)
        res_m = solve(state, 3, _manhattan_distance)
        res_t = solve(state, 3, _misplaced_tiles)
        self.assertTrue(res_m["solved"])
        self.assertTrue(res_t["solved"])
        self.assertEqual(len(res_m["path"]), len(res_t["path"]))

    def test_medium_difficulty_manhattan(self):
        state = (4, 1, 2, 5, 0, 3, 7, 8, 6)
        result = solve(state, 3, _manhattan_distance)
        self.assertTrue(result["solved"])
        self.assertEqual(result["path"][-1], goal_state(3))

    def test_medium_difficulty_misplaced(self):
        state = (4, 1, 2, 5, 0, 3, 7, 8, 6)
        result = solve(state, 3, _misplaced_tiles)
        self.assertTrue(result["solved"])
        self.assertEqual(result["path"][-1], goal_state(3))


# ═══════════════════════════════════════════════════════════════════════
#  Test solve() — giới hạn an toàn (node_limit / timeout)
# ═══════════════════════════════════════════════════════════════════════

class TestAStarSafetyLimits(unittest.TestCase):
    def test_node_limit_stops_search(self):
        """Khi node_limit rất nhỏ, thuật toán phải dừng do chạm node_limit."""
        state = (4, 1, 2, 5, 0, 3, 7, 8, 6)
        result = solve(state, 3, _manhattan_distance, node_limit=1)
        self.assertIn("nodes_expanded", result)
        self.assertIn("stopped_reason", result)
        self.assertFalse(result["solved"])
        self.assertEqual(result["stopped_reason"], "node_limit")

    def test_timeout_stops_search(self):
        """Khi timeout cực nhỏ, thuật toán dừng sớm do timeout hoặc giải xong kịp."""
        state = (4, 1, 2, 5, 0, 3, 7, 8, 6)
        result = solve(state, 3, _manhattan_distance, timeout_seconds=0.000001)
        self.assertIn("stopped_reason", result)
        if not result["solved"]:
            self.assertEqual(result["stopped_reason"], "timeout")

    def test_result_dict_keys(self):
        """Kết quả trả về phải có đúng các key theo spec."""
        state = (1, 2, 3, 4, 5, 6, 7, 0, 8)
        result = solve(state, 3, _manhattan_distance)
        expected_keys = {"path", "nodes_expanded", "time_taken", "solved", "stopped_reason"}
        self.assertEqual(set(result.keys()), expected_keys)


# ═══════════════════════════════════════════════════════════════════════
#  Test solve() — 15-puzzle đơn giản
# ═══════════════════════════════════════════════════════════════════════

class TestAStar15Puzzle(unittest.TestCase):
    def test_15puzzle_one_move(self):
        goal = goal_state(4)
        state = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 0, 15)
        result = solve(state, 4, _manhattan_distance)
        self.assertTrue(result["solved"])
        self.assertEqual(len(result["path"]), 2)
        self.assertEqual(result["path"][-1], goal)

    def test_15puzzle_goal(self):
        result = solve(goal_state(4), 4, _manhattan_distance)
        self.assertTrue(result["solved"])
        self.assertEqual(len(result["path"]), 1)


if __name__ == "__main__":
    unittest.main()
