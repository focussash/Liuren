# ui/sidebar.py
# 结果侧边栏组件

import pygame
from typing import Optional, List, Callable
from liuren.plate import LiurenPlate, Lesson, Pass

# 颜色
COLOR_SIDEBAR_BG = (25, 25, 30)
COLOR_SECTION_BG = (35, 35, 42)
COLOR_TITLE = (220, 190, 100)
COLOR_TEXT = (200, 180, 140)
COLOR_DIM = (150, 130, 100)
COLOR_ACCENT = (255, 200, 100)
COLOR_PASS = (100, 200, 255)
COLOR_BORDER = (80, 70, 55)
COLOR_CHECK = (100, 200, 120)
COLOR_BTN_BG = (50, 45, 35)
COLOR_BTN_HOVER = (80, 70, 55)


class ResultSidebar:
    """结果显示侧边栏"""

    def __init__(self, x: int, y: int, width: int, height: int, font: pygame.font.Font):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.small_font = pygame.font.SysFont(font.get_name() if hasattr(font, 'get_name') else 'simhei', 16)

        self.plate: Optional[LiurenPlate] = None
        self.lessons: List[Lesson] = []
        self.passes: List[Pass] = []
        self.lesson_type: str = ""

        # 滚动状态
        self.scroll_offset = 0
        self.content_height = 0

        # 详解按钮
        self.detail_btn_rect = pygame.Rect(0, 0, 45, 22)
        self.detail_btn_hovered = False
        self.detail_callback = None

        # LLM解盘区域
        self.llm_expanded = False
        self.persona_options = ['管辂', '贺茂忠行']
        self.persona_selected = [True, True]  # 默认全选
        self.purpose_options = ['射覆', '占卜明日运势']
        self.purpose_selected = 0
        self.interpret_callback: Optional[Callable] = None

        # LLM区域动态rect（draw中更新位置）
        self.llm_toggle_rect = pygame.Rect(0, 0, 0, 0)
        self.llm_toggle_hovered = False
        self.persona_rects: List[pygame.Rect] = []
        self.purpose_rects: List[pygame.Rect] = []
        self.interpret_btn_rect = pygame.Rect(0, 0, 0, 0)
        self.interpret_btn_hovered = False

    def set_detail_callback(self, callback):
        """设置详解按钮回调"""
        self.detail_callback = callback

    def set_interpret_callback(self, callback):
        """设置LLM解盘按钮回调"""
        self.interpret_callback = callback

    def get_selected_personas(self) -> List[str]:
        """返回勾选的人物名列表"""
        return [name for name, sel in zip(self.persona_options, self.persona_selected) if sel]

    def get_selected_purpose(self) -> str:
        """返回选中的占卜目的"""
        return self.purpose_options[self.purpose_selected]

    def set_plate(self, plate: LiurenPlate, lessons: List[Lesson],
                  passes: List[Pass], lesson_type: str):
        self.plate = plate
        self.lessons = lessons
        self.passes = passes
        self.lesson_type = lesson_type
        self.scroll_offset = 0

    def clear(self):
        self.plate = None
        self.lessons = []
        self.passes = []
        self.lesson_type = ""
        self.scroll_offset = 0

    def handle_event(self, event: pygame.event.Event) -> bool:
        """处理事件"""
        if event.type == pygame.MOUSEMOTION:
            self.detail_btn_hovered = self.detail_btn_rect.collidepoint(event.pos)
            self.llm_toggle_hovered = self.llm_toggle_rect.collidepoint(event.pos)
            self.interpret_btn_hovered = self.interpret_btn_rect.collidepoint(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.rect.collidepoint(event.pos):
                return False

            # 详解按钮
            if self.plate and self.detail_btn_rect.collidepoint(event.pos):
                if self.detail_callback:
                    self.detail_callback()
                return True

            # LLM toggle
            if self.plate and self.llm_toggle_rect.collidepoint(event.pos):
                self.llm_expanded = not self.llm_expanded
                return True

            # LLM expanded area interactions
            if self.llm_expanded and self.plate:
                # Persona checkboxes
                for i, rect in enumerate(self.persona_rects):
                    if rect.collidepoint(event.pos):
                        self.persona_selected[i] = not self.persona_selected[i]
                        # Ensure at least one selected
                        if not any(self.persona_selected):
                            self.persona_selected[i] = True
                        return True

                # Purpose radio buttons
                for i, rect in enumerate(self.purpose_rects):
                    if rect.collidepoint(event.pos):
                        self.purpose_selected = i
                        return True

                # Interpret button
                if self.interpret_btn_rect.collidepoint(event.pos):
                    if self.interpret_callback:
                        self.interpret_callback()
                    return True

        if event.type == pygame.MOUSEWHEEL:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.scroll_offset -= event.y * 20
                max_scroll = max(0, self.content_height - self.rect.height + 40)
                self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))
                return True

        return False

    def draw(self, screen: pygame.Surface):
        """绘制侧边栏"""
        # 背景
        pygame.draw.rect(screen, COLOR_SIDEBAR_BG, self.rect, border_radius=10)
        pygame.draw.rect(screen, COLOR_BORDER, self.rect, width=1, border_radius=10)

        if not self.plate:
            self._draw_empty(screen)
            return

        # 创建裁剪区域
        clip_rect = pygame.Rect(self.rect.x + 5, self.rect.y + 5,
                                self.rect.width - 10, self.rect.height - 10)

        # 计算内容起始位置
        y = self.rect.y + 15 - self.scroll_offset

        # 绘制各部分
        y = self._draw_basic_info(screen, y, clip_rect)
        y = self._draw_four_lessons(screen, y, clip_rect)
        y = self._draw_three_passes(screen, y, clip_rect)
        y = self._draw_derivation_log(screen, y, clip_rect)
        y = self._draw_llm_section(screen, y, clip_rect)

        self.content_height = y - self.rect.y + self.scroll_offset

    def _draw_empty(self, screen: pygame.Surface):
        text = "请选择日干支和时支"
        text_surf = self.font.render(text, True, COLOR_DIM)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

        hint = "点击「排盘」开始"
        hint_surf = self.small_font.render(hint, True, COLOR_DIM)
        hint_rect = hint_surf.get_rect(center=(self.rect.centerx, self.rect.centery + 30))
        screen.blit(hint_surf, hint_rect)

    def _draw_section_title(self, screen: pygame.Surface, title: str,
                           y: int, clip_rect: pygame.Rect) -> int:
        if y > clip_rect.bottom or y + 25 < clip_rect.top:
            return y + 30

        text_surf = self.font.render(title, True, COLOR_TITLE)
        screen.blit(text_surf, (self.rect.x + 15, y))

        line_y = y + 22
        pygame.draw.line(screen, COLOR_BORDER,
                        (self.rect.x + 15, line_y),
                        (self.rect.x + self.rect.width - 15, line_y), 1)

        return y + 30

    def _draw_basic_info(self, screen: pygame.Surface, y: int,
                        clip_rect: pygame.Rect) -> int:
        y = self._draw_section_title(screen, "【盘局信息】", y, clip_rect)

        guiren_info = f"贵  人：{self.plate.guiren_branch}宫" if self.plate.guiren_branch else ""
        info_lines = [
            f"日干支：{self.plate.day_stem}{self.plate.day_branch}",
            f"时  支：{self.plate.hour_branch}",
            f"月  将：{self.plate.moon_general}（{self.plate.moon_general_name}）",
            guiren_info,
            f"课  体：{self.lesson_type}"
        ]
        info_lines = [line for line in info_lines if line]

        for line in info_lines:
            if clip_rect.top <= y <= clip_rect.bottom - 20:
                text_surf = self.small_font.render(line, True, COLOR_TEXT)
                screen.blit(text_surf, (self.rect.x + 20, y))
            y += 22

        return y + 10

    def _draw_four_lessons(self, screen: pygame.Surface, y: int,
                          clip_rect: pygame.Rect) -> int:
        y = self._draw_section_title(screen, "【四课】", y, clip_rect)

        if len(self.lessons) < 4:
            return y + 10

        if clip_rect.top <= y <= clip_rect.bottom - 20:
            header = "      一课  二课  三课  四课"
            header_surf = self.small_font.render(header, True, COLOR_DIM)
            screen.blit(header_surf, (self.rect.x + 15, y))
        y += 22

        if clip_rect.top <= y <= clip_rect.bottom - 20:
            generals = [self.lessons[i].general[:2] if self.lessons[i].general else "  " for i in range(4)]
            general_row = f"将：  {generals[0]}  {generals[1]}  {generals[2]}  {generals[3]}"
            general_surf = self.small_font.render(general_row, True, COLOR_PASS)
            screen.blit(general_surf, (self.rect.x + 15, y))
        y += 22

        if clip_rect.top <= y <= clip_rect.bottom - 20:
            heaven_row = f"天：  {self.lessons[0].heaven}    {self.lessons[1].heaven}    {self.lessons[2].heaven}    {self.lessons[3].heaven}"
            heaven_surf = self.small_font.render(heaven_row, True, COLOR_ACCENT)
            screen.blit(heaven_surf, (self.rect.x + 15, y))
        y += 22

        if clip_rect.top <= y <= clip_rect.bottom - 20:
            earth_row = f"地：  {self.lessons[0].earth}    {self.lessons[1].earth}    {self.lessons[2].earth}    {self.lessons[3].earth}"
            earth_surf = self.small_font.render(earth_row, True, COLOR_TEXT)
            screen.blit(earth_surf, (self.rect.x + 15, y))
        y += 22

        return y + 10

    def _draw_three_passes(self, screen: pygame.Surface, y: int,
                          clip_rect: pygame.Rect) -> int:
        y = self._draw_section_title(screen, "【三传】", y, clip_rect)

        if len(self.passes) < 3:
            return y + 10

        if clip_rect.top <= y <= clip_rect.bottom - 20:
            passes_str = f"初传：{self.passes[0].branch}  →  中传：{self.passes[1].branch}  →  末传：{self.passes[2].branch}"
            passes_surf = self.small_font.render(passes_str, True, COLOR_PASS)
            screen.blit(passes_surf, (self.rect.x + 15, y))
        y += 22

        if clip_rect.top <= y <= clip_rect.bottom - 20:
            generals = [p.general if p.general else "无" for p in self.passes]
            generals_str = f"天将：{generals[0]}  →  {generals[1]}  →  {generals[2]}"
            generals_surf = self.small_font.render(generals_str, True, COLOR_ACCENT)
            screen.blit(generals_surf, (self.rect.x + 15, y))
        y += 25

        return y + 10

    def _draw_derivation_log(self, screen: pygame.Surface, y: int,
                            clip_rect: pygame.Rect) -> int:
        if not self.plate.derivation_log:
            return y

        y = self._draw_section_title(screen, "【推导过程】", y, clip_rect)

        # 详解按钮（在推导标题右侧）
        btn_x = self.rect.x + self.rect.width - 60
        btn_y = y - 28
        self.detail_btn_rect = pygame.Rect(btn_x, btn_y, 45, 22)

        if clip_rect.top <= btn_y <= clip_rect.bottom:
            btn_color = (80, 70, 55) if self.detail_btn_hovered else (60, 50, 40)
            pygame.draw.rect(screen, btn_color, self.detail_btn_rect, border_radius=4)
            pygame.draw.rect(screen, COLOR_BORDER, self.detail_btn_rect, width=1, border_radius=4)
            btn_text = self.small_font.render("详解", True, COLOR_ACCENT)
            btn_text_rect = btn_text.get_rect(center=self.detail_btn_rect.center)
            screen.blit(btn_text, btn_text_rect)

        for line in self.plate.derivation_log:
            if clip_rect.top <= y <= clip_rect.bottom - 20:
                line_surf = self.small_font.render(line, True, COLOR_DIM)
                screen.blit(line_surf, (self.rect.x + 15, y))
            y += 20

        return y + 10

    def _draw_llm_section(self, screen: pygame.Surface, y: int,
                         clip_rect: pygame.Rect) -> int:
        """绘制自动解盘区域"""
        if not self.plate:
            return y

        left = self.rect.x + 15
        right = self.rect.x + self.rect.width - 15
        usable_width = right - left

        # ── Toggle button ──
        arrow = "▼" if self.llm_expanded else "▶"
        toggle_text = f"自动解盘 {arrow}"
        toggle_w = 110
        toggle_h = 24
        self.llm_toggle_rect = pygame.Rect(left, y, toggle_w, toggle_h)

        if clip_rect.top <= y <= clip_rect.bottom:
            bg = COLOR_BTN_HOVER if self.llm_toggle_hovered else COLOR_BTN_BG
            pygame.draw.rect(screen, bg, self.llm_toggle_rect, border_radius=4)
            pygame.draw.rect(screen, COLOR_BORDER, self.llm_toggle_rect, width=1, border_radius=4)
            text_surf = self.small_font.render(toggle_text, True, COLOR_ACCENT)
            text_rect = text_surf.get_rect(center=self.llm_toggle_rect.center)
            screen.blit(text_surf, text_rect)

        y += toggle_h + 8

        if not self.llm_expanded:
            return y

        # ── Persona checkboxes ──
        if clip_rect.top <= y <= clip_rect.bottom:
            label_surf = self.small_font.render("解盘人物：", True, COLOR_TEXT)
            screen.blit(label_surf, (left, y))
        y += 22

        self.persona_rects = []
        cx = left + 10
        for i, name in enumerate(self.persona_options):
            check_size = 16
            check_rect = pygame.Rect(cx, y + 1, check_size, check_size)
            self.persona_rects.append(pygame.Rect(cx, y, check_size + 50, 20))

            if clip_rect.top <= y <= clip_rect.bottom:
                # Checkbox border
                pygame.draw.rect(screen, COLOR_BORDER, check_rect, width=1, border_radius=2)
                if self.persona_selected[i]:
                    # Checkmark
                    inner = check_rect.inflate(-4, -4)
                    pygame.draw.rect(screen, COLOR_CHECK, inner, border_radius=2)

                # Label
                name_surf = self.small_font.render(name, True, COLOR_TEXT)
                screen.blit(name_surf, (cx + check_size + 5, y))

            cx += check_size + 5 + self.small_font.size(name)[0] + 20

        y += 26

        # ── Purpose radio buttons ──
        if clip_rect.top <= y <= clip_rect.bottom:
            label_surf = self.small_font.render("占卜目的：", True, COLOR_TEXT)
            screen.blit(label_surf, (left, y))
        y += 22

        self.purpose_rects = []
        cx = left + 10
        for i, name in enumerate(self.purpose_options):
            radio_r = 7
            radio_center = (cx + radio_r, y + radio_r + 1)
            name_w = self.small_font.size(name)[0]
            self.purpose_rects.append(pygame.Rect(cx, y, radio_r * 2 + 5 + name_w, 18))

            if clip_rect.top <= y <= clip_rect.bottom:
                # Radio outer circle
                pygame.draw.circle(screen, COLOR_BORDER, radio_center, radio_r, width=1)
                if self.purpose_selected == i:
                    pygame.draw.circle(screen, COLOR_CHECK, radio_center, radio_r - 3)

                # Label
                name_surf = self.small_font.render(name, True, COLOR_TEXT)
                screen.blit(name_surf, (cx + radio_r * 2 + 5, y))

            cx += radio_r * 2 + 5 + name_w + 20

        y += 26

        # ── Interpret button ──
        btn_h = 28
        self.interpret_btn_rect = pygame.Rect(left, y, usable_width, btn_h)

        if clip_rect.top <= y <= clip_rect.bottom:
            bg = COLOR_BTN_HOVER if self.interpret_btn_hovered else COLOR_BTN_BG
            pygame.draw.rect(screen, bg, self.interpret_btn_rect, border_radius=5)
            pygame.draw.rect(screen, COLOR_BORDER, self.interpret_btn_rect, width=1, border_radius=5)
            btn_text = self.font.render("解  盘", True, COLOR_ACCENT)
            btn_text_rect = btn_text.get_rect(center=self.interpret_btn_rect.center)
            screen.blit(btn_text, btn_text_rect)

        y += btn_h + 10

        return y
