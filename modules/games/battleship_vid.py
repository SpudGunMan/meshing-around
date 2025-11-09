#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Battleship Display Module Meshing Around
# 2025 K7MHI Kelly Keeton
import pygame
import sys
import time

from modules.games.battleship import Battleship, SHIP_NAMES, SIZE, OCEAN, FIRE, HIT

CELL_SIZE = 40
BOARD_MARGIN = 50
STATUS_WIDTH = 320

latest_battleship_board = None
latest_battleship_meta = None

def draw_board(screen, board, top_left, cell_size, show_ships=False):
    font = pygame.font.Font(None, 28)
    x0, y0 = top_left
    for y in range(SIZE):
        for x in range(SIZE):
            rect = pygame.Rect(x0 + x*cell_size, y0 + y*cell_size, cell_size, cell_size)
            pygame.draw.rect(screen, (100, 100, 200), rect, 1)
            val = board[y][x]
            # Show ships if requested, otherwise hide ship numbers
            if not show_ships and val.isdigit():
                val = OCEAN
            color = (200, 200, 255) if val == OCEAN else (255, 0, 0) if val == FIRE else (0, 255, 0) if val == HIT else (255,255,255)
            if val != OCEAN:
                pygame.draw.rect(screen, color, rect)
            text = font.render(val, True, (0,0,0))
            screen.blit(text, rect.move(10, 5))
    # Draw row/col labels
    for i in range(SIZE):
        # Col numbers
        num_surface = font.render(str(i+1), True, (255, 255, 0))
        screen.blit(num_surface, (x0 + i*cell_size + cell_size//2 - 8, y0 - 24))
        # Row letters
        letter_surface = font.render(chr(ord('A') + i), True, (255, 255, 0))
        screen.blit(letter_surface, (x0 - 28, y0 + i*cell_size + cell_size//2 - 10))

def draw_status_panel(screen, game, top_left, width, height, is_player=True):
    font = pygame.font.Font(None, 32)
    x0, y0 = top_left
    pygame.draw.rect(screen, (30, 30, 60), (x0, y0, width, height), border_radius=10)
    # Title
    title = font.render("Game Status", True, (255, 255, 0))
    screen.blit(title, (x0 + 10, y0 + 10))
    # Ships status
    ships_title = font.render("Ships Remaining:", True, (200, 200, 255))
    screen.blit(ships_title, (x0 + 10, y0 + 60))
    # Get ship status
    if is_player:
        status_dict = game.get_ship_status(game.player_board)
    else:
        status_dict = game.get_ship_status(game.ai_board)
    for i, ship in enumerate(SHIP_NAMES):
        status = status_dict.get(i, "Afloat")
        name_color = (200, 200, 255)
        if status.lower() == "sunk":
            status_color = (255, 0, 0)
            status_text = "Sunk"
        else:
            status_color = (0, 255, 0)
            status_text = "Afloat"
        ship_name_surface = font.render(f"{ship}:", True, name_color)
        screen.blit(ship_name_surface, (x0 + 20, y0 + 100 + i * 35))
        status_surface = font.render(f"{status_text}", True, status_color)
        screen.blit(status_surface, (x0 + 180, y0 + 100 + i * 35))

def battleship_visual_main(game):
    pygame.init()
    screen = pygame.display.set_mode((2*SIZE*CELL_SIZE + STATUS_WIDTH + 3*BOARD_MARGIN, SIZE*CELL_SIZE + 2*BOARD_MARGIN))
    pygame.display.set_caption("Battleship Visualizer")
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
        screen.fill((20, 20, 30))
        # Draw radar (left)
        draw_board(screen, game.get_player_radar(), (BOARD_MARGIN, BOARD_MARGIN+30), CELL_SIZE, show_ships=False)
        radar_label = pygame.font.Font(None, 36).render("Your Radar", True, (0,255,255))
        screen.blit(radar_label, (BOARD_MARGIN, BOARD_MARGIN))
        # Draw player board (right)
        draw_board(screen, game.get_player_board(), (SIZE*CELL_SIZE + 2*BOARD_MARGIN, BOARD_MARGIN+30), CELL_SIZE, show_ships=True)
        board_label = pygame.font.Font(None, 36).render("Your Board", True, (0,255,255))
        screen.blit(board_label, (SIZE*CELL_SIZE + 2*BOARD_MARGIN, BOARD_MARGIN))
        # Draw status panel (far right)
        draw_status_panel(screen, game, (2*SIZE*CELL_SIZE + 2*BOARD_MARGIN, BOARD_MARGIN), STATUS_WIDTH, SIZE*CELL_SIZE)
        pygame.display.flip()
        clock.tick(30)
    pygame.quit()
    sys.exit()

def parse_battleship_message(msg):
    # Expected payload:
    # MBSP|label|timestamp|nodeID|deviceID|sessionID|status|shotsFired|boardType|shipsStatus|boardString
    print("Parsing Battleship message:", msg)

# if __name__ == "__main__":
#     # Example: create a new game and show the boards
#     game = Battleship(vs_ai=True)
#     battleship_visual_main(game)