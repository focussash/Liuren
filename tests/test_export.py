# tests/test_export.py
# 子项目14：导出功能测试

import pytest
import sys
import os
import re
import tempfile
import shutil
from datetime import datetime
from unittest.mock import MagicMock, patch

sys.path.insert(0, 'E:/Random/Pet_projects/Liuren')

from liuren.plate import LiurenPlate, Lesson, Pass, build_heaven_plate
from liuren.four_lessons import calculate_four_lessons
from liuren.three_passes import calculate_three_passes
from export import save_screenshot, export_plate_text, save_to_file


def create_test_plate() -> LiurenPlate:
    """辅助函数：创建完整的测试用式盘"""
    day_stem = '甲'
    day_branch = '子'
    hour_branch = '午'
    moon_general = '亥'
    moon_general_name = '登明'

    heaven_plate = build_heaven_plate(moon_general, hour_branch)
    plate = LiurenPlate(
        day_stem=day_stem,
        day_branch=day_branch,
        hour_branch=hour_branch,
        moon_general=moon_general,
        moon_general_name=moon_general_name,
        heaven_plate=heaven_plate
    )

    # 计算四课和三传
    lessons = calculate_four_lessons(plate)
    passes, lesson_type = calculate_three_passes(plate, lessons)

    # 设置到plate对象
    plate.lessons = lessons
    plate.passes = passes
    plate.lesson_type = lesson_type

    return plate


class TestScreenshot:
    """截图功能测试"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """测试前后清理exports目录"""
        # 保存原始工作目录
        self.original_cwd = os.getcwd()
        # 创建临时目录作为测试工作目录
        self.test_dir = tempfile.mkdtemp()
        os.chdir(self.test_dir)
        yield
        # 清理
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_EX001_screenshot_saves_png(self):
        """EX001: Screenshot saves PNG file"""
        # 创建模拟的pygame screen
        mock_screen = MagicMock()

        with patch('pygame.image.save') as mock_save:
            filepath = save_screenshot(mock_screen)

            # 验证调用了pygame.image.save
            mock_save.assert_called_once()
            call_args = mock_save.call_args

            # 验证第一个参数是screen
            assert call_args[0][0] == mock_screen

            # 验证文件路径以.png结尾
            assert filepath.endswith('.png')

            # 验证在exports目录下
            assert 'exports' in filepath

    def test_EX004_screenshot_timestamp_filename(self):
        """EX004: Auto-generated filenames use timestamps"""
        mock_screen = MagicMock()

        with patch('pygame.image.save'):
            filepath = save_screenshot(mock_screen)

            # 验证文件名格式: liuren_YYYYMMDD_HHMMSS.png
            filename = os.path.basename(filepath)
            pattern = r'^liuren_\d{8}_\d{6}\.png$'
            assert re.match(pattern, filename), f"Filename {filename} doesn't match expected pattern"

    def test_screenshot_custom_filename(self):
        """测试自定义文件名"""
        mock_screen = MagicMock()

        with patch('pygame.image.save'):
            filepath = save_screenshot(mock_screen, "my_custom_name.png")

            assert filepath.endswith("my_custom_name.png")

    def test_screenshot_adds_png_extension(self):
        """测试自动添加.png扩展名"""
        mock_screen = MagicMock()

        with patch('pygame.image.save'):
            filepath = save_screenshot(mock_screen, "no_extension")

            assert filepath.endswith(".png")

    def test_screenshot_creates_exports_dir(self):
        """测试创建exports目录"""
        mock_screen = MagicMock()

        # 确保exports目录不存在
        if os.path.exists("exports"):
            shutil.rmtree("exports")

        with patch('pygame.image.save'):
            save_screenshot(mock_screen)

            # 验证创建了exports目录
            assert os.path.exists("exports")


class TestTextExport:
    """文本导出功能测试"""

    def test_EX002_text_export_format(self):
        """EX002: Text export generates correct format"""
        plate = create_test_plate()
        text = export_plate_text(plate)

        # 验证包含关键部分
        assert '赛博大六壬排盘结果' in text
        assert '【基本信息】' in text
        assert '【四课】' in text
        assert '【三传】' in text
        assert '【推导过程】' in text

        # 验证日干支信息
        assert f"日干支: {plate.day_stem}{plate.day_branch}" in text
        assert f"时支: {plate.hour_branch}" in text
        assert f"月将: {plate.moon_general}" in text
        assert f"课体: {plate.lesson_type}" in text

    def test_text_export_four_lessons(self):
        """测试四课显示"""
        plate = create_test_plate()
        text = export_plate_text(plate)

        # 验证四课标题
        assert '一课' in text
        assert '二课' in text
        assert '三课' in text
        assert '四课' in text
        assert '天盘' in text
        assert '地盘' in text

    def test_text_export_three_passes(self):
        """测试三传显示"""
        plate = create_test_plate()
        text = export_plate_text(plate)

        # 验证三传标签
        assert '初传' in text
        assert '中传' in text
        assert '末传' in text
        assert '→' in text

    def test_text_export_derivation_log(self):
        """测试推导过程显示"""
        plate = create_test_plate()
        text = export_plate_text(plate)

        # 验证推导日志内容（由calculate_three_passes生成）
        assert '开始计算三传' in text

    def test_text_export_timestamp(self):
        """测试生成时间戳"""
        plate = create_test_plate()
        text = export_plate_text(plate)

        assert '生成时间:' in text


class TestFileSave:
    """文件保存功能测试"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """测试前后清理exports目录"""
        self.original_cwd = os.getcwd()
        self.test_dir = tempfile.mkdtemp()
        os.chdir(self.test_dir)
        yield
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_EX003_file_save_creates_txt(self):
        """EX003: File save creates TXT file"""
        plate = create_test_plate()
        filepath = save_to_file(plate)

        # 验证文件存在
        assert os.path.exists(filepath)

        # 验证是txt文件
        assert filepath.endswith('.txt')

        # 验证文件非空
        assert os.path.getsize(filepath) > 0

        # 验证内容正确
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            assert '赛博大六壬排盘结果' in content
            assert plate.day_stem in content

    def test_EX004_file_save_timestamp_filename(self):
        """EX004: Auto-generated filenames use timestamps"""
        plate = create_test_plate()
        filepath = save_to_file(plate)

        # 验证文件名格式: liuren_YYYYMMDD_HHMMSS.txt
        filename = os.path.basename(filepath)
        pattern = r'^liuren_\d{8}_\d{6}\.txt$'
        assert re.match(pattern, filename), f"Filename {filename} doesn't match expected pattern"

    def test_file_save_custom_filename(self):
        """测试自定义文件名"""
        plate = create_test_plate()
        filepath = save_to_file(plate, "custom_export.txt")

        assert filepath.endswith("custom_export.txt")
        assert os.path.exists(filepath)

    def test_file_save_adds_txt_extension(self):
        """测试自动添加.txt扩展名"""
        plate = create_test_plate()
        filepath = save_to_file(plate, "no_extension")

        assert filepath.endswith(".txt")

    def test_file_save_creates_exports_dir(self):
        """测试创建exports目录"""
        plate = create_test_plate()

        # 确保exports目录不存在
        if os.path.exists("exports"):
            shutil.rmtree("exports")

        save_to_file(plate)

        # 验证创建了exports目录
        assert os.path.exists("exports")

    def test_file_save_utf8_encoding(self):
        """测试UTF-8编码"""
        plate = create_test_plate()
        filepath = save_to_file(plate)

        # 验证可以正确读取中文
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            # 确保中文字符正确
            assert '甲' in content or '乙' in content
            assert '子' in content or '丑' in content


class TestIntegration:
    """集成测试"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """测试前后清理"""
        self.original_cwd = os.getcwd()
        self.test_dir = tempfile.mkdtemp()
        os.chdir(self.test_dir)
        yield
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_full_export_workflow(self):
        """完整导出工作流测试"""
        plate = create_test_plate()

        # 导出文本
        text = export_plate_text(plate)
        assert len(text) > 0

        # 保存到文件
        filepath = save_to_file(plate)
        assert os.path.exists(filepath)

        # 读取并验证
        with open(filepath, 'r', encoding='utf-8') as f:
            saved_content = f.read()
            assert saved_content == text

    def test_multiple_exports(self):
        """测试多次导出生成不同文件"""
        plate = create_test_plate()

        import time

        filepath1 = save_to_file(plate)
        time.sleep(1)  # 确保时间戳不同
        filepath2 = save_to_file(plate)

        # 两个文件应该是不同的
        assert filepath1 != filepath2
        assert os.path.exists(filepath1)
        assert os.path.exists(filepath2)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
