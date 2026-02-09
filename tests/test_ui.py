# tests/test_ui.py
# 子项目10-12：UI组件测试

import pytest
import sys
sys.path.insert(0, 'E:/Random/Pet_projects/Liuren')

# 初始化pygame用于测试
import pygame
pygame.init()


class TestInputPanel:
    """输入面板测试"""

    def test_UI001_dropdown_creation(self):
        """UI001: 下拉选择器创建"""
        from ui.input_panel import DropdownSelector
        font = pygame.font.SysFont('simhei', 18)

        dropdown = DropdownSelector(0, 0, 60, 30, ['甲', '乙', '丙'], '测试', font)
        assert dropdown.get_value() == '甲'

    def test_UI002_dropdown_selection(self):
        """UI002: 选项选择"""
        from ui.input_panel import DropdownSelector
        font = pygame.font.SysFont('simhei', 18)

        dropdown = DropdownSelector(0, 0, 60, 30, ['甲', '乙', '丙'], '测试', font)
        dropdown.set_value('乙')
        assert dropdown.get_value() == '乙'

    def test_UI003_all_stems_available(self):
        """UI003: 所有天干可用"""
        from ui.input_panel import InputPanel
        from config import HEAVENLY_STEMS
        font = pygame.font.SysFont('simhei', 18)

        panel = InputPanel(0, 0, font)
        for stem in HEAVENLY_STEMS:
            panel.day_stem_selector.set_value(stem)
            assert panel.day_stem_selector.get_value() == stem

    def test_UI003_all_branches_available(self):
        """UI003: 所有地支可用"""
        from ui.input_panel import InputPanel
        from config import EARTHLY_BRANCHES
        font = pygame.font.SysFont('simhei', 18)

        panel = InputPanel(0, 0, font)
        for branch in EARTHLY_BRANCHES:
            panel.day_branch_selector.set_value(branch)
            assert panel.day_branch_selector.get_value() == branch

    def test_UI004_get_input(self):
        """UI004: 获取输入值"""
        from ui.input_panel import InputPanel
        font = pygame.font.SysFont('simhei', 18)

        panel = InputPanel(0, 0, font)
        panel.day_stem_selector.set_value('甲')
        panel.day_branch_selector.set_value('子')
        panel.hour_branch_selector.set_value('午')

        result = panel.get_input()
        assert result['day_stem'] == '甲'
        assert result['day_branch'] == '子'
        assert result['hour_branch'] == '午'

    def test_button_creation(self):
        """按钮创建测试"""
        from ui.input_panel import Button
        font = pygame.font.SysFont('simhei', 18)

        button = Button(0, 0, 80, 30, '测试', font)
        assert button.text == '测试'
        assert button.hovered == False


class TestHighlighter:
    """高亮组件测试"""

    def test_HL001_branch_position(self):
        """HL001: 地支位置计算"""
        from ui.highlight import PlateHighlighter

        highlighter = PlateHighlighter((400, 400), 200)

        # 子在底部
        pos = highlighter.get_branch_position('子', 0, 0.65)
        assert isinstance(pos, tuple)
        assert len(pos) == 2

    def test_HL002_lesson_highlight(self):
        """HL002: 四课高亮"""
        from ui.highlight import PlateHighlighter
        from liuren.plate import Lesson

        highlighter = PlateHighlighter((400, 400), 200)
        lessons = [
            Lesson(heaven='未', earth='寅', index=1),
            Lesson(heaven='子', earth='未', index=2),
            Lesson(heaven='巳', earth='子', index=3),
            Lesson(heaven='戌', earth='巳', index=4)
        ]

        # 创建测试surface
        screen = pygame.Surface((800, 800), pygame.SRCALPHA)
        # 应该不抛出异常
        highlighter.highlight_lessons(screen, lessons, 0)

    def test_HL003_pass_highlight(self):
        """HL003: 三传高亮"""
        from ui.highlight import PlateHighlighter
        from liuren.plate import Pass

        highlighter = PlateHighlighter((400, 400), 200)
        passes = [
            Pass(branch='未', index=1),
            Pass(branch='子', index=2),
            Pass(branch='巳', index=3)
        ]

        screen = pygame.Surface((800, 800), pygame.SRCALPHA)
        highlighter.highlight_passes(screen, passes, 0)

    def test_branch_angle(self):
        """地支角度计算"""
        from ui.highlight import PlateHighlighter
        import math

        highlighter = PlateHighlighter((400, 400), 200)

        # 子在底部（-90度）
        angle_zi = highlighter.get_branch_angle('子', 0)
        assert abs(angle_zi - math.radians(-90)) < 0.01

        # 午在顶部（90度）
        angle_wu = highlighter.get_branch_angle('午', 0)
        assert abs(angle_wu - math.radians(90)) < 0.01


class TestSidebar:
    """侧边栏测试"""

    def test_SB001_creation(self):
        """SB001: 侧边栏创建"""
        from ui.sidebar import ResultSidebar
        font = pygame.font.SysFont('simhei', 18)

        sidebar = ResultSidebar(0, 0, 300, 600, font)
        assert sidebar.plate is None

    def test_SB002_set_plate(self):
        """SB002: 设置盘局"""
        from ui.sidebar import ResultSidebar
        from liuren.plate import LiurenPlate, Lesson, Pass, build_heaven_plate
        font = pygame.font.SysFont('simhei', 18)

        sidebar = ResultSidebar(0, 0, 300, 600, font)

        # 创建测试盘局
        heaven_plate = build_heaven_plate('亥', '午')
        plate = LiurenPlate(
            day_stem='甲',
            day_branch='子',
            hour_branch='午',
            moon_general='亥',
            moon_general_name='登明',
            heaven_plate=heaven_plate
        )
        lessons = [
            Lesson(heaven='未', earth='寅', index=1),
            Lesson(heaven='子', earth='未', index=2),
            Lesson(heaven='巳', earth='子', index=3),
            Lesson(heaven='戌', earth='巳', index=4)
        ]
        passes = [
            Pass(branch='未', index=1),
            Pass(branch='子', index=2),
            Pass(branch='巳', index=3)
        ]

        sidebar.set_plate(plate, lessons, passes, '元首')

        assert sidebar.plate is not None
        assert sidebar.lesson_type == '元首'
        assert len(sidebar.lessons) == 4
        assert len(sidebar.passes) == 3

    def test_SB003_clear(self):
        """SB003: 清除内容"""
        from ui.sidebar import ResultSidebar
        font = pygame.font.SysFont('simhei', 18)

        sidebar = ResultSidebar(0, 0, 300, 600, font)
        sidebar.lesson_type = '测试'
        sidebar.clear()

        assert sidebar.plate is None
        assert sidebar.lesson_type == ""

    def test_draw_empty(self):
        """绘制空状态不抛出异常"""
        from ui.sidebar import ResultSidebar
        font = pygame.font.SysFont('simhei', 18)

        sidebar = ResultSidebar(0, 0, 300, 600, font)
        screen = pygame.Surface((800, 800))
        sidebar.draw(screen)


class TestUIIntegration:
    """UI集成测试"""

    def test_all_components_importable(self):
        """所有UI组件可导入"""
        from ui import InputPanel, DropdownSelector, Button
        from ui import PlateHighlighter
        from ui import ResultSidebar

        assert InputPanel is not None
        assert DropdownSelector is not None
        assert Button is not None
        assert PlateHighlighter is not None
        assert ResultSidebar is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
