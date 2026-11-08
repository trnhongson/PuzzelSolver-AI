from __future__ import annotations

import argparse
import csv
import os
import random
import sys
from typing import Sequence

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.core.puzzle_state import get_neighbors, goal_state


def random_walk_state(
    size: int,
    num_moves: int,
    seed: int | None = None,
) -> tuple:
    """Sinh trạng thái giải được bằng cách đi ngẫu nhiên từ trạng thái đích.

    Parameters
    ----------
    size : int
        Kích thước cạnh bàn cờ (3 cho 8-puzzle, 4 cho 15-puzzle).
    num_moves : int
        Số bước di chuyển ngẫu nhiên lùi từ trạng thái đích.
    seed : int | None, optional
        Seed cho bộ sinh số ngẫu nhiên để đảm bảo tính tái lập.

    Returns
    -------
    tuple
        Trạng thái bàn cờ sau ``num_moves`` bước di chuyển hợp lệ.
    """
    if num_moves < 0:
        raise ValueError("num_moves phải là số nguyên không âm.")

    rng = random.Random(seed)
    goal = goal_state(size)
    current = goal
    prev_state: tuple | None = None

    for _ in range(num_moves):
        neighbors = get_neighbors(current, size)
        candidates = [n for n in neighbors if n != prev_state]
        if not candidates:
            candidates = neighbors
        next_state = rng.choice(candidates)
        prev_state = current
        current = next_state

    if num_moves > 0 and current == goal:
        neighbors = get_neighbors(current, size)
        current = rng.choice(neighbors)

    return current


def generate_testcases(
    output_dir: str | None = None,
    seed: int = 42,
    moves_8puzzle: Sequence[int] = (5, 10, 15, 20, 25),
    moves_15puzzle: Sequence[int] = (5, 10, 15, 20, 25),
    cases_per_level: int = 5,
    out_8puzzle: str | None = None,
    out_15puzzle: str | None = None,
) -> dict[str, str]:
    """Sinh bộ test case chuẩn cho 8-puzzle và 15-puzzle và lưu ra file CSV.

    Parameters
    ----------
    output_dir : str | None
        Thư mục chứa các file CSV đầu ra (mặc định là ``src/benchmark``).
    seed : int
        Seed gốc để sinh dữ liệu cố định, tái lập được.
    moves_8puzzle : Sequence[int]
        Các mức số bước xáo trộn cho 8-puzzle.
    moves_15puzzle : Sequence[int]
        Các mức số bước xáo trộn cho 15-puzzle.
    cases_per_level : int
        Số lượng test case sinh ra cho mỗi mức ``num_moves``.
    out_8puzzle : str | None
        Đường dẫn file CSV cho 8-puzzle (nếu muốn chỉ định cụ thể).
    out_15puzzle : str | None
        Đường dẫn file CSV cho 15-puzzle (nếu muốn chỉ định cụ thể).

    Returns
    -------
    dict[str, str]
        Dictionary chứa đường dẫn của 2 file CSV đã tạo.
    """
    if output_dir is None:
        output_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "benchmark")
        )
    os.makedirs(output_dir, exist_ok=True)

    path_8 = out_8puzzle or os.path.join(output_dir, "testcases_8puzzle.csv")
    path_15 = out_15puzzle or os.path.join(output_dir, "testcases_15puzzle.csv")

    _write_testcase_csv(
        filepath=path_8,
        size=3,
        moves_levels=moves_8puzzle,
        cases_per_level=cases_per_level,
        base_seed=seed,
    )
    _write_testcase_csv(
        filepath=path_15,
        size=4,
        moves_levels=moves_15puzzle,
        cases_per_level=cases_per_level,
        base_seed=seed + 1000,
    )

    return {"8puzzle": path_8, "15puzzle": path_15}


def _write_testcase_csv(
    filepath: str,
    size: int,
    moves_levels: Sequence[int],
    cases_per_level: int,
    base_seed: int,
) -> None:
    """Ghi danh sách test case của một kích thước bàn cờ ra file CSV."""
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    fieldnames = ["case_id", "size", "num_moves", "seed", "state"]

    rows: list[dict] = []
    case_idx = 1
    for moves in moves_levels:
        for i in range(cases_per_level):
            case_seed = base_seed + moves * 100 + i
            state = random_walk_state(size=size, num_moves=moves, seed=case_seed)
            state_str = " ".join(str(x) for x in state)
            rows.append(
                {
                    "case_id": f"{size}x{size}_{case_idx:02d}",
                    "size": size,
                    "num_moves": moves,
                    "seed": case_seed,
                    "state": state_str,
                }
            )
            case_idx += 1

    with open(filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Sinh bộ test case cố định cho 8-puzzle và 15-puzzle."
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Seed cố định để tái lập bộ test case (mặc định: 42).",
    )
    parser.add_argument(
        "--out",
        type=str,
        default=None,
        help="Đường dẫn file CSV đầu ra (tùy chọn).",
    )
    parser.add_argument(
        "--cases-per-level",
        type=int,
        default=5,
        help="Số lượng test case cho mỗi mức độ khó (mặc định: 5).",
    )
    args = parser.parse_args()

    if args.out:
        out_abs = os.path.abspath(args.out)
        out_dir = os.path.dirname(out_abs)
        basename = os.path.basename(out_abs).lower()
        if "15" in basename:
            paths = generate_testcases(
                output_dir=out_dir,
                seed=args.seed,
                cases_per_level=args.cases_per_level,
                out_15puzzle=out_abs,
            )
        else:
            paths = generate_testcases(
                output_dir=out_dir,
                seed=args.seed,
                cases_per_level=args.cases_per_level,
                out_8puzzle=out_abs,
            )
    else:
        paths = generate_testcases(
            seed=args.seed,
            cases_per_level=args.cases_per_level,
        )

    print(f"Đã tạo test cases 8-puzzle : {paths['8puzzle']}")
    print(f"Đã tạo test cases 15-puzzle: {paths['15puzzle']}")


if __name__ == "__main__":
    main()
