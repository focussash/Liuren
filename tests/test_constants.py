# tests/test_constants.py
# 子项目1：常量系统测试

import pytest
import sys
sys.path.insert(0, 'E:/Random/Pet_projects/Liuren')

from config import (
    STEM_WUXING, BRANCH_WUXING, WUXING_KE, WUXING_SHENG,
    STEM_YINYANG, BRANCH_YINYANG, STEM_JIGONG, BRANCH_CHONG, BRANCH_YIMA
)
from liuren.constants import ZHONGQI_MOON_GENERAL, MOON_GENERAL_NAMES, TWELVE_GENERALS


class TestWuxing:
    """五行系统测试"""

    def test_C001_wuxing_ke_completeness(self):
        """C001: 五行克关系完整性"""
        assert len(WUXING_KE) == 5

    def test_C002_wuxing_ke_cycle(self):
        """C002: 五行克循环验证 木->土->水->火->金->木"""
        cycle = ['木', '土', '水', '火', '金']
        for i in range(5):
            current = cycle[i]
            next_elem = cycle[(i + 1) % 5]
            assert WUXING_KE[current] == next_elem, f"{current}克{WUXING_KE[current]}, 期望{next_elem}"

    def test_C003_stem_wuxing_jia(self):
        """C003: 天干五行正确性 - 甲"""
        assert STEM_WUXING['甲'] == '木'

    def test_C004_branch_wuxing_si(self):
        """C004: 地支五行正确性 - 巳"""
        assert BRANCH_WUXING['巳'] == '火'

    def test_stem_wuxing_completeness(self):
        """天干五行完整性"""
        assert len(STEM_WUXING) == 10

    def test_branch_wuxing_completeness(self):
        """地支五行完整性"""
        assert len(BRANCH_WUXING) == 12


class TestJigong:
    """寄宫系统测试"""

    def test_C005_jigong_completeness(self):
        """C005: 寄宫完整性"""
        assert len(STEM_JIGONG) == 10

    def test_C006_jigong_jia(self):
        """C006: 寄宫正确性 - 甲寄寅"""
        assert STEM_JIGONG['甲'] == '寅'

    def test_C007_jigong_wu(self):
        """C007: 寄宫正确性 - 戊寄巳"""
        assert STEM_JIGONG['戊'] == '巳'

    def test_jigong_all_values(self):
        """验证所有寄宫对应"""
        expected = {
            '甲': '寅', '乙': '辰', '丙': '巳', '丁': '未',
            '戊': '巳', '己': '未', '庚': '申', '辛': '戌',
            '壬': '亥', '癸': '丑'
        }
        for stem, branch in expected.items():
            assert STEM_JIGONG[stem] == branch, f"{stem}寄宫应为{branch}"


class TestChong:
    """六冲系统测试"""

    def test_C008_chong_symmetry(self):
        """C008: 六冲对称性 - A冲B则B冲A"""
        for a, b in BRANCH_CHONG.items():
            assert BRANCH_CHONG[b] == a, f"{a}冲{b}, 但{b}冲{BRANCH_CHONG[b]}"

    def test_chong_completeness(self):
        """六冲完整性"""
        assert len(BRANCH_CHONG) == 12


class TestYinyang:
    """阴阳系统测试"""

    def test_C009_yinyang_completeness(self):
        """C009: 阴阳完整性"""
        assert len(STEM_YINYANG) == 10
        assert len(BRANCH_YINYANG) == 12

    def test_stem_yinyang_values(self):
        """天干阴阳值域"""
        for stem, yy in STEM_YINYANG.items():
            assert yy in ('阳', '阴')

    def test_branch_yinyang_values(self):
        """地支阴阳值域"""
        for branch, yy in BRANCH_YINYANG.items():
            assert yy in ('阳', '阴')


class TestMoonGeneral:
    """月将系统测试"""

    def test_C010_moon_general_names_completeness(self):
        """C010: 月将名称完整性"""
        assert len(MOON_GENERAL_NAMES) == 12

    def test_zhongqi_moon_general_completeness(self):
        """中气月将映射完整性"""
        assert len(ZHONGQI_MOON_GENERAL) == 12

    def test_twelve_generals_completeness(self):
        """十二天将完整性"""
        assert len(TWELVE_GENERALS) == 12


class TestYima:
    """驿马测试"""

    def test_yima_completeness(self):
        """驿马完整性"""
        assert len(BRANCH_YIMA) == 12

    def test_yima_values_are_branches(self):
        """驿马值都是有效地支"""
        branches = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
        for key, val in BRANCH_YIMA.items():
            assert val in branches, f"驿马{key}->{val}不是有效地支"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
