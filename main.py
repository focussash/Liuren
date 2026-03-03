# main.py
# 赛博大六壬 - 主程序

import pygame
import math
import sys
import datetime
import numpy as np
from pyrr import matrix44, Vector3
from config import *
from core import get_chinese_hour, get_moon_general

# 导入六壬核心模块
from liuren.plate import LiurenPlate, build_heaven_plate
from liuren.four_lessons import calculate_four_lessons
from liuren.three_passes import calculate_three_passes
from liuren.moon_general import get_moon_general as get_moon_general_new
from liuren.generals import build_generals_plate
from liuren.constants import GENERAL_ORDER
from lunar_calendar.ganzhi import get_day_ganzhi, get_hour_branch

# 导入UI组件
from ui import InputPanel, PlateHighlighter, ResultSidebar, DerivationOverlay
from ui.interpretation_overlay import InterpretationOverlay

# 导入LLM解盘
from llm.interpreter import LLMInterpreter

# 导入3D渲染模块
from renderer3d import GLContext, OrbitCamera, PlateRenderer3D, CelestialRenderer3D


def ease_out_cubic(t):
    """Ease-out cubic: decelerating curve."""
    return 1.0 - (1.0 - t) ** 3


class CyberLiuren:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("赛博大六壬 - 汝阴侯漆器复原版")
        self.clock = pygame.time.Clock()

        # --- 字体加载 ---
        self.load_fonts()

        # --- 尺寸参数 (式盘居左，为侧边栏留空间) ---
        self.plate_area_width = 800  # 式盘区域宽度
        self.center = (self.plate_area_width // 2, WINDOW_SIZE[1] // 2)
        self.earth_size = 700
        self.heaven_diameter = 420
        self.heaven_radius = self.heaven_diameter // 2

        # --- 预渲染素材 (提升性能) ---
        self.earth_surf = self.create_earth_plate(self.earth_size, self.heaven_diameter)
        self.shadow_surf = self.create_drop_shadow(self.heaven_radius)
        self.heaven_surf = self.create_heaven_plate(self.heaven_diameter)

        # --- 物理与状态 ---
        self.angle = 0.0
        self.velocity = 0.0
        self.dragging = False
        self.last_mouse_pos = (0, 0)
        self.friction = 0.95
        self.target_angle = None
        self.animation_speed = 0.2

        # --- UI组件 ---
        # 输入面板移至侧边栏下方（避开盘体中心区域）
        input_panel_x = 830  # 对齐侧边栏左边缘（820+10）
        input_panel_y = 640  # 侧边栏底部(20+600=620) + 20px间距
        self.input_panel = InputPanel(input_panel_x, input_panel_y, self.hud_font)
        self.input_panel.set_paipan_callback(self.on_paipan)
        self.input_panel.set_instant_paipan_callback(self.auto_paipan)

        self.sidebar = ResultSidebar(820, 20, 360, 600, self.hud_font)
        self.derivation_overlay = DerivationOverlay(50, 50, 700, 700, self.hud_font)
        self.sidebar.set_detail_callback(lambda: self.derivation_overlay.toggle())
        self.highlighter = PlateHighlighter(self.center, self.heaven_radius)

        # LLM解盘
        self.llm_interpreter = LLMInterpreter()
        self.interpretation_overlay = InterpretationOverlay(50, 30, 750, 720, self.hud_font)
        self.sidebar.set_interpret_callback(self.on_interpret)

        # --- 当前盘局状态 ---
        self.current_plate = None
        self.current_lessons = []
        self.current_passes = []
        self.current_lesson_type = ""

        # --- 天将动画状态 ---
        self.generals_animation_active = False
        self.generals_visible_count = 0  # 当前显示的天将数量 (0-12)
        self.generals_animation_timer = 0
        self.generals_animation_interval = 100  # 每个天将间隔100ms

        # --- 四课三传高亮动画 ---
        self.highlight_anim_active = False
        self.highlight_anim_start = 0
        self.highlight_lesson_interval = 300    # ms per lesson
        self.highlight_pass_interval = 400      # ms per pass
        self.highlight_popin_duration = 200     # ms pop-in scale effect
        self.highlight_visible_lessons = 0      # 0-4
        self.highlight_visible_passes = 0       # 0-3

        # --- 3D星宿升起动画 ---
        self.celestial_rise = 1.0        # 0.0~1.0, 星宿升起进度
        self.beast_alpha = 1.0           # 0.0~1.0, 圣兽淡入
        self.rise_anim_start = None      # 动画开始时间(ticks), None=无动画
        self.RISE_DURATION = 2000        # ms
        self.BEAST_FADE_DURATION = 500   # ms

        # --- 3D模式 ---
        self.mode_3d = False
        self.gl_context = GLContext(self.plate_area_width, WINDOW_SIZE[1])
        self.camera = OrbitCamera(distance=12.0, theta=0.0, phi=45.0)
        self.heaven_surf_3d = self.create_heaven_plate_3d()
        self.heaven_3d_needs_update = False
        self.plate_renderer = PlateRenderer3D(
            self.gl_context.ctx, self.earth_surf, self.heaven_surf_3d
        )
        from renderer3d.plate_renderer import DOME_HEIGHT as _DH, HEAVEN_RADIUS as _HR
        self.celestial_renderer = CelestialRenderer3D(
            self.gl_context.ctx, _DH, _HR
        )

        self.right_dragging = False
        self.last_right_mouse_pos = (0, 0)

        # --- 3D面板隐藏/全屏 ---
        self.panels_visible = True

    def load_fonts(self):
        """字体加载与回退逻辑"""
        font_names = ["simhei", "microsoftyahei", "pingfangsc", "notosanscjksc", "simsun"]
        self.font_l = self.font_m = self.font_s = None
        for name in font_names:
            try:
                self.font_l = pygame.font.SysFont(name, 28, bold=True)
                self.font_m = pygame.font.SysFont(name, 22, bold=True)
                self.font_s = pygame.font.SysFont(name, 18, bold=True)
                self.hud_font = pygame.font.SysFont(name, 18)
                print(f"Loaded font: {name}")
                break
            except:
                continue
        if not self.font_l:
            self.font_l = pygame.font.Font(None, 24)
            self.hud_font = pygame.font.Font(None, 18)

    def auto_paipan(self):
        """使用当前时间自动排盘"""
        # 自动填充当前时间
        self.input_panel._on_auto()
        # 执行排盘
        self.on_paipan()

    def on_paipan(self):
        """排盘按钮回调"""
        input_data = self.input_panel.get_input()
        day_stem = input_data['day_stem']
        day_branch = input_data['day_branch']
        hour_branch = input_data['hour_branch']

        # 1. 计算月将（使用当前时间）
        now = datetime.datetime.now()
        moon_general, moon_general_name = get_moon_general_new(now)

        # 2. 构建天地盘
        heaven_plate = build_heaven_plate(moon_general, hour_branch)

        # 3. 构建天将盘
        generals_plate, guiren_branch = build_generals_plate(day_stem, hour_branch)

        # 4. 创建LiurenPlate
        self.current_plate = LiurenPlate(
            day_stem=day_stem,
            day_branch=day_branch,
            hour_branch=hour_branch,
            moon_general=moon_general,
            moon_general_name=moon_general_name,
            heaven_plate=heaven_plate,
            generals_plate=generals_plate,
            guiren_branch=guiren_branch
        )

        # 5. 计算四课
        self.current_lessons = calculate_four_lessons(self.current_plate)

        # 6. 计算三传
        self.current_passes, self.current_lesson_type = calculate_three_passes(
            self.current_plate, self.current_lessons
        )

        # 7. 生成详细推导
        from liuren.derivation import generate_detailed_derivation
        detailed = generate_detailed_derivation(
            self.current_plate, self.current_lessons,
            self.current_passes, self.current_lesson_type
        )
        self.derivation_overlay.set_content(detailed)

        # 8. 更新侧边栏
        self.sidebar.set_plate(
            self.current_plate,
            self.current_lessons,
            self.current_passes,
            self.current_lesson_type
        )

        # 9. 自动对齐天盘到当前时支
        self.align_to_input(hour_branch, moon_general)

        # 10. 启动布将动画
        self.start_generals_animation()

        # 11. 启动四课三传高亮动画
        self.start_highlight_animation()

        # 12. 标记3D天盘纹理需更新（等布将动画完成后重建）
        self.heaven_3d_needs_update = True

    def on_interpret(self):
        """LLM解盘按钮回调"""
        if not self.current_plate or self.llm_interpreter.is_busy:
            return

        personas = self.sidebar.get_selected_personas()
        purpose = self.sidebar.get_selected_purpose()

        # 构建增强版盘局文本
        from export.text_export import export_plate_text_for_llm
        plate_text = export_plate_text_for_llm(self.current_plate)

        # 显示loading遮罩
        self.interpretation_overlay.show_loading()

        # 异步调用LLM
        self.llm_interpreter.interpret_async(
            plate_text, personas, purpose,
            self.current_plate.day_stem,
            self.current_plate.day_branch
        )

        print(f"排盘完成: {day_stem}{day_branch}日 {hour_branch}时 月将{moon_general}({moon_general_name}) 课体:{self.current_lesson_type}")

    def align_to_input(self, hour_branch: str, moon_general: str):
        """对齐天盘到指定时支和月将"""
        hour_idx = EARTHLY_BRANCHES.index(hour_branch)
        general_idx = EARTHLY_BRANCHES.index(moon_general)

        abs_target_angle = -(hour_idx + general_idx) * 30

        delta = abs_target_angle - self.angle
        while delta > 180: delta -= 360
        while delta <= -180: delta += 360

        if abs(delta) < 0.1:
            return

        self.target_angle = self.angle + delta

    def start_generals_animation(self):
        """开始布将动画"""
        self.generals_animation_active = True
        self.generals_visible_count = 0
        self.generals_animation_timer = pygame.time.get_ticks()

    def update_generals_animation(self):
        """更新布将动画"""
        if not self.generals_animation_active:
            return
        now = pygame.time.get_ticks()
        elapsed = now - self.generals_animation_timer
        new_count = min(12, elapsed // self.generals_animation_interval)
        if new_count > self.generals_visible_count:
            self.generals_visible_count = new_count
        if self.generals_visible_count >= 12:
            self.generals_animation_active = False
            # Rebuild 3D heaven texture with all generals baked in
            if self.heaven_3d_needs_update:
                self.heaven_surf_3d = self.create_heaven_plate_3d()
                self.plate_renderer.update_heaven_texture(self.heaven_surf_3d)
                self.heaven_3d_needs_update = False

    def start_highlight_animation(self):
        """开始四课三传高亮动画"""
        self.highlight_anim_active = True
        self.highlight_visible_lessons = 0
        self.highlight_visible_passes = 0
        self.highlight_anim_start = pygame.time.get_ticks()

    def update_highlight_animation(self):
        """更新四课三传高亮动画"""
        if not self.highlight_anim_active:
            return
        elapsed = pygame.time.get_ticks() - self.highlight_anim_start
        total_lessons = len(self.current_lessons)
        lessons_done_time = total_lessons * self.highlight_lesson_interval

        self.highlight_visible_lessons = min(total_lessons,
                                             elapsed // self.highlight_lesson_interval)
        if elapsed > lessons_done_time:
            pass_elapsed = elapsed - lessons_done_time
            total_passes = len(self.current_passes)
            self.highlight_visible_passes = min(total_passes,
                                                 pass_elapsed // self.highlight_pass_interval)
            if pass_elapsed >= total_passes * self.highlight_pass_interval + self.highlight_popin_duration:
                self.highlight_anim_active = False
                self.highlight_visible_lessons = total_lessons
                self.highlight_visible_passes = total_passes

    def get_popin_scale(self, item_index, is_pass=False):
        """返回 0.0（未出现）~ 1.0（到位）的缩放因子"""
        if not self.highlight_anim_active:
            return 1.0
        elapsed = pygame.time.get_ticks() - self.highlight_anim_start
        if is_pass:
            appear_time = (len(self.current_lessons) * self.highlight_lesson_interval
                           + item_index * self.highlight_pass_interval)
        else:
            appear_time = item_index * self.highlight_lesson_interval
        if elapsed < appear_time:
            return 0.0
        t = min((elapsed - appear_time) / self.highlight_popin_duration, 1.0)
        return 0.3 + 0.7 * ease_out_cubic(t)

    def draw_generals(self, screen, angle_offset):
        """
        绘制天将（跟随天盘旋转）

        Args:
            screen: 绘制目标
            angle_offset: 天盘旋转角度（弧度）
        """
        if not self.current_plate or not self.current_plate.generals_plate:
            return

        # 天将显示半径（在月将内侧）
        r_general = self.heaven_radius * 0.35

        # 获取需要显示的天将数量
        visible_count = self.generals_visible_count if self.generals_animation_active else 12

        # 按照地支顺序绘制天将
        for i, branch in enumerate(EARTHLY_BRANCHES):
            general = self.current_plate.generals_plate.get(branch, '')
            if not general:
                continue

            # 检查此天将是否在当前动画显示范围内
            general_index = GENERAL_ORDER.index(general)
            if general_index >= visible_count:
                continue

            # 计算角度（从子位开始，子位在正下方即-90度位置）
            # 地支顺序：子(0)在下，顺时针排列
            base_angle = -90 + i * 30  # 子位在-90度
            angle_rad = math.radians(base_angle) + angle_offset

            # 计算位置
            x = self.center[0] + r_general * math.cos(angle_rad)
            y = self.center[1] + r_general * math.sin(angle_rad)

            # 计算文字旋转角度（让文字朝外可读）
            text_angle = -base_angle - math.degrees(angle_offset) - 90

            # 绘制天将名称（只取前两个字符）
            general_short = general[:2]
            # 贵人用金色，其他天将用红色
            if general == '贵人':
                color = (255, 215, 0)  # 金色
            else:
                color = (180, 100, 100)  # 暗红色
            self.draw_rotated_text(screen, general_short, self.font_s,
                                   color, (x, y), text_angle)

    def _get_toggle_btn_rect(self):
        """3D模式面板切换按钮的矩形区域"""
        return pygame.Rect(self.plate_area_width - 40, 10, 30, 30)

    def _draw_toggle_btn(self, screen):
        """绘制3D模式面板切换按钮"""
        rect = self._get_toggle_btn_rect()
        # Background
        btn_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(btn_surf, (40, 40, 50, 180), (0, 0, rect.width, rect.height),
                         border_radius=5)
        pygame.draw.rect(btn_surf, (120, 100, 60, 200), (0, 0, rect.width, rect.height),
                         1, border_radius=5)
        screen.blit(btn_surf, rect.topleft)
        # Icon: "◀" when panels visible (click to hide), "▶" when hidden (click to show)
        icon = "◀" if self.panels_visible else "▶"
        icon_surf = self.hud_font.render(icon, True, COLOR_TEXT_DIM)
        icon_rect = icon_surf.get_rect(center=rect.center)
        screen.blit(icon_surf, icon_rect)

    def save_screenshot(self):
        """保存截图到文件"""
        from export import save_screenshot
        filename = save_screenshot(self.screen)
        print(f"Screenshot saved: {filename}")

    def export_text(self):
        """导出盘局文本到文件"""
        if self.current_plate:
            # 确保plate对象包含完整数据
            self.current_plate.lessons = self.current_lessons
            self.current_plate.passes = self.current_passes
            self.current_plate.lesson_type = self.current_lesson_type

            from export import save_to_file
            filename = save_to_file(self.current_plate)
            print(f"Text exported: {filename}")
        else:
            print("No plate to export. Please paipan first.")

    # --- 特效渲染函数 ---

    def create_drop_shadow(self, radius):
        """生成天盘下方的柔和阴影"""
        offset = 50
        shadow_size = radius * 2 + offset * 2
        surf = pygame.Surface((shadow_size, shadow_size), pygame.SRCALPHA)
        center = shadow_size // 2

        shadow_width = 40
        for r in range(radius, radius + shadow_width):
            progress = (r - radius) / shadow_width
            alpha = int(160 * (1 - progress))
            pygame.draw.circle(surf, (0, 0, 0, alpha), (center, center), r)
        return surf

    def draw_convex_lighting(self, surf, radius):
        """在天盘表面绘制球体光照效果"""
        light_offset_x = -radius * 0.25
        light_offset_y = -radius * 0.25
        max_r = radius * 0.95
        steps = 60

        for i in range(steps):
            current_r = max_r * (1 - i/steps)
            alpha = int(5 + i * 1.3)
            if alpha > 255: alpha = 255

            highlight_color = (255, 250, 220, alpha)
            shift_factor = math.pow(i / steps, 0.8)
            draw_pos = (radius + light_offset_x * shift_factor, radius + light_offset_y * shift_factor)

            pygame.draw.circle(surf, highlight_color, (int(draw_pos[0]), int(draw_pos[1])), int(current_r))

        spec_surf = pygame.Surface((radius, radius), pygame.SRCALPHA)
        pygame.draw.ellipse(spec_surf, (255, 255, 255, 120), (0, 0, 100, 60))
        pygame.draw.ellipse(spec_surf, (255, 255, 255, 60), (-10, -10, 120, 80), 10)

        spec_surf = pygame.transform.rotate(spec_surf, 45)
        surf.blit(spec_surf, (radius*0.15, radius*0.15), special_flags=pygame.BLEND_ADD)

    # --- 辅助绘图 ---

    def draw_rotated_text(self, surf, text, font, color, center, angle_deg):
        # 先用2倍大小渲染，旋转后缩回，减少模糊
        txt_surf = font.render(text, True, color)
        scaled_up = pygame.transform.scale(txt_surf,
            (txt_surf.get_width() * 2, txt_surf.get_height() * 2))
        rotated = pygame.transform.rotozoom(scaled_up, angle_deg, 0.5)  # 旋转并缩回50%
        rect = rotated.get_rect(center=center)
        surf.blit(rotated, rect)

    def get_mouse_angle(self, pos):
        dx = pos[0] - self.center[0]
        dy = pos[1] - self.center[1]
        return math.degrees(math.atan2(dy, dx))

    # --- 核心绘制逻辑 ---

    def create_earth_plate(self, size, inner_dia):
        """绘制方形地盘"""
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        rect = pygame.Rect(0, 0, size, size)
        pygame.draw.rect(surf, COLOR_EARTH_BG, rect, border_radius=10)

        m_xiu = 32; m_mid = 110
        r_inner = inner_dia // 2 + 5
        mid = size // 2

        # 结构线
        lw = 4
        pygame.draw.rect(surf, COLOR_DECO, (m_xiu, m_xiu, size-m_xiu*2, size-m_xiu*2), lw, border_radius=5)
        pygame.draw.rect(surf, COLOR_DECO, (m_mid, m_mid, size-m_mid*2, size-m_mid*2), lw, border_radius=5)
        pygame.draw.circle(surf, COLOR_DECO, (mid, mid), r_inner, lw)

        corners_mid = [(m_mid, m_mid), (size-m_mid, m_mid), (size-m_mid, size-m_mid), (m_mid, size-m_mid)]
        angles = [225, 315, 45, 135]
        for i, ang in enumerate(angles):
            rad = math.radians(ang)
            end_pt = (mid + r_inner*math.cos(rad), mid + r_inner*math.sin(rad))
            pygame.draw.line(surf, COLOR_DECO, corners_mid[i], end_pt, lw)

        # 节点
        nodes = corners_mid + [(mid, m_mid), (size-m_mid, mid), (mid, size-m_mid), (m_mid, mid)]
        for pt in nodes:
            pygame.draw.circle(surf, COLOR_EARTH_BG, pt, 14)
            pygame.draw.circle(surf, COLOR_NODE, pt, 14, 2)
            pygame.draw.circle(surf, COLOR_NODE, pt, 4)

        # 外圈星宿
        def draw_side_xiu(char_list, side):
            step = size / 8
            for i, char in enumerate(char_list):
                angle = [180, 90, 0, -90][side]
                margin = 16
                if side==0: x,y = step*(i+1), margin
                elif side==1: x,y = size-margin, step*(i+1)
                elif side==2: x,y = size-step*(i+1), size-margin
                elif side==3: x,y = margin, size-step*(i+1)
                self.draw_rotated_text(surf, char, self.font_m, COLOR_TEXT_DIM, (x,y), angle)

        draw_side_xiu(XIU_S, 0); draw_side_xiu(XIU_W, 1)
        draw_side_xiu(XIU_N[::-1], 2); draw_side_xiu(XIU_E[::-1], 3)

        # 中层干支
        def draw_row(chars, p1, p2):
            count = len(chars)
            for i, char in enumerate(chars):
                t = (i + 1) / (count + 1)
                cx = p1[0] + (p2[0] - p1[0]) * t
                cy = p1[1] + (p2[1] - p1[1]) * t
                color = COLOR_STEM if char in HEAVENLY_STEMS else COLOR_TEXT
                font = self.font_l if char in ['子','午','卯','酉'] else self.font_m
                dx, dy = cx - mid, cy - mid
                angle = math.degrees(math.atan2(dy, dx)) + 90
                self.draw_rotated_text(surf, char, font, color, (cx, cy), -angle)

        m_row = (m_xiu + m_mid) / 2
        draw_row(['巳','丙','午','丁','未'], (m_mid, m_row), (size-m_mid, m_row))
        draw_row(['申','庚','酉','辛','戌'], (size-m_row, m_mid), (size-m_row, size-m_mid))
        draw_row(['丑','癸','子','壬','亥'], (size-m_mid, size-m_row), (m_mid, size-m_row))
        draw_row(['辰','乙','卯','甲','寅'], (m_row, size-m_mid), (m_row, m_mid))

        # 四隅卦
        corner_offset = m_mid + 28
        corners_data = [('巽',(corner_offset, corner_offset)), ('坤',(size-corner_offset, corner_offset)),
                        ('乾',(size-corner_offset, size-corner_offset)), ('艮',(corner_offset, size-corner_offset))]
        for char, pos in corners_data:
            dx, dy = pos[0] - mid, pos[1] - mid
            angle = math.degrees(math.atan2(dy, dx)) + 90
            self.draw_rotated_text(surf, char, self.font_l, COLOR_TEXT_DIM, pos, -angle)

        return surf

    def create_heaven_plate(self, diameter):
        """绘制圆形天盘：光影加强版 + 北斗"""
        surf = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        radius = diameter // 2
        mid = radius

        pygame.draw.circle(surf, COLOR_HEAVEN_BG, (mid, mid), radius)
        self.draw_convex_lighting(surf, radius)

        pygame.draw.circle(surf, COLOR_DECO, (mid, mid), radius, 4)
        pygame.draw.circle(surf, COLOR_DECO, (mid, mid), radius * 0.68, 2)

        rect = pygame.Rect(2, 2, diameter-4, diameter-4)
        pygame.draw.arc(surf, (180, 160, 120), rect, math.pi/2, math.pi, 2)

        # 北斗七星
        star_coords = [
            (-90, -22), (-63, -13), (-32, -9),
            (0, 0),
            (18, 22), (50, 9), (45, -32)
        ]

        screen_points = [(mid + x, mid + y) for x, y in star_coords]

        line_color = (180, 60, 60)
        line_width = 3

        handle_pts = screen_points[0:4]
        pygame.draw.lines(surf, line_color, False, handle_pts, line_width)

        bowl_pts = screen_points[3:]
        pygame.draw.lines(surf, line_color, False, bowl_pts, line_width)

        for i, pt in enumerate(screen_points):
            if i == 3:
                pygame.draw.circle(surf, COLOR_NODE, pt, 8, 2)
                pygame.draw.circle(surf, (200, 50, 50), pt, 2)
            else:
                pygame.draw.circle(surf, COLOR_NODE, pt, 5)
                pygame.draw.circle(surf, (200, 50, 50), pt, 2)

        return surf

    def create_heaven_plate_3d(self):
        """Pre-render heaven plate texture for 3D mode.

        Unlike the 2D heaven_surf, this includes all text (moon generals,
        28 mansions, generals) baked into the texture. Convex lighting is
        omitted since the 3D shader handles Blinn-Phong lighting.
        """
        diameter = self.heaven_diameter
        radius = diameter // 2
        mid = radius

        surf = pygame.Surface((diameter, diameter), pygame.SRCALPHA)

        # Background circle (no convex lighting - shader handles it)
        pygame.draw.circle(surf, COLOR_HEAVEN_BG, (mid, mid), radius)

        # Structural lines
        pygame.draw.circle(surf, COLOR_DECO, (mid, mid), radius, 4)
        pygame.draw.circle(surf, COLOR_DECO, (mid, mid), int(radius * 0.68), 2)
        rect = pygame.Rect(2, 2, diameter - 4, diameter - 4)
        pygame.draw.arc(surf, (180, 160, 120), rect, math.pi / 2, math.pi, 2)

        # Beidou (北斗七星)
        star_coords = [
            (-90, -22), (-63, -13), (-32, -9), (0, 0),
            (18, 22), (50, 9), (45, -32)
        ]
        screen_points = [(mid + x, mid + y) for x, y in star_coords]
        line_color = (180, 60, 60)
        pygame.draw.lines(surf, line_color, False, screen_points[0:4], 3)
        pygame.draw.lines(surf, line_color, False, screen_points[3:], 3)
        for i, pt in enumerate(screen_points):
            if i == 3:
                pygame.draw.circle(surf, COLOR_NODE, pt, 8, 2)
                pygame.draw.circle(surf, (200, 50, 50), pt, 2)
            else:
                pygame.draw.circle(surf, COLOR_NODE, pt, 5)
                pygame.draw.circle(surf, (200, 50, 50), pt, 2)

        # Moon generals (月将) at default angle
        r_gen = radius * 0.52
        for i, gen_name in enumerate(MOON_GENERALS):
            base_angle = 90 + i * 30
            angle_rad = math.radians(base_angle)
            x = mid + r_gen * math.cos(angle_rad)
            y = mid + r_gen * math.sin(angle_rad)
            text_angle = -base_angle - 90
            self.draw_rotated_text(surf, gen_name, self.font_m, COLOR_TEXT, (x, y), text_angle)

        # 28 mansions (二十八宿) at default angle
        r_xiu = radius * 0.88
        step_angle = 360 / 28
        for i, char in enumerate(ORDERED_XIU_R):
            base_angle = 90 + i * step_angle
            angle_rad = math.radians(base_angle)
            x = mid + r_xiu * math.cos(angle_rad)
            y = mid + r_xiu * math.sin(angle_rad)
            text_angle = -base_angle - 90
            self.draw_rotated_text(surf, char, self.font_s, COLOR_TEXT_DIM, (x, y), text_angle)

        # Generals (天将) - only if paipan data exists and animation complete
        if (self.current_plate and self.current_plate.generals_plate
                and not self.generals_animation_active):
            r_general = radius * 0.35
            for i, branch in enumerate(EARTHLY_BRANCHES):
                general = self.current_plate.generals_plate.get(branch, '')
                if not general:
                    continue
                base_angle = -90 + i * 30
                angle_rad = math.radians(base_angle)
                x = mid + r_general * math.cos(angle_rad)
                y = mid + r_general * math.sin(angle_rad)
                text_angle = -base_angle - 90
                general_short = general[:2]
                color = (255, 215, 0) if general == '贵人' else (180, 100, 100)
                self.draw_rotated_text(surf, general_short, self.font_s,
                                       color, (x, y), text_angle)

        return surf

    def draw_heaven_text(self, screen, angle_offset):
        """实时绘制天盘上的文字（月将、二十八宿），避免二次旋转模糊

        Args:
            screen: 绘制目标
            angle_offset: 天盘旋转角度（弧度）
        """
        mid_x, mid_y = self.center

        # 内圈十二月将
        r_gen = self.heaven_radius * 0.52
        for i, gen_name in enumerate(MOON_GENERALS):
            base_angle = 90 + i * 30
            angle_rad = math.radians(base_angle) + angle_offset
            x = mid_x + r_gen * math.cos(angle_rad)
            y = mid_y + r_gen * math.sin(angle_rad)
            text_angle = -base_angle - math.degrees(angle_offset) - 90
            self.draw_rotated_text(screen, gen_name, self.font_m, COLOR_TEXT, (x, y), text_angle)

        # 外圈二十八宿
        r_xiu = self.heaven_radius * 0.88
        step_angle = 360 / 28
        for i, char in enumerate(ORDERED_XIU_R):
            base_angle = 90 + i * step_angle
            angle_rad = math.radians(base_angle) + angle_offset
            x = mid_x + r_xiu * math.cos(angle_rad)
            y = mid_y + r_xiu * math.sin(angle_rad)
            text_angle = -base_angle - math.degrees(angle_offset) - 90
            self.draw_rotated_text(screen, char, self.font_s, COLOR_TEXT_DIM, (x, y), text_angle)

    def align_to_now(self):
        """自动对齐到当前时间"""
        now = datetime.datetime.now()
        hour_idx = get_chinese_hour(now)
        general_idx = get_moon_general(now)

        print(f"Time: {now.hour}点 (地支{EARTHLY_BRANCHES[hour_idx]})")
        print(f"General: {MOON_GENERALS[general_idx]}")

        abs_target_angle = -(hour_idx + general_idx) * 30

        delta = abs_target_angle - self.angle
        while delta > 180: delta -= 360
        while delta <= -180: delta += 360

        if abs(delta) < 0.1:
            return

        self.target_angle = self.angle + delta

    def _render_2d(self):
        """2D渲染路径（原有逻辑）"""
        # A. 地盘
        earth_rect = self.earth_surf.get_rect(center=self.center)
        self.screen.blit(self.earth_surf, earth_rect)

        # B. 阴影
        shadow_rect = self.shadow_surf.get_rect(center=(self.center[0] + 12, self.center[1] + 12))
        self.screen.blit(self.shadow_surf, shadow_rect)

        # C. 天盘（背景）
        rotated_heaven = pygame.transform.rotate(self.heaven_surf, -self.angle)
        heaven_rect = rotated_heaven.get_rect(center=self.center)
        self.screen.blit(rotated_heaven, heaven_rect)

        # C1. 天盘文字（月将、二十八宿）- 实时绘制避免二次旋转模糊
        self.draw_heaven_text(self.screen, math.radians(self.angle))

        # C2. 天将层（跟随天盘旋转）
        self.update_generals_animation()
        self.draw_generals(self.screen, math.radians(self.angle))

        # D. 高亮四课三传（如果有盘局）
        if self.current_plate and self.current_lessons:
            self.update_highlight_animation()
            angle_offset = math.radians(self.angle)
            lesson_scales = [self.get_popin_scale(i) for i in range(len(self.current_lessons))]
            pass_scales = [self.get_popin_scale(i, is_pass=True) for i in range(len(self.current_passes))]
            vis_l = self.highlight_visible_lessons if self.highlight_anim_active else len(self.current_lessons)
            vis_p = self.highlight_visible_passes if self.highlight_anim_active else len(self.current_passes)
            self.highlighter.highlight_all(
                self.screen, self.current_lessons, self.current_passes, angle_offset,
                visible_lessons=vis_l, visible_passes=vis_p,
                lesson_scales=lesson_scales, pass_scales=pass_scales
            )

    def _highlight_3d(self, vp):
        """Draw 3D-projected highlights for four lessons and three passes.

        Projects branch positions on the heaven plate to screen coordinates,
        then draws glow effects using the existing Pygame highlighter.
        """
        if not self.current_plate or not self.current_lessons:
            return

        from renderer3d.plate_renderer import HEAVEN_RADIUS, DOME_HEIGHT

        # Build heaven plate model matrix (matching render_heaven)
        model = self.plate_renderer.get_heaven_model(-self.angle)
        mvp = matrix44.multiply(model, vp)

        viewport_w = self.plate_area_width
        viewport_h = WINDOW_SIZE[1]
        r_highlight = HEAVEN_RADIUS * 0.65
        # Highlight Y sits on the dome surface at this radius
        t = r_highlight / HEAVEN_RADIUS  # = 0.65
        highlight_y = DOME_HEIGHT * (1.0 - t * t)

        def branch_to_screen(branch):
            """Project a branch position on the heaven plate to screen coords."""
            idx = EARTHLY_BRANCHES.index(branch)
            # Mesh angle: texture angle negated due to Y-flip
            mesh_angle = math.radians(-(90 + idx * 30))
            local = np.array([
                r_highlight * math.cos(mesh_angle),
                highlight_y,
                r_highlight * math.sin(mesh_angle),
                1.0
            ], dtype='f4')
            clip = local @ mvp
            if clip[3] <= 0:
                return None  # behind camera
            ndc = clip[:3] / clip[3]
            sx = (ndc[0] + 1) / 2 * viewport_w
            sy = (1 - ndc[1]) / 2 * viewport_h
            return (int(sx), int(sy))

        # Animation visibility
        vis_l = self.highlight_visible_lessons if self.highlight_anim_active else len(self.current_lessons)
        vis_p = self.highlight_visible_passes if self.highlight_anim_active else len(self.current_passes)

        # Highlight four lessons (gold)
        for i, lesson in enumerate(self.current_lessons):
            if i >= vis_l:
                break
            scale = self.get_popin_scale(i)
            pos = branch_to_screen(lesson.heaven)
            if pos:
                self.highlighter._draw_glow(self.screen, pos, (255, 200, 100, 120),
                                            size=15, scale=scale)

        # Highlight three passes (initial=red, others=cyan)
        for i, p in enumerate(self.current_passes):
            if i >= vis_p:
                break
            color = (255, 100, 100, 180) if i == 0 else (100, 200, 255, 150)
            scale = self.get_popin_scale(i, is_pass=True)
            pos = branch_to_screen(p.branch)
            if pos:
                self.highlighter._draw_glow(self.screen, pos, color,
                                            size=15, scale=scale)

        # Connection lines between visible passes only
        visible_passes = self.current_passes[:vis_p]
        if len(visible_passes) >= 2:
            points = []
            for p in visible_passes:
                pos = branch_to_screen(p.branch)
                if pos:
                    points.append(pos)
            for i in range(len(points) - 1):
                pygame.draw.line(self.screen, (150, 200, 255, 100),
                                 points[i], points[i + 1], 2)

    def _update_rise_animation(self):
        """更新星宿升起动画"""
        if self.rise_anim_start is None:
            return
        elapsed = pygame.time.get_ticks() - self.rise_anim_start
        # Phase 1: stars rise (0 ~ RISE_DURATION)
        t = min(elapsed / self.RISE_DURATION, 1.0)
        self.celestial_rise = ease_out_cubic(t)
        # Phase 2: beasts fade in (RISE_DURATION ~ RISE_DURATION + BEAST_FADE_DURATION)
        if elapsed > self.RISE_DURATION:
            bt = min((elapsed - self.RISE_DURATION) / self.BEAST_FADE_DURATION, 1.0)
            self.beast_alpha = bt
        # Animation complete
        if elapsed > self.RISE_DURATION + self.BEAST_FADE_DURATION:
            self.celestial_rise = 1.0
            self.beast_alpha = 1.0
            self.rise_anim_start = None

    def _render_3d(self):
        """3D渲染路径"""
        self._update_rise_animation()
        aspect = self.plate_area_width / WINDOW_SIZE[1]
        vp = self.camera.get_vp_matrix(aspect)
        camera_pos = self.camera.get_eye_position()

        # 渲染3D场景到FBO
        self.gl_context.begin_frame()
        self.gl_context.ctx.enable(self.gl_context.ctx.BLEND)
        self.gl_context.ctx.blend_func = (
            self.gl_context.ctx.SRC_ALPHA,
            self.gl_context.ctx.ONE_MINUS_SRC_ALPHA
        )

        # A. 地盘
        self.plate_renderer.render_earth(vp, camera_pos)

        # C. 盘间阴影（地盘表面，天盘下方）
        self.plate_renderer.render_shadow(vp)

        # D. 天盘（悬浮在地盘上方，随self.angle旋转）
        heaven_model = self.plate_renderer.get_heaven_model(-self.angle)
        self.plate_renderer.render_heaven(vp, camera_pos, -self.angle)

        # E. 天体装饰（穹顶上方，随天盘旋转）
        view = self.camera.get_view_matrix()
        camera_right = np.array(view[:3, 0], dtype='f4')  # column 0 = right
        camera_up = np.array(view[:3, 1], dtype='f4')     # column 1 = up
        self.celestial_renderer.render(vp, heaven_model, camera_right, camera_up,
                                       rise_factor=self.celestial_rise,
                                       beast_alpha=self.beast_alpha)

        surface_3d = self.gl_context.end_frame()

        # 将3D渲染结果blit到屏幕的plate区域
        self.screen.blit(surface_3d, (0, 0))

        # F. 高亮四课三传（2D overlay，投影到屏幕坐标）
        self.update_highlight_animation()
        self._highlight_3d(vp)

        # 天将动画仍需更新（即使不在2D中渲染）
        self.update_generals_animation()

    def run(self):
        running = True
        while running:
            # --- 1. 事件处理 ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    continue

                # LLM解盘遮罩最优先
                if self.interpretation_overlay.handle_event(event):
                    continue

                # 详解遮罩次优先
                if self.derivation_overlay.handle_event(event):
                    continue

                # 3D全屏切换按钮
                if (self.mode_3d and event.type == pygame.MOUSEBUTTONDOWN
                        and event.button == 1):
                    btn_rect = self._get_toggle_btn_rect()
                    if btn_rect.collidepoint(event.pos):
                        self.panels_visible = not self.panels_visible
                        self.plate_area_width = 800 if self.panels_visible else WINDOW_SIZE[0]
                        self.gl_context.resize(self.plate_area_width, WINDOW_SIZE[1])
                        self.center = (self.plate_area_width // 2, WINDOW_SIZE[1] // 2)
                        continue

                # UI事件优先处理（仅面板可见时处理）
                if self.panels_visible or not self.mode_3d:
                    if self.input_panel.handle_event(event):
                        continue
                    if self.sidebar.handle_event(event):
                        continue

                # 式盘交互
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        # 左键：旋转天盘（2D用角度判定，3D用plate区域判定）
                        if self.mode_3d:
                            if event.pos[0] < self.plate_area_width:
                                self.dragging = True
                                self.velocity = 0
                                self.target_angle = None
                        else:
                            dist = math.hypot(event.pos[0]-self.center[0], event.pos[1]-self.center[1])
                            if dist < self.heaven_diameter / 2:
                                self.dragging = True
                                self.velocity = 0
                                self.target_angle = None
                    elif event.button == 3 and self.mode_3d:
                        # 右键：3D模式下旋转相机
                        self.right_dragging = True
                        self.last_right_mouse_pos = event.pos
                    elif event.button == 4 and self.mode_3d:
                        # 滚轮上：缩放
                        if event.pos[0] < self.plate_area_width:
                            self.camera.zoom(1)
                    elif event.button == 5 and self.mode_3d:
                        # 滚轮下：缩放
                        if event.pos[0] < self.plate_area_width:
                            self.camera.zoom(-1)
                elif event.type == pygame.MOUSEWHEEL and self.mode_3d:
                    # 部分系统用MOUSEWHEEL而非button 4/5
                    mouse_pos = pygame.mouse.get_pos()
                    if mouse_pos[0] < self.plate_area_width:
                        self.camera.zoom(event.y)
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.dragging = False
                    elif event.button == 3:
                        self.right_dragging = False
                elif event.type == pygame.MOUSEMOTION and self.right_dragging and self.mode_3d:
                    # 右键拖拽：旋转相机
                    dx = event.pos[0] - self.last_right_mouse_pos[0]
                    dy = event.pos[1] - self.last_right_mouse_pos[1]
                    self.camera.orbit(dx, dy)
                    self.last_right_mouse_pos = event.pos
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if self.current_plate:
                            # 已排盘：对齐到排盘时的时支
                            self.align_to_input(
                                self.current_plate.hour_branch,
                                self.current_plate.moon_general
                            )
                        else:
                            # 未排盘：自动排盘（当前时间）
                            self.auto_paipan()
                    elif event.key == pygame.K_TAB:
                        self.mode_3d = not self.mode_3d
                        if self.mode_3d:
                            # 触发星宿升起动画
                            self.celestial_rise = 0.0
                            self.beast_alpha = 0.0
                            self.rise_anim_start = pygame.time.get_ticks()
                        else:
                            # 回到2D时恢复面板
                            if not self.panels_visible:
                                self.panels_visible = True
                                self.plate_area_width = 800
                                self.gl_context.resize(self.plate_area_width, WINDOW_SIZE[1])
                        print(f"Mode: {'3D' if self.mode_3d else '2D'}")
                    elif event.key == pygame.K_EQUALS and self.mode_3d:
                        # "=" 键: 切换面板显示 (仅3D模式)
                        self.panels_visible = not self.panels_visible
                        self.plate_area_width = 800 if self.panels_visible else WINDOW_SIZE[0]
                        self.gl_context.resize(self.plate_area_width, WINDOW_SIZE[1])
                        self.center = (self.plate_area_width // 2, WINDOW_SIZE[1] // 2)
                    elif event.key == pygame.K_F5:
                        self.save_screenshot()
                    elif event.key == pygame.K_HOME and self.mode_3d:
                        self.camera.reset()
                    elif event.key == pygame.K_F6:
                        self.export_text()

            # --- 2. 物理更新 ---
            if self.dragging:
                mouse_pos = pygame.mouse.get_pos()
                if self.mode_3d:
                    # 3D模式：水平拖拽增量直接映射到旋转角度
                    if self.last_mouse_pos != (0, 0):
                        delta = (mouse_pos[0] - self.last_mouse_pos[0]) * 0.5
                        self.angle += delta
                        self.velocity = delta
                    self.last_mouse_pos = mouse_pos
                else:
                    # 2D模式：基于角度的拖拽（原有逻辑）
                    current_mouse_angle = self.get_mouse_angle(mouse_pos)
                    if self.last_mouse_pos != (0,0):
                        last = self.get_mouse_angle(self.last_mouse_pos)
                        delta = current_mouse_angle - last
                        if delta > 180: delta -= 360
                        if delta < -180: delta += 360
                        self.angle += delta
                        self.velocity = delta
                    self.last_mouse_pos = mouse_pos
            else:
                self.last_mouse_pos = (0,0)
                if self.target_angle is not None:
                    diff = self.target_angle - self.angle
                    if abs(diff) < 0.1:
                        self.angle = self.target_angle
                        self.target_angle = None
                        self.velocity = 0
                    else:
                        self.angle += diff * self.animation_speed
                else:
                    self.angle += self.velocity
                    self.velocity *= self.friction
                    if abs(self.velocity) < 0.01:
                        self.velocity = 0

            # --- 2b. LLM结果轮询 ---
            if self.llm_interpreter.has_result:
                self.interpretation_overlay.set_result(self.llm_interpreter.get_result())
            elif self.llm_interpreter.has_error:
                self.interpretation_overlay.set_error(self.llm_interpreter.get_error())

            # --- 3. 渲染 ---
            self.screen.fill(COLOR_BG)

            if self.mode_3d:
                # === 3D渲染路径 ===
                self._render_3d()
            else:
                # === 2D渲染路径（原有逻辑不变）===
                self._render_2d()

            # E. 绘制UI组件
            if self.panels_visible or not self.mode_3d:
                self.sidebar.draw(self.screen)       # 先绘制侧边栏
                self.input_panel.draw(self.screen)   # 后绘制输入面板（下拉菜单在上层）

            # E2. 3D模式面板切换按钮
            if self.mode_3d:
                self._draw_toggle_btn(self.screen)

            # F. 详解遮罩
            self.derivation_overlay.draw(self.screen)

            # F2. LLM解盘遮罩（最上层）
            self.interpretation_overlay.draw(self.screen)

            # G. HUD
            now = datetime.datetime.now()
            mode_str = "3D" if self.mode_3d else "2D"
            if self.mode_3d:
                info_text = f"[{mode_str}] {now.strftime('%Y-%m-%d %H:%M')} | TAB: 2D | =: {'显示面板' if not self.panels_visible else '全屏'} | SPACE: 归位 | F5: 截图"
            else:
                info_text = f"[{mode_str}] {now.strftime('%Y-%m-%d %H:%M')} | TAB: 3D | SPACE: 自动归位 | F5: 截图"
            hud = self.hud_font.render(info_text, True, COLOR_TEXT_DIM)
            self.screen.blit(hud, (20, WINDOW_SIZE[1] - 35))

            pygame.display.flip()
            self.clock.tick(FPS)

        self.celestial_renderer.release()
        self.plate_renderer.release()
        self.gl_context.release()
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    app = CyberLiuren()
    app.run()
