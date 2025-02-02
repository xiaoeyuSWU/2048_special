import random
import pygame
import sys
import copy
import time
import json
import os

pygame.init()

GRID_GAP = 5
CORNER_RADIUS = 15
BORDER_WIDTH = 3
BORDER_COLOR = (150, 140, 130)
WIDTH, HEIGHT = 400, 500
INFO_HEIGHT = 100

GAME_HEIGHT = HEIGHT - INFO_HEIGHT
GRID_SIZE = 4
CELL_SIZE = WIDTH // GRID_SIZE
MAX_HISTORY_SIZE = 20
SAVE_FILE = "savegame.json"

FONT = pygame.font.SysFont("Microsoft YaHei", 24)

BACKGROUND_COLOR = (187, 173, 160)

CELL_COLOR = (204, 192, 179)
TEXT_COLOR = (119, 110, 101)
OVERLAY_COLOR = (50, 50, 50, 200)

MILESTONE_ORDER = ["小", "鳄", "鱼", "就", "是", "喜", "欢", "麦", "芽", "糖", "呀"]

MILESTONE_UNLOCKED_COLOR = (0, 0, 0)
MILESTONE_LOCKED_COLOR = (160, 160, 160)

NUM_TO_TEXT = {
    2: "小", 4: "鳄", 8: "鱼", 16: "就", 32: "是",
    64: "喜", 128: "欢", 256: "麦", 512: "芽",
    1024: "糖", 2048: "呀",
    4096: "而", 8192: "且", 16384: "会",
    32768: "爱", 65536: "很", 131072: "久"
}

CELL_COLORS = {
    "小": (238, 228, 218),
    "鳄": (237, 224, 200),
    "鱼": (242, 177, 121),
    "就": (245, 149, 99),
    "是": (246, 124, 95),
    "喜": (246, 94, 59),
    "欢": (237, 207, 114),
    "麦": (237, 204, 97),
    "芽": (237, 200, 80),
    "糖": (237, 197, 63),
    "呀": (237, 194, 46),
    "而": (200, 180, 100),
    "且": (180, 160, 80),
    "会": (180, 160, 80),
    "爱": (180, 160, 80),
    "很": (180, 160, 80),
    "久": (180, 160, 80)
}

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2048")

RESTART_BUTTON_WIDTH = 80
RESTART_BUTTON_HEIGHT = 30
RESTART_BUTTON_TEXT = "重新开始"

RESTART_BTN_COLOR_NORMAL = (161, 209, 222)
RESTART_BTN_COLOR_HOVER = (181, 229, 242)
RESTART_BTN_COLOR_CLICK = (141, 189, 202)

def confirm_action(prompt_text="呜呜宝宝，真的吗? (yes/no)"):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill(OVERLAY_COLOR)
    screen.blit(overlay, (0, 0))

    dialog_font = pygame.font.SysFont("Microsoft YaHei", 32)
    text = dialog_font.render(prompt_text, True, (255, 182, 193))

    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20))
    screen.blit(text, text_rect)

    input_font = pygame.font.SysFont("Microsoft YaHei", 28)
    input_prompt = input_font.render("输入答案：", True, (255, 255, 255))
    prompt_rect = input_prompt.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
    screen.blit(input_prompt, prompt_rect)

    pygame.display.update()

    input_buffer = ""
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return input_buffer.lower() == "yes"
                elif event.key == pygame.K_BACKSPACE:
                    input_buffer = input_buffer[:-1]
                else:
                    if len(input_buffer) < 10:
                        input_buffer += event.unicode

        screen.blit(overlay, (0, 0))
        screen.blit(text, text_rect)
        screen.blit(input_prompt, prompt_rect)

        input_text = input_font.render(input_buffer, True, (255, 255, 255))
        input_rect = input_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
        screen.blit(input_text, input_rect)

        pygame.draw.line(screen, (255, 255, 255), 
                        (input_rect.left, input_rect.bottom + 2),
                        (input_rect.right, input_rect.bottom + 2), 2)

        pygame.display.update()

def show_temp_message(message, duration=1.5):
    start_time = time.time()

    lines = message.split('\n')

    dialog_font = pygame.font.SysFont("Microsoft YaHei", 24)
    line_height = dialog_font.get_linesize()

    while True:
        elapsed = time.time() - start_time
        if elapsed > duration:
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill(OVERLAY_COLOR)
        screen.blit(overlay, (0, 0))

        total_text_height = len(lines) * line_height
        start_y = (HEIGHT - total_text_height) // 2

        for i, line in enumerate(lines):
            text_surface = dialog_font.render(line, True, (255, 255, 255))
            text_rect = text_surface.get_rect(
                center=(WIDTH // 2, start_y + i * line_height + line_height // 2)
            )
            screen.blit(text_surface, text_rect)

        pygame.display.update()
        pygame.time.delay(50)

def shuffle_board(board):
    tiles = [val for row in board for val in row if val != 0]

    if len(tiles) < 2:
        return copy_board(board)
    
    # Fix: If all nonzero tiles are identical, simply return a copy of the board
    if len(set(tiles)) == 1:
        return copy_board(board)
    
    while True:
        random.shuffle(tiles)
        new_board = []
        idx = 0
        for r in range(GRID_SIZE):
            new_row = []
            for c in range(GRID_SIZE):
                if board[r][c] == 0:
                    new_row.append(0)
                else:
                    new_row.append(tiles[idx])
                    idx += 1
            new_board.append(new_row)
        if any(new_board[r][c] != board[r][c] 
              for r in range(GRID_SIZE) 
              for c in range(GRID_SIZE)):
            return new_board

def handle_special_input(input_buffer, board):
    if input_buffer.endswith("mytlikelbyforever"):
        if confirm_action():
            remove_random_tile(board)
            remove_random_tile(board)
            show_temp_message("宝宝偷偷移除了 2 个格子^ ^\n小鳄鱼要伤心啦T＿T", 1.5)
        return ""
    return input_buffer

def draw_board(board, score, playtime, moves, new_tiles, merge_animations, movement_animations, current_time):
    # Determine destination cells that are currently animated (movement in progress)
    animated_destinations = {tuple(anim['to']) for anim in movement_animations if current_time - anim['start_time'] < anim['duration']}
    
    # Draw grid cells and static tiles (skip those that are animating)
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            x = col * CELL_SIZE
            y = INFO_HEIGHT + row * CELL_SIZE
            cell_rect = pygame.Rect(x + GRID_GAP//2, y + GRID_GAP//2, CELL_SIZE - GRID_GAP, CELL_SIZE - GRID_GAP)
            pygame.draw.rect(screen, CELL_COLOR, cell_rect, border_radius=CORNER_RADIUS)
            if board[row][col]:
                if (row, col) in animated_destinations:
                    continue  # This tile is being animated via movement animation
                # Check for new tile animation
                new_tile = next((tile for tile in new_tiles if tile['pos'] == (row, col)), None)
                if new_tile:
                    elapsed_time = current_time - new_tile['start_time']
                    if elapsed_time < 0.3:
                        progress = elapsed_time / 0.3
                        scale = 0.5 + 0.5 * progress
                        alpha = int(255 * progress)
                    else:
                        scale = 1.0
                        alpha = 255
                else:
                    scale = 1.0
                    alpha = 255

                # Check merge animation (if any)
                merge_tile = next((merge for merge in merge_animations if merge['pos'] == (row, col)), None)
                if merge_tile:
                    elapsed_time = current_time - merge_tile['start_time']
                    if elapsed_time < 0.3:
                        progress = elapsed_time / 0.3
                        scale = 1.0 + 0.15 * (1 - (1 - progress) ** 2)
                    else:
                        scale = 1.15 - 0.15 * (elapsed_time - 0.3) / 0.3
                        if scale < 1.0:
                            scale = 1.0

                scaled_width = int(CELL_SIZE * scale)
                scaled_height = int(CELL_SIZE * scale)
                offset_x = (CELL_SIZE - GRID_GAP - scaled_width) // 2 + GRID_GAP//2
                offset_y = (CELL_SIZE - GRID_GAP - scaled_height) // 2 + GRID_GAP//2

                rect = pygame.Rect(x + offset_x, y + offset_y, scaled_width, scaled_height)
                tile_surface = pygame.Surface((scaled_width, scaled_height), pygame.SRCALPHA)
                tile_color = CELL_COLORS.get(NUM_TO_TEXT.get(board[row][col], ""), (126, 170, 196))
                pygame.draw.rect(tile_surface, tile_color,
                                (0, 0, scaled_width, scaled_height), border_radius=CORNER_RADIUS + 8)
                text_str = NUM_TO_TEXT.get(board[row][col], f"{board[row][col]}")
                text = FONT.render(text_str, True, TEXT_COLOR)
                text_rect = text.get_rect(center=(scaled_width//2, scaled_height//2))
                tile_surface.blit(text, text_rect)

                if new_tile and (current_time - new_tile['start_time'] < 0.3):
                    tile_surface.set_alpha(alpha)

                screen.blit(tile_surface, rect)
                
    # Draw movement animations for moving tiles
    for anim in movement_animations:
        elapsed = current_time - anim['start_time']
        if elapsed < anim['duration']:
            progress = elapsed / anim['duration']
            # Linear interpolation from start to destination
            from_row, from_col = anim['from']
            to_row, to_col = anim['to']
            current_row = from_row + (to_row - from_row) * progress
            current_col = from_col + (to_col - from_col) * progress
            # Compute pixel position for the moving tile
            x = int(current_col * CELL_SIZE)
            y = int(INFO_HEIGHT + current_row * CELL_SIZE)
            scaled_width = CELL_SIZE - GRID_GAP
            scaled_height = CELL_SIZE - GRID_GAP
            rect = pygame.Rect(x + GRID_GAP//2, y + GRID_GAP//2, scaled_width, scaled_height)
            tile_surface = pygame.Surface((scaled_width, scaled_height), pygame.SRCALPHA)
            tile_color = CELL_COLORS.get(NUM_TO_TEXT.get(anim['value'], ""), (126, 170, 196))
            pygame.draw.rect(tile_surface, tile_color, (0, 0, scaled_width, scaled_height), border_radius=CORNER_RADIUS + 8)
            text_str = NUM_TO_TEXT.get(anim['value'], f"{anim['value']}")
            text = FONT.render(text_str, True, TEXT_COLOR)
            text_rect = text.get_rect(center=(scaled_width//2, scaled_height//2))
            tile_surface.blit(text, text_rect)
            screen.blit(tile_surface, rect)
    
    # Draw border rectangle
    border_rect = pygame.Rect(0, INFO_HEIGHT - 3, WIDTH, GAME_HEIGHT + 5)
    pygame.draw.rect(screen, BORDER_COLOR, border_rect, BORDER_WIDTH, border_radius=CORNER_RADIUS * 2)

    draw_info(score, playtime, moves, board)

def draw_info(score, playtime, moves, board):
    score_text = FONT.render(f"麦芽糖得分: {score}", True, TEXT_COLOR)
    screen.blit(score_text, (10, 5))

    time_text = FONT.render(f"时间: {int(playtime)}秒", True, TEXT_COLOR)
    screen.blit(time_text, (10, 35))

    moves_text = FONT.render(f"动作数: {moves}", True, TEXT_COLOR)
    moves_text_rect = moves_text.get_rect(topright=(WIDTH - 10, 5))
    screen.blit(moves_text, moves_text_rect)

    unlocked_chars = set()
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            tile_val = board[r][c]
            if tile_val in NUM_TO_TEXT:
                unlocked_chars.add(NUM_TO_TEXT[tile_val])

    milestone_str = "".join(MILESTONE_ORDER)
    base_x = 10
    base_y = 65
    cur_x = base_x

    for ch in milestone_str:
        color = MILESTONE_UNLOCKED_COLOR if ch in unlocked_chars else MILESTONE_LOCKED_COLOR
        ch_surface = FONT.render(ch, True, color)
        screen.blit(ch_surface, (cur_x, base_y))
        cur_x += ch_surface.get_width() + 2

    draw_restart_button()

def draw_restart_button(mouse_down=False):
    x = WIDTH - RESTART_BUTTON_WIDTH - 10
    y = 65
    button_rect = pygame.Rect(x, y, RESTART_BUTTON_WIDTH, RESTART_BUTTON_HEIGHT)

    mx, my = pygame.mouse.get_pos()
    if button_rect.collidepoint(mx, my):
        if mouse_down:
            color = RESTART_BTN_COLOR_CLICK
        else:
            color = RESTART_BTN_COLOR_HOVER
    else:
        color = RESTART_BTN_COLOR_NORMAL

    pygame.draw.rect(screen, color, button_rect, border_radius=CORNER_RADIUS)

    btn_font = pygame.font.SysFont("Microsoft YaHei", 18)
    text_surface = btn_font.render(RESTART_BUTTON_TEXT, True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=button_rect.center)
    screen.blit(text_surface, text_rect)

def add_new_tile(board):
    empty_cells = [
        (r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if board[r][c] == 0
    ]
    if empty_cells:
        r, c = random.choice(empty_cells)
        # 90% chance of generating a 2 and 10% chance of generating a 4
        value = 2 if random.random() < 0.9 else 4
        board[r][c] = value
        return (r, c, value)
    return None

def remove_random_tile(board):
    non_zero_cells = [
        (r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if board[r][c] != 0
    ]
    if non_zero_cells:
        r, c = random.choice(non_zero_cells)
        board[r][c] = 0

def copy_board(board):
    return [row[:] for row in board]

def save_game(board, history, score, moves, accumulated_time):
    data = {
        "board": board,
        "history": history,
        "score": score,
        "moves": moves,
        "accumulated_time": accumulated_time,
    }
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception as e:
        print("Error saving game:", e)

def load_game():
    if not os.path.exists(SAVE_FILE):
        return None
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if all(k in data for k in ("board", "history", "score", "moves", "accumulated_time")):
            return data
        else:
            return None
    except Exception as e:
        print("Error loading game:", e)
        return None

# --- New helper functions for movement animation ---

def process_row_left(row, row_index, current_time):
    """
    Process a row for a left move.
    Returns: new_row, row_score, list of merge animations, list of movement animations, and a flag if changed.
    Each merge animation is a dict: {'pos': (row, dest_index), 'value': merged_value, 'start_time': current_time}
    Each movement animation is a dict: {'from': (row, orig_col), 'to': (row, dest_index), 'value': tile_value, 'start_time': current_time, 'duration': 0.07}
    """
    filtered = [(val, col) for col, val in enumerate(row) if val != 0]
    new_row = []
    row_score = 0
    merge_anims = []
    move_anims = []
    dest_index = 0
    i = 0
    changed = False
    while i < len(filtered):
        if i + 1 < len(filtered) and filtered[i][0] == filtered[i+1][0]:
            new_val = filtered[i][0] * 2
            new_row.append(new_val)
            row_score += new_val
            merge_anims.append({'pos': (row_index, dest_index), 'value': new_val, 'start_time': current_time})
            # Animate movement for both tiles if they are not already at dest_index.
            if filtered[i][1] != dest_index:
                move_anims.append({'from': (row_index, filtered[i][1]), 'to': (row_index, dest_index), 'value': filtered[i][0], 'start_time': current_time, 'duration': 0.07})
            if filtered[i+1][1] != dest_index:
                move_anims.append({'from': (row_index, filtered[i+1][1]), 'to': (row_index, dest_index), 'value': filtered[i+1][0], 'start_time': current_time, 'duration': 0.07})
            if filtered[i][1] != dest_index or filtered[i+1][1] != dest_index:
                changed = True
            i += 2
            dest_index += 1
        else:
            new_val = filtered[i][0]
            new_row.append(new_val)
            if filtered[i][1] != dest_index:
                move_anims.append({'from': (row_index, filtered[i][1]), 'to': (row_index, dest_index), 'value': filtered[i][0], 'start_time': current_time, 'duration': 0.07})
                changed = True
            i += 1
            dest_index += 1
    # Pad with zeros
    while len(new_row) < GRID_SIZE:
        new_row.append(0)
    if new_row != row:
        changed = True
    return new_row, row_score, merge_anims, move_anims, changed

def process_row_right(row, row_index, current_time):
    """
    Process a row for a right move.
    We reverse the row, process as left, then reverse the result and adjust the animation coordinates.
    """
    reversed_row = list(reversed(row))
    new_temp, row_score, merge_anims_temp, move_anims_temp, changed = process_row_left(reversed_row, row_index, current_time)
    new_row = list(reversed(new_temp))
    merge_anims = []
    for anim in merge_anims_temp:
        orig_pos = anim['pos']
        new_pos = (orig_pos[0], GRID_SIZE - 1 - orig_pos[1])
        merge_anims.append({'pos': new_pos, 'value': anim['value'], 'start_time': anim['start_time']})
    move_anims = []
    for anim in move_anims_temp:
        orig_from = anim['from']
        orig_to = anim['to']
        new_from = (orig_from[0], GRID_SIZE - 1 - orig_from[1])
        new_to = (orig_to[0], GRID_SIZE - 1 - orig_to[1])
        move_anims.append({'from': new_from, 'to': new_to, 'value': anim['value'], 'start_time': anim['start_time'], 'duration': anim['duration']})
    return new_row, row_score, merge_anims, move_anims, changed

def move_left(board):
    moved = False
    total_score = 0
    merges_global = []
    moves_global = []  # movement animations
    current_time = time.time()
    for r in range(GRID_SIZE):
        original_row = board[r]
        new_row, row_score, merge_anims, move_anims, row_changed = process_row_left(original_row, r, current_time)
        total_score += row_score
        board[r] = new_row
        if row_changed:
            moved = True
        merges_global.extend(merge_anims)
        moves_global.extend(move_anims)
    return moved, total_score, merges_global, moves_global

def move_right(board):
    moved = False
    total_score = 0
    merges_global = []
    moves_global = []
    current_time = time.time()
    for r in range(GRID_SIZE):
        original_row = board[r]
        new_row, row_score, merge_anims, move_anims, row_changed = process_row_right(original_row, r, current_time)
        total_score += row_score
        board[r] = new_row
        if row_changed:
            moved = True
        merges_global.extend(merge_anims)
        moves_global.extend(move_anims)
    return moved, total_score, merges_global, moves_global

def move_up(board):
    # Transpose the board
    board_t = [list(row) for row in zip(*board)]
    moved, score, merge_anims, move_anims = move_left(board_t)
    # Transpose back
    new_board = [list(row) for row in zip(*board_t)]
    for r in range(GRID_SIZE):
        board[r] = new_board[r]
    # Adjust animations (swap row and col)
    merge_anims_adjusted = []
    for anim in merge_anims:
        r_t, c_t = anim['pos']
        merge_anims_adjusted.append({'pos': (c_t, r_t), 'value': anim['value'], 'start_time': anim['start_time']})
    move_anims_adjusted = []
    for anim in move_anims:
        frm = anim['from']
        to = anim['to']
        move_anims_adjusted.append({'from': (frm[1], frm[0]), 'to': (to[1], to[0]), 'value': anim['value'], 'start_time': anim['start_time'], 'duration': anim['duration']})
    return moved, score, merge_anims_adjusted, move_anims_adjusted

def move_down(board):
    # Use move_right on the transposed board to simulate downward movement
    board_t = [list(row) for row in zip(*board)]
    moved, score, merge_anims, move_anims = move_right(board_t)
    new_board = [list(row) for row in zip(*board_t)]
    for r in range(GRID_SIZE):
        board[r] = new_board[r]
    # Adjust animations (swap row and col)
    merge_anims_adjusted = []
    for anim in merge_anims:
        r_t, c_t = anim['pos']
        merge_anims_adjusted.append({'pos': (c_t, r_t), 'value': anim['value'], 'start_time': anim['start_time']})
    move_anims_adjusted = []
    for anim in move_anims:
        frm = anim['from']
        to = anim['to']
        move_anims_adjusted.append({'from': (frm[1], frm[0]), 'to': (to[1], to[0]), 'value': anim['value'], 'start_time': anim['start_time'], 'duration': anim['duration']})
    return moved, score, merge_anims_adjusted, move_anims_adjusted

def init_new_game():
    board = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
    new_tiles = []
    tile1 = add_new_tile(board)
    if tile1:
        new_tiles.append({'pos': (tile1[0], tile1[1]), 'value': tile1[2], 'start_time': time.time()})
    tile2 = add_new_tile(board)
    if tile2:
        new_tiles.append({'pos': (tile2[0], tile2[1]), 'value': tile2[2], 'start_time': time.time()})
    history = [copy_board(board)]
    score = 0
    moves = 0
    accumulated_time = 0.0
    merge_animations = []
    movement_animations = []
    return board, history, score, moves, accumulated_time, new_tiles, merge_animations, movement_animations

def fade_out_animation(old_board, new_board, duration=1.5):
    clock = pygame.time.Clock()
    start_time = time.time()
    
    old_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    old_surface.fill(BACKGROUND_COLOR)
    
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            value = old_board[row][col]
            x = col * CELL_SIZE
            y = INFO_HEIGHT + row * CELL_SIZE
            pygame.draw.rect(old_surface, CELL_COLOR, (x, y, CELL_SIZE, CELL_SIZE))
            if value:
                tile_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                tile_color = CELL_COLORS.get(NUM_TO_TEXT.get(value, ""), (126, 170, 196))
                tile_surface.fill(tile_color)
                text_str = NUM_TO_TEXT.get(value, f"{value}")
                text = FONT.render(text_str, True, TEXT_COLOR)
                text_rect = text.get_rect(center=(CELL_SIZE//2, CELL_SIZE//2))
                tile_surface.blit(text, text_rect)
                old_surface.blit(tile_surface, (x, y))
    
    while True:
        elapsed = time.time() - start_time
        if elapsed > duration:
            break
        
        alpha = int(255 * (1 - elapsed/duration))
        temp_surface = old_surface.copy()
        temp_surface.set_alpha(alpha)
        
        screen.fill(BACKGROUND_COLOR)
        draw_board(new_board, 0, 0, 0, [], [], [], time.time())
        
        screen.blit(temp_surface, (0, 0))
        
        pygame.display.update()
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

def main():
    loaded_data = load_game()

    current_time_init = time.strftime("%m月%d日，%H点%M分")
    welcome_msg = f"现在是{current_time_init}\n欢迎进入2048麦芽糖特别版~\nMade with LOVE by XiaoEYu^ ^"
    show_temp_message(welcome_msg, duration=5)

    if loaded_data:
        board = loaded_data["board"]
        history = loaded_data["history"]
        score = loaded_data["score"]
        moves = loaded_data["moves"]
        accumulated_time = loaded_data["accumulated_time"]
        new_tiles = []
        merge_animations = []
        movement_animations = []
    else:
        board, history, score, moves, accumulated_time, new_tiles, merge_animations, movement_animations = init_new_game()

    start_time = time.time()
    input_buffer = ""
    mouse_down_on_button = False

    # Create a clock for frame rate limiting
    clock = pygame.time.Clock()

    while True:
        screen.fill(BACKGROUND_COLOR)
        current_session_time = time.time() - start_time
        playtime = accumulated_time + current_session_time
        current_time = time.time()
        draw_board(board, score, playtime, moves, new_tiles, merge_animations, movement_animations, current_time)
        pygame.display.update()

        # Limit frame rate to 60 FPS
        clock.tick(60)
        
        # Remove expired new tile and merge animations
        new_tiles = [tile for tile in new_tiles if current_time - tile['start_time'] < 0.3]
        merge_animations = [merge for merge in merge_animations if current_time - merge['start_time'] < 0.3]
        # Remove movement animations that have completed
        movement_animations = [move for move in movement_animations if current_time - move['start_time'] < move['duration']]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                accumulated_time += (time.time() - start_time)
                save_game(board, history, score, moves, accumulated_time)
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    x = WIDTH - RESTART_BUTTON_WIDTH - 10
                    y = 65
                    button_rect = pygame.Rect(x, y, RESTART_BUTTON_WIDTH, RESTART_BUTTON_HEIGHT)
                    if button_rect.collidepoint(event.pos):
                        mouse_down_on_button = True

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    x = WIDTH - RESTART_BUTTON_WIDTH - 10
                    y = 65
                    button_rect = pygame.Rect(x, y, RESTART_BUTTON_WIDTH, RESTART_BUTTON_HEIGHT)
                    if button_rect.collidepoint(event.pos) and mouse_down_on_button:
                        if confirm_action("宝宝要重新开始吗 (yes/no)"):
                            board, history, score, moves, accumulated_time, new_new_tiles, new_merge_animations, new_move_anims = init_new_game()
                            new_tiles = new_new_tiles
                            merge_animations = new_merge_animations
                            movement_animations = new_move_anims
                            save_game(board, history, score, moves, accumulated_time)
                    mouse_down_on_button = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if confirm_action("宝宝确定要洗牌吗? (yes/no)"):
                        history.append(copy_board(board))
                        if len(history) > MAX_HISTORY_SIZE:
                            history.pop(0)
                        board = shuffle_board(board)
                        accumulated_time += time.time() - start_time
                        save_game(board, history, score, moves, accumulated_time)
                        start_time = time.time()
                        show_temp_message("牌牌洗香香中~", 1.2)
                    continue

                board_copy = copy_board(board)
                move_score = 0
                merges_info = []
                move_anims = []
                moved = False

                if event.key == pygame.K_LEFT:
                    moved, move_score, merges_info, move_anims = move_left(board)
                elif event.key == pygame.K_RIGHT:
                    moved, move_score, merges_info, move_anims = move_right(board)
                elif event.key == pygame.K_UP:
                    moved, move_score, merges_info, move_anims = move_up(board)
                elif event.key == pygame.K_DOWN:
                    moved, move_score, merges_info, move_anims = move_down(board)
                elif event.key == pygame.K_z:
                    if len(history) > 1:
                        old_board = copy_board(board)
                        history.pop()
                        new_board = history[-1]
                        fade_out_animation(old_board, new_board)
                        board = new_board
                        show_temp_message("麦芽糖成功撤回了上一步操作~", 1.5)
                    continue
                else:
                    input_buffer += event.unicode
                    input_buffer = handle_special_input(input_buffer, board)
                    continue

                if moved:
                    score += move_score
                    moves += 1
                    # Add merge animations
                    merge_animations.extend(merges_info)
                    # Add movement animations for sliding tiles
                    movement_animations.extend(move_anims)

                    new_tile = add_new_tile(board)
                    if new_tile:
                        new_tiles.append({'pos': (new_tile[0], new_tile[1]), 'value': new_tile[2], 'start_time': current_time})

                    history.append(copy_board(board))
                    if len(history) > MAX_HISTORY_SIZE:
                        history.pop(0)

                    accumulated_time += (time.time() - start_time)
                    start_time = time.time()
                    save_game(board, history, score, moves, accumulated_time)

if __name__ == "__main__":
    main()
