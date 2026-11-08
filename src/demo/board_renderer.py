from __future__ import annotations

from typing import Callable

import pygame

# Bảng màu giao diện hiện đại (Dark Slate Theme)
COLOR_BG = (15, 23, 42)              # #0F172A
COLOR_BOARD_BG = (30, 41, 59)        # #1E293B
COLOR_SLOT_EMPTY = (15, 23, 42)      # #0F172A
COLOR_TILE_DEFAULT = (59, 130, 246)  # #3B82F6 (Blue)
COLOR_TILE_CORRECT = (16, 185, 129)  # #10B981 (Emerald - đúng vị trí đích)
COLOR_TILE_MOVING = (245, 158, 11)   # #F59E0B (Amber - ô đang trượt)
COLOR_TILE_SHADOW = (10, 15, 28)
COLOR_TILE_BORDER = (148, 163, 184)
COLOR_TEXT = (248, 250, 252)


def get_default_board_rect(screen: pygame.Surface) -> pygame.Rect:
    """Tính vùng hình vuông mặc định để vẽ bàn cờ trên cửa sổ Pygame."""
    width, height = screen.get_size()
    board_px = min(width - 60, height - 180)
    board_px = max(240, board_px)
    left = 30
    top = (height - board_px) // 2 + 10
    return pygame.Rect(left, top, board_px, board_px)


def _compute_tile_rect(
    board_rect: pygame.Rect,
    size: int,
    row: float,
    col: float,
    padding: int = 10,
) -> pygame.Rect:
    """Tính tọa độ hình chữ nhật của một ô tại vị trí (row, col) (hỗ trợ số thực cho animation)."""
    total_padding = padding * (size + 1)
    tile_size = (board_rect.width - total_padding) / size
    x = board_rect.left + padding + col * (tile_size + padding)
    y = board_rect.top + padding + row * (tile_size + padding)
    return pygame.Rect(round(x), round(y), round(tile_size), round(tile_size))


def _draw_single_tile(
    screen: pygame.Surface,
    rect: pygame.Rect,
    tile_value: int,
    is_correct: bool,
    is_moving: bool,
    font: pygame.font.Font,
) -> None:
    """Vẽ một ô số với đổ bóng, bo góc và căn giữa chữ số."""
    shadow_rect = rect.move(0, 4)
    pygame.draw.rect(screen, COLOR_TILE_SHADOW, shadow_rect, border_radius=12)

    if is_moving:
        fill_color = COLOR_TILE_MOVING
    elif is_correct:
        fill_color = COLOR_TILE_CORRECT
    else:
        fill_color = COLOR_TILE_DEFAULT

    pygame.draw.rect(screen, fill_color, rect, border_radius=12)
    pygame.draw.rect(screen, COLOR_TILE_BORDER, rect, width=2, border_radius=12)

    text_surf = font.render(str(tile_value), True, COLOR_TEXT)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)


def draw_board(
    screen: pygame.Surface,
    state: tuple,
    size: int,
    board_rect: pygame.Rect | None = None,
    font: pygame.font.Font | None = None,
    skip_tile: int | None = None,
    moving_tile_info: tuple[int, pygame.Rect, bool] | None = None,
) -> None:
    """Vẽ trạng thái bàn cờ lên bề mặt Pygame.

    Parameters
    ----------
    screen : pygame.Surface
        Bề mặt cửa sổ Pygame cần vẽ.
    state : tuple
        Trạng thái bàn cờ hiện tại (tuple các số nguyên, 0 là ô trống).
    size : int
        Kích thước cạnh bàn cờ (3 cho 8-puzzle, 4 cho 15-puzzle).
    board_rect : pygame.Rect | None, optional
        Vùng hình chữ nhật chứa bàn cờ.
    font : pygame.font.Font | None, optional
        Font chữ để vẽ số trên các ô.
    skip_tile : int | None, optional
        Giá trị ô cần ẩn tạm thời ở lưới tĩnh (phục vụ hiệu ứng trượt).
    moving_tile_info : tuple[int, pygame.Rect, bool] | None, optional
        Thông tin ``(tile_value, rect, is_correct)`` của ô đang di chuyển.
    """
    if board_rect is None:
        board_rect = get_default_board_rect(screen)

    if font is None:
        font_size = max(24, board_rect.width // (size * 2))
        font = pygame.font.SysFont("Segoe UI", font_size, bold=True)

    padding = max(6, board_rect.width // (size * 12))

    # Vẽ khung nền bàn cờ
    pygame.draw.rect(screen, COLOR_BOARD_BG, board_rect, border_radius=16)
    pygame.draw.rect(screen, COLOR_TILE_BORDER, board_rect, width=2, border_radius=16)

    # Vẽ tất cả các hốc ô (slots) trước
    for idx in range(size * size):
        r, c = divmod(idx, size)
        slot_rect = _compute_tile_rect(board_rect, size, r, c, padding)
        pygame.draw.rect(screen, COLOR_SLOT_EMPTY, slot_rect, border_radius=12)

    # Vẽ các ô số tĩnh
    for idx, tile in enumerate(state):
        if tile == 0 or tile == skip_tile:
            continue
        r, c = divmod(idx, size)
        tile_rect = _compute_tile_rect(board_rect, size, r, c, padding)
        is_correct = tile == idx + 1
        _draw_single_tile(
            screen=screen,
            rect=tile_rect,
            tile_value=tile,
            is_correct=is_correct,
            is_moving=False,
            font=font,
        )

    # Vẽ ô đang trượt lên lớp trên cùng
    if moving_tile_info is not None:
        m_tile, m_rect, m_correct = moving_tile_info
        _draw_single_tile(
            screen=screen,
            rect=m_rect,
            tile_value=m_tile,
            is_correct=m_correct,
            is_moving=True,
            font=font,
        )


def animate_transition(
    screen: pygame.Surface,
    from_state: tuple,
    to_state: tuple,
    size: int,
    duration_ms: int = 180,
    fps: int = 60,
    board_rect: pygame.Rect | None = None,
    font: pygame.font.Font | None = None,
    overlay_callback: Callable[[pygame.Surface], None] | None = None,
) -> bool:
    """Tạo hiệu ứng trượt mượt mà khi chuyển giữa hai trạng thái liên tiếp.

    Parameters
    ----------
    screen : pygame.Surface
        Bề mặt hiển thị Pygame.
    from_state : tuple
        Trạng thái trước khi di chuyển.
    to_state : tuple
        Trạng thái sau khi di chuyển 1 bước.
    size : int
        Kích thước cạnh bàn cờ (3 hoặc 4).
    duration_ms : int
        Thời lượng hiệu ứng trượt (mili-giây).
    fps : int
        Số khung hình trên giây.
    board_rect : pygame.Rect | None, optional
        Vùng vẽ bàn cờ.
    font : pygame.font.Font | None, optional
        Font vẽ số trên ô.
    overlay_callback : Callable[[pygame.Surface], None] | None, optional
        Hàm callback vẽ thêm giao diện nền/bảng thông tin xung quanh bàn cờ.

    Returns
    -------
    bool
        ``True`` nếu hoàn tất hiệu ứng bình thường, ``False`` nếu người dùng đóng cửa sổ.
    """
    if from_state == to_state:
        return True

    if board_rect is None:
        board_rect = get_default_board_rect(screen)

    if font is None:
        font_size = max(24, board_rect.width // (size * 2))
        font = pygame.font.SysFont("Segoe UI", font_size, bold=True)

    padding = max(6, board_rect.width // (size * 12))

    # Ô trống ở from_state chính là vị trí đích mà ô số trượt tới
    to_idx = from_state.index(0)
    # Ô trống ở to_state chính là vị trí xuất phát của ô số đó
    from_idx = to_state.index(0)
    moving_tile = from_state[from_idx]

    start_row, start_col = divmod(from_idx, size)
    end_row, end_col = divmod(to_idx, size)
    will_be_correct = moving_tile == to_idx + 1

    clock = pygame.time.Clock()
    total_frames = max(1, int((duration_ms / 1000.0) * fps))

    for frame in range(1, total_frames + 1):
        for event in pygame.event.get([pygame.QUIT]):
            if event.type == pygame.QUIT:
                return False

        t = frame / total_frames
        # Hàm nội suy Ease-Out Cubic giúp chuyển động tự nhiên
        eased_t = 1.0 - (1.0 - t) ** 3

        curr_row = start_row + (end_row - start_row) * eased_t
        curr_col = start_col + (end_col - start_col) * eased_t
        moving_rect = _compute_tile_rect(board_rect, size, curr_row, curr_col, padding)

        screen.fill(COLOR_BG)
        if overlay_callback is not None:
            overlay_callback(screen)

        draw_board(
            screen=screen,
            state=from_state,
            size=size,
            board_rect=board_rect,
            font=font,
            skip_tile=moving_tile,
            moving_tile_info=(moving_tile, moving_rect, will_be_correct),
        )

        pygame.display.flip()
        clock.tick(fps)

    return True


# Alias tương thích ngược
animate_step = animate_transition
