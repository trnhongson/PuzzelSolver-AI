import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.core.astar import solve
from src.core.generator import random_walk_state
from src.core.heuristics import manhattan_distance, misplaced_tiles
from src.core.puzzle_state import goal_state, is_solvable


class TestHeuristics(unittest.TestCase):
    def test_goal_state_8puzzle_zero(self):
        goal = goal_state(3)
        self.assertEqual(manhattan_distance(goal, 3), 0)
        self.assertEqual(misplaced_tiles(goal, 3), 0)

    def test_goal_state_15puzzle_zero(self):
        goal = goal_state(4)
        self.assertEqual(manhattan_distance(goal, 4), 0)
        self.assertEqual(misplaced_tiles(goal, 4), 0)

    def test_one_move_from_goal_8puzzle(self):
        state = (1, 2, 3, 4, 5, 6, 7, 0, 8)
        self.assertEqual(manhattan_distance(state, 3), 1)
        self.assertEqual(misplaced_tiles(state, 3), 1)

    def test_blank_not_counted(self):
        state = (0, 2, 3, 4, 5, 6, 7, 8, 1)
        self.assertEqual(manhattan_distance(state, 3), 4)
        self.assertEqual(misplaced_tiles(state, 3), 1)

    def test_known_state_8puzzle(self):
        state = (8, 1, 3, 4, 0, 2, 7, 6, 5)
        self.assertEqual(manhattan_distance(state, 3), 10)
        self.assertEqual(misplaced_tiles(state, 3), 5)

    def test_manhattan_dominates_misplaced(self):
        states = [
            (1, 2, 3, 4, 0, 5, 7, 8, 6),
            (4, 1, 2, 5, 0, 3, 7, 8, 6),
            (8, 1, 3, 4, 0, 2, 7, 6, 5),
        ]
        for s in states:
            self.assertGreaterEqual(manhattan_distance(s, 3), misplaced_tiles(s, 3))


class TestGenerator(unittest.TestCase):
    def test_random_walk_8puzzle_solvable(self):
        for moves in (5, 10, 15, 20):
            state = random_walk_state(size=3, num_moves=moves, seed=42 + moves)
            self.assertIsInstance(state, tuple)
            self.assertEqual(len(state), 9)
            self.assertTrue(is_solvable(state, 3))

    def test_random_walk_15puzzle_solvable(self):
        for moves in (5, 10, 15, 20):
            state = random_walk_state(size=4, num_moves=moves, seed=100 + moves)
            self.assertIsInstance(state, tuple)
            self.assertEqual(len(state), 16)
            self.assertTrue(is_solvable(state, 4))

    def test_seed_reproducibility(self):
        s1 = random_walk_state(size=3, num_moves=15, seed=12345)
        s2 = random_walk_state(size=3, num_moves=15, seed=12345)
        self.assertEqual(s1, s2)

    def test_random_walk_solved_by_astar(self):
        state = random_walk_state(size=3, num_moves=12, seed=99)
        res_m = solve(state, 3, manhattan_distance)
        res_t = solve(state, 3, misplaced_tiles)
        self.assertTrue(res_m["solved"])
        self.assertTrue(res_t["solved"])
        self.assertEqual(len(res_m["path"]), len(res_t["path"]))
        self.assertLessEqual(res_m["nodes_expanded"], res_t["nodes_expanded"])


if __name__ == "__main__":
    unittest.main()
