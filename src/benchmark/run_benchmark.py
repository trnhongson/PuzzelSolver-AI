from __future__ import annotations

import argparse
import csv
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.core.astar import solve
from src.core.generator import generate_testcases
from src.core.heuristics import manhattan_distance, misplaced_tiles


def parse_state(state_str: str) -> tuple:
    """Chuyển chuỗi biểu diễn trạng thái trong CSV thành tuple các số nguyên."""
    cleaned = (
        state_str.strip()
        .replace("(", "")
        .replace(")", "")
        .replace("[", "")
        .replace("]", "")
        .replace(",", " ")
    )
    return tuple(int(x) for x in cleaned.split())


def load_testcases(csv_path: str) -> list[dict]:
    """Đọc danh sách test case từ file CSV."""
    cases: list[dict] = []
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cases.append(
                {
                    "case_id": row["case_id"],
                    "size": int(row["size"]),
                    "num_moves": int(row["num_moves"]),
                    "seed": int(row.get("seed", 0)),
                    "state": parse_state(row["state"]),
                }
            )
    return cases


def run_benchmark(
    testcases_8_path: str | None = None,
    testcases_15_path: str | None = None,
    output_csv_path: str | None = None,
    node_limit: int = 100_000,
    timeout_seconds: float = 5.0,
) -> str:
    """Chạy thuật toán A* với 2 hàm heuristic trên bộ test case 8-puzzle & 15-puzzle.

    Parameters
    ----------
    testcases_8_path : str | None
        Đường dẫn file CSV test case 8-puzzle.
    testcases_15_path : str | None
        Đường dẫn file CSV test case 15-puzzle.
    output_csv_path : str | None
        Đường dẫn lưu file kết quả ``benchmark_results.csv``.
    node_limit : int
        Giới hạn số node mở rộng tối đa cho mỗi lần chạy A*.
    timeout_seconds : float
        Giới hạn thời gian tối đa (giây) cho mỗi lần chạy A*.

    Returns
    -------
    str
        Đường dẫn tới file CSV kết quả đã lưu.
    """
    benchmark_dir = os.path.abspath(os.path.dirname(__file__))
    if testcases_8_path is None:
        testcases_8_path = os.path.join(benchmark_dir, "testcases_8puzzle.csv")
    if testcases_15_path is None:
        testcases_15_path = os.path.join(benchmark_dir, "testcases_15puzzle.csv")
    if output_csv_path is None:
        output_csv_path = os.path.join(benchmark_dir, "results", "benchmark_results.csv")

    if not os.path.exists(testcases_8_path) or not os.path.exists(testcases_15_path):
        generate_testcases(output_dir=benchmark_dir)

    all_cases: list[dict] = []
    if os.path.exists(testcases_8_path):
        all_cases.extend(load_testcases(testcases_8_path))
    if os.path.exists(testcases_15_path):
        all_cases.extend(load_testcases(testcases_15_path))

    heuristics = [
        ("Manhattan Distance", manhattan_distance),
        ("Misplaced Tiles", misplaced_tiles),
    ]

    results: list[dict] = []

    for case in all_cases:
        case_id = case["case_id"]
        size = case["size"]
        num_moves = case["num_moves"]
        state = case["state"]
        puzzle_type = "8-puzzle" if size == 3 else f"{size * size - 1}-puzzle"

        for h_name, h_fn in heuristics:
            res = solve(
                start_state=state,
                size=size,
                heuristic_fn=h_fn,
                node_limit=node_limit,
                timeout_seconds=timeout_seconds,
            )
            solution_steps = (
                len(res["path"]) - 1
                if res["solved"] and res["path"] is not None
                else -1
            )
            results.append(
                {
                    "case_id": case_id,
                    "puzzle_type": puzzle_type,
                    "size": size,
                    "num_moves": num_moves,
                    "heuristic": h_name,
                    "solved": res["solved"],
                    "stopped_reason": res["stopped_reason"],
                    "solution_length": solution_steps,
                    "nodes_expanded": res["nodes_expanded"],
                    "time_taken": round(res["time_taken"], 6),
                }
            )

    os.makedirs(os.path.dirname(os.path.abspath(output_csv_path)), exist_ok=True)
    fieldnames = [
        "case_id",
        "puzzle_type",
        "size",
        "num_moves",
        "heuristic",
        "solved",
        "stopped_reason",
        "solution_length",
        "nodes_expanded",
        "time_taken",
    ]

    with open(output_csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    return output_csv_path


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Chạy benchmark so sánh Manhattan Distance và Misplaced Tiles."
    )
    parser.add_argument(
        "--node-limit",
        type=int,
        default=100_000,
        help="Giới hạn số node mở rộng tối đa (mặc định: 100000).",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=5.0,
        help="Giới hạn thời gian chạy mỗi test case (giây, mặc định: 5.0).",
    )
    parser.add_argument(
        "--out",
        type=str,
        default=None,
        help="Đường dẫn file CSV kết quả đầu ra.",
    )
    args = parser.parse_args()

    out_path = run_benchmark(
        output_csv_path=args.out,
        node_limit=args.node_limit,
        timeout_seconds=args.timeout,
    )
    print(f"Đã hoàn thành benchmark. Kết quả được lưu tại: {out_path}")


if __name__ == "__main__":
    main()
