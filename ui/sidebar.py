# ui/sidebar.py
# 结果侧边栏组件

import pygame
from typing import Optional, List
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


class ResultSidebar:
    """结果显示侧边栏"""

    def __init__(self, x: int, y: int, width: int, height: int, font: pygame.font.Font):
        """
        初始化侧边栏

        Args:
            x, y: 左上角位置
            width, height: 尺寸
            font: 字体
        """
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

    def set_plate(self, plate: LiurenPlate, lessons: List[Lesson],
                  passes: List[Pass], lesson_type: str):
        """
        设置要显示的盘局

        Args:
            plate: LiurenPlate对象
            lessons: 四课列表
            passes: 三传列表
            lesson_type: 课体名称
        """
        self.plate = plate
        self.lessons = lessons
        self.passes = passes
        self.lesson_type = lesson_type
        self.scroll_offset = 0

    def clear(self):
        """清除显示内容"""
        self.plate = None
        self.lessons = []
        self.passes = []
        self.lesson_type = ""
        self.scroll_offset = 0

    def handle_event(self, event: pygame.event.Event) -> bool:
        """处理事件（主要是滚动）"""
        if event.type == pygame.MOUSEWHEEL:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.scroll_offset -= event.y * 20
                # 限制滚动范围
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

        self.content_height = y - self.rect.y + self.scroll_offset

    def _draw_empty(self, screen: pygame.Surface):
        """绘制空状态"""
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
        """绘制分区标题"""
        if y > clip_rect.bottom or y + 25 < clip_rect.top:
            return y + 30

        text_surf = self.font.render(title, True, COLOR_TITLE)
        screen.blit(text_surf, (self.rect.x + 15, y))

        # 分隔线
        line_y = y + 22
        pygame.draw.line(screen, COLOR_BORDER,
                        (self.rect.x + 15, line_y),
                        (self.rect.x + self.rect.width - 15, line_y), 1)

        return y + 30

    def _draw_basic_info(self, screen: pygame.Surface, y: int,
                        clip_rect: pygame.Rect) -> int:
        """绘制基本信息"""
        y = self._draw_section_title(screen, "【盘局信息】", y, clip_rect)

        guiren_info = f"贵  人：{self.plate.guiren_branch}宫" if self.plate.guiren_branch else ""
        info_lines = [
            f"日干支：{self.plate.day_stem}{self.plate.day_branch}",
            f"时  支：{self.plate.hour_branch}",
            f"月  将：{self.plate.moon_general}（{self.plate.moon_general_name}）",
            guiren_info,
            f"课  体：{self.lesson_type}"
        ]
        info_lines = [line for line in info_lines if line]  # 过滤空行

        for line in info_lines:
            if clip_rect.top <= y <= clip_rect.bottom - 20:
                text_surf = self.small_font.render(line, True, COLOR_TEXT)
                screen.blit(text_surf, (self.rect.x + 20, y))
            y += 22

        return y + 10

    def _draw_four_lessons(self, screen: pygame.Surface, y: int,
                          clip_rect: pygame.Rect) -> int:
        """绘制四课"""
        y = self._draw_section_title(screen, "【四课】", y, clip_rect)

        if len(self.lessons) < 4:
            return y + 10

        # 表头
        if clip_rect.top <= y <= clip_rect.bottom - 20:
            header = "      一课  二课  三课  四课"
            header_surf = self.small_font.render(header, True, COLOR_DIM)
            screen.blit(header_surf, (self.rect.x + 15, y))
        y += 22

        # 天将
        if clip_rect.top <= y <= clip_rect.bottom - 20:
            generals = [self.lessons[i].general[:2] if self.lessons[i].general else "  " for i in range(4)]
            general_row = f"将：  {generals[0]}  {generals[1]}  {generals[2]}  {generals[3]}"
            general_surf = self.small_font.render(general_row, True, COLOR_PASS)
            screen.blit(general_surf, (self.rect.x + 15, y))
        y += 22

        # 天盘（上神）
        if clip_rect.top <= y <= clip_rect.bottom - 20:
            heaven_row = f"天：  {self.lessons[0].heaven}    {self.lessons[1].heaven}    {self.lessons[2].heaven}    {self.lessons[3].heaven}"
            heaven_surf = self.small_font.render(heaven_row, True, COLOR_ACCENT)
            screen.blit(heaven_surf, (self.rect.x + 15, y))
        y += 22

        # 地盘
        if clip_rect.top <= y <= clip_rect.bottom - 20:
            earth_row = f"地：  {self.lessons[0].earth}    {self.lessons[1].earth}    {self.lessons[2].earth}    {self.lessons[3].earth}"
            earth_surf = self.small_font.render(earth_row, True, COLOR_TEXT)
            screen.blit(earth_surf, (self.rect.x + 15, y))
        y += 22

        return y + 10

    def _draw_three_passes(self, screen: pygame.Surface, y: int,
                          clip_rect: pygame.Rect) -> int:
        """绘制三传"""
        y = self._draw_section_title(screen, "【三传】", y, clip_rect)

        if len(self.passes) < 3:
            return y + 10

        # 三传显示（地支）
        if clip_rect.top <= y <= clip_rect.bottom - 20:
            passes_str = f"初传：{self.passes[0].branch}  →  中传：{self.passes[1].branch}  →  末传：{self.passes[2].branch}"
            passes_surf = self.small_font.render(passes_str, True, COLOR_PASS)
            screen.blit(passes_surf, (self.rect.x + 15, y))
        y += 22

        # 三传天将
        if clip_rect.top <= y <= clip_rect.bottom - 20:
            generals = [p.general if p.general else "无" for p in self.passes]
            generals_str = f"天将：{generals[0]}  →  {generals[1]}  →  {generals[2]}"
            generals_surf = self.small_font.render(generals_str, True, COLOR_ACCENT)
            screen.blit(generals_surf, (self.rect.x + 15, y))
        y += 25

        return y + 10

    def _draw_derivation_log(self, screen: pygame.Surface, y: int,
                            clip_rect: pygame.Rect) -> int:
        """绘制推导过程"""
        if not self.plate.derivation_log:
            return y

        y = self._draw_section_title(screen, "【推导过程】", y, clip_rect)

        for line in self.plate.derivation_log:
            if clip_rect.top <= y <= clip_rect.bottom - 20:
                line_surf = self.small_font.render(line, True, COLOR_DIM)
                screen.blit(line_surf, (self.rect.x + 15, y))
            y += 20

        return y + 10
