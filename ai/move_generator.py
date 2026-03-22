from core.constants import BOARD_ROWS, BOARD_COLS, EMPTY


class MoveGenerator:
    def __init__(self, board, rules, game_manager=None):
        self.board = board
        self.rules = rules
        self.game_manager = game_manager  # dùng tạm nếu cần check

    def get_all_moves(self, color):
        """
        Trả về tất cả nước đi hợp lệ (legal moves) của một bên
        """
        moves = []

        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                piece = self.board.get_piece(row, col)

                if piece == EMPTY or piece.color != color:
                    continue

                candidate_moves = self.rules.get_valid_moves(row, col)

                for move in candidate_moves:
                    self.board.make_move(move)

                    # ❗ Lọc nước đi không hợp lệ
                    if not self.is_illegal_move(color):
                        moves.append(move)

                    self.board.undo_move()

        return moves

    def is_illegal_move(self, color):
        """
        Kiểm tra nước đi có vi phạm luật không:
        - tự chiếu
        - 2 tướng đối mặt
        """
        # Nếu có game_manager thì tận dụng luôn
        if self.game_manager:
            if self.game_manager.is_in_check(color):
                return True
            if self.game_manager.kings_face_each_other():
                return True
            return False

        # Nếu không có, fallback (sau này nên chuyển hết vào rules)
        return False