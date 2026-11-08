from __future__ import annotations

from typing import Callable

import pygame

# Bảng màu Deep Navy (Lấy cảm hứng từ tone #1C1C28 - Tối giản, độ tương phản cao)
COLOR_BG = (14, 15, 22)                # #0E0F16 - Nền chính tối sâu
COLOR_BOARD_BG = (28, 28, 40)          # #1C1C28 - Deep Navy (Nền khung bàn cờ)
COLOR_BOARD_BORDER = (58, 62, 84)      # #3A3E54 - Viền mảnh tinh tế
COLOR_SLOT_EMPTY = (18, 19, 28)        # #12131C - Hốc ô trống

# Màu sắc các ô số (Trực quan, phân tách rõ trạng thái nhưng cùng dải màu Navy)
COLOR_TILE_DEFAULT = (42, 48, 68)      # #2A3044 - Ô bình thường (Slate Navy)
COLOR_TILE_DEFAULT_BORDER = (75, 86, 118)

COLOR_TILE_CORRECT = (72, 92, 132)     # #485C84 - Ô đã đúng vị trí đích (Steel Blue)
COLOR_TILE_CORRECT_BORDER = (154, 168, 199)  # #9AA8C7 - Viền sáng nhẹ báo hiệu đúng vị trí

COLOR_TILE_MOVING = (108, 128, 168)    # #6C80A8 - Ô đang trượt
COLOR_TILE_MOVING_BORDER = (226, 232, 245)

COLOR_TILE_SHADOW = (9, 10, 15)
COLOR_TEXT = (242, 244, 250)           # #F2F4FA - Trắng sáng sắc nét


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
    padding: int = 12,
) -> pygame.Rect:
    """Tính tọa độ hình chữ nhật của một ô tại vị trí (row, col)."""
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
    """Vẽ một ô số với phong cách Deep Navy phẳng, tự động co giãn theo kích thước ô."""
    radius = max(12, rect.width // 9)
    shadow_offset = max(3, rect.width // 40)
    shadow_rect = rect.move(0, shadow_offset)
    pygame.draw.rect(screen, COLOR_TILE_SHADOW, shadow_rect, border_radius=radius)

    if is_moving:
        fill_color = COLOR_TILE_MOVING
        border_color = COLOR_TILE_MOVING_BORDER
        border_w = max(2, rect.width // 70)
    elif is_correct:
        fill_color = COLOR_TILE_CORRECT
        border_color = COLOR_TILE_CORRECT_BORDER
        border_w = max(2, rect.width // 70)
    else:
        fill_color = COLOR_TILE_DEFAULT
        border_color = COLOR_TILE_DEFAULT_BORDER
        border_w = max(1, rect.width // 90)

    pygame.draw.rect(screen, fill_color, rect, border_radius=radius)
    pygame.draw.rect(screen, border_color, rect, width=border_w, border_radius=radius)

    # Điểm báo góc trên phải cho các ô đã nằm đúng vị trí đích để dễ quan sát từ xa
    if is_correct and not is_moving:
        dot_sz = max(7, rect.width // 16)
        margin = max(10, rect.width // 12)
        dot_rect = pygame.Rect(rect.right - margin - dot_sz, rect.top + margin, dot_sz, dot_sz)
        pygame.draw.rect(screen, COLOR_TILE_CORRECT_BORDER, dot_rect, border_radius=dot_sz // 2)

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
        font_size = max(26, board_rect.width // (size * 2))
        font = pygame.font.SysFont("Segoe UI", font_size, bold=True)

    padding = max(8, board_rect.width // (size * 11))

    # Vẽ khung nền bàn cờ
    pygame.draw.rect(screen, COLOR_BOARD_BG, board_rect, border_radius=18)
    pygame.draw.rect(screen, COLOR_BOARD_BORDER, board_rect, width=1, border_radius=18)

    # Vẽ tất cả các hốc ô trống
    for idx in range(size * size):
        r, c = divmod(idx, size)
        slot_rect = _compute_tile_rect(board_rect, size, r, c, padding)
        pygame.draw.rect(screen, COLOR_SLOT_EMPTY, slot_rect, border_radius=14)

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
    duration_ms: int = 175,
    fps: int = 60,
    board_rect: pygame.Rect | None = None,
    font: pygame.font.Font | None = None,
    overlay_callback: Callable[[pygame.Surface], None] | None = None,
) -> bool:
    """Tạo hiệu ứng trượt mượt mà khi chuyển giữa hai trạng thái liên tiếp."""
    if from_state == to_state:
        return True

    if board_rect is None:
        board_rect = get_default_board_rect(screen)

    if font is None:
        font_size = max(26, board_rect.width // (size * 2))
        font = pygame.font.SysFont("Segoe UI", font_size, bold=True)

    padding = max(8, board_rect.width // (size * 11))

    to_idx = from_state.index(0)
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


animate_step = animate_transition
