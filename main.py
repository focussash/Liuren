# main.py
# 赛博大六壬 - 主程序

import pygame
import math
import sys
import datetime
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
from ui import InputPanel, PlateHighlighter, ResultSidebar


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
        self.highlighter = PlateHighlighter(self.center, self.heaven_radius)

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

        # 7. 更新侧边栏
        self.sidebar.set_plate(
            self.current_plate,
            self.current_lessons,
            self.current_passes,
            self.current_lesson_type
        )

        # 8. 自动对齐天盘到当前时支
        self.align_to_input(hour_branch, moon_general)

        # 9. 启动布将动画
        self.start_generals_animation()

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

    def run(self):
        running = True
        while running:
            # --- 1. 事件处理 ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    continue

                # UI事件优先处理
                if self.input_panel.handle_event(event):
                    continue
                if self.sidebar.handle_event(event):
                    continue

                # 式盘交互
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        dist = math.hypot(event.pos[0]-self.center[0], event.pos[1]-self.center[1])
                        if dist < self.heaven_diameter / 2:
                            self.dragging = True
                            self.velocity = 0
                            self.target_angle = None
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.dragging = False
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
                    elif event.key == pygame.K_F5:
                        self.save_screenshot()
                    elif event.key == pygame.K_F6:
                        self.export_text()

            # --- 2. 物理更新 ---
            if self.dragging:
                mouse_pos = pygame.mouse.get_pos()
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

            # --- 3. 渲染 ---
            self.screen.fill(COLOR_BG)

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
            self.draw_heaven_text(self.screen, math.radians(-self.angle))

            # C2. 天将层（跟随天盘旋转）
            self.update_generals_animation()
            self.draw_generals(self.screen, math.radians(-self.angle))

            # D. 高亮四课三传（如果有盘局）
            if self.current_plate and self.current_lessons:
                angle_offset = math.radians(-self.angle)
                self.highlighter.highlight_all(
                    self.screen,
                    self.current_lessons,
                    self.current_passes,
                    angle_offset
                )

            # E. 绘制UI组件
            self.sidebar.draw(self.screen)       # 先绘制侧边栏
            self.input_panel.draw(self.screen)   # 后绘制输入面板（下拉菜单在上层）

            # F. HUD
            now = datetime.datetime.now()
            info_text = f"{now.strftime('%Y-%m-%d %H:%M')} | SPACE: 自动归位 | F5: 截图 | F6: 导出文本"
            hud = self.hud_font.render(info_text, True, COLOR_TEXT_DIM)
            self.screen.blit(hud, (20, WINDOW_SIZE[1] - 35))

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    app = CyberLiuren()
    app.run()
