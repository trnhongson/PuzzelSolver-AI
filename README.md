<div align="center">
  <h1>PuzzleSolver-AI - Bộ giải 8-Puzzle / 15-Puzzle bằng A* và So sánh Heuristic</h1>
  <p><em>
    <b>Đề tài:</b> Bộ giải bài toán 8-puzzle / 15-puzzle, tìm lời giải tối ưu và so sánh hiệu năng các hàm heuristic <br>
    <b>Môn học:</b> Trí tuệ nhân tạo
  </em></p>
  <p>
    <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+"/>
    <img src="https://img.shields.io/badge/Pygame-000000?style=for-the-badge&logo=python&logoColor=white" alt="Pygame"/>
    <img src="https://img.shields.io/badge/Matplotlib-11557c?style=for-the-badge&logo=plotly&logoColor=white" alt="Matplotlib"/>
    <img src="https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white" alt="Pandas"/>
    <img src="https://img.shields.io/badge/Pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white" alt="Pytest"/>
  </p>
</div>

---

## Mục lục

1. [Giới thiệu đề tài (Introduction)](#giới-thiệu-đề-tài-introduction)
2. [Danh sách thành viên nhóm & Phân công nhiệm vụ (Members & Tasks)](#danh-sách-thành-viên-nhóm--phân-công-nhiệm-vụ-members--tasks)
3. [Tiến độ triển khai dự án (Project Progress)](#tiến-độ-triển-khai-dự-án-project-progress)
4. [Công nghệ sử dụng (Tech Stack)](#công-nghệ-sử-dụng-tech-stack)
5. [Cấu trúc thư mục (Project Structure)](#cấu-trúc-thư-mục-project-structure)
6. [Cách chạy (How to Run)](#cách-chạy-how-to-run)
   - [1. Yêu cầu môi trường](#1-yêu-cầu-môi-trường)
   - [2. Clone mã nguồn](#2-clone-mã-nguồn)
   - [3. Cài đặt & chạy chương trình](#3-cài-đặt--chạy-chương-trình)
   - [4. Chạy bộ kiểm thử tự động](#4-chạy-bộ-kiểm-thử-tự-động)

---

## Giới thiệu đề tài (Introduction)

**PuzzleSolver-AI** xây dựng bộ giải tự động cho bài toán **8-puzzle** và mở rộng **15-puzzle**, sử dụng thuật toán tìm kiếm có thông tin **A\*** kết hợp hai hàm heuristic khác nhau, kèm module trực quan hoá từng bước giải và module đo lường/so sánh hiệu năng.

### 1. Bài toán
- 8-puzzle/15-puzzle là bài toán kinh điển trong AI: từ một bàn cờ xáo trộn ngẫu nhiên, tìm chuỗi di chuyển ngắn nhất để đưa về trạng thái đích.
- Thách thức chính: không gian trạng thái tăng rất nhanh khi mở rộng từ 8-puzzle (3x3) sang 15-puzzle (4x4), đòi hỏi heuristic tốt để thuật toán tìm kiếm không bị "bùng nổ tổ hợp".

### 2. Giải pháp cốt lõi
- **Thuật toán A\* tổng quát**: áp dụng được cho cả 8-puzzle lẫn 15-puzzle thông qua cùng một cách biểu diễn trạng thái.
- **Hai hàm heuristic để so sánh**: Manhattan Distance và Misplaced Tiles, dùng để đo lường và so sánh định lượng số node được duyệt cũng như thời gian chạy giữa hai cách tiếp cận.
- **Sinh đề tự động có kiểm soát độ khó**: trạng thái được sinh bằng random walk có giới hạn số bước từ trạng thái đích, đảm bảo luôn giải được và kiểm soát được độ khó (đặc biệt quan trọng khi mở rộng sang 15-puzzle để tránh thời gian chạy quá lâu).
- **Demo trực quan**: hiển thị trực tiếp từng bước máy di chuyển để giải bàn cờ bằng giao diện Pygame.

### 3. Mục tiêu đánh giá
- Tìm được lời giải tối ưu (ít bước di chuyển nhất).
- So sánh định lượng hiệu quả giữa các heuristic trên nhiều mức độ khó.
- Đánh giá khả năng mở rộng của thuật toán khi tăng kích thước bài toán (8-puzzle → 15-puzzle).

---

## Danh sách thành viên nhóm & Phân công nhiệm vụ (Members & Tasks)

| STT | Họ và Tên | MSSV | Vai trò | Nhiệm vụ |
| :---: | :--- | :---: | :---: | :--- |
| 1 | [Trần Hồng Sơn](https://github.com/trnhongson) | `060206012202` | **Trưởng nhóm (Leader)** | Điều khiển giao diện Pygame, kiến trúc State Machine, bảng HUD và tích hợp hệ thống. |
| 2 | [Hoàng Công Minh Tâm](https://github.com/hcmtam74-maker) | `045206008142` | **Thành viên (Member)** | Biểu diễn trạng thái Tuple, sinh trạng thái con láng giềng, đếm Inversion và kiểm tra khả giải. |
| 3 | [Lê Quốc Thắng](https://github.com/lequocthangg) | `079206003650` | **Thành viên (Member)** | Cài đặt thuật toán A* tổng quát, hàng đợi Min-Heap (heapq), cơ chế an toàn Timeout & Node Limit. |
| 4 | [Trần Duy Tân](https://github.com/dzytan) | `083206003584` | **Thành viên (Member)** | Cài đặt 2 hàm Heuristic (Manhattan, Misplaced) và thuật toán sinh test case Random Walk có kiểm soát độ khó. |
| 5 | [Võ Thị Anh Tú](https://github.com/Vthianhtu) | `052306001040` | **Thành viên (Member)** | Xây dựng hệ thống đo lường hiệu năng tự động (Benchmark), xuất CSV, phân tích Pandas và vẽ biểu đồ Matplotlib. |
| 6 | [Nguyễn Hồ Diễm My](https://github.com/DiemMy105) | `075306001575` | **Thành viên (Member)** | Thiết kế hiển thị bàn cờ responsive bo góc, hiệu ứng 3D đổ bóng và hoạt ảnh trượt mượt mà Ease-Out Cubic. |

---

## Tiến độ triển khai dự án (Project Progress)

- **Mô hình làm việc**: chia công việc theo tuần, tổng thời gian dự kiến 4 tuần.
- **Quản lý công việc**: Trello (Kanban) cho việc theo dõi task; Zalo/Discord cho trao đổi hằng ngày.
- **Quản lý mã nguồn**: GitHub, mỗi thành viên code làm việc trên branch riêng, gộp về `main` qua Pull Request.

---

## Công nghệ sử dụng (Tech Stack)

| Thành phần | Công nghệ / Thư viện | Vai trò |
| :--- | :--- | :--- |
| **Ngôn ngữ** | Python 3.10+ | Ngôn ngữ cài đặt toàn bộ thuật toán và công cụ. |
| **Thuật toán** | A* Search, thiết kế heuristic tùy biến | Tìm kiếm có thông tin, đảm bảo tối ưu với heuristic admissible. |
| **Giao diện demo** | Pygame | Hiển thị bàn cờ và hoạt ảnh từng bước giải trực quan. |
| **Phân tích & trực quan hoá dữ liệu** | Matplotlib, Pandas | Đọc kết quả benchmark, vẽ biểu đồ so sánh heuristic. |
| **Kiểm thử** | Pytest | Unit test cho core, heuristic, và thuật toán tìm kiếm. |
| **Quản lý mã nguồn** | Git, GitHub | Quản lý phiên bản, làm việc song song qua branch & Pull Request. |

---

## Cấu trúc thư mục (Project Structure)

```text
PuzzleSolver-AI/
├── src/
│   ├── core/
│   │   ├── puzzle_state.py       # Biểu diễn trạng thái bàn cờ, kiểm tra khả giải
│   │   ├── astar.py              # Thuật toán A* tổng quát (có node_limit/timeout an toàn)
│   │   ├── heuristics.py         # Hàm heuristic: Manhattan Distance & Misplaced Tiles
│   │   └── generator.py          # Sinh trạng thái ngẫu nhiên có kiểm soát độ khó (random walk)
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
├── tests/                         # Unit test cho core, heuristics, astar
├── docs/                          # Báo cáo, slide thuyết trình, tài liệu đặc tả
├── requirements.txt                # Danh sách thư viện Python cần cài đặt
├── .gitignore
└── README.md
```

> **Ghi chú:** bộ test case (`testcases_*.csv`) được sinh **một lần duy nhất** bằng seed cố định rồi commit lên Git, để kết quả benchmark trong báo cáo **tái lập được** mỗi lần chạy lại.

---

## Cách chạy (How to Run)

### 1. Yêu cầu môi trường
- **Python**: phiên bản `3.10` trở lên.
- **pip**: đi kèm sẵn với Python.

### 2. Clone mã nguồn

```bash
git clone https://github.com/trnhongson/PuzzelSolver-AI.git
cd PuzzelSolver-AI
```

### 3. Cài đặt & chạy chương trình

```bash
# 1. Tạo môi trường ảo (khuyến nghị)
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 2. Cài đặt thư viện
pip install -r requirements.txt

# 3. Sinh bộ test case cố định (chỉ cần chạy 1 lần)
python src/core/generator.py --seed 42

# 4. Chạy demo trực quan
python src/demo/main.py

# 5. Chạy benchmark so sánh heuristic
python src/benchmark/run_benchmark.py
python src/benchmark/compare_heuristics.py
```

### 4. Chạy bộ kiểm thử tự động

```bash
pytest tests/ -v
```

---

<p align="center">
  <b>Đồ án môn Trí tuệ nhân tạo</b>
</p>
