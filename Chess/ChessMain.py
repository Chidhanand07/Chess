import pygame as p
from Chess import ChessEngine

Width = Height = 640
Dimension = 8
SQ_Size = Height // Dimension
MAX_FPS = 60
IMAGES = {}

# Enhanced color scheme
LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)
HIGHLIGHT_COLOR = (186, 202, 68, 180)
SELECTED_COLOR = (246, 246, 105, 200)
VALID_MOVE_COLOR = (100, 100, 100, 120)


def load_images():
    pieces = [
        "bP", "bR", "bN", "bB", "bQ", "bK", "wP", "wR", "wN", "wB", "wQ", "wK"
    ]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(
            p.image.load("Chess pieces/" + piece + ".png"),
            (SQ_Size, SQ_Size)
        )


def main():
    p.init()
    screen = p.display.set_mode((Width, Height))
    p.display.set_caption("Chess")
    clock = p.time.Clock()

    game_state = ChessEngine.GameState()
    valid_moves = game_state.get_valid_moves()
    move_made = False
    load_images()

    running = True
    sq_selected = ()
    player_clicks = []

    # Font for notifications
    p.font.init()
    font = p.font.SysFont("Arial", 24, bold=True)

    while running:
        for event in p.event.get():
            if event.type == p.QUIT:
                running = False

            elif event.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()
                col = location[0] // SQ_Size
                row = location[1] // SQ_Size

                if sq_selected == (row, col):
                    sq_selected = ()
                    player_clicks = []
                else:
                    sq_selected = (row, col)
                    player_clicks.append(sq_selected)

                if len(player_clicks) == 2:
                    move = ChessEngine.Move(player_clicks[0], player_clicks[1], game_state.Board)

                    for i in range(len(valid_moves)):
                        if move == valid_moves[i]:
                            game_state.make_move(valid_moves[i])
                            move_made = True
                            sq_selected = ()
                            player_clicks = []
                            break

                    if not move_made:
                        player_clicks = [sq_selected]

            elif event.type == p.KEYDOWN:
                if event.key == p.K_LEFT:
                    game_state.undo_move()
                    move_made = True
                elif event.key == p.K_RIGHT:
                    game_state.redo_move()
                    move_made = True
                elif event.key == p.K_r:
                    game_state = ChessEngine.GameState()
                    valid_moves = game_state.get_valid_moves()
                    sq_selected = ()
                    player_clicks = []
                    move_made = False

        if move_made:
            valid_moves = game_state.get_valid_moves()
            move_made = False

        draw_game_state(screen, game_state, valid_moves, sq_selected, player_clicks)

        clock.tick(MAX_FPS)
        p.display.flip()


def draw_game_state(screen, game_state, valid_moves, sq_selected, player_clicks):
    draw_board(screen)
    highlight_squares(screen, game_state, valid_moves, sq_selected, player_clicks)
    draw_pieces(screen, game_state.Board)
    draw_move_indicator(screen, game_state)


def draw_board(screen):
    colors = [p.Color(LIGHT_SQUARE), p.Color(DARK_SQUARE)]
    for row in range(Dimension):
        for column in range(Dimension):
            color = colors[(row + column) % 2]
            p.draw.rect(screen, color, p.Rect(column * SQ_Size, row * SQ_Size, SQ_Size, SQ_Size))

    # Add coordinate labels
    font = p.font.SysFont("Arial", 16)
    for i in range(Dimension):
        # File labels (a-h)
        label = font.render(chr(97 + i), True, DARK_SQUARE if i % 2 == 0 else LIGHT_SQUARE)
        screen.blit(label, (i * SQ_Size + SQ_Size - 18, Height - 18))

        # Rank labels (1-8)
        label = font.render(str(8 - i), True, LIGHT_SQUARE if i % 2 == 0 else DARK_SQUARE)
        screen.blit(label, (5, i * SQ_Size + 5))


def highlight_squares(screen, game_state, valid_moves, sq_selected, player_clicks):
    if sq_selected:
        row, col = sq_selected
        if game_state.Board[row][col] != "--":
            # Highlight selected square
            s = p.Surface((SQ_Size, SQ_Size))
            s.set_alpha(SELECTED_COLOR[3])
            s.fill(SELECTED_COLOR[:3])
            screen.blit(s, (col * SQ_Size, row * SQ_Size))

            # Highlight valid moves
            for move in valid_moves:
                if move.startRow == row and move.startColumn == col:
                    s = p.Surface((SQ_Size, SQ_Size))
                    s.set_alpha(VALID_MOVE_COLOR[3])
                    s.fill(VALID_MOVE_COLOR[:3])
                    screen.blit(s, (move.endColumn * SQ_Size, move.endRow * SQ_Size))

                    # Draw circle for valid move indication
                    center = (move.endColumn * SQ_Size + SQ_Size // 2, move.endRow * SQ_Size + SQ_Size // 2)
                    if game_state.Board[move.endRow][move.endColumn] == "--":
                        p.draw.circle(screen, (100, 100, 100), center, SQ_Size // 6)
                    else:
                        # Draw ring for capture
                        p.draw.circle(screen, (100, 100, 100), center, SQ_Size // 2, 4)


def draw_pieces(screen, board):
    for row in range(Dimension):
        for column in range(Dimension):
            piece = board[row][column]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(column * SQ_Size, row * SQ_Size, SQ_Size, SQ_Size))


def draw_move_indicator(screen, game_state):
    font = p.font.SysFont("Arial", 20, bold=True)
    text = "White to move" if game_state.White_To_Move else "Black to move"
    color = (255, 255, 255) if game_state.White_To_Move else (50, 50, 50)

    # Create semi-transparent background
    s = p.Surface((200, 35))
    s.set_alpha(200)
    s.fill((50, 50, 50) if game_state.White_To_Move else (240, 240, 240))
    screen.blit(s, (Width // 2 - 100, 10))

    # Render text
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(Width // 2, 27))
    screen.blit(text_surface, text_rect)


if __name__ == '__main__':
    main()