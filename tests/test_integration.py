# tests/test_integration.py
# 子项目13：集成测试

import pytest
import sys
sys.path.insert(0, 'E:/Random/Pet_projects/Liuren')

# 初始化pygame
import pygame
pygame.init()


class TestIntegration:
    """集成测试"""

    def test_INT001_all_modules_importable(self):
        """INT001: 所有模块可导入"""
        # Core modules
        from config import HEAVENLY_STEMS, EARTHLY_BRANCHES
        from core import get_chinese_hour, get_moon_general

        # Liuren modules
        from liuren.plate import LiurenPlate, build_heaven_plate
        from liuren.four_lessons import calculate_four_lessons
        from liuren.three_passes import calculate_three_passes
        from liuren.moon_general import get_moon_general as get_moon_general_new

        # Calendar modules
        from lunar_calendar.ganzhi import get_day_ganzhi, get_hour_branch

        # UI modules
        from ui import InputPanel, PlateHighlighter, ResultSidebar

        assert True

    def test_INT002_complete_paipan_flow(self):
        """INT002: 完整排盘流程"""
        from datetime import datetime
        from liuren.plate import LiurenPlate, build_heaven_plate
        from liuren.four_lessons import calculate_four_lessons
        from liuren.three_passes import calculate_three_passes
        from liuren.moon_general import get_moon_general

        # 输入: 甲子日 午时
        day_stem = '甲'
        day_branch = '子'
        hour_branch = '午'

        # 1. 计算月将
        now = datetime.now()
        moon_general, moon_general_name = get_moon_general(now)
        assert moon_general in ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

        # 2. 构建天地盘
        heaven_plate = build_heaven_plate(moon_general, hour_branch)
        assert len(heaven_plate) == 12

        # 3. 创建式盘
        plate = LiurenPlate(
            day_stem=day_stem,
            day_branch=day_branch,
            hour_branch=hour_branch,
            moon_general=moon_general,
            moon_general_name=moon_general_name,
            heaven_plate=heaven_plate
        )
        assert plate.day_stem == '甲'

        # 4. 计算四课
        lessons = calculate_four_lessons(plate)
        assert len(lessons) == 4

        # 5. 计算三传
        passes, lesson_type = calculate_three_passes(plate, lessons)
        assert len(passes) == 3
        assert lesson_type != ""

    def test_INT003_known_case_jiaziri(self):
        """INT003: 已知案例 - 甲子日午时亥将"""
        from liuren.plate import LiurenPlate, build_heaven_plate
        from liuren.four_lessons import calculate_four_lessons
        from liuren.three_passes import calculate_three_passes

        # 构建亥加午的天盘
        heaven_plate = build_heaven_plate('亥', '午')

        plate = LiurenPlate(
            day_stem='甲',
            day_branch='子',
            hour_branch='午',
            moon_general='亥',
            moon_general_name='登明',
            heaven_plate=heaven_plate
        )

        # 计算四课
        lessons = calculate_four_lessons(plate)

        # 验证四课 (根据plan中的计算)
        # 一课: 未/寅, 二课: 子/未, 三课: 巳/子, 四课: 戌/巳
        assert lessons[0].heaven == '未'
        assert lessons[0].earth == '寅'
        assert lessons[1].heaven == '子'
        assert lessons[1].earth == '未'
        assert lessons[2].heaven == '巳'
        assert lessons[2].earth == '子'
        assert lessons[3].heaven == '戌'
        assert lessons[3].earth == '巳'

        # 计算三传
        passes, lesson_type = calculate_three_passes(plate, lessons)
        assert len(passes) == 3
        # 此案例有3个下克上，比用后子(阳)与日干甲(阳)同，为重审课
        assert lesson_type == '重审'

    def test_INT004_highlighter_sync(self):
        """INT004: 高亮跟随旋转"""
        import math
        from ui.highlight import PlateHighlighter

        highlighter = PlateHighlighter((400, 400), 200)

        # 不同角度偏移应产生不同位置
        pos1 = highlighter.get_branch_position('子', 0)
        pos2 = highlighter.get_branch_position('子', math.radians(30))

        # 位置应该不同
        assert pos1 != pos2

    def test_INT005_ui_sidebar_with_plate(self):
        """INT005: 侧边栏显示盘局"""
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

    def test_INT006_fuyin_case(self):
        """INT006: 伏吟案例验证"""
        from liuren.plate import LiurenPlate, build_heaven_plate
        from liuren.four_lessons import calculate_four_lessons
        from liuren.three_passes import calculate_three_passes, is_fuyin

        # 伏吟: 月将等于时支（如子将子时）
        heaven_plate = build_heaven_plate('子', '子')

        plate = LiurenPlate(
            day_stem='甲',
            day_branch='子',
            hour_branch='子',
            moon_general='子',
            moon_general_name='神后',
            heaven_plate=heaven_plate
        )

        assert is_fuyin(plate) == True

        lessons = calculate_four_lessons(plate)
        passes, lesson_type = calculate_three_passes(plate, lessons)

        assert lesson_type == '伏吟'
        assert len(passes) == 3

    def test_INT007_fanyin_case(self):
        """INT007: 返吟案例验证"""
        from liuren.plate import LiurenPlate, build_heaven_plate
        from liuren.four_lessons import calculate_four_lessons
        from liuren.three_passes import calculate_three_passes, is_fanyin

        # 返吟: 月将冲时支（如子将午时）
        heaven_plate = build_heaven_plate('子', '午')

        plate = LiurenPlate(
            day_stem='甲',
            day_branch='子',
            hour_branch='午',
            moon_general='子',
            moon_general_name='神后',
            heaven_plate=heaven_plate
        )

        assert is_fanyin(plate) == True

        lessons = calculate_four_lessons(plate)
        passes, lesson_type = calculate_three_passes(plate, lessons)

        assert lesson_type == '返吟'
        assert len(passes) == 3

    def test_INT008_input_panel_creation(self):
        """INT008: 输入面板创建"""
        from ui.input_panel import InputPanel

        font = pygame.font.SysFont('simhei', 18)
        panel = InputPanel(0, 0, font)

        # 设置值
        panel.day_stem_selector.set_value('乙')
        panel.day_branch_selector.set_value('丑')
        panel.hour_branch_selector.set_value('卯')

        result = panel.get_input()
        assert result['day_stem'] == '乙'
        assert result['day_branch'] == '丑'
        assert result['hour_branch'] == '卯'

    def test_INT009_all_stems_branches(self):
        """INT009: 所有干支组合可计算"""
        from liuren.plate import LiurenPlate, build_heaven_plate
        from liuren.four_lessons import calculate_four_lessons
        from liuren.three_passes import calculate_three_passes
        from config import HEAVENLY_STEMS, EARTHLY_BRANCHES

        # 测试几个代表性组合
        test_cases = [
            ('甲', '子', '午', '亥'),  # 阳干阳支
            ('乙', '丑', '卯', '戌'),  # 阴干阴支
            ('丙', '寅', '申', '酉'),  # 阳干阳支
            ('癸', '亥', '巳', '寅'),  # 阴干阴支
        ]

        for day_stem, day_branch, hour_branch, moon_general in test_cases:
            heaven_plate = build_heaven_plate(moon_general, hour_branch)
            plate = LiurenPlate(
                day_stem=day_stem,
                day_branch=day_branch,
                hour_branch=hour_branch,
                moon_general=moon_general,
                moon_general_name='测试',
                heaven_plate=heaven_plate
            )

            lessons = calculate_four_lessons(plate)
            passes, lesson_type = calculate_three_passes(plate, lessons)

            assert len(lessons) == 4
            assert len(passes) == 3
            assert lesson_type != ""

    def test_INT010_derivation_log(self):
        """INT010: 推导过程日志"""
        from liuren.plate import LiurenPlate, build_heaven_plate
        from liuren.four_lessons import calculate_four_lessons
        from liuren.three_passes import calculate_three_passes

        heaven_plate = build_heaven_plate('亥', '午')
        plate = LiurenPlate(
            day_stem='甲',
            day_branch='子',
            hour_branch='午',
            moon_general='亥',
            moon_general_name='登明',
            heaven_plate=heaven_plate
        )

        lessons = calculate_four_lessons(plate)
        passes, lesson_type = calculate_three_passes(plate, lessons)

        # 检查推导日志已填写
        assert len(plate.derivation_log) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
