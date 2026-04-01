"""
ai_battle_menu.py — AI vs AI setup.
Mỗi bên chọn algo riêng → difficulty list tự động đổi:
  - Minimax  → 3 cấp: Easy / Medium / Hard  (depth 1/2/3)
  - AlphaBeta → 5 cấp: Beginner/Easy/Medium/Hard/Master
"""
import pygame
from ui.button import Button
from core.constants import (
    AI_MINIMAX, AI_ALPHABETA,
    DIFFICULTY_LEVELS, DIFFICULTY_LEVELS_MINIMAX,
    SCREEN_WIDTH, SCREEN_HEIGHT,
    BUTTON_BG, BUTTON_BG_HOVER, BUTTON_BG_2, BUTTON_BG_2_HOV,
    BUTTON_BG_3, BUTTON_BG_3_HOV, BUTTON_BG_4, BUTTON_BG_4_HOV,
    BUTTON_TEXT_COLOR, TEXT_DIM,
)

# Danh sách cấp độ theo algo
_AB_LEVELS = list(DIFFICULTY_LEVELS.keys())          # 5 cấp
_MM_LEVELS = ["Easy", "Medium", "Hard"]              # 3 cấp Minimax

def _levels(algo):
    return _MM_LEVELS if algo == AI_MINIMAX else _AB_LEVELS

def _get_depth(algo, diff_name):
    if algo == AI_MINIMAX:
        return DIFFICULTY_LEVELS_MINIMAX.get(diff_name, {"depth": 2})["depth"]
    return DIFFICULTY_LEVELS[diff_name]


class AIBattleMenu:
    def __init__(self):
        self.title_font  = pygame.font.SysFont("segoeui,arial", 38, bold=True)
        self.button_font = pygame.font.SysFont("segoeui,arial", 18, bold=True)
        self.label_font  = pygame.font.SysFont("segoeui,arial", 15)
        self.sub_font    = pygame.font.SysFont("segoeui,arial", 17)

        self.red_algo   = AI_ALPHABETA
        self.black_algo = AI_ALPHABETA

        # Index trong danh sách tương ứng algo hiện tại
        self.red_diff_index   = 2
        self.black_diff_index = 2

        cx = SCREEN_WIDTH // 2
        lx = cx - 250
        rx = cx + 30
        cw = 210

        self.red_algo_btn  = Button(lx, 240, cw, 44, "", BUTTON_BG,   BUTTON_TEXT_COLOR, BUTTON_BG_HOVER)
        self.red_diff_btn  = Button(lx, 295, cw, 44, "", BUTTON_BG_3, BUTTON_TEXT_COLOR, BUTTON_BG_3_HOV)
        self.blk_algo_btn  = Button(rx, 240, cw, 44, "", BUTTON_BG,   BUTTON_TEXT_COLOR, BUTTON_BG_HOVER)
        self.blk_diff_btn  = Button(rx, 295, cw, 44, "", BUTTON_BG_3, BUTTON_TEXT_COLOR, BUTTON_BG_3_HOV)
        self.start_btn     = Button(cx-130, 530, 260, 52, "Start Match",
                                     BUTTON_BG_2, BUTTON_TEXT_COLOR, BUTTON_BG_2_HOV)
        self.back_btn      = Button(cx-130, 598, 260, 44, "Back to Menu",
                                     BUTTON_BG_4, BUTTON_TEXT_COLOR, BUTTON_BG_4_HOV)

    # ── helpers ───────────────────────────────────────────────────────────────

    def _toggle(self, algo):
        return AI_MINIMAX if algo == AI_ALPHABETA else AI_ALPHABETA

    def _red_diff_name(self):
        lvls = _levels(self.red_algo)
        idx  = min(self.red_diff_index, len(lvls)-1)
        return lvls[idx]

    def _blk_diff_name(self):
        lvls = _levels(self.black_algo)
        idx  = min(self.black_diff_index, len(lvls)-1)
        return lvls[idx]

    # ── draw ──────────────────────────────────────────────────────────────────

    def draw(self, screen):
        # Background gradient
        sw, sh = screen.get_size()
        for y in range(sh):
            t = y/sh
            pygame.draw.line(screen,(int(22+12*t),int(12+6*t),int(4+2*t)),(0,y),(sw,y))

        pygame.draw.rect(screen,(140,85,25),(0,0,6,sh))
        pygame.draw.rect(screen,(140,85,25),(sw-6,0,6,sh))

        cx = sw // 2
        title = self.title_font.render("AI  vs  AI  Setup", True, (240,205,120))
        screen.blit(title, title.get_rect(center=(cx, 90)))
        pygame.draw.line(screen,(160,110,35),(cx-200,125),(cx+200,125),2)

        lx, rx, cw = cx-250, cx+30, 210

        # Column headers
        rl = self.sub_font.render("RED Side", True, (230,90,90))
        bl = self.sub_font.render("BLACK Side", True, (120,175,240))
        screen.blit(rl, rl.get_rect(centerx=lx+cw//2, y=195))
        screen.blit(bl, bl.get_rect(centerx=rx+cw//2, y=195))
        pygame.draw.line(screen,(100,70,30),(cx,185),(cx,390),1)

        mp = pygame.mouse.get_pos()

        # Labels cho diff: hiển thị rõ số cấp
        r_name = self._red_diff_name()
        b_name = self._blk_diff_name()

        r_algo_lbl  = "Minimax" if self.red_algo   == AI_MINIMAX else "Alpha-Beta"
        b_algo_lbl  = "Minimax" if self.black_algo == AI_MINIMAX else "Alpha-Beta"
        r_diff_info = f"depth={_get_depth(self.red_algo, r_name)}"
        b_diff_info = f"depth={_get_depth(self.black_algo, b_name)}"

        self.red_algo_btn.text = f"Algo: {r_algo_lbl}"
        self.red_diff_btn.text = f"{r_name}  ({r_diff_info})"
        self.blk_algo_btn.text = f"Algo: {b_algo_lbl}"
        self.blk_diff_btn.text = f"{b_name}  ({b_diff_info})"

        for btn in (self.red_algo_btn, self.red_diff_btn,
                    self.blk_algo_btn, self.blk_diff_btn,
                    self.start_btn, self.back_btn):
            btn.update_hover(mp)
            btn.draw(screen, self.button_font)

        # Hiển thị danh sách cấp độ nhỏ bên dưới nút diff
        for algo, diff_idx, col_x, col_w in [
            (self.red_algo,   self.red_diff_index,   lx, cw),
            (self.black_algo, self.black_diff_index, rx, cw),
        ]:
            lvls = _levels(algo)
            y_hint = 348
            for i, name in enumerate(lvls):
                is_sel = (i == min(diff_idx, len(lvls)-1))
                color  = (230,200,120) if is_sel else (130,110,70)
                d = _get_depth(algo, name)
                hint = self.label_font.render(
                    f"{'>' if is_sel else ' '} {name}  (depth {d})", True, color)
                screen.blit(hint, (col_x + 8, y_hint + i*18))

        # Summary
        rd = _get_depth(self.red_algo,   r_name)
        bd = _get_depth(self.black_algo, b_name)
        info = self.label_font.render(
            f"Red: {r_algo_lbl} depth {rd}   vs   Black: {b_algo_lbl} depth {bd}",
            True, (155,130,80))
        screen.blit(info, info.get_rect(center=(cx, 588)))

        footer = self.label_font.render("Made by Vu Nam Sang & Thai Doan Thinh",
                                         True, (90,72,42))
        screen.blit(footer, footer.get_rect(center=(cx, sh-22)))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            # Toggle algo — clamp difficulty index về phạm vi mới
            if self.red_algo_btn.is_clicked(pos):
                self.red_algo = self._toggle(self.red_algo)
                self.red_diff_index = min(self.red_diff_index,
                                          len(_levels(self.red_algo))-1)
                return None
            if self.blk_algo_btn.is_clicked(pos):
                self.black_algo = self._toggle(self.black_algo)
                self.black_diff_index = min(self.black_diff_index,
                                             len(_levels(self.black_algo))-1)
                return None

            # Cycle difficulty trong danh sách của algo hiện tại
            if self.red_diff_btn.is_clicked(pos):
                self.red_diff_index = (self.red_diff_index + 1) % len(_levels(self.red_algo))
                return None
            if self.blk_diff_btn.is_clicked(pos):
                self.black_diff_index = (self.black_diff_index + 1) % len(_levels(self.black_algo))
                return None

            if self.start_btn.is_clicked(pos):
                r_name = self._red_diff_name()
                b_name = self._blk_diff_name()
                return (
                    "start",
                    self.red_algo,   _get_depth(self.red_algo,   r_name),
                    self.black_algo, _get_depth(self.black_algo, b_name),
                )
            if self.back_btn.is_clicked(pos):
                return ("back",)
        return None

    # Expose diff_names cho main.py (set_difficulty)
    @property
    def diff_names(self):
        return _AB_LEVELS

    @property
    def red_diff_name(self):
        return self._red_diff_name()

    @property
    def black_diff_name(self):
        return self._blk_diff_name()