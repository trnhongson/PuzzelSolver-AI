from __future__ import annotations

import argparse
import os
import sys
from typing import Callable

import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.core.astar import solve
from src.core.generator import random_walk_state
from src.core.heuristics import manhattan_distance, misplaced_tiles
from src.demo.board_renderer import COLOR_BG, animate_transition, draw_board

WINDOW_WIDTH = 980
WINDOW_HEIGHT = 640
FPS = 60

COLOR_PANEL = (30, 41, 59)
COLOR_PANEL_BORDER = (71, 85, 105)
COLOR_TEXT_PRIMARY = (248, 250, 252)
COLOR_TEXT_SECONDARY = (148, 163, 184)
COLOR_ACCENT_BLUE = (59, 130, 246)
COLOR_ACCENT_GREEN = (16, 185, 129)
COLOR_ACCENT_ORANGE = (249, 115, 22)
COLOR_BTN_BG = (51, 65, 85)
COLOR_BTN_HOVER = (71, 85, 105)

HEURISTICS: list[tuple[str, Callable[[tuple, int], int]]] = [
    ("Manhattan Distance", manhattan_distance),
    ("Misplaced Tiles", misplaced_tiles),
]


class PuzzleDemoApp:
    """Ứng dụng giao diện Pygame minh họa giải 8-puzzle / 15-puzzle bằng A*."""

    def __init__(self, size: int = 3, num_moves: int = 16) -> None:
        pygame.init()
        pygame.display.set_caption("PuzzleSolver-AI — Bộ giải 8-Puzzle / 15-Puzzle bằng A*")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()

        self.font_title = pygame.font.SysFont("Segoe UI", 24, bold=True)
        self.font_heading = pygame.font.SysFont("Segoe UI", 17, bold=True)
        self.font_body = pygame.font.SysFont("Segoe UI", 15)
        self.font_small = pygame.font.SysFont("Segoe UI", 13)

        self.board_rect = pygame.Rect(35, 85, 490, 490)
        self.panel_rect = pygame.Rect(550, 85, 395, 490)

        self.size = size
        self.num_moves = num_moves
        self.heuristic_idx = 0

        self.initial_state: tuple = ()
        self.current_state: tuple = ()
        self.solution_path: list[tuple] = []
        self.step_idx: int = 0
        self.auto_play: bool = True
        self.last_step_tick: int = 0
        self.step_interval_ms: int = 320

        self.solve_result: dict = {}
        self.comparison_results: dict[str, dict] = {}

        self.buttons: list[dict] = []
        self._init_buttons()
        self.reset_puzzle(new_board=True)

    def _init_buttons(self) -> None:
        """Khởi tạo danh sách các nút bấm tương tác trên bảng điều khiển."""
        bx = self.panel_rect.left + 20
        bw = (self.panel_rect.width - 52) // 2
        bh = 38
        y_start = self.panel_rect.bottom - 145

        self.buttons = [
            {
                "id": "reset",
                "label": "Bàn cờ mới (R)",
                "rect": pygame.Rect(bx, y_start, bw, bh),
            },
            {
                "id": "heuristic",
                "label": "Đổi Heuristic (H)",
                "rect": pygame.Rect(bx + bw + 12, y_start, bw, bh),
            },
            {
                "id": "toggle_play",
                "label": "Tạm dừng / Chạy (Space)",
                "rect": pygame.Rect(bx, y_start + 46, bw, bh),
            },
            {
                "id": "toggle_size",
                "label": "Đổi 8 / 15-Puzzle (M)",
                "rect": pygame.Rect(bx + bw + 12, y_start + 46, bw, bh),
            },
            {
                "id": "moves_down",
                "label": "Độ khó - (Down)",
                "rect": pygame.Rect(bx, y_start + 92, bw, bh),
            },
            {
                "id": "moves_up",
                "label": "Độ khó + (Up)",
                "rect": pygame.Rect(bx + bw + 12, y_start + 92, bw, bh),
            },
        ]

    def reset_puzzle(self, new_board: bool = True) -> None:
        """Sinh bàn cờ mới (hoặc giữ bàn cờ gốc hiện tại) và giải bằng A*."""
        if new_board or not self.initial_state:
            self.initial_state = random_walk_state(self.size, self.num_moves)

        self.current_state = self.initial_state
        self.step_idx = 0

        # Chạy A* với cả 2 heuristic trên cùng bàn cờ để so sánh trực quan
        self.comparison_results = {}
        for h_name, h_fn in HEURISTICS:
            self.comparison_results[h_name] = solve(
                start_state=self.initial_state,
                size=self.size,
                heuristic_fn=h_fn,
                node_limit=100_000,
                timeout_seconds=5.0,
            )

        active_h_name, _ = HEURISTICS[self.heuristic_idx]
        self.solve_result = self.comparison_results[active_h_name]

        if self.solve_result.get("solved") and self.solve_result.get("path"):
            self.solution_path = self.solve_result["path"]
        else:
            self.solution_path = [self.initial_state]

        self.auto_play = True
        self.last_step_tick = pygame.time.get_ticks()

    def switch_heuristic(self) -> None:
        """Chuyển đổi hàm heuristic và chạy lại từ trạng thái ban đầu của bàn cờ."""
        self.heuristic_idx = (self.heuristic_idx + 1) % len(HEURISTICS)
        self.reset_puzzle(new_board=False)

    def toggle_board_size(self) -> None:
        """Chuyển đổi giữa 8-puzzle (3x3) và 15-puzzle (4x4)."""
        self.size = 4 if self.size == 3 else 3
        if self.size == 4 and self.num_moves > 20:
            self.num_moves = 15
        self.initial_state = ()
        self.reset_puzzle(new_board=True)

    def adjust_difficulty(self, delta: int) -> None:
        """Thay đổi số bước xáo trộn num_moves và tạo bàn cờ mới."""
        max_moves = 35 if self.size == 3 else 25
        self.num_moves = max(4, min(max_moves, self.num_moves + delta))
        self.reset_puzzle(new_board=True)

    def step_forward(self, animate: bool = True) -> bool:
        """Tiến 1 bước trong chuỗi lời giải."""
        if self.step_idx + 1 >= len(self.solution_path):
            return True

        prev_s = self.solution_path[self.step_idx]
        next_s = self.solution_path[self.step_idx + 1]
        self.step_idx += 1
        self.current_state = next_s

        if animate:
            tile_font_size = max(24, self.board_rect.width // (self.size * 2))
            tile_font = pygame.font.SysFont("Segoe UI", tile_font_size, bold=True)
            ok = animate_transition(
                screen=self.screen,
                from_state=prev_s,
                to_state=next_s,
                size=self.size,
                duration_ms=170,
                fps=FPS,
                board_rect=self.board_rect,
                font=tile_font,
                overlay_callback=self._draw_ui_chrome,
            )
            self.last_step_tick = pygame.time.get_ticks()
            return ok
        return True

    def step_backward(self) -> None:
        """Lùi 1 bước trong chuỗi lời giải."""
        if self.step_idx > 0:
            self.step_idx -= 1
            self.current_state = self.solution_path[self.step_idx]

    def _draw_ui_chrome(self, surface: pygame.Surface) -> None:
        """Vẽ tiêu đề, bảng thông số A*, bảng so sánh Heuristic và các nút điều khiển."""
        puzzle_label = "8-PUZZLE (3x3)" if self.size == 3 else "15-PUZZLE (4x4)"
        title_surf = self.font_title.render(
            f"PuzzleSolver-AI — Demo A* ({puzzle_label})", True, COLOR_TEXT_PRIMARY
        )
        surface.blit(title_surf, (35, 28))

        subtitle_surf = self.font_small.render(
            "Phím tắt: [R] Bàn cờ mới | [H] Đổi Heuristic | [Space] Chạy/Dừng | [M] 8/15-Puzzle | [Left/Right] Từng bước",
            True,
            COLOR_TEXT_SECONDARY,
        )
        surface.blit(subtitle_surf, (35, 58))

        # Khung thông tin bên phải
        pygame.draw.rect(surface, COLOR_PANEL, self.panel_rect, border_radius=16)
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, self.panel_rect, width=2, border_radius=16)

        px = self.panel_rect.left + 20
        py = self.panel_rect.top + 18

        active_h_name, _ = HEURISTICS[self.heuristic_idx]
        total_steps = max(0, len(self.solution_path) - 1)
        solved = self.solve_result.get("solved", False)
        status_text = (
            "ĐÃ GIẢI XONG"
            if (solved and self.step_idx == total_steps)
            else ("ĐANG CHẠY" if self.auto_play and solved else "TẠM DỪNG")
        )
        if not solved:
            status_text = f"DỪNG ({self.solve_result.get('stopped_reason', 'limit')})"

        header = self.font_heading.render("THÔNG SỐ THUẬT TOÁN A*", True, COLOR_ACCENT_BLUE)
        surface.blit(header, (px, py))
        py += 28

        info_lines = [
            f"Heuristic đang chọn : {active_h_name}",
            f"Độ khó xáo trộn     : {self.num_moves} bước (random walk)",
            f"Trạng thái trình diễn: {status_text}",
            f"Tiến độ bước giải    : {self.step_idx} / {total_steps} bước",
            f"Số node đã mở rộng  : {self.solve_result.get('nodes_expanded', 0):,}",
            f"Thời gian tìm kiếm   : {self.solve_result.get('time_taken', 0.0) * 1000:.2f} ms",
        ]

        for line in info_lines:
            surf = self.font_body.render(line, True, COLOR_TEXT_PRIMARY)
            surface.blit(surf, (px, py))
            py += 24

        py += 8
        cmp_header = self.font_heading.render(
            "SO SÁNH TRỰC QUAN TRÊN BÀN CỜ NÀY", True, COLOR_ACCENT_GREEN
        )
        surface.blit(cmp_header, (px, py))
        py += 26

        for h_name, _ in HEURISTICS:
            res = self.comparison_results.get(h_name, {})
            is_active = h_name == active_h_name
            marker = "► " if is_active else "   "
            color = COLOR_ACCENT_ORANGE if is_active else COLOR_TEXT_SECONDARY
            nodes = res.get("nodes_expanded", 0)
            t_ms = res.get("time_taken", 0.0) * 1000.0
            steps = len(res["path"]) - 1 if res.get("solved") and res.get("path") else -1
            step_str = f"{steps} bước" if steps >= 0 else res.get("stopped_reason", "N/A")

            line_surf = self.font_small.render(
                f"{marker}{h_name}: {nodes:,} nodes | {t_ms:.2f} ms ({step_str})",
                True,
                color,
            )
            surface.blit(line_surf, (px, py))
            py += 22

        # Vẽ các nút bấm tương tác
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            rect = btn["rect"]
            hovered = rect.collidepoint(mouse_pos)
            bg_color = COLOR_BTN_HOVER if hovered else COLOR_BTN_BG
            pygame.draw.rect(surface, bg_color, rect, border_radius=8)
            pygame.draw.rect(surface, COLOR_PANEL_BORDER, rect, width=1, border_radius=8)

            txt_surf = self.font_small.render(btn["label"], True, COLOR_TEXT_PRIMARY)
            txt_rect = txt_surf.get_rect(center=rect.center)
            surface.blit(txt_surf, txt_rect)

    def _handle_button_click(self, pos: tuple[int, int]) -> None:
        """Xử lý sự kiện nhấn chuột vào các nút điều khiển."""
        for btn in self.buttons:
            if btn["rect"].collidepoint(pos):
                btn_id = btn["id"]
                if btn_id == "reset":
                    self.reset_puzzle(new_board=True)
                elif btn_id == "heuristic":
                    self.switch_heuristic()
                elif btn_id == "toggle_play":
                    if self.step_idx >= len(self.solution_path) - 1:
                        self.step_idx = 0
                        self.current_state = self.initial_state
                    self.auto_play = not self.auto_play
                    self.last_step_tick = pygame.time.get_ticks()
                elif btn_id == "toggle_size":
                    self.toggle_board_size()
                elif btn_id == "moves_down":
                    self.adjust_difficulty(-3)
                elif btn_id == "moves_up":
                    self.adjust_difficulty(3)
                break

    def run(self, max_frames: int | None = None) -> None:
        """Vòng lặp chính của ứng dụng Pygame."""
        running = True
        frame_count = 0
        tile_font_size = max(24, self.board_rect.width // (self.size * 2))
        tile_font = pygame.font.SysFont("Segoe UI", tile_font_size, bold=True)
        cached_size = self.size

        while running:
            if cached_size != self.size:
                tile_font_size = max(24, self.board_rect.width // (self.size * 2))
                tile_font = pygame.font.SysFont("Segoe UI", tile_font_size, bold=True)
                cached_size = self.size

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_q):
                        running = False
                    elif event.key == pygame.K_r:
                        self.reset_puzzle(new_board=True)
                    elif event.key == pygame.K_h:
                        self.switch_heuristic()
                    elif event.key == pygame.K_SPACE:
                        if self.step_idx >= len(self.solution_path) - 1:
                            self.step_idx = 0
                            self.current_state = self.initial_state
                        self.auto_play = not self.auto_play
                        self.last_step_tick = pygame.time.get_ticks()
                    elif event.key == pygame.K_m:
                        self.toggle_board_size()
                    elif event.key == pygame.K_UP:
                        self.adjust_difficulty(3)
                    elif event.key == pygame.K_DOWN:
                        self.adjust_difficulty(-3)
                    elif event.key == pygame.K_RIGHT:
                        self.auto_play = False
                        if not self.step_forward(animate=True):
                            running = False
                    elif event.key == pygame.K_LEFT:
                        self.auto_play = False
                        self.step_backward()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self._handle_button_click(event.pos)

            if not running:
                break

            now = pygame.time.get_ticks()
            if (
                self.auto_play
                and self.step_idx + 1 < len(self.solution_path)
                and now - self.last_step_tick >= self.step_interval_ms
            ):
                if not self.step_forward(animate=True):
                    break

            self.screen.fill(COLOR_BG)
            self._draw_ui_chrome(self.screen)
            draw_board(
                screen=self.screen,
                state=self.current_state,
                size=self.size,
                board_rect=self.board_rect,
                font=tile_font,
            )
            pygame.display.flip()
            self.clock.tick(FPS)

            frame_count += 1
            if max_frames is not None and frame_count >= max_frames:
                running = False

        pygame.quit()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Chạy giao diện Demo giải 8-puzzle / 15-puzzle bằng thuật toán A*."
    )
    parser.add_argument(
        "--size",
        type=int,
        choices=[3, 4],
        default=3,
        help="Kích thước bàn cờ: 3 (8-puzzle) hoặc 4 (15-puzzle).",
    )
    parser.add_argument(
        "--moves",
        type=int,
        default=16,
        help="Số bước xáo trộn ngẫu nhiên từ đích (mặc định: 16).",
    )
    parser.add_argument(
        "--max-frames",
        type=int,
        default=None,
        help="Giới hạn số frame chạy (dùng khi kiểm thử tự động).",
    )
    args = parser.parse_args()

    app = PuzzleDemoApp(size=args.size, num_moves=args.moves)
    app.run(max_frames=args.max_frames)


if __name__ == "__main__":
    main()
