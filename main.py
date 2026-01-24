import pygame
import math
import sys
import datetime
from config import * # 确保 config.py 在同目录下
from core import get_chinese_hour, get_moon_general # 确保 core.py 在同目录下

class CyberLiuren:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("赛博大六壬 - 汝阴侯漆器复原版 [按空格自动归位]")
        self.clock = pygame.time.Clock()

        # --- 字体加载 ---
        self.load_fonts()

        # --- 尺寸参数 ---
        self.center = (WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2)
        self.earth_size = 760
        self.heaven_diameter = 460
        self.heaven_radius = self.heaven_diameter // 2
        
        # --- 预渲染素材 (提升性能) ---
        # 1. 地盘
        self.earth_surf = self.create_earth_plate(self.earth_size, self.heaven_diameter)
        # 2. 阴影层 (加宽加大)
        self.shadow_surf = self.create_drop_shadow(self.heaven_radius)
        # 3. 天盘 (含强力3D光照 + 终极文物版北斗)
        self.heaven_surf = self.create_heaven_plate(self.heaven_diameter)

        # --- 物理与状态 ---
        self.angle = 0.0
        self.velocity = 0.0
        self.dragging = False
        self.last_mouse_pos = (0, 0)
        self.friction = 0.95
        self.target_angle = None
        self.animation_speed = 0.2

    def load_fonts(self):
        """ 字体加载与回退逻辑 """
        font_names = ["simhei", "microsoftyahei", "pingfangsc", "notosanscjksc", "simsun"]
        self.font_l = self.font_m = self.font_s = None
        for name in font_names:
            try:
                self.font_l = pygame.font.SysFont(name, 28, bold=True)
                self.font_m = pygame.font.SysFont(name, 22, bold=True)
                self.font_s = pygame.font.SysFont(name, 18, bold=True)
                self.hud_font = pygame.font.SysFont(name, 20)
                print(f"Loaded font: {name}")
                break
            except:
                continue
        if not self.font_l:
            self.font_l = pygame.font.Font(None, 24)

    # --- ✨ 特效渲染函数 (Heavy Vibe) ---
    
    def create_drop_shadow(self, radius):
        """ 生成天盘下方的柔和阴影 (增强版) """
        offset = 50 # 阴影扩散范围
        shadow_size = radius * 2 + offset * 2
        surf = pygame.Surface((shadow_size, shadow_size), pygame.SRCALPHA)
        center = shadow_size // 2
        
        # 阴影带宽度
        shadow_width = 40
        # 从半径往外画一圈圈的半透明黑
        for r in range(radius, radius + shadow_width):
            # Alpha 从 160 (很深) 衰减到 0
            progress = (r - radius) / shadow_width
            alpha = int(160 * (1 - progress))
            pygame.draw.circle(surf, (0, 0, 0, alpha), (center, center), r)
        return surf

    def draw_convex_lighting(self, surf, radius):
        """ 在天盘表面绘制球体光照效果 (模拟漆器强反光) """
        # 光源在左上
        light_offset_x = -radius * 0.25
        light_offset_y = -radius * 0.25
        max_r = radius * 0.95
        steps = 60 
        
        # 1. 漫反射 (Diffuse) - 让中间鼓起来
        for i in range(steps):
            current_r = max_r * (1 - i/steps)
            # Alpha 提升到 80，肉眼可见的凸起
            alpha = int(5 + i * 1.3) 
            if alpha > 255: alpha = 255
            
            # 暖黄色高光，配合黑底
            highlight_color = (255, 250, 220, alpha)
            
            # 非线性偏移，让光斑聚拢
            shift_factor = math.pow(i / steps, 0.8)
            draw_pos = (radius + light_offset_x * shift_factor, radius + light_offset_y * shift_factor)
            
            pygame.draw.circle(surf, highlight_color, (int(draw_pos[0]), int(draw_pos[1])), int(current_r))

        # 2. 镜面高光 (Specular) - 漆器的灵魂
        spec_surf = pygame.Surface((radius, radius), pygame.SRCALPHA)
        # 画一个亮白的椭圆
        pygame.draw.ellipse(spec_surf, (255, 255, 255, 120), (0, 0, 100, 60))
        # 边缘模糊
        pygame.draw.ellipse(spec_surf, (255, 255, 255, 60), (-10, -10, 120, 80), 10)
        
        spec_surf = pygame.transform.rotate(spec_surf, 45)
        # 叠加
        surf.blit(spec_surf, (radius*0.15, radius*0.15), special_flags=pygame.BLEND_ADD)

    # --- 辅助绘图 ---

    def draw_rotated_text(self, surf, text, font, color, center, angle_deg):
        txt_surf = font.render(text, True, color)
        rotated_txt = pygame.transform.rotate(txt_surf, angle_deg)
        rect = rotated_txt.get_rect(center=center)
        surf.blit(rotated_txt, rect)

    def get_mouse_angle(self, pos):
        dx = pos[0] - self.center[0]
        dy = pos[1] - self.center[1]
        return math.degrees(math.atan2(dy, dx))

    # --- 核心绘制逻辑 ---

    def create_earth_plate(self, size, inner_dia):
        """ 绘制方形地盘 """
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        rect = pygame.Rect(0, 0, size, size)
        pygame.draw.rect(surf, COLOR_EARTH_BG, rect, border_radius=10)

        m_xiu = 35; m_mid = 120
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

        # 外圈星宿 (调用 config.py 中的数据)
        def draw_side_xiu(char_list, side):
            step = size / 8
            for i, char in enumerate(char_list):
                angle = [180, 90, 0, -90][side]
                margin = 18
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
        corner_offset = m_mid + 30
        corners_data = [('巽',(corner_offset, corner_offset)), ('坤',(size-corner_offset, corner_offset)),
                        ('乾',(size-corner_offset, size-corner_offset)), ('艮',(corner_offset, size-corner_offset))]
        for char, pos in corners_data:
            dx, dy = pos[0] - mid, pos[1] - mid
            angle = math.degrees(math.atan2(dy, dx)) + 90
            self.draw_rotated_text(surf, char, self.font_l, COLOR_TEXT_DIM, pos, -angle)

        return surf

    def create_heaven_plate(self, diameter):
        """ 绘制圆形天盘：光影加强版 + 终极修正北斗(指向太冲/天罡) """
        surf = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        radius = diameter // 2
        mid = radius
        
        # 1. 底座
        pygame.draw.circle(surf, COLOR_HEAVEN_BG, (mid, mid), radius)
        
        # --- ✨应用加强版光照 ---
        self.draw_convex_lighting(surf, radius)
        # --------------------

        # 2. 结构线
        pygame.draw.circle(surf, COLOR_DECO, (mid, mid), radius, 4)
        pygame.draw.circle(surf, COLOR_DECO, (mid, mid), radius * 0.68, 2)
        
        # 3. 边缘倒角
        rect = pygame.Rect(2, 2, diameter-4, diameter-4)
        pygame.draw.arc(surf, (180, 160, 120), rect, math.pi/2, math.pi, 2) 

        # ================== 终极修正：北斗七星 (Correct Alignment) ==================
        # 修正1：斗柄(Handle)应指向左方 (太冲/天罡方向，West on plate/Left on screen)
        # 修正2：去掉多余连线 (closed=False)
        # 修正3：第四星(天权)居中
        
        star_coords = [
            # --- 斗柄 (Handle) - 指向左/左上 (Taichong/Tiangang) ---
            (-100, -25), # 7. 摇光 (Tip) - Points Left/Up
            (-70, -15),  # 6. 开阳
            (-35, -10),  # 5. 玉衡
            
            # --- 中心枢轴 ---
            (0, 0),      # 4. 天权 (Center)
            
            # --- 勺体 (Bowl) - 位于右侧 (Congkui area) ---
            (20, 25),    # 3. 天玑 (Bottom-Inner)
            (55, 10),    # 2. 天璇 (Bottom)
            (50, -35)    # 1. 天枢 (Top)
        ]
        
        screen_points = [(mid + x, mid + y) for x, y in star_coords]
        
        line_color = (180, 60, 60)
        line_width = 3
        
        # 分两段绘制，确保中间断开或样式正确 (这里我们连在一起，但用 open line)
        # 也可以为了美观分段画
        
        # 绘制斗柄 (Handle -> Center): 0->1->2->3
        handle_pts = screen_points[0:4]
        pygame.draw.lines(surf, line_color, False, handle_pts, line_width)
        
        # 绘制勺体 (Center -> Bowl): 3->4->5->6
        # 注意：这里我们不需要闭合 6->3，只画折线，完美复刻复原图
        bowl_pts = screen_points[3:]
        pygame.draw.lines(surf, line_color, False, bowl_pts, line_width)

        # 绘制星点
        for i, pt in enumerate(screen_points):
            # i=3 是中心天权星，画空心金环
            if i == 3:
                pygame.draw.circle(surf, COLOR_NODE, pt, 8, 2) # 环
                pygame.draw.circle(surf, (200, 50, 50), pt, 2) # 极小芯
            else:
                pygame.draw.circle(surf, COLOR_NODE, pt, 5)
                pygame.draw.circle(surf, (200, 50, 50), pt, 2)
        # ================== 修正结束 ==================

        # 5. 内圈：十二月将
        r_gen = radius * 0.52
        for i, gen_name in enumerate(MOON_GENERALS):
            angle_deg = 90 + i * 30
            rad = math.radians(angle_deg)
            x = mid + r_gen * math.cos(rad)
            y = mid + r_gen * math.sin(rad)
            self.draw_rotated_text(surf, gen_name, self.font_m, COLOR_TEXT, (x, y), -angle_deg - 90)

        # 6. 外圈：二十八宿
        r_xiu = radius * 0.88
        step_angle = 360 / 28
        for i, char in enumerate(ORDERED_XIU_R):
            angle_deg = 90 + i * step_angle
            rad = math.radians(angle_deg)
            x = mid + r_xiu * math.cos(rad)
            y = mid + r_xiu * math.sin(rad)
            self.draw_rotated_text(surf, char, self.font_s, COLOR_TEXT_DIM, (x, y), -angle_deg - 90)

        return surf

    def align_to_now(self):
        """ 修复：绝对坐标对齐 """
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
            # --- 1. 事件 ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        dist = math.hypot(event.pos[0]-self.center[0], event.pos[1]-self.center[1])
                        if dist < self.heaven_diameter / 2:
                            self.dragging = True
                            self.velocity = 0
                            self.target_angle = None
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1: self.dragging = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE: self.align_to_now()

            # --- 2. 物理 ---
            if self.dragging:
                mouse_pos = pygame.mouse.get_pos()
                current_mouse_angle = self.get_mouse_angle(mouse_pos)
                if self.last_mouse_pos != (0,0):
                    last = self.get_mouse_angle(self.last_mouse_pos)
                    delta = current_mouse_angle - last
                    if delta > 180: delta -= 360
                    if delta < -180: delta += 360
                    self.angle += delta # 顺时针跟随
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
                    if abs(self.velocity) < 0.01: self.velocity = 0

            # --- 3. 渲染 ---
            self.screen.fill(COLOR_BG)

            # A. 地盘
            earth_rect = self.earth_surf.get_rect(center=self.center)
            self.screen.blit(self.earth_surf, earth_rect)

            # B. 阴影 (天盘下方，偏移加大到 15px)
            shadow_rect = self.shadow_surf.get_rect(center=(self.center[0] + 15, self.center[1] + 15))
            self.screen.blit(self.shadow_surf, shadow_rect)

            # C. 天盘 (顺时针旋转视觉，用 -angle)
            rotated_heaven = pygame.transform.rotate(self.heaven_surf, -self.angle)
            heaven_rect = rotated_heaven.get_rect(center=self.center)
            self.screen.blit(rotated_heaven, heaven_rect)

            # D. HUD
            now = datetime.datetime.now()
            info_text = f"DATE: {now.strftime('%Y-%m-%d %H:%M')} | SPACE: Auto Align"
            hud = self.hud_font.render(info_text, True, COLOR_TEXT_DIM)
            self.screen.blit(hud, (20, WINDOW_SIZE[1] - 40))

            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = CyberLiuren()
    app.run()