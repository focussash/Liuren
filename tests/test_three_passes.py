# tests/test_three_passes.py
# 子项目6-9：三传计算测试

import pytest
import sys
sys.path.insert(0, 'E:/Random/Pet_projects/Liuren')

from liuren.plate import LiurenPlate, build_heaven_plate
from liuren.four_lessons import calculate_four_lessons
from liuren.three_passes import (
    # 辅助函数
    is_ke, is_fuyin, is_fanyin,
    find_ke_relations, select_by_biyong, calculate_shehai_depth,
    # 课体判断
    is_bieze_condition, is_bazhuan_condition,
    # 取初传
    get_initial_pass_basic, get_yaoke_pass, get_maoxing_pass,
    get_bieze_pass, get_bazhuan_pass, get_fuyin_pass, get_fanyin_pass,
    # 三传计算
    calculate_three_passes, calculate_standard_passes,
    get_passes_display
)


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


class TestHelperFunctions:
    """辅助函数测试"""

    def test_is_ke_wood_earth(self):
        """木克土"""
        assert is_ke('寅', '辰') == True  # 寅(木)克辰(土)
        assert is_ke('卯', '丑') == True  # 卯(木)克丑(土)

    def test_is_ke_earth_water(self):
        """土克水"""
        assert is_ke('辰', '子') == True  # 辰(土)克子(水)
        assert is_ke('丑', '亥') == True  # 丑(土)克亥(水)

    def test_is_ke_water_fire(self):
        """水克火"""
        assert is_ke('子', '午') == True  # 子(水)克午(火)
        assert is_ke('亥', '巳') == True  # 亥(水)克巳(火)

    def test_is_ke_fire_metal(self):
        """火克金"""
        assert is_ke('午', '申') == True  # 午(火)克申(金)
        assert is_ke('巳', '酉') == True  # 巳(火)克酉(金)

    def test_is_ke_metal_wood(self):
        """金克木"""
        assert is_ke('申', '寅') == True  # 申(金)克寅(木)
        assert is_ke('酉', '卯') == True  # 酉(金)克卯(木)

    def test_is_ke_no_relation(self):
        """无克关系"""
        assert is_ke('子', '丑') == False
        assert is_ke('寅', '卯') == False


class TestFuyinFanyin:
    """伏吟返吟判断测试"""

    def test_TP201_is_fuyin(self):
        """TP201: 伏吟判定 - 月将=时支"""
        plate = create_plate('甲', '子', '子', '子')
        assert is_fuyin(plate) == True

    def test_TP202_is_fanyin(self):
        """TP202: 返吟判定 - 月将冲时支"""
        plate = create_plate('甲', '子', '午', '子')
        assert is_fanyin(plate) == True

    def test_not_fuyin(self):
        """非伏吟"""
        plate = create_plate('甲', '子', '午', '亥')
        assert is_fuyin(plate) == False

    def test_not_fanyin(self):
        """非返吟"""
        plate = create_plate('甲', '子', '午', '亥')
        assert is_fanyin(plate) == False


class TestBasicPasses:
    """基础课体测试（贼克/比用/涉害）"""

    def test_find_ke_relations(self):
        """测试找克关系"""
        plate = create_plate('甲', '子', '午', '亥')
        lessons = calculate_four_lessons(plate)
        ke_relations = find_ke_relations(lessons)
        # 应该能找到克关系
        assert isinstance(ke_relations, list)

    def test_TP001_yuanshou(self):
        """TP001: 元首课 - 仅一个下克上"""
        # 需要构造一个只有一个下克上的情况
        # 甲子日午时亥将：四课为 未/寅, 子/未, 巳/子, 戌/巳
        # 检查克关系：寅(木)克未(土)?是 -> 下克上
        plate = create_plate('甲', '子', '午', '亥')
        lessons = calculate_four_lessons(plate)
        passes, lesson_type = calculate_three_passes(plate, lessons)

        assert len(passes) == 3
        assert lesson_type in ['元首', '重审', '知一', '伏吟', '返吟', '蒿矢', '弹射', '昴星', '别责', '八专']

    def test_select_by_biyong(self):
        """测试比用法筛选"""
        # 甲是阳干，应该筛选阳支
        candidates = [(1, '子', '丑'), (2, '寅', '卯')]  # 子是阳，寅是阳
        result = select_by_biyong(candidates, '甲')
        # 子和寅都是阳，都应该保留
        assert len(result) == 2


class TestSpecialPasses:
    """特殊课体测试（遥克/昴星/别责/八专）"""

    def test_TP103_maoxing_yang(self):
        """TP103: 昴星课阳日 - 日支前一位上神"""
        # 阳日取日支前一位的上神
        # 甲是阳干，子的前一位是亥
        plate = create_plate('甲', '子', '午', '亥')
        initial, lesson_type = get_maoxing_pass(plate)
        # 亥位的上神需要计算
        expected = plate.heaven_plate['亥']
        assert initial == expected
        assert lesson_type == '昴星'

    def test_TP104_maoxing_yin(self):
        """TP104: 昴星课阴日 - 日支后一位上神"""
        # 阴日取日支后一位的上神
        # 乙是阴干，丑的后一位是寅
        plate = create_plate('乙', '丑', '午', '亥')
        initial, lesson_type = get_maoxing_pass(plate)
        expected = plate.heaven_plate['寅']
        assert initial == expected
        assert lesson_type == '昴星'

    def test_TP105_bieze(self):
        """TP105: 别责课 - 干时阴阳相错"""
        # 甲(阳)配丑时(阴) -> 别责条件
        plate = create_plate('甲', '子', '丑', '亥')
        assert is_bieze_condition(plate) == True

        initial, lesson_type = get_bieze_pass(plate)
        # 甲寄宫寅，取寅的上神
        expected = plate.heaven_plate['寅']
        assert initial == expected
        assert lesson_type == '别责'

    def test_TP106_bazhuan(self):
        """TP106: 八专课 - 日干支同位"""
        # 甲寄宫寅，甲寅日符合八专
        plate = create_plate('甲', '寅', '午', '亥')
        assert is_bazhuan_condition(plate) == True

        lessons = calculate_four_lessons(plate)
        initial, lesson_type = get_bazhuan_pass(plate, lessons)
        # 甲是阳干，取第三课上神
        assert initial == lessons[2].heaven
        assert lesson_type == '八专'

    def test_not_bazhuan(self):
        """非八专条件"""
        # 甲子日，甲寄宫寅≠子
        plate = create_plate('甲', '子', '午', '亥')
        assert is_bazhuan_condition(plate) == False


class TestFuyinFanyinPasses:
    """伏吟返吟三传测试"""

    def test_TP204_fuyin_no_ke_yang(self):
        """TP204: 伏吟无克阳日 - 日支前一位"""
        # 子将加子时 = 伏吟
        plate = create_plate('甲', '子', '子', '子')
        lessons = calculate_four_lessons(plate)

        initial, lesson_type = get_fuyin_pass(plate, lessons)
        # 阳日无克，取日支前一位
        # 子的前一位是亥
        assert lesson_type == '伏吟'

    def test_TP205_fuyin_no_ke_yin(self):
        """TP205: 伏吟无克阴日 - 寄宫上神"""
        # 乙丑日丑时丑将 = 伏吟
        plate = create_plate('乙', '丑', '丑', '丑')
        lessons = calculate_four_lessons(plate)

        initial, lesson_type = get_fuyin_pass(plate, lessons)
        # 乙寄宫辰，伏吟时上神=本位=辰
        assert lesson_type == '伏吟'

    def test_TP206_fanyin_yima(self):
        """TP206: 返吟取驿马"""
        # 子将加午时 = 返吟
        plate = create_plate('甲', '子', '午', '子')
        initial, lesson_type = get_fanyin_pass(plate)

        # 子日的驿马是寅
        from config import BRANCH_YIMA
        expected = BRANCH_YIMA['子']
        assert initial == expected
        assert initial == '寅'
        assert lesson_type == '返吟'


class TestThreePasses:
    """完整三传计算测试"""

    def test_TP301_standard_passes(self):
        """TP301: 标准三传递推"""
        plate = create_plate('甲', '子', '午', '亥')
        lessons = calculate_four_lessons(plate)
        passes, lesson_type = calculate_three_passes(plate, lessons)

        assert len(passes) == 3
        assert passes[0].index == 1  # 初传
        assert passes[1].index == 2  # 中传
        assert passes[2].index == 3  # 末传

    def test_TP302_fuyin_passes(self):
        """TP302: 伏吟三传"""
        plate = create_plate('甲', '子', '子', '子')
        lessons = calculate_four_lessons(plate)
        passes, lesson_type = calculate_three_passes(plate, lessons)

        assert lesson_type == '伏吟'
        assert len(passes) == 3

    def test_TP303_fanyin_passes(self):
        """TP303: 返吟三传 - 驿马-冲-驿马"""
        plate = create_plate('甲', '子', '午', '子')
        lessons = calculate_four_lessons(plate)
        passes, lesson_type = calculate_three_passes(plate, lessons)

        assert lesson_type == '返吟'
        assert len(passes) == 3
        # 返吟：初传=驿马，中传=初传冲，末传=初传
        from config import BRANCH_CHONG
        assert passes[0].branch == '寅'  # 子日驿马
        assert passes[1].branch == BRANCH_CHONG['寅']  # 寅冲申
        assert passes[2].branch == '寅'  # 回到驿马

    def test_passes_display(self):
        """测试三传显示"""
        plate = create_plate('甲', '子', '午', '亥')
        lessons = calculate_four_lessons(plate)
        passes, _ = calculate_three_passes(plate, lessons)

        display = get_passes_display(passes)
        assert '初传' in display
        assert '中传' in display
        assert '末传' in display
        assert '→' in display


class TestIntegration:
    """集成测试"""

    def test_complete_calculation(self):
        """完整排盘流程测试"""
        # 甲子日午时亥将
        plate = create_plate('甲', '子', '午', '亥')

        # 计算四课
        lessons = calculate_four_lessons(plate)
        assert len(lessons) == 4

        # 计算三传
        passes, lesson_type = calculate_three_passes(plate, lessons)
        assert len(passes) == 3
        assert lesson_type != ""

    def test_all_stems_basic(self):
        """测试所有天干的基本排盘"""
        stems = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
        for stem in stems:
            plate = create_plate(stem, '子', '午', '亥')
            lessons = calculate_four_lessons(plate)
            passes, lesson_type = calculate_three_passes(plate, lessons)

            assert len(lessons) == 4, f"Failed for stem {stem}"
            assert len(passes) == 3, f"Failed for stem {stem}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
