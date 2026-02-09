# ui/input_panel.py
# 输入面板组件

import pygame
from datetime import datetime
from config import HEAVENLY_STEMS, EARTHLY_BRANCHES, COLOR_TEXT, COLOR_DECO, COLOR_BG

# UI颜色
COLOR_PANEL_BG = (30, 30, 35)
COLOR_BUTTON = (60, 50, 40)
COLOR_BUTTON_HOVER = (80, 70, 55)
COLOR_BUTTON_TEXT = (220, 190, 100)
COLOR_DROPDOWN_BG = (40, 35, 30)
COLOR_DROPDOWN_HOVER = (60, 55, 45)
COLOR_BORDER = (100, 85, 60)


class TextInput:
    """数字文本输入框组件"""

    def __init__(self, x: int, y: int, width: int, height: int,
                 placeholder: str, font: pygame.font.Font, max_length: int = 4):
        self.rect = pygame.Rect(x, y, width, height)
        self.placeholder = placeholder
        self.font = font
        self.max_length = max_length
        self.text = ""
        self.focused = False

    def get_text(self) -> str:
        return self.text

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.focused = self.rect.collidepoint(event.pos)
            return self.focused

        if event.type == pygame.KEYDOWN and self.focused:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
                return True
            elif event.key == pygame.K_TAB or event.key == pygame.K_RETURN:
                return False  # let parent handle tab/enter
            elif event.unicode.isdigit() and len(self.text) < self.max_length:
                self.text += event.unicode
                return True

        return False

    def draw(self, screen: pygame.Surface):
        bg = (50, 45, 38) if self.focused else COLOR_DROPDOWN_BG
        pygame.draw.rect(screen, bg, self.rect, border_radius=3)
        border = COLOR_BUTTON_TEXT if self.focused else COLOR_BORDER
        pygame.draw.rect(screen, border, self.rect, width=1, border_radius=3)

        if self.text:
            surf = self.font.render(self.text, True, COLOR_BUTTON_TEXT)
        else:
            surf = self.font.render(self.placeholder, True, (100, 90, 70))
        rect = surf.get_rect(midleft=(self.rect.x + 5, self.rect.centery))
        screen.blit(surf, rect)


class Button:
    """按钮组件"""

    def __init__(self, x: int, y: int, width: int, height: int, text: str, font: pygame.font.Font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.hovered = False
        self.callback = None

    def set_callback(self, callback):
        """设置点击回调"""
        self.callback = callback

    def handle_event(self, event: pygame.event.Event) -> bool:
        """处理事件，返回是否被点击"""
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.callback:
                    self.callback()
                return True
        return False

    def draw(self, screen: pygame.Surface):
        """绘制按钮"""
        color = COLOR_BUTTON_HOVER if self.hovered else COLOR_BUTTON
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, COLOR_BORDER, self.rect, width=1, border_radius=5)

        text_surf = self.font.render(self.text, True, COLOR_BUTTON_TEXT)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)


class DropdownSelector:
    """下拉选择器组件"""

    def __init__(self, x: int, y: int, width: int, height: int,
                 options: list, label: str, font: pygame.font.Font,
                 open_upward: bool = False):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.options = options
        self.label = label
        self.font = font
        self.open_upward = open_upward  # 是否向上展开

        self.selected_index = 0
        self.expanded = False
        self.hovered_index = -1

        # 主显示区域
        self.main_rect = pygame.Rect(x, y, width, height)
        # 下拉列表区域（展开时计算）
        self.dropdown_rect = None

    def get_value(self) -> str:
        """获取当前选中的值"""
        return self.options[self.selected_index]

    def set_value(self, value: str):
        """设置选中的值"""
        if value in self.options:
            self.selected_index = self.options.index(value)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """处理事件，返回是否消费了事件"""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            # 点击主区域
            if self.main_rect.collidepoint(pos):
                self.expanded = not self.expanded
                # 预计算dropdown_rect以便后续碰撞检测
                if self.expanded:
                    dropdown_height = len(self.options) * self.height
                    if self.open_upward:
                        self.dropdown_rect = pygame.Rect(
                            self.x, self.y - dropdown_height,
                            self.width, dropdown_height
                        )
                    else:
                        self.dropdown_rect = pygame.Rect(
                            self.x, self.y + self.height,
                            self.width, dropdown_height
                        )
                return True

            # 展开状态下点击选项
            if self.expanded and self.dropdown_rect:
                if self.dropdown_rect.collidepoint(pos):
                    # 计算点击的是哪个选项
                    relative_y = pos[1] - self.dropdown_rect.y
                    index = relative_y // self.height
                    if 0 <= index < len(self.options):
                        self.selected_index = index
                        self.expanded = False
                        return True

            # 点击其他地方，收起下拉
            if self.expanded:
                self.expanded = False
                return True

        if event.type == pygame.MOUSEMOTION and self.expanded:
            pos = event.pos
            if self.dropdown_rect and self.dropdown_rect.collidepoint(pos):
                relative_y = pos[1] - self.dropdown_rect.y
                self.hovered_index = relative_y // self.height
            else:
                self.hovered_index = -1

        return False

    def draw(self, screen: pygame.Surface):
        """绘制选择器"""
        # 绘制标签
        label_surf = self.font.render(self.label, True, COLOR_TEXT)
        screen.blit(label_surf, (self.x, self.y - 22))

        # 绘制主选择框
        pygame.draw.rect(screen, COLOR_DROPDOWN_BG, self.main_rect, border_radius=3)
        pygame.draw.rect(screen, COLOR_BORDER, self.main_rect, width=1, border_radius=3)

        # 绘制当前选中值
        value_surf = self.font.render(self.get_value(), True, COLOR_BUTTON_TEXT)
        value_rect = value_surf.get_rect(midleft=(self.x + 10, self.y + self.height // 2))
        screen.blit(value_surf, value_rect)

        # 绘制下拉箭头
        arrow = "▼" if not self.expanded else "▲"
        arrow_surf = self.font.render(arrow, True, COLOR_DECO)
        arrow_rect = arrow_surf.get_rect(midright=(self.x + self.width - 8, self.y + self.height // 2))
        screen.blit(arrow_surf, arrow_rect)

        # 展开状态下绘制下拉列表
        if self.expanded:
            self._draw_dropdown(screen)

    def _draw_dropdown(self, screen: pygame.Surface):
        """绘制下拉列表"""
        dropdown_height = len(self.options) * self.height

        if self.open_upward:
            # 向上展开
            self.dropdown_rect = pygame.Rect(
                self.x, self.y - dropdown_height,
                self.width, dropdown_height
            )
        else:
            # 向下展开
            self.dropdown_rect = pygame.Rect(
                self.x, self.y + self.height,
                self.width, dropdown_height
            )

        # 背景
        pygame.draw.rect(screen, COLOR_DROPDOWN_BG, self.dropdown_rect)
        pygame.draw.rect(screen, COLOR_BORDER, self.dropdown_rect, width=1)

        # 选项
        for i, option in enumerate(self.options):
            if self.open_upward:
                option_rect = pygame.Rect(
                    self.x, self.y - dropdown_height + i * self.height,
                    self.width, self.height
                )
            else:
                option_rect = pygame.Rect(
                    self.x, self.y + self.height + i * self.height,
                    self.width, self.height
                )

            # 悬停高亮
            if i == self.hovered_index:
                pygame.draw.rect(screen, COLOR_DROPDOWN_HOVER, option_rect)

            # 选中标记
            if i == self.selected_index:
                pygame.draw.rect(screen, COLOR_BORDER, option_rect, width=1)

            # 文字
            text_surf = self.font.render(option, True, COLOR_BUTTON_TEXT)
            text_rect = text_surf.get_rect(midleft=(self.x + 10, option_rect.centery))
            screen.blit(text_surf, text_rect)


class InputPanel:
    """输入面板：包含日干、日支、时支选择器和按钮"""

    def __init__(self, x: int, y: int, font: pygame.font.Font, open_upward: bool = True):
        self.x = x
        self.y = y
        self.font = font
        self.open_upward = open_upward

        # 创建选择器
        selector_width = 80
        selector_height = 30
        spacing = 130

        self.day_stem_selector = DropdownSelector(
            x, y + 25, selector_width, selector_height,
            list(HEAVENLY_STEMS), "日干", font, open_upward=open_upward
        )
        self.day_branch_selector = DropdownSelector(
            x + spacing, y + 25, selector_width, selector_height,
            list(EARTHLY_BRANCHES), "日支", font, open_upward=open_upward
        )
        self.hour_branch_selector = DropdownSelector(
            x + spacing * 2, y + 25, selector_width, selector_height,
            list(EARTHLY_BRANCHES), "时支", font, open_upward=open_upward
        )

        # 创建按钮
        button_y = y + 75
        self.auto_button = Button(x, button_y, 65, 30, "当前", font)
        self.paipan_button = Button(x + 125, button_y, 65, 30, "排盘", font)
        self.instant_button = Button(x + 250, button_y, 90, 30, "即时起卦", font)

        # --- 公历换算上拉菜单 ---
        self.gregorian_expanded = False
        self.toggle_button = Button(x + 315, y - 2, 25, 22, "▲", font)
        self.toggle_button.set_callback(self._toggle_gregorian)

        # 展开区域的文本输入框（位于面板上方）
        expand_y = y - 55
        self.year_input = TextInput(x, expand_y, 65, 26, "年", font, max_length=4)
        self.month_input = TextInput(x + 75, expand_y, 50, 26, "月", font, max_length=2)
        self.day_input = TextInput(x + 135, expand_y, 50, 26, "日", font, max_length=2)
        self.hour_input = TextInput(x + 195, expand_y, 50, 26, "时", font, max_length=2)
        self.convert_button = Button(x + 270, expand_y, 70, 26, "换算", font)
        self.convert_button.set_callback(self._on_convert)

        # 回调
        self.on_paipan = None
        self.on_instant_paipan = None
        self.auto_button.set_callback(self._on_auto)

    def set_paipan_callback(self, callback):
        """设置排盘按钮回调"""
        self.on_paipan = callback
        self.paipan_button.set_callback(callback)

    def set_instant_paipan_callback(self, callback):
        """设置即时起卦按钮回调"""
        self.on_instant_paipan = callback
        self.instant_button.set_callback(callback)

    def _toggle_gregorian(self):
        """切换公历输入区域展开/折叠"""
        self.gregorian_expanded = not self.gregorian_expanded
        self.toggle_button.text = "▼" if self.gregorian_expanded else "▲"

    def _on_convert(self):
        """公历换算为天干地支"""
        from lunar_calendar.ganzhi import get_day_ganzhi, get_hour_branch

        try:
            year = int(self.year_input.get_text())
            month = int(self.month_input.get_text())
            day = int(self.day_input.get_text())
            hour = int(self.hour_input.get_text())
        except ValueError:
            return  # 输入不完整，忽略

        day_stem, day_branch = get_day_ganzhi(year, month, day)
        hour_branch = get_hour_branch(hour)

        self.day_stem_selector.set_value(day_stem)
        self.day_branch_selector.set_value(day_branch)
        self.hour_branch_selector.set_value(hour_branch)

    def _on_auto(self):
        """自动填入当前时间的干支"""
        from lunar_calendar.ganzhi import get_day_ganzhi, get_hour_branch

        now = datetime.now()
        day_stem, day_branch = get_day_ganzhi(now.year, now.month, now.day)
        hour_branch = get_hour_branch(now.hour)

        self.day_stem_selector.set_value(day_stem)
        self.day_branch_selector.set_value(day_branch)
        self.hour_branch_selector.set_value(hour_branch)

    def get_input(self) -> dict:
        """获取输入值"""
        return {
            'day_stem': self.day_stem_selector.get_value(),
            'day_branch': self.day_branch_selector.get_value(),
            'hour_branch': self.hour_branch_selector.get_value()
        }

    def handle_event(self, event: pygame.event.Event) -> bool:
        """处理事件"""
        # 公历toggle按钮
        if self.toggle_button.handle_event(event):
            return True

        # 公历展开区域的事件
        if self.gregorian_expanded:
            if self.convert_button.handle_event(event):
                return True
            for inp in (self.year_input, self.month_input, self.day_input, self.hour_input):
                if inp.handle_event(event):
                    return True

        # 按钮事件
        if self.auto_button.handle_event(event):
            return True
        if self.paipan_button.handle_event(event):
            return True
        if self.instant_button.handle_event(event):
            return True

        # 选择器事件（注意顺序，展开的要先处理）
        selectors = [self.day_stem_selector, self.day_branch_selector, self.hour_branch_selector]

        # 先处理展开的选择器
        for selector in selectors:
            if selector.expanded:
                if selector.handle_event(event):
                    return True

        # 再处理其他选择器
        for selector in selectors:
            if not selector.expanded:
                if selector.handle_event(event):
                    return True

        return False

    def draw(self, screen: pygame.Surface):
        """绘制面板"""
        # 绘制展开的公历区域背景
        if self.gregorian_expanded:
            expand_rect = pygame.Rect(self.x - 10, self.y - 70, 360, 65)
            pygame.draw.rect(screen, COLOR_PANEL_BG, expand_rect, border_radius=8)
            pygame.draw.rect(screen, COLOR_BORDER, expand_rect, width=1, border_radius=8)
            # 绘制文本输入框和换算按钮
            self.year_input.draw(screen)
            self.month_input.draw(screen)
            self.day_input.draw(screen)
            self.hour_input.draw(screen)
            self.convert_button.draw(screen)

        # 绘制主面板背景
        panel_rect = pygame.Rect(self.x - 10, self.y - 5, 360, 125)
        pygame.draw.rect(screen, COLOR_PANEL_BG, panel_rect, border_radius=8)
        pygame.draw.rect(screen, COLOR_BORDER, panel_rect, width=1, border_radius=8)

        # 绘制公历toggle按钮
        self.toggle_button.draw(screen)

        # 绘制选择器（先绘制未展开的，再绘制展开的，确保展开的在上层）
        selectors = [self.day_stem_selector, self.day_branch_selector, self.hour_branch_selector]

        for selector in selectors:
            if not selector.expanded:
                selector.draw(screen)

        for selector in selectors:
            if selector.expanded:
                selector.draw(screen)

        # 绘制按钮
        self.auto_button.draw(screen)
        self.paipan_button.draw(screen)
        self.instant_button.draw(screen)
