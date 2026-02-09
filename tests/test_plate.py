# tests/test_plate.py
# 子项目4：天地盘与式盘状态测试

import pytest
import sys
sys.path.insert(0, 'E:/Random/Pet_projects/Liuren')

from liuren.plate import (
    Lesson, Pass, LiurenPlate,
    build_heaven_plate, get_heaven_branch,
    is_fuyin, is_fanyin
)


class TestHeavenPlate:
    """天盘构建测试"""

    def test_PL001_hai_jia_wu(self):
        """PL001: 天盘构建 - 亥将加临午时，亥应在午位"""
        heaven_plate = build_heaven_plate('亥', '午')
        # 亥将在午位，意味着查午位应得亥
        assert heaven_plate['午'] == '亥'

    def test_PL002_fuyin(self):
        """PL002: 天盘构建 - 子加子（伏吟），天地盘重合"""
        heaven_plate = build_heaven_plate('子', '子')
        # 伏吟时，每个位置天地盘相同
        for branch in ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']:
            assert heaven_plate[branch] == branch

    def test_PL003_fanyin(self):
        """PL003: 天盘构建 - 子加午（返吟），天地盘对冲"""
        heaven_plate = build_heaven_plate('子', '午')
        # 返吟时，每个位置天盘是地盘的对冲
        chong_pairs = [('子', '午'), ('丑', '未'), ('寅', '申'), ('卯', '酉'), ('辰', '戌'), ('巳', '亥')]
        for a, b in chong_pairs:
            assert heaven_plate[a] == b
            assert heaven_plate[b] == a

    def test_PL004_query_yin(self):
        """PL004: 上神查询 - 亥加午，查寅位

        根据计算：亥(11)加午(6), offset=5
        寅(2) -> (2+5)%12 = 7 = 未
        """
        heaven_plate = build_heaven_plate('亥', '午')
        assert get_heaven_branch(heaven_plate, '寅') == '未'

    def test_PL005_query_zi(self):
        """PL005: 上神查询 - 亥加午，查子位

        根据计算：亥(11)加午(6), offset=5
        子(0) -> (0+5)%12 = 5 = 巳
        """
        heaven_plate = build_heaven_plate('亥', '午')
        assert get_heaven_branch(heaven_plate, '子') == '巳'

    def test_PL006_completeness(self):
        """PL006: 天盘完整性 - 应有12个映射"""
        heaven_plate = build_heaven_plate('亥', '午')
        assert len(heaven_plate) == 12

    def test_PL007_bijection(self):
        """PL007: 天盘双射性 - 天盘地支不重复"""
        heaven_plate = build_heaven_plate('亥', '午')
        values = list(heaven_plate.values())
        assert len(values) == len(set(values))  # 所有值唯一

    def test_heaven_plate_example(self):
        """验证计划中的完整示例

        月将亥(登明)加临午时:
        地盘: 子丑寅卯辰巳午未申酉戌亥
        天盘: 巳午未申酉戌亥子丑寅卯辰
        """
        heaven_plate = build_heaven_plate('亥', '午')
        expected = {
            '子': '巳', '丑': '午', '寅': '未', '卯': '申',
            '辰': '酉', '巳': '戌', '午': '亥', '未': '子',
            '申': '丑', '酉': '寅', '戌': '卯', '亥': '辰'
        }
        assert heaven_plate == expected


class TestFuyinFanyin:
    """伏吟返吟判断测试"""

    def test_is_fuyin_true(self):
        """月将等于时支时为伏吟"""
        assert is_fuyin('子', '子') == True
        assert is_fuyin('午', '午') == True

    def test_is_fuyin_false(self):
        """月将不等于时支时不是伏吟"""
        assert is_fuyin('子', '午') == False
        assert is_fuyin('亥', '午') == False

    def test_is_fanyin_true(self):
        """月将冲时支时为返吟"""
        assert is_fanyin('子', '午') == True
        assert is_fanyin('午', '子') == True
        assert is_fanyin('寅', '申') == True

    def test_is_fanyin_false(self):
        """月将不冲时支时不是返吟"""
        assert is_fanyin('子', '子') == False
        assert is_fanyin('亥', '午') == False


class TestDataClasses:
    """数据类测试"""

    def test_lesson_creation(self):
        """Lesson数据类创建"""
        lesson = Lesson(heaven='未', earth='寅', index=1)
        assert lesson.heaven == '未'
        assert lesson.earth == '寅'
        assert lesson.index == 1

    def test_pass_creation(self):
        """Pass数据类创建"""
        p = Pass(branch='巳', index=1)
        assert p.branch == '巳'
        assert p.index == 1

    def test_liuren_plate_creation(self):
        """LiurenPlate数据类创建"""
        heaven_plate = build_heaven_plate('亥', '午')
        plate = LiurenPlate(
            day_stem='甲',
            day_branch='子',
            hour_branch='午',
            moon_general='亥',
            moon_general_name='登明',
            heaven_plate=heaven_plate
        )
        assert plate.day_stem == '甲'
        assert plate.day_branch == '子'
        assert plate.hour_branch == '午'
        assert plate.moon_general == '亥'
        assert plate.moon_general_name == '登明'
        assert len(plate.heaven_plate) == 12
        assert plate.lessons == []
        assert plate.passes == []
        assert plate.lesson_type == ""
        assert plate.derivation_log == []


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
