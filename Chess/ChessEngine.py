"""
This class is responsible for storing all information about current game state of a Chess game. It will also be
responsible for determining the valid moves at the current state and also keep the move log.
"""
import copy


class GameState:
    def __init__(self):
        self.Board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.move_functions = {'P': self.get_pawn_moves, 'R': self.get_rook_moves, 'B': self.get_bishop_moves,
                               'N': self.get_knight_moves, 'Q': self.get_queen_moves, 'K': self.get_king_moves}
        self.Redo_Stack = []
        self.Undo_STack = []
        self.White_To_Move = True
        self.Bin = []
        self.Move_Log = []
        self.isCheck = False
        self.Pins = []
        self.Checks = []
        self.enpassant_move = ()
    '''
    Takes a move as a parameter and executes it (This won't work for castling and enpassant)
    '''
    def make_move(self, move):
        # This method is used prevent modification of 'previous board pos' if the board is modified
        self.Undo_STack.append(copy.deepcopy(self.Board))
        self.Board[move.startRow][move.startColumn] = "--"
        self.Board[move.endRow][move.endColumn] = move.pieceMoved
        self.Move_Log.append(move)  # log the moves to undo
        self.White_To_Move = not self.White_To_Move  # swap players

        if move.is_pawn_promotion:
            self.Board[move.endRow][move.endColumn] = move.pieceMoved[0] + 'Q'

        if move.enpassant_valid:
            self.Board[move.startRow][move.endColumn] = '--'  # Capturing

        if move.pieceMoved[1] == 'P' and abs(move.startRow - move.endRow) == 2:
            self.enpassant_move = ((move.startRow + move.endRow) // 2, move.startColumn)
        else:
            self.enpassant_move = ()

    def undo_move(self):
        # With this modified function reversing castling and enpassant is possible
        if len(self.Move_Log) != 0:
            move = self.Move_Log.pop()
            self.Bin.append(move)
            self.Redo_Stack.append(copy.deepcopy(self.Board))
            self.Board = self.Undo_STack.pop()
            self.White_To_Move = not self.White_To_Move

            if move.enpassant_valid:
                self.enpassant_move = (move.endRow, move.endColumn)

    def redo_move(self):
        if self.Redo_Stack:
            self.Undo_STack.append(copy.deepcopy(self.Board))
            self.Board = self.Redo_Stack.pop()
            self.Move_Log.append(self.Bin.pop())
            self.White_To_Move = not self.White_To_Move

    '''
    All the moves considering checks 
    '''
    def get_valid_moves(self):
        moves = []
        self.isCheck, self.Pins, self.Checks = self.check_for_pins_and_check()
        location = self.find_kings()
        if location is None:
            return False  # No king found, not in check
        r, c = location
        if self.White_To_Move:
            king_row = r
            king_column = c
        else:
            king_row = r
            king_column = c
        if self.isCheck:
            if len(self.Checks) == 1:
                moves = self.get_all_possible_moves()
                check = self.Checks[0]
                check_row = check[0]
                check_col = check[1]
                piece_checking = self.Board[check_row][check_col]
                valid_squares = []
                if piece_checking[1] == 'N':
                    valid_squares = [(check_row, check_col)]
                else:
                    for i in range(1, 8):
                        valid_square = (king_row + check[2] * i, king_column + check[3] * i)
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[1] == check_col:
                            break
                for i in range(len(moves) - 1, -1, -1):  # always go backwards when iterating towards list
                    if moves[i].pieceMoved[1] != 'K':
                        if not (moves[i].endRow, moves[i].endColumn) in valid_squares:
                            moves.remove(moves[i])
            else:
                self.get_king_moves(king_row, king_column, moves)
        else:
            moves = self.get_all_possible_moves()

        return moves

    def check_for_pins_and_check(self):
        pins = []
        checks = []
        in_check = False
        location = self.find_kings()
        if location is None:
            return False  # No king found, not in check
        r, c = location
        if self.White_To_Move:
            enemy_colour = 'b'
            friend_colour = 'w'
            start_row = r
            start_col = c
        else:
            enemy_colour = 'w'
            friend_colour = 'b'
            start_row = r
            start_col = c
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possible_pin = None
            for i in range(1, 8):
                end_row = start_row + d[0] * i
                end_col = start_col + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.Board[end_row][end_col]
                    if end_piece[0] == friend_colour:
                        if possible_pin is None:
                            possible_pin = (end_row, end_col, d[0], d[1])
                        else:
                            break
                    elif end_piece[0] == enemy_colour:
                        piece_type = end_piece[1]
                        if (0 <= j <= 3 and piece_type == 'R') or \
                                (4 <= j <= 7 and piece_type == 'B') or \
                                (i == 1 and piece_type == 'P' and ((enemy_colour == 'w' and 6 <= j <= 7) or
                                                                   (enemy_colour == 'b' and 4 <= j <= 5))) or \
                                (piece_type == 'Q') or (i == 1 and piece_type == 'K'):
                            if possible_pin is None:
                                in_check = True
                                checks.append((end_row, end_col, d[0], d[1]))
                                break
                            else:
                                pins.append(possible_pin)
                                break
                        else:
                            break
                else:
                    break

        knight_direction = ((-1, -2), (-2, -1), (-2, 1), (-1, 2), (1, -2), (2, -1), (2, 1), (1, 2))
        for m in knight_direction:
            end_row = start_row + m[0]
            end_col = start_col + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.Board[end_row][end_col]
                if end_piece[0] == enemy_colour and end_piece[1] == 'N':
                    in_check = True
                    checks.append((end_row, end_col, m[0], m[1]))
        return in_check, pins, checks

    '''
    All the moves not considering checks
    '''
    def get_all_possible_moves(self):
        moves = []
        for r in range(len(self.Board)):  # Number of rows
            for c in range(len(self.Board[r])):  # number of cols in given row
                turn = self.Board[r][c][0]
                if (turn == 'w' and self.White_To_Move) or (turn == 'b' and not self.White_To_Move):
                    piece = self.Board[r][c][1]
                    self.move_functions[piece](r, c, moves)
        return moves
    '''
    This function will get all the pawn moves 
    '''

    def get_pawn_moves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.Pins) - 1, -1, -1):
            if self.Pins[i][0] == r and self.Pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.Pins[i][2], self.Pins[i][3])
                self.Pins.remove(self.Pins[i])
                break

        if self.White_To_Move:  # White pawn moves
            if self.Board[r - 1][c] == '--':  # one square pawn advance
                if not piece_pinned or pin_direction == (-1, 0):
                    moves.append(Move((r, c), (r - 1, c), self.Board))
                    if r == 6 and self.Board[r - 2][c] == '--':  # 2 square pawn advance
                        moves.append(Move((r, c), (r - 2, c), self.Board))

            if c - 1 >= 0:  # Captures to the left
                if self.Board[r - 1][c - 1][0] == 'b':  # Capturing an enemy piece
                    if not piece_pinned or pin_direction == (-1, -1):
                        moves.append(Move((r, c), (r - 1, c - 1), self.Board))
                if (r - 1, c - 1) == self.enpassant_move:  # en passant
                    if not piece_pinned or pin_direction == (-1, -1):
                        moves.append(Move((r, c), (r - 1, c - 1), self.Board, is_enpassant_move=True))

            if c + 1 <= 7:  # Captures to right
                if self.Board[r - 1][c + 1][0] == 'b':  # Capturing an enemy piece
                    if not piece_pinned or pin_direction == (-1, 1):
                        moves.append(Move((r, c), (r - 1, c + 1), self.Board))
                if (r - 1, c + 1) == self.enpassant_move:  # en passant
                    if not piece_pinned or pin_direction == (-1, 1):
                        moves.append(Move((r, c), (r - 1, c + 1), self.Board, is_enpassant_move=True))

        else:  # Black pawn moves
            if self.Board[r + 1][c] == '--':  # one square pawn advance
                if not piece_pinned or pin_direction == (1, 0):
                    moves.append(Move((r, c), (r + 1, c), self.Board))
                    if r == 1 and self.Board[r + 2][c] == '--':  # 2 square pawn advance
                        moves.append(Move((r, c), (r + 2, c), self.Board))

            if c + 1 <= 7:  # Captures to right
                if self.Board[r + 1][c + 1][0] == 'w':  # Capturing an enemy piece
                    if not piece_pinned or pin_direction == (1, 1):
                        moves.append(Move((r, c), (r + 1, c + 1), self.Board))
                if (r + 1, c + 1) == self.enpassant_move:  # en passant
                    if not piece_pinned or pin_direction == (1, 1):
                        moves.append(Move((r, c), (r + 1, c + 1), self.Board, is_enpassant_move=True))

            if c - 1 >= 0:  # Captures to Left
                if self.Board[r + 1][c - 1][0] == 'w':  # Capturing an enemy piece
                    if not piece_pinned or pin_direction == (1, -1):
                        moves.append(Move((r, c), (r + 1, c - 1), self.Board))
                if (r + 1, c - 1) == self.enpassant_move:  # en passant
                    if not piece_pinned or pin_direction == (1, -1):
                        moves.append(Move((r, c), (r + 1, c - 1), self.Board, is_enpassant_move=True))

    def get_rook_moves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.Pins) - 1, -1, -1):
            if self.Pins[i][0] == r and self.Pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.Pins[i][2], self.Pins[i][3])
                if self.Board[r][c][1] == 'Q':
                    self.Pins.remove(self.Pins[i])
                break

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemy_color = 'b' if self.White_To_Move else 'w'
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_column = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_column < 8:
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        end_piece = self.Board[end_row][end_column]
                        if end_piece == '--':
                            moves.append(Move((r, c), (end_row, end_column), self.Board))
                        elif end_piece[0] == enemy_color:
                            moves.append(Move((r, c), (end_row, end_column), self.Board))
                            break
                        else:  # if friendly piece was encountered
                            break
                else:  # out of the board case
                    break

    def get_bishop_moves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.Pins) - 1, -1, -1):
            if self.Pins[i][0] == r and self.Pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.Pins[i][2], self.Pins[i][3])
                if self.Board[r][c][1] == 'Q':
                    self.Pins.remove(self.Pins[i])
                break
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemy_color = 'b' if self.White_To_Move else 'w'
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_column = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_column < 8:
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        end_place = self.Board[end_row][end_column]
                        if end_place == '--':
                            moves.append(Move((r, c), (end_row, end_column), self.Board))
                        elif end_place[0] == enemy_color:
                            moves.append(Move((r, c), (end_row, end_column), self.Board))
                            break
                        else:  # if friendly piece was encountered
                            break
                else:  # out of the board case
                    break

    def get_knight_moves(self, r, c, moves):
        directions = ((-1, -2), (-2, -1), (-2, 1), (-1, 2), (1, -2), (2, -1), (2, 1), (1, 2))
        enemy_color = 'b' if self.White_To_Move else 'w'
        for d in directions:
            end_row = r + d[0]
            end_column = c + d[1]
            if 0 <= end_row < 8 and 0 <= end_column < 8:
                enemy_piece = self.Board[end_row][end_column]
                if self.Board[end_row][end_column] == '--':
                    moves.append(Move((r, c), (end_row, end_column), self.Board))
                elif enemy_piece[0] == enemy_color:
                    moves.append(Move((r, c), (end_row, end_column), self.Board))

    def get_queen_moves(self, r, c, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.Pins) - 1, -1, -1):
            if self.Pins[i][0] == r and self.Pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.Pins[i][2], self.Pins[i][3])
                if self.Board[r][c][1] == 'Q':
                    self.Pins.remove(self.Pins[i])
                break
        direction = ((-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (0, -1), (1, 0), (0, 1))
        enemy_color = 'b' if self.White_To_Move else 'w'
        for d in direction:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_column = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_column < 8:
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        end_place = self.Board[end_row][end_column]
                        if end_place == '--':
                            moves.append(Move((r, c), (end_row, end_column), self.Board))
                        elif end_place[0] == enemy_color:
                            moves.append(Move((r, c), (end_row, end_column), self.Board))
                            break
                        else:  # if friendly piece was encountered
                            break
                else:  # out of the board case
                    break

    def get_king_moves(self, r, c, moves):
        king_direction = ((-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (0, -1), (1, 0), (0, 1))
        enemy_color = 'b' if self.White_To_Move else 'w'
        for i in range(8):
            end_row = r + king_direction[i][0]
            end_column = c + king_direction[i][1]
            if 0 <= end_row < 8 and 0 <= end_column < 8:
                end_place = self.Board[end_row][end_column]
                if end_place == '--':
                    moves.append(Move((r, c), (end_row, end_column), self.Board))
                elif end_place[0] == enemy_color:
                    moves.append(Move((r, c), (end_row, end_column), self.Board))

    def find_kings(self):
        wk_location = None
        bk_location = None

        for row in range(len(self.Board)):
            for col in range(len(self.Board[row])):
                if self.Board[row][col] == "wK":
                    wk_location = (row, col)
                elif self.Board[row][col] == "bK":
                    bk_location = (row, col)

        if self.White_To_Move:
            return wk_location
        else:
            return bk_location


class Move:
    # Maps keys to vals
    Ranks_To_Rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                     "5": 3, "6": 2, "7": 1, "8": 0}
    Rows_To_Ranks = {v: k for k, v in Ranks_To_Rows.items()}
    Files_To_Col = {"a": 7, "b": 6, "c": 5, "d": 4,
                    "e": 3, "f": 2, "g": 1, "h": 0}
    Col_To_Files = {v: k for k, v in Files_To_Col.items()}

    def __init__(self, start_sq, end_sq, board, is_enpassant_move=False):
        self.startRow = start_sq[0]
        self.startColumn = start_sq[1]
        self.endRow = end_sq[0]
        self.endColumn = end_sq[1]
        self.pieceMoved = board[self.startRow][self.startColumn]
        self.pieceCaptured = board[self.endRow][self.endColumn]
        self.promotion_choice = 'Q'
        # Pawn promotion
        self.is_pawn_promotion = False
        if (self.pieceMoved == 'wP' and self.endRow == 0) or (self.pieceMoved == 'bP' and self.endRow == 7):
            self.is_pawn_promotion = True
        # en-passant
        self.enpassant_valid = is_enpassant_move

        self.moveID = self.startRow * 1000 + self.startColumn * 100 + self.endRow * 10 + self.endColumn
        # print(self.moveID)

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def get_chess_notation(self):
        return self.get_rank_files(self.startRow, self.startColumn) + self.get_rank_files(self.endRow, self.endColumn)

    def get_rank_files(self, r, c):
        return self.Col_To_Files[c] + self.Rows_To_Ranks[r]
