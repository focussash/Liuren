# tests/test_moon_general.py
# 子项目3：月将计算测试

import pytest
import sys
sys.path.insert(0, 'E:/Random/Pet_projects/Liuren')

from datetime import datetime
from liuren.moon_general import get_moon_general, get_moon_general_by_zhongqi


class TestMoonGeneral:
    """月将计算测试 - 按12中气验证"""

    def test_MG001_after_yushui(self):
        """MG001: 雨水后月将 - 亥将(登明)"""
        branch, name = get_moon_general(datetime(2024, 2, 20))
        assert branch == '亥'
        assert name == '登明'

    def test_MG002_after_chunfen(self):
        """MG002: 春分后月将 - 戌将(河魁)"""
        branch, name = get_moon_general(datetime(2024, 3, 25))
        assert branch == '戌'
        assert name == '河魁'

    def test_MG003_after_guyu(self):
        """MG003: 谷雨后月将 - 酉将(从魁)"""
        branch, name = get_moon_general(datetime(2024, 4, 25))
        assert branch == '酉'
        assert name == '从魁'

    def test_MG004_after_xiaoman(self):
        """MG004: 小满后月将 - 申将(传送)"""
        branch, name = get_moon_general(datetime(2024, 5, 25))
        assert branch == '申'
        assert name == '传送'

    def test_MG005_after_xiazhi(self):
        """MG005: 夏至后月将 - 未将(小吉)"""
        branch, name = get_moon_general(datetime(2024, 6, 25))
        assert branch == '未'
        assert name == '小吉'

    def test_MG006_after_dashu(self):
        """MG006: 大暑后月将 - 午将(胜光)"""
        branch, name = get_moon_general(datetime(2024, 7, 25))
        assert branch == '午'
        assert name == '胜光'

    def test_MG007_after_chushu(self):
        """MG007: 处暑后月将 - 巳将(太乙)"""
        branch, name = get_moon_general(datetime(2024, 8, 25))
        assert branch == '巳'
        assert name == '太乙'

    def test_MG008_after_qiufen(self):
        """MG008: 秋分后月将 - 辰将(天罡)"""
        branch, name = get_moon_general(datetime(2024, 9, 25))
        assert branch == '辰'
        assert name == '天罡'

    def test_MG009_after_shuangjiang(self):
        """MG009: 霜降后月将 - 卯将(太冲)"""
        branch, name = get_moon_general(datetime(2024, 10, 25))
        assert branch == '卯'
        assert name == '太冲'

    def test_MG010_after_xiaoxue(self):
        """MG010: 小雪后月将 - 寅将(功曹)"""
        branch, name = get_moon_general(datetime(2024, 11, 25))
        assert branch == '寅'
        assert name == '功曹'

    def test_MG011_after_dongzhi(self):
        """MG011: 冬至后月将 - 丑将(大吉)"""
        branch, name = get_moon_general(datetime(2024, 12, 25))
        assert branch == '丑'
        assert name == '大吉'

    def test_MG012_after_dahan(self):
        """MG012: 大寒后月将 - 子将(神后)"""
        branch, name = get_moon_general(datetime(2025, 1, 25))
        assert branch == '子'
        assert name == '神后'


class TestMoonGeneralByZhongqi:
    """根据中气名称获取月将测试"""

    def test_by_zhongqi_chunfen(self):
        """春分对应戌将"""
        branch, name = get_moon_general_by_zhongqi('春分')
        assert branch == '戌'
        assert name == '河魁'

    def test_by_zhongqi_xiazhi(self):
        """夏至对应未将"""
        branch, name = get_moon_general_by_zhongqi('夏至')
        assert branch == '未'
        assert name == '小吉'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
