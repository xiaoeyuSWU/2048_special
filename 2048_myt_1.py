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

def draw_board(board, score, playtime, moves, new_tiles, merge_animations, current_time):
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            value = board[row][col]
            x = col * CELL_SIZE
            y = INFO_HEIGHT + row * CELL_SIZE
            cell_rect = pygame.Rect(x + GRID_GAP//2, 
                                y + GRID_GAP//2, 
                                CELL_SIZE - GRID_GAP, 
                                CELL_SIZE - GRID_GAP)
            pygame.draw.rect(screen, CELL_COLOR, cell_rect, border_radius=CORNER_RADIUS)
            if value:
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
                tile_color = CELL_COLORS.get(NUM_TO_TEXT.get(value, ""), (126, 170, 196))
                pygame.draw.rect(tile_surface, tile_color,
                                (0, 0, scaled_width, scaled_height), border_radius=CORNER_RADIUS + 8)
                text_str = NUM_TO_TEXT.get(value, f"{value}")
                text = FONT.render(text_str, True, TEXT_COLOR)
                text_rect = text.get_rect(center=(scaled_width//2, scaled_height//2))
                tile_surface.blit(text, text_rect)

                if new_tile and elapsed_time < 0.3:
                    tile_surface.set_alpha(alpha)

                screen.blit(tile_surface, rect)
                
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
    if random.random() > 0.2:
        empty_cells = [
            (r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if board[r][c] == 0
        ]
        if empty_cells:
            r, c = random.choice(empty_cells)
            value = random.choice([2, 4])
            board[r][c] = value
            return (r, c, value)
    return None

def merge_row(row):
    merged = []
    score = 0
    merges_info = []
    i = 0
    while i < len(row):
        if i + 1 < len(row) and row[i] == row[i + 1] and row[i] != 0:
            merged_value = row[i] * 2
            merged.append(merged_value)
            score += merged_value
            merges_info.append((len(merged) - 1, merged_value))
            i += 2
        else:
            merged.append(row[i])
            i += 1
    return merged, score, merges_info

def move_left(board):
    moved = False
    total_score = 0
    merges_global = []

    for r in range(GRID_SIZE):
        filtered = [x for x in board[r] if x != 0]
        merged_row, row_score, merges_info = merge_row(filtered)
        total_score += row_score
        merged_row += [0] * (GRID_SIZE - len(merged_row))

        if merged_row != board[r]:
            moved = True

        board[r] = merged_row

        for (col_in_merged, val) in merges_info:
            merges_global.append({'pos': (r, col_in_merged), 'value': val, 'start_time': time.time()})

    return moved, total_score, merges_global

def move_right(board):
    moved = False
    total_score = 0
    merges_global = []

    for r in range(GRID_SIZE):
        reversed_row = list(reversed(board[r]))
        filtered = [x for x in reversed_row if x != 0]
        merged_row, row_score, merges_info = merge_row(filtered)
        total_score += row_score

        merged_row += [0] * (GRID_SIZE - len(merged_row))
        final_row = list(reversed(merged_row))

        if final_row != board[r]:
            moved = True

        board[r] = final_row

        for (col_in_merged, val) in merges_info:
            actual_col = (GRID_SIZE - 1) - col_in_merged
            merges_global.append({'pos': (r, actual_col), 'value': val, 'start_time': time.time()})

    return moved, total_score, merges_global

def move_up(board):
    moved = False
    total_score = 0
    merges_global = []

    board_t = [list(row) for row in zip(*board)]
    m2, s2, merges_t = move_left(board_t)
    moved = moved or m2
    total_score += s2

    board_new = [list(row) for row in zip(*board_t)]
    for r in range(GRID_SIZE):
        board[r] = board_new[r]

    for merge in merges_t:
        r_t, c_t = merge['pos']
        merges_global.append({'pos': (c_t, r_t), 'value': merge['value'], 'start_time': merge['start_time']})

    return moved, total_score, merges_global

def move_down(board):
    moved = False
    total_score = 0
    merges_global = []

    board_t = [list(row) for row in zip(*board)]
    for r in range(GRID_SIZE):
        board_t[r] = list(reversed(board_t[r]))

    m2, s2, merges_t = move_left(board_t)
    moved = moved or m2
    total_score += s2

    for r in range(GRID_SIZE):
        board_t[r] = list(reversed(board_t[r]))

    board_new = [list(row) for row in zip(*board_t)]
    for r in range(GRID_SIZE):
        board[r] = board_new[r]

    for merge in merges_t:
        r_t, c_t = merge['pos']
        actual_col_t = (GRID_SIZE - 1) - c_t
        actual_row = actual_col_t
        actual_col = r_t
        merges_global.append({'pos': (actual_row, actual_col), 'value': merge['value'], 'start_time': merge['start_time']})

    return moved, total_score, merges_global

def copy_board(board):
    return [row[:] for row in board]

def remove_random_tile(board):
    non_zero_cells = [
        (r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if board[r][c] != 0
    ]
    if non_zero_cells:
        r, c = random.choice(non_zero_cells)
        board[r][c] = 0

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
    return board, history, score, moves, accumulated_time, new_tiles, merge_animations

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
    else:
        board, history, score, moves, accumulated_time, new_tiles, merge_animations = init_new_game()

    start_time = time.time()
    input_buffer = ""
    mouse_down_on_button = False

    while True:
        screen.fill(BACKGROUND_COLOR)
        current_session_time = time.time() - start_time
        playtime = accumulated_time + current_session_time
        current_time = time.time()
        draw_board(board, score, playtime, moves, new_tiles, merge_animations, current_time)
        pygame.display.update()

        new_tiles = [tile for tile in new_tiles if current_time - tile['start_time'] < 0.3]
        merge_animations = [merge for merge in merge_animations if current_time - merge['start_time'] < 0.3]

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
                            board, history, score, moves, accumulated_time, new_new_tiles, new_merge_animations = init_new_game()
                            new_tiles.extend(new_new_tiles)
                            merge_animations.extend(new_merge_animations)
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
                score_copy = score
                merges_info = []
                moved = False
                move_score = 0

                if event.key == pygame.K_LEFT:
                    moved, move_score, merges_info = move_left(board)
                elif event.key == pygame.K_RIGHT:
                    moved, move_score, merges_info = move_right(board)
                elif event.key == pygame.K_UP:
                    moved, move_score, merges_info = move_up(board)
                elif event.key == pygame.K_DOWN:
                    moved, move_score, merges_info = move_down(board)
                elif event.key == pygame.K_z:
                    if len(history) > 1:
                        old_board = copy_board(board)
                        history.pop()
                        new_board = history[-1]
                        fade_out_animation(old_board, new_board)
                        board = new_board
                        show_temp_message("麦芽糖成功撤回了上一步操作~", 1.5)
                else:
                    input_buffer += event.unicode
                    input_buffer = handle_special_input(input_buffer, board)
                    continue

                if moved:
                    score += move_score
                    moves += 1

                    for merge in merges_info:
                        merge_animations.append({'pos': merge['pos'], 'value': merge['value'], 'start_time': current_time})

                    new_tile = add_new_tile(board)
                    if new_tile:
                        new_tiles.append({'pos': (new_tile[0], new_tile[1]), 'value': new_tile[2], 'start_time': current_time})

                    history.append(copy_board(board))
                    if len(history) > MAX_HISTORY_SIZE:
                        history.pop(0)

                    accumulated_time += (time.time() - start_time)
                    start_time = time.time()
                    save_game(board, history, score, moves, accumulated_time)

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
        draw_board(new_board, 0, 0, 0, [], [], time.time())
        
        screen.blit(temp_surface, (0, 0))
        
        pygame.display.update()
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

if __name__ == "__main__":
    main()
