# tests/test_generals.py
# 天将计算测试

import pytest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from liuren.generals import (
    is_daytime, get_guiren_branch, build_generals_plate,
    get_general_for_heaven_branch
)
from liuren.constants import GENERAL_ORDER


class TestIsDaytime:
    """测试昼夜判断"""

    def test_daytime_branches(self):
        """卯辰巳午未申为昼"""
        day_branches = ['卯', '辰', '巳', '午', '未', '申']
        for branch in day_branches:
            assert is_daytime(branch) is True, f"{branch}应为昼"

    def test_nighttime_branches(self):
        """酉戌亥子丑寅为夜"""
        night_branches = ['酉', '戌', '亥', '子', '丑', '寅']
        for branch in night_branches:
            assert is_daytime(branch) is False, f"{branch}应为夜"


class TestGetGuirenBranch:
    """测试贵人起点"""

    def test_jia_wu_geng(self):
        """甲戊庚牛羊：阳贵丑，阴贵未"""
        for stem in ['甲', '戊', '庚']:
            # 昼用阳贵
            assert get_guiren_branch(stem, '午') == '丑', f"{stem}日午时应用阳贵丑"
            # 夜用阴贵
            assert get_guiren_branch(stem, '子') == '未', f"{stem}日子时应用阴贵未"

    def test_yi_ji(self):
        """乙己鼠猴乡：阳贵子，阴贵申"""
        for stem in ['乙', '己']:
            assert get_guiren_branch(stem, '午') == '子', f"{stem}日午时应用阳贵子"
            assert get_guiren_branch(stem, '子') == '申', f"{stem}日子时应用阴贵申"

    def test_bing_ding(self):
        """丙丁猪鸡位：阳贵亥，阴贵酉"""
        for stem in ['丙', '丁']:
            assert get_guiren_branch(stem, '午') == '亥', f"{stem}日午时应用阳贵亥"
            assert get_guiren_branch(stem, '子') == '酉', f"{stem}日子时应用阴贵酉"

    def test_ren_gui(self):
        """壬癸蛇兔藏：阴贵口诀"壬蛇癸兔"，壬阴贵巳，癸阴贵卯"""
        # 壬：阳贵卯，阴贵巳
        assert get_guiren_branch('壬', '午') == '卯', "壬日午时应用阳贵卯"
        assert get_guiren_branch('壬', '子') == '巳', "壬日子时应用阴贵巳"
        # 癸：阳贵巳，阴贵卯（与壬相反）
        assert get_guiren_branch('癸', '午') == '巳', "癸日午时应用阳贵巳"
        assert get_guiren_branch('癸', '子') == '卯', "癸日子时应用阴贵卯"

    def test_xin(self):
        """六辛逢马虎：阳贵午，阴贵寅"""
        assert get_guiren_branch('辛', '午') == '午', "辛日午时应用阳贵午"
        assert get_guiren_branch('辛', '子') == '寅', "辛日子时应用阴贵寅"


class TestBuildGeneralsPlate:
    """测试天将盘构建"""

    def test_generals_plate_has_12_entries(self):
        """天将盘应有12个条目"""
        gp, guiren = build_generals_plate('甲', '午')
        assert len(gp) == 12, "天将盘应有12个地支对应"

    def test_all_generals_present(self):
        """天将盘应包含所有12天将"""
        gp, guiren = build_generals_plate('甲', '午')
        generals = set(gp.values())
        expected = set(GENERAL_ORDER)
        assert generals == expected, "天将盘应包含所有12天将"

    def test_returns_guiren_branch(self):
        """应返回贵人所临地支"""
        gp, guiren = build_generals_plate('甲', '午')
        assert guiren == '丑', "甲日午时贵人应在丑位"

        gp, guiren = build_generals_plate('甲', '子')
        assert guiren == '未', "甲日子时贵人应在未位"

    def test_guiren_at_correct_branch(self):
        """贵人应在正确的地支位置"""
        # 甲日午时，阳贵丑
        gp, guiren = build_generals_plate('甲', '午')
        assert gp['丑'] == '贵人', "甲日午时贵人应在丑位"

        # 甲日子时，阴贵未
        gp, guiren = build_generals_plate('甲', '子')
        assert gp['未'] == '贵人', "甲日子时贵人应在未位"

    def test_shun_bu_when_guiren_in_hai_zi_chou_yin_mao_chen(self):
        """贵人临亥子丑寅卯辰时顺布"""
        # 甲日午时，贵人在丑（属于亥子丑寅卯辰组），应顺布
        gp, guiren = build_generals_plate('甲', '午')
        assert guiren == '丑'
        # 贵人在丑，顺布，腾蛇应在寅
        assert gp['寅'] == '腾蛇', "贵人丑顺布，腾蛇应在寅"
        assert gp['卯'] == '朱雀', "贵人丑顺布，朱雀应在卯"

    def test_ni_bu_when_guiren_in_si_wu_wei_shen_you_xu(self):
        """贵人临巳午未申酉戌时逆布"""
        # 甲日子时，贵人在未（属于巳午未申酉戌组），应逆布
        gp, guiren = build_generals_plate('甲', '子')
        assert guiren == '未'
        # 贵人在未，逆布，腾蛇应在午
        assert gp['午'] == '腾蛇', "贵人未逆布，腾蛇应在午"
        assert gp['巳'] == '朱雀', "贵人未逆布，朱雀应在巳"


class TestGetGeneralForHeavenBranch:
    """测试获取天盘地支对应的天将"""

    def test_get_existing_general(self):
        """获取存在的天将"""
        gp, _ = build_generals_plate('甲', '午')
        general = get_general_for_heaven_branch(gp, '丑')
        assert general == '贵人'

    def test_get_nonexistent_returns_empty(self):
        """获取不存在的返回空字符串"""
        gp = {'子': '贵人'}
        general = get_general_for_heaven_branch(gp, '丑')
        assert general == ''


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
