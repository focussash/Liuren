import pygame
import math
import sys
import datetime

# --- 🎨 赛博漆器配色 (Vibe Palette) ---
COLOR_BG = (20, 20, 24)         # 深空灰背景
COLOR_EARTH_BG = (50, 15, 15)   # 深朱红漆底
COLOR_HEAVEN_BG = (10, 10, 12)  # 玄黑天盘底
COLOR_TEXT = (220, 190, 100)    # 流金（文字主色）
COLOR_TEXT_DIM = (160, 130, 80) # 暗金（次要文字）
COLOR_STEM = (200, 80, 80)      # 赤金（天干/特殊标识）
COLOR_DECO = (140, 110, 60)     # 青铜/暗金（结构线）
COLOR_NODE = (180, 150, 90)     # 亮金（节点/铆钉）
COLOR_HIGHLIGHT = (255, 255, 200) # 高亮色

WINDOW_SIZE = (900, 900)
FPS = 60

# --- 数据常量 ---
# 二十八宿 (按方位，顺序调整为顺时针连续)
XIU_S = ['轸', '翼', '张', '星', '柳', '鬼', '井'] # 南(上) 左->右
XIU_W = ['参', '觜', '毕', '昴', '胃', '娄', '奎'] # 西(右) 上->下
XIU_N = ['壁', '室', '危', '虚', '女', '牛', '斗'] # 北(下) 右->左
XIU_E = ['箕', '尾', '心', '房', '氐', '亢', '角'] # 东(左) 下->上
# 合并为一个完整列表用于天盘 (逆时针排布在天盘上，或顺时针，视具体流派，此处参考图示为顺时针)
XIU_ALL = XIU_E[::-1] + XIU_S + XIU_W + XIU_N[::-1] 

ORDERED_XIU_R = [
    '虚', '女', '牛', '斗', '箕', '尾', '心', '房', '氐', '亢', '角', '轸', '翼', '张', 
    '星', '柳', '鬼', '井', '参', '觜', '毕', '昴', '胃', '娄', '奎', '壁', '室', '危'
]

# --- 🛠️ 修正后的数据结构：分野对应表 ---
# 格式：{ 月将(地支): [管辖的星宿列表] }
# 依据：淮南子/六壬式盘经典分野
# 注意：列表顺序需要符合圆周上的逆时针/顺时针排布，这里依据图片视觉调整
GEN_TO_XIU_MAP = {
    '神后': ['女', '虚', '危'],      # 子
    '大吉': ['斗', '牛'],            # 丑
    '功曹': ['尾', '箕'],            # 寅
    '太冲': ['氐', '房', '心'],      # 卯
    '天罡': ['角', '亢'],            # 辰
    '太乙': ['翼', '轸'],            # 巳
    '胜光': ['柳', '星', '张'],      # 午
    '小吉': ['井', '鬼'],            # 未
    '传送': ['觜', '参'],            # 申
    '从魁': ['胃', '昴', '毕'],      # 酉
    '河魁': ['奎', '娄'],            # 戌
    '登明': ['室', '壁']             # 亥
}

# 十二月将神名 (子->亥) 
# 注意：在六壬中，神后(子)对应正北，但在天盘上随月将移动
MOON_GENERALS = ['神后', '大吉', '功曹', '太冲', '天罡', '太乙', '胜光', '小吉', '传送', '从魁', '河魁', '登明']# 十二地支 (方位：子在北/下，午在南/上)
EARTHLY_BRANCHES = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
# 天干
HEAVENLY_STEMS = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']

# 节气映射 (简化版：月份 -> 月将索引)
# 实际上月将是太阳过宫，中气换将。这里做简化处理：
# 1月(丑月-大吉), 2月(寅月-功曹)... 实际上月将 = 合流月建 (正月建寅, 月将为亥-登明)
# 简单对照表 (大致)：
# 正月(寅)-亥将(登明), 二月(卯)-戌将(河魁), ...
# 索引 11, 10, ...
SOLAR_TERMS_MAP = {
    1: 11, 2: 10, 3: 9, 4: 8, 5: 7, 6: 6, 
    7: 5, 8: 4, 9: 3, 10: 2, 11: 1, 12: 0
}

# --- 🧠 六壬核心算法 (The Brain) ---

def get_chinese_hour(dt):
    """ 获取当前时辰的地支索引 (0=子, 1=丑...) """
    h = dt.hour
    # 23:00-01:00 是子时
    if h >= 23 or h < 1: return 0
    return (h + 1) // 2

def get_moon_general(dt):
    """ 获取当前月将索引 (简化版：基于月份) """
    # 真正的排盘需要查万年历看是否过了中气，这里用月份粗略模拟
    # 假设当前是农历/节气月大致对应公历
    # 比如 1月(小寒-大寒) -> 丑月 -> 月将为子(神后, idx 0)
    # 这里使用一个简单的月份偏移，实际应用建议接入万年历库
    m = dt.month
    # 修正映射：1月->子将(0), 2月->亥将(11)... 这是一个循环偏移
    # 简单写一个偏移量让它动起来即可
    idx = (13 - m) % 12 
    return idx

# --- 🖥️ 渲染引擎 ---

class CyberLiuren:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("赛博大六壬 - 汝阴侯漆器复原版 [按空格自动归位]")
        self.clock = pygame.time.Clock()

        # --- 字体加载 (带回退) ---
        self.font_size_l = 28
        self.font_size_m = 22
        self.font_size_s = 18
        
        # 尝试加载中文字体列表
        font_names = ["simhei", "microsoftyahei", "pingfangsc", "notosanscjksc", "simsun"]
        self.font_l = self.font_m = self.font_s = None
        
        for name in font_names:
            try:
                self.font_l = pygame.font.SysFont(name, self.font_size_l, bold=True)
                self.font_m = pygame.font.SysFont(name, self.font_size_m, bold=True)
                self.font_s = pygame.font.SysFont(name, self.font_size_s, bold=True)
                self.hud_font = pygame.font.SysFont(name, 20)
                print(f"Loaded font: {name}")
                break
            except:
                continue
        
        if not self.font_l:
            print("Warning: No Chinese font found. Text may handle incorrectly.")
            self.font_l = pygame.font.Font(None, 24)

        # --- 尺寸参数 ---
        self.center = (WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2)
        self.earth_size = 760
        self.heaven_diameter = 460
        
        # 预渲染盘面 (静态纹理)
        self.earth_surf = self.create_earth_plate(self.earth_size, self.heaven_diameter)
        self.heaven_surf = self.create_heaven_plate(self.heaven_diameter)

        # --- 物理与状态 ---
        self.angle = 0.0          # 当前天盘角度
        self.velocity = 0.0       # 角速度
        self.dragging = False     # 是否正在拖拽
        self.last_mouse_pos = (0, 0)
        self.friction = 0.95      # 阻尼系数 (漆器手感)
        
        # 自动排盘目标
        self.target_angle = None
        self.animation_speed = 0.2

    def get_mouse_angle(self, pos):
        """ 计算鼠标相对于中心的角度 (degrees) """
        dx = pos[0] - self.center[0]
        dy = pos[1] - self.center[1]
        return math.degrees(math.atan2(dy, dx))

    def align_to_now(self):
        """ 核心功能：月将加时 (天盘月将 指向 地盘时辰) """
        now = datetime.datetime.now()
        hour_idx = get_chinese_hour(now)      # 地盘时辰位置 (0=子=下)
        general_idx = get_moon_general(now)   # 当前月将索引
        
        print(f"Time: {now.hour}点 (地支{EARTHLY_BRANCHES[hour_idx]})")
        print(f"General: {MOON_GENERALS[general_idx]}")

        # 计算目标角度
        # 1. 地盘 '子' 在正下方 (90度 / 270度视坐标系而定)
        #    根据 draw_row 逻辑，地盘的'子'是在下边框中间。
        #    在Pygame屏幕坐标中，正下是 90度 (假设0度是正右)，或者 270度。
        #    让我们看 create_earth_plate 的排布：
        #    draw_row(['丑','癸','子','壬','亥']...) -> 子在下方正中。
        
        # 2. 天盘 '月将' 在哪里？
        #    create_heaven_plate 中，MOON_GENERALS[0] (神后/子) 画在 90度 (正下)。
        #    所以初始状态下，天盘的子(神后) 对准 地盘的子。
        
        # 3. 目标：要把 general_idx (月将) 对准 hour_idx (时辰)。
        #    地盘时辰位置角度：
        #    子(0): 90度 (下)
        #    丑(1): 60度 (右下) ... (逆时针排布)
        #    公式：target_pos_angle = 90 - hour_idx * 30
        
        #    天盘月将初始角度：
        #    gen(0): 90度
        #    gen(1): 60度 ...
        #    公式：current_gen_angle = 90 - general_idx * 30
        
        #    我们需要旋转天盘 R 度，使得：
        #    current_gen_angle + R = target_pos_angle
        #    R = target_pos_angle - current_gen_angle
        #      = (90 - h*30) - (90 - g*30)
        #      = (g - h) * 30
        
        diff = (general_idx - hour_idx) * 30
        self.target_angle = diff 
        # 处理一下旋转圈数，走最短路径
        current_mod = self.angle % 360
        target_mod = self.target_angle % 360
        delta = target_mod - current_mod
        if delta > 180: delta -= 360
        if delta < -180: delta += 360
        self.target_angle = self.angle + delta

    def draw_rotated_text(self, surf, text, font, color, center, angle_deg):
        txt_surf = font.render(text, True, color)
        rotated_txt = pygame.transform.rotate(txt_surf, angle_deg)
        rect = rotated_txt.get_rect(center=center)
        surf.blit(rotated_txt, rect)

    def create_earth_plate(self, size, inner_dia):
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # 1. 底色
        rect = pygame.Rect(0, 0, size, size)
        pygame.draw.rect(surf, COLOR_EARTH_BG, rect, border_radius=10)

        # 关键尺寸
        m_xiu = 35; m_mid = 120
        r_inner = inner_dia // 2 + 5
        mid = size // 2

        # 2. 结构线
        lw = 4
        pygame.draw.rect(surf, COLOR_DECO, (m_xiu, m_xiu, size-m_xiu*2, size-m_xiu*2), lw, border_radius=5)
        pygame.draw.rect(surf, COLOR_DECO, (m_mid, m_mid, size-m_mid*2, size-m_mid*2), lw, border_radius=5)
        pygame.draw.circle(surf, COLOR_DECO, (mid, mid), r_inner, lw)
        
        # 连线 (中框角 -> 内圆)
        corners_mid = [(m_mid, m_mid), (size-m_mid, m_mid), (size-m_mid, size-m_mid), (m_mid, size-m_mid)]
        angles = [225, 315, 45, 135] 
        for i, ang in enumerate(angles):
            rad = math.radians(ang)
            end_pt = (mid + r_inner*math.cos(rad), mid + r_inner*math.sin(rad))
            pygame.draw.line(surf, COLOR_DECO, corners_mid[i], end_pt, lw)

        # 节点
        node_r = 14
        nodes = corners_mid + [(mid, m_mid), (size-m_mid, mid), (mid, size-m_mid), (m_mid, mid)]
        for pt in nodes:
            pygame.draw.circle(surf, COLOR_EARTH_BG, pt, node_r)
            pygame.draw.circle(surf, COLOR_NODE, pt, node_r, 2)
            pygame.draw.circle(surf, COLOR_NODE, pt, 4)

        # 3. 文字 - 外圈二十八宿
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

        # 4. 文字 - 中层干支 (地盘核心)
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

        # 5. 文字 - 四隅卦
        corner_offset = m_mid + 30
        corners_data = [('巽',(corner_offset, corner_offset)), ('坤',(size-corner_offset, corner_offset)),
                        ('乾',(size-corner_offset, size-corner_offset)), ('艮',(corner_offset, size-corner_offset))]
        for char, pos in corners_data:
            dx, dy = pos[0] - mid, pos[1] - mid
            angle = math.degrees(math.atan2(dy, dx)) + 90
            self.draw_rotated_text(surf, char, self.font_l, COLOR_TEXT_DIM, pos, -angle)

        # 修正：地盘不需要绘制内圈神名，那是天盘的事
        return surf

    def create_heaven_plate(self, diameter):
        """ 绘制圆形天盘：神将顺行，星宿逆行，完美对齐文物 """
        surf = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        radius = diameter // 2
        mid = radius
        
        # 1. 基础结构
        pygame.draw.circle(surf, COLOR_HEAVEN_BG, (mid, mid), radius)
        pygame.draw.circle(surf, COLOR_DECO, (mid, mid), radius, 3)
        pygame.draw.circle(surf, COLOR_DECO, (mid, mid), radius * 0.68, 2)

        # 2. 北斗七星 (保持修正后的勺子形状)
        scale = 0.8
        star_coords = [
            (20, -30), (20, 10), (-15, 15), (-15, -25), 
            (-45, -35), (-70, -25), (-100, -50)
        ]
        screen_points = []
        for x, y in star_coords:
            # 旋转一点让它横置，更好看
            rx = x * math.cos(0.2) - y * math.sin(0.2)
            ry = x * math.sin(0.2) + y * math.cos(0.2)
            screen_points.append((mid + rx * scale + 20, mid + ry * scale))

        if len(screen_points) >= 2:
            pygame.draw.lines(surf, (160, 60, 60), False, screen_points, 3)
        pygame.draw.line(surf, (160, 60, 60), screen_points[0], screen_points[1], 3)
        pygame.draw.line(surf, (160, 60, 60), screen_points[1], screen_points[2], 3)
        for pt in screen_points:
            pygame.draw.circle(surf, COLOR_NODE, pt, 5)
            pygame.draw.circle(surf, (255, 255, 200), pt, 2)

        # 3. 绘制内圈：十二月将 (顺时针)
        # 参考图：神后在下，往左(顺时针)是大吉
        r_gen = radius * 0.52
        for i, gen_name in enumerate(MOON_GENERALS):
            # 角度：90(下) -> 120(左下) -> 150... (Pygame坐标系中增加角度=顺时针/左移)
            # 公式：90 + i * 30
            angle_deg = 90 + i * 30
            
            rad = math.radians(angle_deg)
            x = mid + r_gen * math.cos(rad)
            y = mid + r_gen * math.sin(rad)
            
            # 文字旋转：字头朝内
            self.draw_rotated_text(surf, gen_name, self.font_m, COLOR_TEXT, (x, y), -angle_deg - 90)

        # 4. 绘制外圈：二十八宿 (顺时针排布逆序列表)
        # 参考图：底部正中是"虚"，往左(顺时针)是"女"
        # 我们的 ORDERED_XIU_R 列表就是 ['虚', '女'...]
        # 所以也是顺时针绘制即可
        r_xiu = radius * 0.88
        step_angle = 360 / 28
        
        for i, char in enumerate(ORDERED_XIU_R):
            # 虚(i=0) 在正下(90度)
            # 女(i=1) 在左边(90 + step)
            angle_deg = 90 + i * step_angle
            
            rad = math.radians(angle_deg)
            x = mid + r_xiu * math.cos(rad)
            y = mid + r_xiu * math.sin(rad)
            
            self.draw_rotated_text(surf, char, self.font_s, COLOR_TEXT_DIM, (x, y), -angle_deg - 90)

        return surf

    def run(self):
        running = True
        while running:
            # --- 1. 事件处理 ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        # 检查是否点中天盘区域
                        dist = math.hypot(event.pos[0]-self.center[0], event.pos[1]-self.center[1])
                        if dist < self.heaven_diameter / 2:
                            self.dragging = True
                            self.velocity = 0 # 拖拽时清除惯性
                            self.target_angle = None # 打断自动旋转
                
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.dragging = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.align_to_now()

            # --- 2. 物理逻辑 ---
            if self.dragging:
                mouse_pos = pygame.mouse.get_pos()
                current_mouse_angle = self.get_mouse_angle(mouse_pos)
                if self.last_mouse_pos != (0,0):
                    last_mouse_angle = self.get_mouse_angle(self.last_mouse_pos)
                    # 处理跨越 180/-180 度的情况
                    delta = current_mouse_angle - last_mouse_angle
                    if delta > 180: delta -= 360
                    if delta < -180: delta += 360
                    self.angle -= delta # 逆向跟随
                    self.velocity = -delta # 记录速度用于惯性
                self.last_mouse_pos = mouse_pos
            else:
                self.last_mouse_pos = (0,0)
                
                # 自动归位逻辑
                if self.target_angle is not None:
                    diff = self.target_angle - self.angle
                    if abs(diff) < 0.1:
                        self.angle = self.target_angle
                        self.target_angle = None
                        self.velocity = 0
                    else:
                        self.angle += diff * self.animation_speed
                else:
                    # 惯性阻尼
                    self.angle += self.velocity
                    self.velocity *= self.friction
                    if abs(self.velocity) < 0.01: self.velocity = 0

            # --- 3. 渲染绘制 ---
            self.screen.fill(COLOR_BG)

            # A. 绘制地盘 (不动)
            earth_rect = self.earth_surf.get_rect(center=self.center)
            self.screen.blit(self.earth_surf, earth_rect)

            # B. 绘制天盘 (旋转)
            # Pygame旋转是逆时针为正，但我们需要符合直觉
            rotated_heaven = pygame.transform.rotate(self.heaven_surf, self.angle)
            heaven_rect = rotated_heaven.get_rect(center=self.center)
            self.screen.blit(rotated_heaven, heaven_rect)

            # C. HUD 信息
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