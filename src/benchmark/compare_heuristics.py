from __future__ import annotations

import argparse
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


def compare_heuristics(
    results_csv_path: str | None = None,
    output_dir: str | None = None,
) -> dict[str, str]:
    """Đọc file kết quả benchmark và vẽ 2 biểu đồ so sánh hiệu năng 2 heuristic.

    Parameters
    ----------
    results_csv_path : str | None
        Đường dẫn tới file ``benchmark_results.csv``.
    output_dir : str | None
        Thư mục lưu các ảnh biểu đồ ``.png``.

    Returns
    -------
    dict[str, str]
        Đường dẫn tới 2 file ảnh biểu đồ đã lưu.
    """
    benchmark_dir = os.path.abspath(os.path.dirname(__file__))
    if output_dir is None:
        output_dir = os.path.join(benchmark_dir, "results")
    os.makedirs(output_dir, exist_ok=True)

    if results_csv_path is None:
        candidate = os.path.join(output_dir, "benchmark_results.csv")
        if os.path.exists(candidate):
            results_csv_path = candidate
        else:
            results_csv_path = os.path.join(benchmark_dir, "benchmark_results.csv")

    if not os.path.exists(results_csv_path):
        raise FileNotFoundError(
            f"Không tìm thấy file kết quả benchmark tại: {results_csv_path}. "
            "Hãy chạy src/benchmark/run_benchmark.py trước."
        )

    df = pd.read_csv(results_csv_path)

    summary = (
        df.groupby(["puzzle_type", "num_moves", "heuristic"], as_index=False)
        .agg(
            avg_nodes=("nodes_expanded", "mean"),
            avg_time=("time_taken", "mean"),
        )
        .sort_values(["puzzle_type", "num_moves", "heuristic"])
    )

    puzzle_types = [pt for pt in ["8-puzzle", "15-puzzle"] if pt in summary["puzzle_type"].unique()]
    if not puzzle_types:
        puzzle_types = list(summary["puzzle_type"].unique())

    nodes_chart_path = os.path.join(output_dir, "nodes_comparison.png")
    time_chart_path = os.path.join(output_dir, "time_comparison.png")

    _plot_metric(
        summary=summary,
        puzzle_types=puzzle_types,
        metric_col="avg_nodes",
        ylabel="Số node mở rộng trung bình (Nodes)",
        suptitle="So sánh Số Node Duyệt Trung Bình: Manhattan Distance vs Misplaced Tiles",
        output_path=nodes_chart_path,
    )

    _plot_metric(
        summary=summary,
        puzzle_types=puzzle_types,
        metric_col="avg_time",
        ylabel="Thời gian chạy trung bình (Giây)",
        suptitle="So sánh Thời Gian Chạy Trung Bình: Manhattan Distance vs Misplaced Tiles",
        output_path=time_chart_path,
    )

    return {
        "nodes_chart": nodes_chart_path,
        "time_chart": time_chart_path,
    }


def _plot_metric(
    summary: pd.DataFrame,
    puzzle_types: list[str],
    metric_col: str,
    ylabel: str,
    suptitle: str,
    output_path: str,
) -> None:
    """Vẽ biểu đồ cột nhóm (grouped bar chart) kèm đường xu hướng cho metric."""
    num_plots = len(puzzle_types)
    fig, axes = plt.subplots(1, num_plots, figsize=(7 * num_plots, 5.5), squeeze=False)
    fig.suptitle(suptitle, fontsize=14, fontweight="bold", y=0.98)

    colors = {
        "Manhattan Distance": "#2563EB",
        "Misplaced Tiles": "#F97316",
    }

    for idx, ptype in enumerate(puzzle_types):
        ax = axes[0, idx]
        sub = summary[summary["puzzle_type"] == ptype]
        moves_list = sorted(sub["num_moves"].unique())
        heuristics = sorted(sub["heuristic"].unique())

        width = 0.35
        x_positions = list(range(len(moves_list)))

        for h_idx, h_name in enumerate(heuristics):
            h_data = sub[sub["heuristic"] == h_name].set_index("num_moves")
            values = [float(h_data.loc[m, metric_col]) if m in h_data.index else 0.0 for m in moves_list]
            offset = (h_idx - (len(heuristics) - 1) / 2) * width
            bar_x = [x + offset for x in x_positions]
            bars = ax.bar(
                bar_x,
                values,
                width=width,
                label=h_name,
                color=colors.get(h_name, None),
                alpha=0.9,
                edgecolor="#1E293B",
                linewidth=0.7,
            )
            for bar, val in zip(bars, values):
                label_text = f"{val:.0f}" if metric_col == "avg_nodes" else f"{val:.4f}s"
                ax.annotate(
                    label_text,
                    xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                    xytext=(0, 5),
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                    fontsize=8.5,
                    fontweight="medium",
                )

        max_y = float(sub[metric_col].max()) if not sub.empty else 1.0
        ax.set_ylim(0, max_y * 1.16 if max_y > 0 else 1.0)
        ax.set_title(f"Bài toán {ptype}", fontsize=12, fontweight="bold", pad=10)
        ax.set_xlabel("Số bước xáo trộn từ đích (num_moves)", fontsize=10)
        ax.set_ylabel(ylabel, fontsize=10)
        ax.set_xticks(x_positions)
        ax.set_xticklabels([str(m) for m in moves_list])
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        ax.legend(frameon=True, fontsize=9, loc="upper left")

    plt.tight_layout(rect=[0, 0, 1, 0.93])
    plt.savefig(output_path, dpi=150)
    plt.close(fig)


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Vẽ biểu đồ so sánh hiệu năng giữa các hàm heuristic."
    )
    parser.add_argument(
        "--input",
        type=str,
        default=None,
        help="Đường dẫn tới file benchmark_results.csv.",
    )
    parser.add_argument(
        "--out-dir",
        type=str,
        default=None,
        help="Thư mục xuất ảnh biểu đồ .png.",
    )
    args = parser.parse_args()

    charts = compare_heuristics(
        results_csv_path=args.input,
        output_dir=args.out_dir,
    )
    print(f"Đã lưu biểu đồ số node duyệt : {charts['nodes_chart']}")
    print(f"Đã lưu biểu đồ thời gian chạy: {charts['time_chart']}")


if __name__ == "__main__":
    main()
