# ui/highlight.py
# 式盘高亮渲染组件

import pygame
import math
from typing import List, Tuple
from liuren.plate import Lesson, Pass

# 地支列表（用于角度计算）
EARTHLY_BRANCHES = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

# 高亮颜色
COLOR_LESSON_HIGHLIGHT = (255, 200, 100, 120)  # 四课：金黄色
COLOR_PASS_HIGHLIGHT = (100, 200, 255, 150)    # 三传：青蓝色
COLOR_INITIAL_PASS = (255, 100, 100, 180)       # 初传：红色


class PlateHighlighter:
    """式盘高亮渲染器"""

    def __init__(self, center: Tuple[int, int], radius: int):
        """
        初始化高亮器

        Args:
            center: 天盘圆心坐标
            radius: 天盘半径
        """
        self.center = center
        self.radius = radius
        # 月将位置的半径（在天盘内圈）
        self.inner_radius = radius * 0.65

    def get_branch_angle(self, branch: str, angle_offset: float = 0) -> float:
        """
        获取地支对应的角度

        地支从子开始，按顺时针排列
        子在底部（270度或-90度）

        Args:
            branch: 地支
            angle_offset: 天盘旋转偏移量（弧度）

        Returns:
            角度（弧度）
        """
        idx = EARTHLY_BRANCHES.index(branch)
        # 子在底部，每个地支间隔30度
        base_angle = math.radians(-90 + idx * 30)
        return base_angle + angle_offset

    def get_branch_position(self, branch: str, angle_offset: float = 0,
                           radius_ratio: float = 0.65) -> Tuple[int, int]:
        """
        获取地支在屏幕上的位置

        Args:
            branch: 地支
            angle_offset: 天盘旋转偏移量（弧度）
            radius_ratio: 半径比例

        Returns:
            (x, y) 坐标
        """
        angle = self.get_branch_angle(branch, angle_offset)
        r = self.radius * radius_ratio
        x = self.center[0] + r * math.cos(angle)
        y = self.center[1] + r * math.sin(angle)
        return (int(x), int(y))

    def highlight_branch(self, screen: pygame.Surface, branch: str,
                        color: Tuple[int, int, int, int], angle_offset: float = 0,
                        radius_ratio: float = 0.65):
        """
        高亮某个地支位置

        Args:
            screen: pygame屏幕
            branch: 地支
            color: RGBA颜色
            angle_offset: 天盘旋转偏移量
            radius_ratio: 半径比例
        """
        pos = self.get_branch_position(branch, angle_offset, radius_ratio)
        self._draw_glow(screen, pos, color)

    def _draw_glow(self, screen: pygame.Surface, pos: Tuple[int, int],
                   color: Tuple[int, int, int, int], size: int = 25):
        """
        绘制发光效果

        Args:
            screen: pygame屏幕
            pos: 中心位置
            color: RGBA颜色
            size: 发光半径
        """
        # 创建临时surface用于alpha混合
        glow_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)

        # 绘制多层圆形，从外到内alpha递增
        for i in range(size, 0, -2):
            alpha = int(color[3] * (1 - i / size))
            glow_color = (color[0], color[1], color[2], alpha)
            pygame.draw.circle(glow_surf, glow_color, (size, size), i)

        # 绘制到屏幕
        screen.blit(glow_surf, (pos[0] - size, pos[1] - size), special_flags=pygame.BLEND_RGBA_ADD)

    def highlight_lessons(self, screen: pygame.Surface, lessons: List[Lesson],
                         angle_offset: float = 0):
        """
        高亮四课位置

        Args:
            screen: pygame屏幕
            lessons: 四课列表
            angle_offset: 天盘旋转偏移量
        """
        for lesson in lessons:
            # 高亮天盘位置（上神）
            self.highlight_branch(screen, lesson.heaven, COLOR_LESSON_HIGHLIGHT,
                                 angle_offset, 0.65)

    def highlight_passes(self, screen: pygame.Surface, passes: List[Pass],
                        angle_offset: float = 0):
        """
        高亮三传位置

        Args:
            screen: pygame屏幕
            passes: 三传列表
            angle_offset: 天盘旋转偏移量
        """
        for i, p in enumerate(passes):
            if i == 0:
                # 初传用特殊颜色
                color = COLOR_INITIAL_PASS
            else:
                color = COLOR_PASS_HIGHLIGHT

            self.highlight_branch(screen, p.branch, color, angle_offset, 0.65)

    def draw_connection_lines(self, screen: pygame.Surface, passes: List[Pass],
                             angle_offset: float = 0):
        """
        绘制三传之间的连接线

        Args:
            screen: pygame屏幕
            passes: 三传列表
            angle_offset: 天盘旋转偏移量
        """
        if len(passes) < 2:
            return

        points = [self.get_branch_position(p.branch, angle_offset, 0.65) for p in passes]

        # 绘制连接线
        for i in range(len(points) - 1):
            pygame.draw.line(screen, (150, 200, 255, 100), points[i], points[i + 1], 2)

    def highlight_all(self, screen: pygame.Surface, lessons: List[Lesson],
                     passes: List[Pass], angle_offset: float = 0):
        """
        高亮所有四课三传位置

        Args:
            screen: pygame屏幕
            lessons: 四课列表
            passes: 三传列表
            angle_offset: 天盘旋转偏移量
        """
        # 先绘制四课（底层）
        self.highlight_lessons(screen, lessons, angle_offset)
        # 再绘制三传（顶层）
        self.highlight_passes(screen, passes, angle_offset)
        # 绘制连接线
        self.draw_connection_lines(screen, passes, angle_offset)
