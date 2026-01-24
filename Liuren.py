import pygame
import math
import sys

# --- 🎨 赛博漆器配色 (Vibe Palette) ---
COLOR_BG = (20, 20, 24)        # 深空灰背景
COLOR_EARTH_BG = (60, 10, 10)  # 漆器红（朱砂）
COLOR_HEAVEN_BG = (10, 10, 10) # 玄黑（天盘）
COLOR_TEXT = (220, 180, 50)    # 流金（文字）
COLOR_GRID = (100, 30, 30)     # 暗红（边框线）

WINDOW_SIZE = (800, 800)
FPS = 60

# 十二地支 (用于显示)
EARTHLY_BRANCHES = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# --- 新增配置：月将神名 (对应 子, 丑, 寅... 亥) ---
# 注意：列表顺序必须对应 子 -> 亥
MOON_GENERALS = [
    '神后', '大吉', '功曹', '太冲', '天罡', '太乙', 
    '胜光', '小吉', '传送', '从魁', '河魁', '登明'
]

# --- 新增数据：二十八星宿 (按方位分组) ---
# 顺序：上(南), 右(西), 下(北), 左(东) -> 顺时针排列
# 注意：古代排盘有时是逆时针，但为了视觉对齐，我们按屏幕坐标系逻辑来
# 1. 南方 (上边 Top): 从左(东) -> 右(西) 绘制
# 顺序：轸 -> 井 (为了让左边的'轸'衔接左侧的'角'，右边的'井'衔接右侧的'参')
XIU_SOUTH = ['轸', '翼', '张', '星', '柳', '鬼', '井'] 

# 2. 西方 (右边 Right): 从上(南) -> 下(北) 绘制
# 顺序：参 -> 奎 (为了让上边的'参'衔接上侧的'井'，下边的'奎'衔接底部的'壁')
XIU_WEST = ['参', '觜', '毕', '昴', '胃', '娄', '奎']

# 3. 北方 (下边 Bottom): 从左(东) -> 右(西) 绘制
# 顺序：斗 -> 壁 (为了让左边的'斗'衔接左侧的'箕')
XIU_NORTH = ['斗', '牛', '女', '虚', '危', '室', '壁']

# 4. 东方 (左边 Left): 从上(南) -> 下(北) 绘制
# 顺序：角 -> 箕 (为了让上边的'角'衔接顶部的'轸')
XIU_EAST = ['角', '亢', '氐', '房', '心', '尾', '箕']

class CyberLiuren:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(WINDOW_SIZE)
        pygame.display.set_caption("赛博六壬 Cyber-Liuren v0.2")
        self.clock = pygame.time.Clock()

        # --- 字体设置 ---
        # 尝试加载系统中的中文字体 (Windows通常有SimHei, Mac有PingFang)
        self.font_size = 32
        try:
            # Windows 优先尝试黑体
            self.font = pygame.font.SysFont("simhei", self.font_size, bold=True)
        except:
            # 如果失败，回退到默认（中文会显示乱码，需要你自己指定字体路径）
            self.font = pygame.font.Font(None, self.font_size)

        # --- 生成盘面素材 ---
        self.center = (WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2)
        
        # 1. 生成地盘 (静止的方形)
        self.earth_surf = self.create_earth_plate(600)
        
        # 2. 生成天盘 (旋转的圆形)
        self.heaven_surf = self.create_heaven_plate(320)

        # 状态变量
        self.angle = 0
        self.target_angle = 0
        self.dragging = False

    def create_earth_plate(self, size):
        """ 绘制方形地盘：增加二十八星宿外圈 """
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # 1. 绘制底座 (朱红漆器质感)
        rect = pygame.Rect(0, 0, size, size)
        pygame.draw.rect(surf, COLOR_EARTH_BG, rect, border_radius=15)
        pygame.draw.rect(surf, COLOR_GRID, rect, 3, border_radius=15) # 外框金边
        
        # 内部再画一个框，区分 星宿层 和 地支层
        inner_margin = 60
        inner_rect = pygame.Rect(inner_margin, inner_margin, size-inner_margin*2, size-inner_margin*2)
        pygame.draw.rect(surf, COLOR_GRID, inner_rect, 2, border_radius=10)

        # 2. 绘制二十八星宿 (最外圈)
        # 我们使用较小的字体，因为字多
        xiu_font = pygame.font.SysFont("simhei", 20, bold=True)
        
        def draw_side_text(char_list, side):
            """ 辅助函数：绘制带旋转的边框文字 """
            step = size / 8
            for i, char in enumerate(char_list):
                # 1. 确定位置和基础角度
                if side == 0:   # 上 (南)
                    x, y = step * (i + 1), 30
                    angle = 180 # 字头朝下(朝圆心)
                elif side == 1: # 右 (西)
                    x, y = size - 30, step * (i + 1)
                    angle = 90  # 字头朝左(朝圆心)
                elif side == 2: # 下 (北)
                    x, y = step * (i + 1), size - 30
                    angle = 0   # 字头朝上(朝圆心)
                elif side == 3: # 左 (东)
                    x, y = 30, step * (i + 1)
                    angle = -90 # 字头朝右(朝圆心)
                
                # 2. 渲染并旋转
                text = xiu_font.render(char, True, (160, 140, 120)) # 暗金
                rotated_text = pygame.transform.rotate(text, angle)
                text_rect = rotated_text.get_rect(center=(x, y))
                surf.blit(rotated_text, text_rect)

        # 绘制四边
        draw_side_text(XIU_SOUTH, 0) # 上
        draw_side_text(XIU_WEST, 1)  # 右
        draw_side_text(XIU_NORTH, 2) # 下
        draw_side_text(XIU_EAST, 3)  # 左

        # 3. 绘制十二地支 (内圈) - 之前的逻辑稍微调整位置
        # 映射字典 {地支: (x_ratio, y_ratio)}
        # 因为加了星宿，地支要往里缩一点
        positions = {
            '巳': (0.32, 0.18), '午': (0.5, 0.18), '未': (0.68, 0.18), # 上
            '申': (0.82, 0.32), '酉': (0.82, 0.5), '戌': (0.82, 0.68), # 右
            '亥': (0.68, 0.82), '子': (0.5, 0.82), '丑': (0.32, 0.82), # 下
            '寅': (0.18, 0.68), '卯': (0.18, 0.5), '辰': (0.18, 0.32)  # 左
        }

        for char, (rx, ry) in positions.items():
            # 地支字体大一点，亮一点
            text = self.font.render(char, True, COLOR_TEXT)
            text_rect = text.get_rect(center=(size * rx, size * ry))
            surf.blit(text, text_rect)
            
            # 格子框
            box_size = 45
            pygame.draw.rect(surf, COLOR_GRID, 
                           (size*rx - box_size/2, size*ry - box_size/2, box_size, box_size), 1)

        # 4. 补充四角文字 (严格对应六壬方位：上南下北，左东右西)
        # 修正逻辑：
        # 右下(NW) = 天门 (戌亥)
        # 左上(SE) = 地户 (辰巳)
        # 右上(SW) = 人门 (未申)
        # 左下(NE) = 鬼门 (丑寅)
        
        corners = {
            '天': (0.88, 0.88), # 右下 (西北)
            '地': (0.12, 0.12), # 左上 (东南)
            '人': (0.88, 0.12), # 右上 (西南)
            '鬼': (0.12, 0.88)  # 左下 (东北)
        }
        
        for char, (rx, ry) in corners.items():
            # 用一种篆刻风格的暗红色，或者深灰色
            text = self.font.render(char, True, (80, 40, 40)) 
            surf.blit(text, text.get_rect(center=(size*rx, size*ry)))
        for char, (rx, ry) in corners.items():
            text = self.font.render(char, True, (100, 50, 50)) # 暗色装饰
            surf.blit(text, text.get_rect(center=(size*rx, size*ry)))

        return surf

    def create_heaven_plate(self, diameter):
        """ 绘制圆形天盘：使用月将神名 """
        surf = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        radius = diameter // 2
        
        # 绘制圆盘 (玄黑底色)
        pygame.draw.circle(surf, COLOR_HEAVEN_BG, (radius, radius), radius)
        pygame.draw.circle(surf, COLOR_TEXT, (radius, radius), radius, 2) # 金圈

        # --- 🔧 新增：定义天盘专属小字体 ---
        # 原来是 self.font (32号)，这里改成 22号 或 20号
        # 如果你觉得还是大，就继续把 22 改小
        heaven_font = pygame.font.SysFont("simhei", 22, bold=True)
        
        # 绘制北斗七星意象 (这次我们画稍微像一点)
        # 简单的北斗七星连线坐标 (示意)
        star_points = [
            (0, -50), (20, -30), (40, -40), (60, -20), # 斗身
            (80, 0), (100, 20), (120, 60)              # 斗柄
        ]
        # 将坐标平移到圆心
        adjusted_points = [(x + radius - 60, y + radius) for x, y in star_points]
        pygame.draw.lines(surf, (160, 40, 40), False, adjusted_points, 4) # 线条宽度设为 4
        for pt in adjusted_points:
            pygame.draw.circle(surf, (220, 180, 50), pt, 5) # 星星点大一点

        for i, name in enumerate(MOON_GENERALS):
            angle_deg = i * 30 + 90 
            angle_rad = math.radians(angle_deg)
            
            # 半径微调：因为字变小了，可以稍微离圆心远一丢丢，或者保持不变
            dist = radius * 0.80 
            x = radius + dist * math.cos(angle_rad)
            y = radius + dist * math.sin(angle_rad)
            
            # --- 🔧 修改：使用 heaven_font 渲染 ---
            text = heaven_font.render(name, True, COLOR_TEXT)
            
            # 旋转文字
            rotated_text = pygame.transform.rotate(text, -angle_deg - 90)
            
            text_rect = rotated_text.get_rect(center=(x, y))
            surf.blit(rotated_text, text_rect)

        return surf

    def get_angle_from_mouse(self):
        mx, my = pygame.mouse.get_pos()
        dx = mx - self.center[0]
        dy = my - self.center[1]
        return math.degrees(math.atan2(-dy, dx)) - 90

    def run(self):
        running = True
        last_mouse_angle = 0
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    if math.hypot(mx - self.center[0], my - self.center[1]) < 210:
                        self.dragging = True
                        last_mouse_angle = self.get_angle_from_mouse()
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.dragging = False
                    # 磁吸逻辑 (1格=30度)
                    self.target_angle = round(self.angle / 30) * 30
            
            if self.dragging:
                curr = self.get_angle_from_mouse()
                self.angle += (curr - last_mouse_angle)
                self.target_angle = self.angle
                last_mouse_angle = curr
            else:
                # 阻尼回弹
                self.angle += (self.target_angle - self.angle) * 0.15

            # 渲染
            self.screen.fill(COLOR_BG)
            
            # 绘制地盘 (不动)
            earth_rect = self.earth_surf.get_rect(center=self.center)
            self.screen.blit(self.earth_surf, earth_rect)
            
            # 绘制天盘 (旋转)
            rotated_heaven = pygame.transform.rotate(self.heaven_surf, self.angle)
            heaven_rect = rotated_heaven.get_rect(center=self.center)
            self.screen.blit(rotated_heaven, heaven_rect)

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    app = CyberLiuren()
    app.run()