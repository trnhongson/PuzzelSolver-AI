from __future__ import annotations

import argparse
import ctypes
import os
import sys
from typing import Callable

import pygame

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.core.astar import solve
from src.core.generator import random_walk_state
from src.core.heuristics import manhattan_distance, misplaced_tiles
from src.demo.board_renderer import COLOR_BG, animate_transition, draw_board

DEFAULT_WIDTH = 1240
DEFAULT_HEIGHT = 760
MIN_WIDTH = 920
MIN_HEIGHT = 600
FPS = 60

# Bảng màu Deep Navy (#1C1C28) đồng bộ theo thiết kế tối giản
COLOR_PANEL = (28, 28, 40)              # #1C1C28 - Deep Navy
COLOR_PANEL_BORDER = (62, 67, 92)       # #3E435C
COLOR_DIVIDER = (46, 50, 70)            # #2E3246
COLOR_TEXT_PRIMARY = (244, 246, 252)    # #F4F6FC - Trắng sáng rõ nét
COLOR_TEXT_SECONDARY = (182, 190, 212)  # #B6BED4 - Xám bạc sáng dễ đọc từ xa
COLOR_TEXT_MUTED = (134, 144, 170)      # #8690AA
COLOR_ACCENT = (162, 178, 212)          # #A2B2D4 - Periwinkle Silver
COLOR_BADGE_BG = (42, 48, 68)           # #2A3044
COLOR_BTN_BG = (38, 42, 58)             # #262A3A
COLOR_BTN_HOVER = (56, 62, 86)          # #383E56
COLOR_BTN_BORDER = (82, 92, 122)        # #525C7A

HEURISTICS: list[tuple[str, Callable[[tuple, int], int]]] = [
    ("Manhattan Distance", manhattan_distance),
    ("Misplaced Tiles", misplaced_tiles),
]


def _enable_windows_dpi_awareness() -> None:
    """Bật DPI Awareness trên Windows để hiển thị độ phân giải thực sắc nét."""
    if sys.platform == "win32":
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass


class PuzzleDemoApp:
    """Ứng dụng giao diện Pygame minh họa giải bài toán N-Puzzle bằng A*."""

    def __init__(self, size: int = 3, num_moves: int = 16) -> None:
        _enable_windows_dpi_awareness()
        pygame.init()
        pygame.display.set_caption("PuzzleSolver-AI")

        # Tự động chọn kích thước cửa sổ mặc định rộng rãi (~82% màn hình) và cho phép phóng to (RESIZABLE)
        display_info = pygame.display.Info()
        if display_info.current_w > 0 and display_info.current_h > 0:
            init_w = max(MIN_WIDTH, min(1440, int(display_info.current_w * 0.80)))
            init_h = max(MIN_HEIGHT, min(900, int(display_info.current_h * 0.82)))
        else:
            init_w, init_h = DEFAULT_WIDTH, DEFAULT_HEIGHT

        self.is_fullscreen = False
        self.windowed_size = (init_w, init_h)
        self.screen = pygame.display.set_mode(self.windowed_size, pygame.RESIZABLE)
        self.clock = pygame.time.Clock()

        self.size = size
        self.num_moves = num_moves
        self.heuristic_idx = 0

        self.scale: float = 1.0
        self.header_x: int = 40
        self.header_y: int = 24
        self.board_rect = pygame.Rect(40, 100, 520, 520)
        self.panel_rect = pygame.Rect(584, 100, 440, 520)
        self.buttons: list[dict] = []

        self._recalculate_layout(init_w, init_h)

        self.initial_state: tuple = ()
        self.current_state: tuple = ()
        self.solution_path: list[tuple] = []
        self.step_idx: int = 0
        self.auto_play: bool = True
        self.last_step_tick: int = 0
        self.step_interval_ms: int = 310

        self.solve_result: dict = {}
        self.comparison_results: dict[str, dict] = {}

        self.reset_puzzle(new_board=True)

    def _recalculate_layout(self, width: int, height: int) -> None:
        """Tính toán lại toàn bộ bố cục, kích thước bàn cờ và cỡ chữ khi phóng to/thu nhỏ cửa sổ."""
        width = max(MIN_WIDTH, width)
        height = max(MIN_HEIGHT, height)

        self.scale = min(width / 1080.0, height / 680.0)
        s = self.scale

        gap = round(28 * s)
        header_h = round(82 * s)
        board_px = round(510 * s)
        panel_w = round(430 * s)

        total_w = board_px + gap + panel_w
        total_h = header_h + board_px

        start_x = max(24, (width - total_w) // 2)
        start_y = max(18, (height - total_h) // 2)

        self.header_x = start_x
        self.header_y = start_y

        content_top = start_y + header_h
        self.board_rect = pygame.Rect(start_x, content_top, board_px, board_px)
        self.panel_rect = pygame.Rect(start_x + board_px + gap, content_top, panel_w, board_px)

        # Khởi tạo lại bộ font chữ tỷ lệ thuận với kích thước màn hình (rất rõ khi chiếu TV)
        self.font_title = pygame.font.SysFont("Segoe UI", max(22, round(28 * s)), bold=True)
        self.font_badge = pygame.font.SysFont("Segoe UI Semibold", max(13, round(15 * s)))
        self.font_section = pygame.font.SysFont("Segoe UI", max(13, round(15 * s)), bold=True)
        self.font_label = pygame.font.SysFont("Segoe UI", max(14, round(16 * s)))
        self.font_value = pygame.font.SysFont("Segoe UI Semibold", max(14, round(16 * s)))
        self.font_small = pygame.font.SysFont("Segoe UI", max(12, round(14 * s)))
        self.font_btn = pygame.font.SysFont("Segoe UI Semibold", max(13, round(14 * s)))

        tile_font_size = max(28, self.board_rect.width // (self.size * 2))
        self.tile_font = pygame.font.SysFont("Segoe UI", tile_font_size, bold=True)

        self._init_buttons()

    def _init_buttons(self) -> None:
        """Khởi tạo các nút bấm bo tròn (pill buttons) co giãn theo bảng điều khiển."""
        s = self.scale
        pad_x = round(24 * s)
        col_gap = round(14 * s)
        bx = self.panel_rect.left + pad_x
        bw = (self.panel_rect.width - pad_x * 2 - col_gap) // 2
        bh = round(40 * s)
        row_step = round(48 * s)
        y_start = self.panel_rect.bottom - round(156 * s)

        self.buttons = [
            {
                "id": "reset",
                "label": "Bàn cờ mới (R)",
                "rect": pygame.Rect(bx, y_start, bw, bh),
            },
            {
                "id": "heuristic",
                "label": "Đổi Heuristic (H)",
                "rect": pygame.Rect(bx + bw + col_gap, y_start, bw, bh),
            },
            {
                "id": "toggle_play",
                "label": "Chạy / Dừng (Space)",
                "rect": pygame.Rect(bx, y_start + row_step, bw, bh),
            },
            {
                "id": "toggle_size",
                "label": "Chế độ 3x3 / 4x4 (M)",
                "rect": pygame.Rect(bx + bw + col_gap, y_start + row_step, bw, bh),
            },
            {
                "id": "moves_down",
                "label": "Giảm độ khó (Down)",
                "rect": pygame.Rect(bx, y_start + row_step * 2, bw, bh),
            },
            {
                "id": "moves_up",
                "label": "Tăng độ khó (Up)",
                "rect": pygame.Rect(bx + bw + col_gap, y_start + row_step * 2, bw, bh),
            },
        ]

    def toggle_fullscreen(self) -> None:
        """Chuyển đổi giữa chế độ Toàn màn hình (Fullscreen) và Cửa sổ (Resizable)."""
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            self.windowed_size = self.screen.get_size()
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode(self.windowed_size, pygame.RESIZABLE)
        w, h = self.screen.get_size()
        self._recalculate_layout(w, h)

    def reset_puzzle(self, new_board: bool = True) -> None:
        """Sinh bàn cờ mới (hoặc giữ bàn cờ gốc hiện tại) và giải bằng A*."""
        if new_board or not self.initial_state:
            self.initial_state = random_walk_state(self.size, self.num_moves)

        self.current_state = self.initial_state
        self.step_idx = 0

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
        tile_font_size = max(28, self.board_rect.width // (self.size * 2))
        self.tile_font = pygame.font.SysFont("Segoe UI", tile_font_size, bold=True)
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
            ok = animate_transition(
                screen=self.screen,
                from_state=prev_s,
                to_state=next_s,
                size=self.size,
                duration_ms=170,
                fps=FPS,
                board_rect=self.board_rect,
                font=self.tile_font,
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
        s = self.scale
        hx = self.header_x
        hy = self.header_y

        title_surf = self.font_title.render("PuzzleSolver-AI", True, COLOR_TEXT_PRIMARY)
        surface.blit(title_surf, (hx, hy))

        mode_text = "8-Puzzle (3x3)" if self.size == 3 else "15-Puzzle (4x4)"
        badge_surf = self.font_badge.render(mode_text, True, COLOR_TEXT_PRIMARY)
        badge_h = round(30 * s)
        badge_rect = pygame.Rect(
            hx + title_surf.get_width() + round(16 * s),
            hy + (title_surf.get_height() - badge_h) // 2,
            badge_surf.get_width() + round(24 * s),
            badge_h,
        )
        pygame.draw.rect(surface, COLOR_BADGE_BG, badge_rect, border_radius=badge_h // 2)
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, badge_rect, width=1, border_radius=badge_h // 2)
        surface.blit(badge_surf, badge_surf.get_rect(center=badge_rect.center))

        subtitle_surf = self.font_small.render(
            "Phím tắt:  [R] Bàn cờ mới   [H] Đổi Heuristic   [Space] Chạy/Dừng   [M] Đổi 3x3/4x4   [Left/Right] Từng bước   [F11] Toàn màn hình",
            True,
            COLOR_TEXT_SECONDARY,
        )
        surface.blit(subtitle_surf, (hx, hy + title_surf.get_height() + round(6 * s)))

        # Khung thông tin bên phải (Deep Navy #1C1C28)
        panel_radius = round(18 * s)
        pygame.draw.rect(surface, COLOR_PANEL, self.panel_rect, border_radius=panel_radius)
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, self.panel_rect, width=1, border_radius=panel_radius)

        pad_x = round(24 * s)
        px_left = self.panel_rect.left + pad_x
        px_right = self.panel_rect.right - pad_x
        py = self.panel_rect.top + round(22 * s)
        row_h = round(27 * s)

        active_h_name, _ = HEURISTICS[self.heuristic_idx]
        total_steps = max(0, len(self.solution_path) - 1)
        solved = self.solve_result.get("solved", False)
        if not solved:
            status_text = f"Dừng ({self.solve_result.get('stopped_reason', 'limit')})"
        elif self.step_idx == total_steps:
            status_text = "Hoàn thành"
        elif self.auto_play:
            status_text = "Đang mô phỏng"
        else:
            status_text = "Tạm dừng"

        header = self.font_section.render("THÔNG SỐ THUẬT TOÁN A*", True, COLOR_ACCENT)
        surface.blit(header, (px_left, py))
        py += round(26 * s)
        pygame.draw.line(surface, COLOR_DIVIDER, (px_left, py), (px_right, py), 1)
        py += round(12 * s)

        rows = [
            ("Heuristic", active_h_name),
            ("Độ khó xáo trộn", f"{self.num_moves} bước"),
            ("Trạng thái", status_text),
            ("Tiến độ giải", f"{self.step_idx} / {total_steps} bước"),
            ("Số node đã duyệt", f"{self.solve_result.get('nodes_expanded', 0):,}"),
            ("Thời gian tìm kiếm", f"{self.solve_result.get('time_taken', 0.0) * 1000:.2f} ms"),
        ]

        for label, val in rows:
            lbl_surf = self.font_label.render(label, True, COLOR_TEXT_SECONDARY)
            val_surf = self.font_value.render(val, True, COLOR_TEXT_PRIMARY)
            surface.blit(lbl_surf, (px_left, py))
            surface.blit(val_surf, (px_right - val_surf.get_width(), py))
            py += row_h

        py += round(10 * s)
        cmp_header = self.font_section.render(
            "SO SÁNH TRÊN BÀN CỜ HIỆN TẠI", True, COLOR_ACCENT
        )
        surface.blit(cmp_header, (px_left, py))
        py += round(24 * s)
        pygame.draw.line(surface, COLOR_DIVIDER, (px_left, py), (px_right, py), 1)
        py += round(12 * s)

        dot_sz = max(6, round(8 * s))
        for h_name, _ in HEURISTICS:
            res = self.comparison_results.get(h_name, {})
            is_active = h_name == active_h_name
            nodes = res.get("nodes_expanded", 0)
            t_ms = res.get("time_taken", 0.0) * 1000.0
            steps = len(res["path"]) - 1 if res.get("solved") and res.get("path") else -1
            step_str = f"{steps} bước" if steps >= 0 else res.get("stopped_reason", "N/A")

            dot_color = COLOR_TEXT_PRIMARY if is_active else COLOR_PANEL_BORDER
            dot_rect = pygame.Rect(px_left + 1, py + round(7 * s), dot_sz, dot_sz)
            pygame.draw.rect(surface, dot_color, dot_rect, border_radius=dot_sz // 2)

            name_color = COLOR_TEXT_PRIMARY if is_active else COLOR_TEXT_MUTED
            stat_color = COLOR_TEXT_SECONDARY if is_active else COLOR_TEXT_MUTED

            name_surf = self.font_value.render(h_name, True, name_color)
            stat_surf = self.font_small.render(
                f"{nodes:,} nodes  |  {t_ms:.2f} ms  ({step_str})", True, stat_color
            )
            surface.blit(name_surf, (px_left + dot_sz + round(8 * s), py))
            surface.blit(stat_surf, (px_right - stat_surf.get_width(), py + round(2 * s)))
            py += row_h

        # Vẽ các nút bấm tương tác dạng Pill (bo tròn)
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            rect = btn["rect"]
            hovered = rect.collidepoint(mouse_pos)
            bg_color = COLOR_BTN_HOVER if hovered else COLOR_BTN_BG
            border_color = COLOR_ACCENT if hovered else COLOR_BTN_BORDER
            radius = rect.height // 2
            pygame.draw.rect(surface, bg_color, rect, border_radius=radius)
            pygame.draw.rect(surface, border_color, rect, width=1, border_radius=radius)

            txt_surf = self.font_btn.render(btn["label"], True, COLOR_TEXT_PRIMARY)
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

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    if not self.is_fullscreen:
                        self.windowed_size = ( max(MIN_WIDTH, event.w), max(MIN_HEIGHT, event.h) )
                    self._recalculate_layout(event.w, event.h)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.is_fullscreen:
                            self.toggle_fullscreen()
                        else:
                            running = False
                    elif event.key == pygame.K_q:
                        running = False
                    elif event.key == pygame.K_F11 or (
                        event.key == pygame.K_RETURN and (event.mod & pygame.KMOD_ALT)
                    ):
                        self.toggle_fullscreen()
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
                font=self.tile_font,
            )
            pygame.display.flip()
            self.clock.tick(FPS)

            frame_count += 1
            if max_frames is not None and frame_count >= max_frames:
                running = False

        pygame.quit()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Chạy giao diện Demo giải 8-puzzle và 15-puzzle bằng thuật toán A*."
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
