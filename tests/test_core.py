import sys
import os
import unittest

# Đảm bảo đường dẫn gốc của project luôn nằm trong sys.path để không lỗi import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.puzzle_state import goal_state, is_solvable, get_neighbors


class TestGoalState(unittest.TestCase):
    def test_8puzzle(self):
        self.assertEqual(goal_state(3), (1, 2, 3, 4, 5, 6, 7, 8, 0))

    def test_15puzzle(self):
        self.assertEqual(
            goal_state(4),
            (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0),
        )

    def test_size_2(self):
        self.assertEqual(goal_state(2), (1, 2, 3, 0))


class TestIsSolvable(unittest.TestCase):
    # ── 8-puzzle (size=3, lưới lẻ) ────────────────────────────────────

    def test_goal_is_solvable(self):
        """Trạng thái đích luôn giải được."""
        self.assertTrue(is_solvable(goal_state(3), 3))

    def test_simple_solvable_8puzzle(self):
        """Trạng thái chỉ cần 1 bước để về đích."""
        state = (1, 2, 3, 4, 5, 6, 7, 0, 8)
        self.assertTrue(is_solvable(state, 3))

    def test_unsolvable_8puzzle(self):
        """Hoán đổi 2 ô bất kỳ từ goal → không giải được."""
        state = (2, 1, 3, 4, 5, 6, 7, 8, 0)
        self.assertFalse(is_solvable(state, 3))

    def test_known_solvable_8puzzle(self):
        """Trạng thái quen thuộc, biết chắc giải được."""
        state = (1, 2, 3, 4, 0, 5, 7, 8, 6)
        self.assertTrue(is_solvable(state, 3))

    # ── 15-puzzle (size=4, lưới chẵn) ─────────────────────────────────

    def test_goal_15puzzle_is_solvable(self):
        self.assertTrue(is_solvable(goal_state(4), 4))

    def test_unsolvable_15puzzle(self):
        """Hoán đổi 2 ô bất kỳ từ goal 15-puzzle → không giải được."""
        state = list(goal_state(4))
        state[0], state[1] = state[1], state[0]
        self.assertFalse(is_solvable(tuple(state), 4))

    def test_solvable_15puzzle_blank_at_end(self):
        self.assertTrue(is_solvable(goal_state(4), 4))


class TestGetNeighbors(unittest.TestCase):
    def test_blank_at_corner_top_left(self):
        state = (0, 1, 2, 3, 4, 5, 6, 7, 8)
        neighbors = get_neighbors(state, 3)
        self.assertEqual(len(neighbors), 2)

    def test_blank_at_center(self):
        state = (1, 2, 3, 4, 0, 5, 6, 7, 8)
        neighbors = get_neighbors(state, 3)
        self.assertEqual(len(neighbors), 4)

    def test_blank_at_edge(self):
        state = (1, 0, 2, 3, 4, 5, 6, 7, 8)
        neighbors = get_neighbors(state, 3)
        self.assertEqual(len(neighbors), 3)

    def test_blank_at_corner_bottom_right(self):
        neighbors = get_neighbors(goal_state(3), 3)
        self.assertEqual(len(neighbors), 2)

    def test_neighbor_content_is_correct(self):
        state = (1, 2, 3, 4, 0, 5, 6, 7, 8)
        neighbors = get_neighbors(state, 3)

        self.assertIn((1, 0, 3, 4, 2, 5, 6, 7, 8), neighbors)
        self.assertIn((1, 2, 3, 4, 7, 5, 6, 0, 8), neighbors)
        self.assertIn((1, 2, 3, 0, 4, 5, 6, 7, 8), neighbors)
        self.assertIn((1, 2, 3, 4, 5, 0, 6, 7, 8), neighbors)

    def test_all_neighbors_are_valid(self):
        state = (1, 2, 3, 4, 0, 5, 6, 7, 8)
        for neighbor in get_neighbors(state, 3):
            self.assertEqual(len(neighbor), 9)
            self.assertEqual(sorted(neighbor), list(range(9)))

    def test_15puzzle_blank_center(self):
        state = (1, 2, 3, 4, 5, 0, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)
        neighbors = get_neighbors(state, 4)
        self.assertEqual(len(neighbors), 4)
        for n in neighbors:
            self.assertEqual(len(n), 16)
            self.assertEqual(sorted(n), list(range(16)))


if __name__ == "__main__":
    unittest.main()
