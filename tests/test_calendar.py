# tests/test_calendar.py
# 子项目2：万年历与节气计算测试

import pytest
import sys
sys.path.insert(0, 'E:/Random/Pet_projects/Liuren')

from datetime import datetime
from lunar_calendar.solar_terms import (
    get_current_zhongqi, get_solar_term_of_day, get_solar_terms_dict
)
from lunar_calendar.ganzhi import (
    get_day_ganzhi, get_hour_branch, get_hour_ganzhi, get_full_ganzhi,
    get_branch_index, get_branch_by_index
)


class TestSolarTerms:
    """节气计算测试"""

    def test_CAL001_spring_equinox(self):
        """CAL001: 春分节气验证 - 2024-03-20是春分"""
        term = get_solar_term_of_day(datetime(2024, 3, 20))
        assert term == '春分'

    def test_CAL002_summer_solstice(self):
        """CAL002: 夏至节气验证 - 2024-06-21是夏至"""
        term = get_solar_term_of_day(datetime(2024, 6, 21))
        assert term == '夏至'

    def test_CAL003_autumn_equinox(self):
        """CAL003: 秋分节气验证 - 2024-09-22是秋分"""
        term = get_solar_term_of_day(datetime(2024, 9, 22))
        assert term == '秋分'

    def test_CAL004_winter_solstice(self):
        """CAL004: 冬至节气验证 - 2024-12-21是冬至"""
        term = get_solar_term_of_day(datetime(2024, 12, 21))
        assert term == '冬至'

    def test_CAL005_zhongqi_boundary(self):
        """CAL005: 中气边界测试 - 春分前一天应该是雨水"""
        # 2024-03-19 在春分前，应当使用雨水期的月将
        zhongqi = get_current_zhongqi(datetime(2024, 3, 19))
        assert zhongqi == '雨水'

    def test_zhongqi_after_spring_equinox(self):
        """春分后应该是春分"""
        zhongqi = get_current_zhongqi(datetime(2024, 3, 25))
        assert zhongqi == '春分'

    def test_solar_terms_dict_completeness(self):
        """节气字典应包含24个节气"""
        terms = get_solar_terms_dict(2024)
        assert len(terms) == 24


class TestGanzhi:
    """干支推算测试"""

    def test_CAL006_known_day_ganzhi(self):
        """CAL006: 日干支验证 - 2024-03-20是癸未日"""
        stem, branch = get_day_ganzhi(2024, 3, 20)
        assert stem == '癸'
        assert branch == '未'

    def test_CAL007_day_ganzhi_continuity(self):
        """CAL007: 日干支连续性 - 连续三天干支应递增"""
        # 2024-03-20 癸未
        # 2024-03-21 甲申
        # 2024-03-22 乙酉
        gz1 = get_day_ganzhi(2024, 3, 20)
        gz2 = get_day_ganzhi(2024, 3, 21)
        gz3 = get_day_ganzhi(2024, 3, 22)

        assert gz1 == ('癸', '未')
        assert gz2 == ('甲', '申')
        assert gz3 == ('乙', '酉')

    def test_CAL008_hour_branch_zi(self):
        """CAL008: 时支验证 - 23:30应该是子时"""
        assert get_hour_branch(23) == '子'
        assert get_hour_branch(0) == '子'

    def test_CAL009_hour_branch_wu(self):
        """CAL009: 时支验证 - 12:00应该是午时"""
        assert get_hour_branch(12) == '午'

    def test_CAL010_hour_branch_chou(self):
        """CAL010: 时支边界验证 - 01:30应该是丑时"""
        assert get_hour_branch(1) == '丑'
        assert get_hour_branch(2) == '丑'

    def test_hour_branch_all(self):
        """验证所有时支"""
        expected = [
            (23, '子'), (0, '子'),
            (1, '丑'), (2, '丑'),
            (3, '寅'), (4, '寅'),
            (5, '卯'), (6, '卯'),
            (7, '辰'), (8, '辰'),
            (9, '巳'), (10, '巳'),
            (11, '午'), (12, '午'),
            (13, '未'), (14, '未'),
            (15, '申'), (16, '申'),
            (17, '酉'), (18, '酉'),
            (19, '戌'), (20, '戌'),
            (21, '亥'), (22, '亥'),
        ]
        for hour, expected_branch in expected:
            assert get_hour_branch(hour) == expected_branch, f"Hour {hour} should be {expected_branch}"

    def test_hour_ganzhi_jia_day(self):
        """甲日子时应该是甲子时"""
        # 找一个甲日：2024-03-21 是甲申日
        stem, branch = get_hour_ganzhi(2024, 3, 21, 0)
        assert stem == '甲'
        assert branch == '子'

    def test_full_ganzhi(self):
        """完整四柱测试"""
        gz = get_full_ganzhi(datetime(2024, 3, 20, 12))
        assert 'year' in gz
        assert 'month' in gz
        assert 'day' in gz
        assert 'hour' in gz
        # 日柱应该是癸未
        assert gz['day'] == ('癸', '未')


class TestBranchUtils:
    """地支工具函数测试"""

    def test_branch_index(self):
        """地支索引转换"""
        assert get_branch_index('子') == 0
        assert get_branch_index('丑') == 1
        assert get_branch_index('亥') == 11

    def test_branch_by_index(self):
        """索引转地支"""
        assert get_branch_by_index(0) == '子'
        assert get_branch_by_index(11) == '亥'
        assert get_branch_by_index(12) == '子'  # 循环
        assert get_branch_by_index(-1) == '亥'  # 负数


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
