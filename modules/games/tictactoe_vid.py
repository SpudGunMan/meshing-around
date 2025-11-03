# Tic-Tac-Toe Video Display Module for Meshtastic mesh-bot
# Uses Pygame to render the game board visually
# 2025 K7MHI Kelly Keeton

import pygame

latest_board = [" "] * 9  # or 27 for 3D
latest_meta = {} # To store metadata like status

def handle_tictactoe_payload(payload, from_id=None):
    global latest_board, latest_meta
    #print("Received payload:", payload)
    board, meta = parse_tictactoe_message(payload)
    #print("Parsed board:", board)
    if board:
        latest_board = board
        latest_meta = meta if meta else {}

def parse_tictactoe_message(msg):
    # msg is already stripped of 'MTTT:' prefix
    parts = msg.split("|")
    if not parts or len(parts[0]) < 9:
        return None, None  # Not enough data for a board
    board_str = parts[0]
    meta = {}
    if len(parts) > 1:
        meta["nodeID"] = parts[1] if len(parts) > 1 else ""
        meta["channel"] = parts[2] if len(parts) > 2 else ""
        meta["deviceID"] = parts[3] if len(parts) > 3 else ""
        # Look for status in any remaining parts
        for part in parts[4:]:
            if part.startswith("status="):
                meta["status"] = part.split("=", 1)[1]
    symbol_map = {"0": " ", "1": "❌", "2": "⭕️"}
    board = [symbol_map.get(c, " ") for c in board_str]
    return board, meta

def draw_board(screen, board, meta=None):
    screen.fill((30, 30, 30))
    width, height = screen.get_size()
    margin = int(min(width, height) * 0.05)
    font_size = int(height * 0.12)
    font = pygame.font.Font(None, font_size)

    # Draw the title at the top center, scaled
    title_font = pygame.font.Font(None, int(height * 0.08))
    title_text = title_font.render("MeshBot Tic-Tac-Toe", True, (220, 220, 255))
    title_rect = title_text.get_rect(center=(width // 2, margin // 2 + 10))
    screen.blit(title_text, title_rect)

    # Add a buffer below the title
    title_buffer = int(height * 0.06)

    # --- Show win/draw message if present ---
    if meta and "status" in meta:
        status = meta["status"]
        msg_font = pygame.font.Font(None, int(height * 0.06))  # Smaller font
        msg_y = title_rect.bottom + int(height * 0.04)         # Just under the title
        if status == "win":
            msg = "Game Won!"
            text = msg_font.render(msg, True, (100, 255, 100))
            text_rect = text.get_rect(center=(width // 2, msg_y))
            screen.blit(text, text_rect)
        elif status == "tie":
            msg = "Tie Game!"
            text = msg_font.render(msg, True, (255, 220, 120))
            text_rect = text.get_rect(center=(width // 2, msg_y))
            screen.blit(text, text_rect)
        elif status == "loss":
            msg = "You Lost!"
            text = msg_font.render(msg, True, (255, 100, 100))
            text_rect = text.get_rect(center=(width // 2, msg_y))
            screen.blit(text, text_rect)
        elif status == "new":
            msg = "Welcome! New Game"
            text = msg_font.render(msg, True, (200, 255, 200))
            text_rect = text.get_rect(center=(width // 2, msg_y))
            screen.blit(text, text_rect)
            # Do NOT return here—let the board draw as normal
        elif status != "refresh":
            msg = status.capitalize()
            text = msg_font.render(msg, True, (255, 220, 120))
            text_rect = text.get_rect(center=(width // 2, msg_y))
            screen.blit(text, text_rect)
            # Don't return here—let the board draw as normal

    # Show waiting message if board is empty, unless status is "new"
    if all(cell.strip() == "" or cell.strip() == " " for cell in board):
        if not (meta and meta.get("status") == "new"):
            msg_font = pygame.font.Font(None, int(height * 0.09))
            msg = "Waiting for player..."
            text = msg_font.render(msg, True, (200, 200, 200))
            text_rect = text.get_rect(center=(width // 2, height // 2))
            screen.blit(text, text_rect)
            pygame.display.flip()
            return

    def draw_x(rect):
        thickness = max(4, rect.width // 12)
        pygame.draw.line(screen, (255, 80, 80), rect.topleft, rect.bottomright, thickness)
        pygame.draw.line(screen, (255, 80, 80), rect.topright, rect.bottomleft, thickness)

    def draw_o(rect):
        center = rect.center
        radius = rect.width // 2 - max(6, rect.width // 16)
        thickness = max(4, rect.width // 12)
        pygame.draw.circle(screen, (80, 180, 255), center, radius, thickness)

    if len(board) == 9:
        # 2D: Center a single 3x3 grid, scale to fit
        size = min((width - 2*margin)//3, (height - 2*margin - title_buffer)//3)
        offset_x = (width - size*3) // 2
        offset_y = (height - size*3) // 2 + title_buffer // 2
        offset_y = max(offset_y, title_rect.bottom + title_buffer)
        # Index number font and buffer
        small_index_font = pygame.font.Font(None, int(size * 0.38))
        index_buffer_x = int(size * 0.16)
        index_buffer_y = int(size * 0.10)
        for i in range(3):
            for j in range(3):
                rect = pygame.Rect(offset_x + j*size, offset_y + i*size, size, size)
                pygame.draw.rect(screen, (200, 200, 200), rect, 2)
                idx = i*3 + j
                # Draw index number in top-left, start at 1
                idx_text = small_index_font.render(str(idx + 1), True, (120, 120, 160))
                idx_rect = idx_text.get_rect(topleft=(rect.x + index_buffer_x, rect.y + index_buffer_y))
                screen.blit(idx_text, idx_rect)
                val = board[idx].strip()
                if val == "❌" or val == "X":
                    draw_x(rect)
                elif val == "⭕️" or val == "O":
                    draw_o(rect)
                elif val:
                    text = font.render(val, True, (255, 255, 255))
                    text_rect = text.get_rect(center=rect.center)
                    screen.blit(text, text_rect)
    elif len(board) == 27:
        # 3D: Stack three 3x3 grids vertically, with horizontal offsets for 3D effect, scale to fit
        size = min((width - 2*margin)//7, (height - 4*margin - title_buffer)//9)
        base_offset_x = (width - (size * 3)) // 2
        offset_y = (height - (size*9 + margin*2)) // 2 + title_buffer // 2
        offset_y = max(offset_y, title_rect.bottom + title_buffer)
        small_font = pygame.font.Font(None, int(height * 0.045))
        small_index_font = pygame.font.Font(None, int(size * 0.38))
        index_buffer_x = int(size * 0.16)
        index_buffer_y = int(size * 0.10)
        for display_idx, layer in enumerate(reversed(range(3))):
            layer_offset_x = base_offset_x + (layer - 1) * 2 * size
            layer_y = offset_y + display_idx * (size*3 + margin)
            label_text = f"Layer {layer+1}"
            label = small_font.render(label_text, True, (180, 180, 220))
            label_rect = label.get_rect(center=(layer_offset_x + size*3//2, layer_y + size*3 + int(size*0.2)))
            screen.blit(label, label_rect)
            for i in range(3):
                for j in range(3):
                    rect = pygame.Rect(layer_offset_x + j*size, layer_y + i*size, size, size)
                    pygame.draw.rect(screen, (200, 200, 200), rect, 2)
                    idx = layer*9 + i*3 + j
                    idx_text = small_index_font.render(str(idx + 1), True, (120, 120, 160))
                    idx_rect = idx_text.get_rect(topleft=(rect.x + index_buffer_x, rect.y + index_buffer_y))
                    screen.blit(idx_text, idx_rect)
                    val = board[idx].strip()
                    if val == "❌" or val == "X":
                        draw_x(rect)
                    elif val == "⭕️" or val == "O":
                        draw_o(rect)
                    elif val:
                        text = font.render(val, True, (255, 255, 255))
                        text_rect = text.get_rect(center=rect.center)
                        screen.blit(text, text_rect)
    pygame.display.flip()

def ttt_main():
    global latest_board, latest_meta
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Tic-Tac-Toe 3D Display")
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
        draw_board(screen, latest_board, latest_meta)  # <-- Pass meta/status
        pygame.display.flip()
        pygame.time.wait(75)  # or 50-100 for lower CPU
    pygame.quit()
