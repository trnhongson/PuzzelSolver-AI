# PuzzleSolver-AI 🧩🔍

**PuzzleSolver-AI** là đồ án môn Trí tuệ nhân tạo xây dựng bộ giải tự động cho bài toán **8-puzzle** và mở rộng **15-puzzle**, sử dụng thuật toán tìm kiếm có thông tin **A\*** kết hợp hai hàm heuristic (Manhattan Distance, Misplaced Tiles). Dự án tập trung vào việc **trực quan hoá từng bước giải** và **so sánh định lượng hiệu năng** giữa các heuristic.

## 🎯 Mục tiêu đề tài

- Cài đặt thuật toán A* tổng quát, áp dụng được cho cả 8-puzzle và 15-puzzle.
- So sánh hiệu năng (số node duyệt, thời gian chạy) giữa 2 heuristic: Manhattan Distance và Misplaced Tiles.
- Demo trực quan quá trình giải puzzle theo thời gian thực.
- Đánh giá khả năng mở rộng thuật toán khi tăng kích thước bài toán (8-puzzle → 15-puzzle).

## 📁 Cấu trúc dự án (Project Structure)

```
PuzzleSolver-AI/
├── src/
│   ├── core/
│   │   ├── puzzle_state.py       # Biểu diễn trạng thái bàn cờ, kiểm tra khả giải
│   │   ├── astar.py              # Cài đặt thuật toán A* tổng quát
│   │   ├── heuristics.py         # Hàm heuristic: Manhattan Distance & Misplaced Tiles
│   │   └── generator.py          # Sinh trạng thái ngẫu nhiên (seed cố định), dùng chung
│   │                              # cho cả demo/ và benchmark/ để tránh viết trùng code
│   │
│   ├── demo/
│   │   ├── main.py               # Điểm khởi chạy ứng dụng demo (Pygame)
│   │   ├── board_renderer.py     # Vẽ bàn cờ & hoạt ảnh từng bước giải
│   │   └── assets/                # Hình ảnh, font phục vụ giao diện demo
│   │
│   └── benchmark/
│       ├── run_benchmark.py      # Chạy benchmark trên bộ test case cố định, đo node/thời gian
│       ├── compare_heuristics.py # Tổng hợp & vẽ biểu đồ so sánh (Matplotlib)
│       ├── testcases_8puzzle.csv # Bộ ca thử 8-puzzle (sinh 1 lần bằng seed cố định)
│       ├── testcases_15puzzle.csv# Bộ ca thử 15-puzzle (sinh 1 lần bằng seed cố định)
│       └── results/               # File CSV/biểu đồ kết quả benchmark
│
├── tests/                         # Unit test cho core, heuristics, solvability check
├── docs/                          # Báo cáo, slide thuyết trình, tài liệu đặc tả
├── requirements.txt                # Danh sách thư viện Python cần cài đặt
├── .gitignore
└── README.md
```

> **Vì sao có `testcases_*.csv` thay vì sinh ngẫu nhiên mỗi lần chạy?**
> Bộ test case được sinh **một lần duy nhất** bằng seed cố định rồi lưu thành CSV, để kết quả benchmark trong báo cáo **tái lập được** — chạy lại bao nhiêu lần cũng ra cùng số liệu, tránh trường hợp biểu đồ trong báo cáo không khớp khi demo lại trước giám khảo.

## 🛠️ Công nghệ sử dụng (Tech Stack)

- **Ngôn ngữ:** Python 3.10+
- **Thuật toán:** A* Search, Heuristic Function Design
- **Giao diện demo:** Pygame
- **Phân tích & trực quan hoá dữ liệu:** Matplotlib, Pandas
- **Kiểm thử:** Pytest

## 🚀 Cài đặt & Chạy thử (Getting Started)

```bash
# 1. Clone repository
git clone https://github.com/<ten-nhom>/PuzzleSolver-AI.git
cd PuzzleSolver-AI

# 2. Tạo môi trường ảo (khuyến nghị)
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Cài đặt thư viện
pip install -r requirements.txt

# 4. Sinh bộ test case cố định (chỉ cần chạy 1 lần)
python src/core/generator.py --seed 42 --out src/benchmark/testcases_8puzzle.csv

# 5. Chạy demo trực quan
python src/demo/main.py

# 6. Chạy benchmark so sánh heuristic
python src/benchmark/run_benchmark.py
```
