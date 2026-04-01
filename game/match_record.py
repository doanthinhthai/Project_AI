"""
match_record.py — Cấu trúc dữ liệu lưu lịch sử ván đấu.

Hierarchy:
    MatchRecord
      └── MoveEntry[]
            ├── move          : Move object
            ├── notation      : str  "Pháo 2 bình 5"
            ├── color         : int  RED / BLACK
            ├── is_ai         : bool
            ├── eval_score    : int | None   (điểm AI đánh giá)
            ├── depth_searched: int | None
            ├── think_time    : float | None (giây)
            └── candidates    : CandidateMove[]  (top-N nước AI cân nhắc)
                      ├── move   : Move
                      ├── score  : int
                      └── notation: str
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
import time

from core.constants import (
    RED, BLACK,
    KING, ADVISOR, ELEPHANT, ROOK, KNIGHT, CANNON, PAWN,
)

# ── Tên tiếng Việt cho loại quân ──────────────────────────────────────────────
_VIET = {
    KING: "Tướng", ADVISOR: "Sĩ", ELEPHANT: "Tượng",
    ROOK: "Xe",    KNIGHT:  "Mã", CANNON:   "Pháo", PAWN: "Tốt",
}

# Cột → số (cờ tướng dùng 1-9 từ phải sang trái cho mỗi bên)
def _col_label(col: int, color: int) -> str:
    if color == RED:
        return str(9 - col)       # đỏ nhìn từ dưới lên
    return str(col + 1)           # đen nhìn từ trên xuống


def build_notation(move, color: int) -> str:
    """
    Tạo ký hiệu cờ tướng đơn giản:
      "Pháo 2 bình 5"   (di ngang)
      "Mã 8 tấn 7"      (đi lên)
      "Xe 1 thoái 2"    (lui về)
    """
    if move is None or move.piece_moved is None:
        return "?"

    piece   = move.piece_moved
    pname   = _VIET.get(piece.piece_type, piece.piece_type)
    from_c  = _col_label(move.start_col, color)
    to_c    = _col_label(move.end_col,   color)

    dr = move.end_row - move.start_row
    if color == RED:
        dr = -dr   # đỏ đi lên → row giảm → "tấn"

    if dr > 0:
        action = "tấn"
        dest   = str(abs(dr))         # số hàng tiến
    elif dr < 0:
        action = "thoái"
        dest   = str(abs(dr))
    else:
        action = "bình"
        dest   = to_c                 # bình → đích là cột đến

    capture = f" (ăn {_VIET.get(move.piece_captured.piece_type,'?')})" \
              if move.is_capture() else ""
    return f"{pname} {from_c} {action} {dest}{capture}"


# ── Candidate move ─────────────────────────────────────────────────────────────
@dataclass
class CandidateMove:
    move:     object          # Move instance
    score:    int
    notation: str = ""

    def __post_init__(self):
        if not self.notation and self.move is not None:
            # notation được set từ bên ngoài (cần color)
            pass


# ── Single move entry ──────────────────────────────────────────────────────────
@dataclass
class MoveEntry:
    move_number:    int
    color:          int             # RED / BLACK
    move:           object          # Move instance
    notation:       str   = ""
    is_ai:          bool  = False
    eval_score:     Optional[int]   = None
    depth_searched: Optional[int]   = None
    think_time:     Optional[float] = None
    candidates:     List[CandidateMove] = field(default_factory=list)

    @property
    def side(self) -> str:
        return "Đỏ" if self.color == RED else "Đen"

    @property
    def think_time_str(self) -> str:
        if self.think_time is None:
            return "—"
        return f"{self.think_time:.3f}s"

    @property
    def eval_str(self) -> str:
        if self.eval_score is None:
            return "—"
        if self.eval_score >= 9_000_000:  return "Chiếu bí +"
        if self.eval_score <= -9_000_000: return "Chiếu bí -"
        return f"{'+' if self.eval_score > 0 else ''}{self.eval_score}"

    def why_chosen(self) -> str:
        """Giải thích ngắn tại sao AI chọn nước này."""
        if not self.is_ai:
            return "Nước đi của người chơi."
        if not self.candidates:
            return "Không có dữ liệu phân tích."

        lines = [f"AI chọn: {self.notation}  (điểm: {self.eval_str})"]
        if self.depth_searched:
            lines.append(f"Tìm kiếm ở độ sâu {self.depth_searched}.")
        if self.candidates:
            lines.append("Các nước khác đã cân nhắc:")
            for i, c in enumerate(self.candidates[:4], 1):
                diff = c.score - (self.eval_score or 0)
                diff_str = f"{'+' if diff >= 0 else ''}{diff}"
                lines.append(f"  {i}. {c.notation}  (điểm: {c.score},  Δ{diff_str})")
        return "\n".join(lines)


# ── Match record ───────────────────────────────────────────────────────────────
@dataclass
class MatchRecord:
    game_mode:   str = ""
    red_algo:    str = ""
    black_algo:  str = ""
    difficulty:  str = ""
    start_time:  float = field(default_factory=time.time)
    end_time:    Optional[float] = None
    result:      str = ""          # "RED_WIN" / "BLACK_WIN" / "DRAW"
    entries:     List[MoveEntry]   = field(default_factory=list)

    # ── append ────────────────────────────────────────────────────────────────

    def add_human_move(self, move, color: int):
        n = len(self.entries) + 1
        entry = MoveEntry(
            move_number=n,
            color=color,
            move=move,
            notation=build_notation(move, color),
            is_ai=False,
        )
        self.entries.append(entry)
        return entry

    def add_ai_move(self, move, color: int, ai_player,
                    candidates: List[CandidateMove] = None):
        n = len(self.entries) + 1
        engine = getattr(ai_player, "engine", None)
        entry = MoveEntry(
            move_number    = n,
            color          = color,
            move           = move,
            notation       = build_notation(move, color),
            is_ai          = True,
            eval_score     = getattr(engine, "best_score",   None) if engine else None,
            depth_searched = getattr(engine, "search_depth", None) if engine else None,
            think_time     = getattr(ai_player, "last_think_time", None),
            candidates     = candidates or [],
        )
        self.entries.append(entry)
        return entry

    def finish(self, result: str):
        self.end_time = time.time()
        self.result   = result

    # ── query ─────────────────────────────────────────────────────────────────

    @property
    def total_moves(self) -> int:
        return len(self.entries)

    @property
    def duration(self) -> str:
        if self.end_time is None:
            return "—"
        s = int(self.end_time - self.start_time)
        return f"{s//60}:{s%60:02d}"

    def get_ai_entries(self) -> List[MoveEntry]:
        return [e for e in self.entries if e.is_ai]

    def summary(self) -> str:
        r_map = {"red_win": "Đỏ thắng", "black_win": "Đen thắng",
                 "draw": "Hòa", "": "Đang chơi"}
        return (f"Kết quả: {r_map.get(self.result, self.result)} | "
                f"Tổng nước: {self.total_moves} | "
                f"Thời gian: {self.duration}")