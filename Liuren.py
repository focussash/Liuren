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
        self.heaven_surf = self.create_heaven_plate(420)

        # 状态变量
        self.angle = 0
        self.target_angle = 0
        self.dragging = False

    def create_earth_plate(self, size):
        """ 绘制方形地盘：十二地支分布在四周 """
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # 绘制底座 (朱红漆器质感)
        rect = pygame.Rect(0, 0, size, size)
        pygame.draw.rect(surf, COLOR_EARTH_BG, rect, border_radius=10)
        pygame.draw.rect(surf, COLOR_GRID, rect, 3, border_radius=10) # 金边

        # 地盘排布逻辑 (注意：六壬地盘通常是 上南下北，即'午'在最上，'子'在最下)
        # 我们定义一下每个位置的坐标比例 (x_ratio, y_ratio)
        # 顺序：子(下), 丑(下偏左)... 这是一个逆时针还是顺时针？
        # 标准六壬地盘是固定的：
        #   巳 午 未  (南)
        # 辰       申
        # 卯       酉
        # 寅       戌
        #   丑 子 亥  (北)
        
        # 简单的映射字典 {地支: (x_ratio, y_ratio)}
        positions = {
            '巳': (0.3, 0.1), '午': (0.5, 0.1), '未': (0.7, 0.1), # 上
            '申': (0.9, 0.3), '酉': (0.9, 0.5), '戌': (0.9, 0.7), # 右
            '亥': (0.7, 0.9), '子': (0.5, 0.9), '丑': (0.3, 0.9), # 下
            '寅': (0.1, 0.7), '卯': (0.1, 0.5), '辰': (0.1, 0.3)  # 左
        }

        for char, (rx, ry) in positions.items():
            text = self.font.render(char, True, COLOR_TEXT)
            text_rect = text.get_rect(center=(size * rx, size * ry))
            surf.blit(text, text_rect)
            
            # 画个小格子框住它，增加仪式感
            box_size = 50
            pygame.draw.rect(surf, COLOR_GRID, 
                           (size*rx - box_size/2, size*ry - box_size/2, box_size, box_size), 1)

        return surf

    def create_heaven_plate(self, diameter):
        """ 绘制圆形天盘：十二地支呈圆周排列 """
        surf = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        radius = diameter // 2
        
        # 绘制圆盘 (玄黑底色)
        pygame.draw.circle(surf, COLOR_HEAVEN_BG, (radius, radius), radius)
        pygame.draw.circle(surf, COLOR_TEXT, (radius, radius), radius, 2) # 金圈
        
        # 绘制北斗七星意向 (一个简单的勺子，指向 '子' 或者是天盘的起算点)
        # 这里先画个十字线代替，后续我们要画北斗
        pygame.draw.line(surf, (50, 50, 50), (radius, 10), (radius, diameter-10), 1)
        pygame.draw.line(surf, (50, 50, 50), (10, radius), (diameter-10, radius), 1)

        # 绘制十二地支 (圆周排列)
        # 注意：数学上的0度是右边，顺时针增加。
        # 我们希望 '子' 对应 0 度位置吗？通常天盘 '子' 是起始点。
        for i, char in enumerate(EARTHLY_BRANCHES):
            # 将圆分成12份
            # 角度调整：我们要让文字头朝内还是头朝上？这里暂时保持水平
            # 计算坐标
            angle_rad = math.radians(i * 30 - 90) # -90是为了让'子'在最上面(或者根据需要调整)
            
            # 这里的顺序决定了天盘是顺转还是逆转。六壬天盘通常顺布。
            # 如果 i=0是子，放在最下面(270度/90度)? 
            # 让我们把 '子' 放在正北方 (视觉下方，即Pygame的+Y，角度90)
            angle_rad = math.radians(i * 30 + 90) 
            
            x = radius + (radius * 0.75) * math.cos(angle_rad)
            y = radius + (radius * 0.75) * math.sin(angle_rad)
            
            text = self.font.render(char, True, COLOR_TEXT)
            # 旋转文字，让它头朝圆心 (可选，看你喜不喜欢)
            # rotated_text = pygame.transform.rotate(text, - (i * 30 + 90))
            text_rect = text.get_rect(center=(x, y))
            surf.blit(text, text_rect)

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