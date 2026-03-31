"""
menu.py — Main menu với ảnh nền pro.png
"""
import os
import pygame
from ui.button import Button
from core.constants import *


class Menu:
    def __init__(self):
        # Dùng font hỗ trợ Unicode/tiếng Việt đầy đủ
        _vn_fonts = "segoeui,tahoma,calibri,arial"
        self.title_font  = pygame.font.SysFont(_vn_fonts, 52, bold=True)
        self.sub_font    = pygame.font.SysFont(_vn_fonts, 20)
        self.button_font = pygame.font.SysFont(_vn_fonts, 22, bold=True)
        self.kanji_font  = pygame.font.SysFont(_vn_fonts, 72, bold=True)

        self._bg_raw   = None   # ảnh gốc chưa scale
        self._bg_cache = None   # ảnh đã scale theo screen size
        self._bg_size  = (0, 0)
        self._load_bg()

        # Buttons — căn giữa, tính lại trong draw() theo screen size
        self.buttons = {
            "pvsai": Button(0, 0, 240, 54, "Player vs AI",
                             BUTTON_BG,   BUTTON_TEXT_COLOR, BUTTON_BG_HOVER),
            "aivai": Button(0, 0, 240, 54, "AI vs AI",
                             BUTTON_BG,   BUTTON_TEXT_COLOR, BUTTON_BG_HOVER),
            "pvp":   Button(0, 0, 240, 54, "Player vs Player",
                             BUTTON_BG_2, BUTTON_TEXT_COLOR, BUTTON_BG_2_HOV, icon="👥"),
            "quit":  Button(0, 0, 240, 50, "Quit",
                             BUTTON_BG_4, BUTTON_TEXT_COLOR, BUTTON_BG_4_HOV, icon="✕"),
        }

        self.difficulty_names = list(DIFFICULTY_LEVELS.keys())
        self.difficulty_index = 2  # Medium
        self.diff_button = Button(0, 0, 240, 48, "",
                                   BUTTON_BG_3, BUTTON_TEXT_COLOR, BUTTON_BG_3_HOV)

    # ── Load background ────────────────────────────────────────────────────────

    def _load_bg(self):
        # Tính đường dẫn tuyệt đối từ vị trí file menu.py
        # menu.py nằm ở ui/ → project root = ui/../
        _here        = os.path.dirname(os.path.abspath(__file__))
        _project_root = os.path.dirname(_here)   # lên 1 cấp từ ui/

        candidates = [
            os.path.join(_project_root, "assets", "images", "pro.png"),
            os.path.join(_project_root, "assets", "pro.png"),
            os.path.join(_project_root, "pro.png"),
            # fallback: chạy từ project root trực tiếp
            os.path.join("assets", "images", "pro.png"),
            "pro.png",
        ]
        for path in candidates:
            if os.path.exists(path):
                try:
                    self._bg_raw = pygame.image.load(path).convert()
                    return
                except Exception:
                    pass
        self._bg_raw = None   # fallback: gradient

    def _get_bg(self, sw, sh):
        """Trả về ảnh nền đã scale vừa màn hình (cache lại)."""
        if self._bg_raw is None:
            return None
        if self._bg_cache is None or self._bg_size != (sw, sh):
            self._bg_cache = pygame.transform.smoothscale(self._bg_raw, (sw, sh))
            self._bg_size  = (sw, sh)
        return self._bg_cache

    # ── Draw ──────────────────────────────────────────────────────────────────

    def draw(self, screen: pygame.Surface):
        sw = screen.get_width()
        sh = screen.get_height()
        cx = sw // 2
        mp = pygame.mouse.get_pos()

        # ── 1. Background ─────────────────────────────────────────────────────
        bg = self._get_bg(sw, sh)
        if bg:
            screen.blit(bg, (0, 0))
        else:
            # Fallback gradient
            for y in range(sh):
                t = y / sh
                pygame.draw.line(screen, (int(22+12*t),int(12+6*t),int(4+2*t)),
                                 (0,y),(sw,y))

        # ── 2. Dark overlay toàn màn hình (làm tối để text nổi) ───────────────
        ov = pygame.Surface((sw, sh), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 105))
        screen.blit(ov, (0, 0))

        # ── 3. Title card (glassmorphism) ─────────────────────────────────────
        card_w, card_h = 480, 175
        card_x = cx - card_w // 2
        card_y = 38

        card = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        # Glass blur feel: semi-transparent dark background
        pygame.draw.rect(card, (10, 5, 2, 148), (0,0,card_w,card_h), border_radius=20)
        # Golden border
        pygame.draw.rect(card, (210, 158, 42, 200), (0,0,card_w,card_h), 2, border_radius=20)
        # Inner highlight line (top)
        pygame.draw.line(card, (255, 215, 80, 60), (20, 4), (card_w-20, 4), 1)
        screen.blit(card, (card_x, card_y))

        # Title lớn
        kanji = self.kanji_font.render("CỜ TƯỚNG", True, (235, 185, 55))
        # Shadow
        ks = self.kanji_font.render("CỜ TƯỚNG", True, (80, 40, 5))
        screen.blit(ks, ks.get_rect(center=(cx+3, card_y+58)))
        screen.blit(kanji, kanji.get_rect(center=(cx, card_y+55)))

        # English title
        title = self.title_font.render("Chinese Chess", True, (255, 228, 160))
        ts    = self.title_font.render("Chinese Chess", True, (60, 30, 5))
        screen.blit(ts, ts.get_rect(center=(cx+2, card_y+124)))
        screen.blit(title, title.get_rect(center=(cx, card_y+122)))



        # ── 4. Divider ────────────────────────────────────────────────────────
        div_y = card_y + card_h + 16
        for dx, alpha in [(0,180),(1,80),(2,30)]:
            dl = pygame.Surface((260, 1), pygame.SRCALPHA)
            dl.fill((210,160,42,alpha))
            screen.blit(dl, (cx-130+dx, div_y+dx))

        # ── 5. Buttons (căn giữa, tính theo screen size) ──────────────────────
        btn_start_y = div_y + 20
        gap         = 62
        keys        = list(self.buttons.keys())
        for i, key in enumerate(keys):
            btn = self.buttons[key]
            btn.rect.x = cx - 120
            btn.rect.y = btn_start_y + i * gap
            btn.update_hover(mp)
            btn.draw(screen, self.button_font)

        # Difficulty button (bên dưới quit)
        self.diff_button.text = f"Difficulty: {self.difficulty_names[self.difficulty_index]}"
        self.diff_button.rect.x = cx - 120
        self.diff_button.rect.y = btn_start_y + len(keys)*gap + 8
        self.diff_button.update_hover(mp)
        self.diff_button.draw(screen, self.button_font)

        # ── 6. Footer ─────────────────────────────────────────────────────────
        footer_surf = pygame.Surface((sw, 28), pygame.SRCALPHA)
        footer_surf.fill((0,0,0,80))
        screen.blit(footer_surf, (0, sh-28))
        footer = self.sub_font.render("Made by Vu Nam Sang & Thai Doan Thinh",
                                       True, (165, 138, 85))
        screen.blit(footer, footer.get_rect(center=(cx, sh-14)))

    # ── Events ────────────────────────────────────────────────────────────────

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if self.diff_button.is_clicked(pos):
                self.difficulty_index = (self.difficulty_index+1) % len(self.difficulty_names)
                return ("difficulty_changed", self.get_selected_depth())
            for key, btn in self.buttons.items():
                if btn.is_clicked(pos):
                    return (key, self.get_selected_depth())
        return None

    def get_selected_depth(self):
        return DIFFICULTY_LEVELS[self.difficulty_names[self.difficulty_index]]

    def get_selected_difficulty_name(self):
        return self.difficulty_names[self.difficulty_index]