# tests/test_four_lessons.py
# 子项目5：四课计算测试

import pytest
import sys
sys.path.insert(0, 'E:/Random/Pet_projects/Liuren')

from liuren.plate import LiurenPlate, build_heaven_plate
from liuren.four_lessons import calculate_four_lessons, get_lesson_display


def create_plate(day_stem: str, day_branch: str, hour_branch: str, moon_general: str) -> LiurenPlate:
    """辅助函数：创建测试用式盘"""
    heaven_plate = build_heaven_plate(moon_general, hour_branch)
    return LiurenPlate(
        day_stem=day_stem,
        day_branch=day_branch,
        hour_branch=hour_branch,
        moon_general=moon_general,
        moon_general_name='',
        heaven_plate=heaven_plate
    )


class TestFourLessons:
    """四课计算测试"""

    def test_FL001_jiazi_wu_hai(self):
        """FL001: 甲子日午时月将亥

        天盘: 亥加午, offset = 11 - 6 = 5
        甲寄宫寅:
        一课: 寅(2) -> (2+5)%12 = 7 = 未 → 未/寅
        二课: 未(7) -> (7+5)%12 = 0 = 子 → 子/未
        三课: 子(0) -> (0+5)%12 = 5 = 巳 → 巳/子
        四课: 巳(5) -> (5+5)%12 = 10 = 戌 → 戌/巳
        """
        plate = create_plate('甲', '子', '午', '亥')
        lessons = calculate_four_lessons(plate)

        assert len(lessons) == 4

        # 一课: 未/寅
        assert lessons[0].heaven == '未'
        assert lessons[0].earth == '寅'
        assert lessons[0].index == 1

        # 二课: 子/未
        assert lessons[1].heaven == '子'
        assert lessons[1].earth == '未'
        assert lessons[1].index == 2

        # 三课: 巳/子
        assert lessons[2].heaven == '巳'
        assert lessons[2].earth == '子'
        assert lessons[2].index == 3

        # 四课: 戌/巳
        assert lessons[3].heaven == '戌'
        assert lessons[3].earth == '巳'
        assert lessons[3].index == 4

    def test_FL002_yichou_mao_xu(self):
        """FL002: 乙丑日卯时月将戌

        天盘: 戌加卯, offset = 10 - 3 = 7
        乙寄宫辰:
        一课: 辰(4) -> (4+7)%12 = 11 = 亥 → 亥/辰
        二课: 亥(11) -> (11+7)%12 = 6 = 午 → 午/亥
        三课: 丑(1) -> (1+7)%12 = 8 = 申 → 申/丑
        四课: 申(8) -> (8+7)%12 = 3 = 卯 → 卯/申
        """
        plate = create_plate('乙', '丑', '卯', '戌')
        lessons = calculate_four_lessons(plate)

        assert lessons[0].heaven == '亥' and lessons[0].earth == '辰'  # 一课
        assert lessons[1].heaven == '午' and lessons[1].earth == '亥'  # 二课
        assert lessons[2].heaven == '申' and lessons[2].earth == '丑'  # 三课
        assert lessons[3].heaven == '卯' and lessons[3].earth == '申'  # 四课

    def test_FL003_bingyin_shen_you(self):
        """FL003: 丙寅日申时月将酉

        天盘: 酉加申, offset = 9 - 8 = 1
        丙寄宫巳:
        一课: 巳(5) -> (5+1)%12 = 6 = 午 → 午/巳
        二课: 午(6) -> (6+1)%12 = 7 = 未 → 未/午
        三课: 寅(2) -> (2+1)%12 = 3 = 卯 → 卯/寅
        四课: 卯(3) -> (3+1)%12 = 4 = 辰 → 辰/卯
        """
        plate = create_plate('丙', '寅', '申', '酉')
        lessons = calculate_four_lessons(plate)

        assert lessons[0].heaven == '午' and lessons[0].earth == '巳'  # 一课
        assert lessons[1].heaven == '未' and lessons[1].earth == '午'  # 二课
        assert lessons[2].heaven == '卯' and lessons[2].earth == '寅'  # 三课
        assert lessons[3].heaven == '辰' and lessons[3].earth == '卯'  # 四课

    def test_FL004_dingmao_si_wei(self):
        """FL004: 丁卯日巳时月将未

        天盘: 未加巳, offset = 7 - 5 = 2
        丁寄宫未:
        一课: 未(7) -> (7+2)%12 = 9 = 酉 → 酉/未
        二课: 酉(9) -> (9+2)%12 = 11 = 亥 → 亥/酉
        三课: 卯(3) -> (3+2)%12 = 5 = 巳 → 巳/卯
        四课: 巳(5) -> (5+2)%12 = 7 = 未 → 未/巳
        """
        plate = create_plate('丁', '卯', '巳', '未')
        lessons = calculate_four_lessons(plate)

        assert lessons[0].heaven == '酉' and lessons[0].earth == '未'  # 一课
        assert lessons[1].heaven == '亥' and lessons[1].earth == '酉'  # 二课
        assert lessons[2].heaven == '巳' and lessons[2].earth == '卯'  # 三课
        assert lessons[3].heaven == '未' and lessons[3].earth == '巳'  # 四课

    def test_FL005_wuchen_yin_wu(self):
        """FL005: 戊辰日寅时月将午

        天盘: 午加寅, offset = 6 - 2 = 4
        戊寄宫巳:
        一课: 巳(5) -> (5+4)%12 = 9 = 酉 → 酉/巳
        二课: 酉(9) -> (9+4)%12 = 1 = 丑 → 丑/酉
        三课: 辰(4) -> (4+4)%12 = 8 = 申 → 申/辰
        四课: 申(8) -> (8+4)%12 = 0 = 子 → 子/申
        """
        plate = create_plate('戊', '辰', '寅', '午')
        lessons = calculate_four_lessons(plate)

        assert lessons[0].heaven == '酉' and lessons[0].earth == '巳'  # 一课
        assert lessons[1].heaven == '丑' and lessons[1].earth == '酉'  # 二课
        assert lessons[2].heaven == '申' and lessons[2].earth == '辰'  # 三课
        assert lessons[3].heaven == '子' and lessons[3].earth == '申'  # 四课

    def test_FL006_jisi_hai_mao(self):
        """FL006: 己巳日亥时月将卯

        天盘: 卯加亥, offset = 3 - 11 = -8 = 4 (mod 12)
        己寄宫未:
        一课: 未(7) -> (7+4)%12 = 11 = 亥 → 亥/未
        二课: 亥(11) -> (11+4)%12 = 3 = 卯 → 卯/亥
        三课: 巳(5) -> (5+4)%12 = 9 = 酉 → 酉/巳
        四课: 酉(9) -> (9+4)%12 = 1 = 丑 → 丑/酉
        """
        plate = create_plate('己', '巳', '亥', '卯')
        lessons = calculate_four_lessons(plate)

        assert lessons[0].heaven == '亥' and lessons[0].earth == '未'  # 一课
        assert lessons[1].heaven == '卯' and lessons[1].earth == '亥'  # 二课
        assert lessons[2].heaven == '酉' and lessons[2].earth == '巳'  # 三课
        assert lessons[3].heaven == '丑' and lessons[3].earth == '酉'  # 四课

    def test_fuyin_case(self):
        """伏吟情况：月将=时支，天地盘重合"""
        # 子将加子时
        plate = create_plate('甲', '子', '子', '子')
        lessons = calculate_four_lessons(plate)

        # 甲寄宫寅，伏吟时寅上神仍是寅
        assert lessons[0].heaven == '寅' and lessons[0].earth == '寅'  # 一课
        assert lessons[1].heaven == '寅' and lessons[1].earth == '寅'  # 二课
        assert lessons[2].heaven == '子' and lessons[2].earth == '子'  # 三课
        assert lessons[3].heaven == '子' and lessons[3].earth == '子'  # 四课

    def test_fanyin_case(self):
        """返吟情况：月将冲时支，天地盘对冲"""
        # 子将加午时
        plate = create_plate('甲', '子', '午', '子')
        lessons = calculate_four_lessons(plate)

        # 甲寄宫寅，返吟时寅上神是申（寅冲申）
        assert lessons[0].heaven == '申' and lessons[0].earth == '寅'  # 一课
        assert lessons[1].heaven == '寅' and lessons[1].earth == '申'  # 二课
        assert lessons[2].heaven == '午' and lessons[2].earth == '子'  # 三课
        assert lessons[3].heaven == '子' and lessons[3].earth == '午'  # 四课


class TestLessonDisplay:
    """四课显示测试"""

    def test_display_format(self):
        """测试四课显示格式"""
        plate = create_plate('甲', '子', '午', '亥')
        lessons = calculate_four_lessons(plate)
        display = get_lesson_display(lessons)

        assert '一课' in display
        assert '二课' in display
        assert '三课' in display
        assert '四课' in display
        assert '未' in display  # 一课天盘
        assert '寅' in display  # 一课地盘


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
