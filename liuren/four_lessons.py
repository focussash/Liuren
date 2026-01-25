# liuren/four_lessons.py
# 四课计算模块

from typing import List
from config import STEM_JIGONG
from liuren.plate import LiurenPlate, Lesson, get_heaven_branch


def calculate_four_lessons(plate: LiurenPlate) -> List[Lesson]:
    """
    计算四课

    四课算法：
    一课：日干寄宫位置的天盘地支 / 日干寄宫
    二课：一课天盘地支位置的天盘地支 / 一课天盘地支
    三课：日支位置的天盘地支 / 日支
    四课：三课天盘地支位置的天盘地支 / 三课天盘地支

    Args:
        plate: LiurenPlate对象（需包含day_stem, day_branch, heaven_plate）

    Returns:
        List[Lesson]: 四课列表
    """
    # 获取日干寄宫
    jigong = STEM_JIGONG[plate.day_stem]

    # 一课: 寄宫上神 / 寄宫
    lesson1_heaven = get_heaven_branch(plate.heaven_plate, jigong)
    lesson1 = Lesson(heaven=lesson1_heaven, earth=jigong, index=1)

    # 二课: 一课天盘上神 / 一课天盘
    lesson2_heaven = get_heaven_branch(plate.heaven_plate, lesson1_heaven)
    lesson2 = Lesson(heaven=lesson2_heaven, earth=lesson1_heaven, index=2)

    # 三课: 日支上神 / 日支
    lesson3_heaven = get_heaven_branch(plate.heaven_plate, plate.day_branch)
    lesson3 = Lesson(heaven=lesson3_heaven, earth=plate.day_branch, index=3)

    # 四课: 三课天盘上神 / 三课天盘
    lesson4_heaven = get_heaven_branch(plate.heaven_plate, lesson3_heaven)
    lesson4 = Lesson(heaven=lesson4_heaven, earth=lesson3_heaven, index=4)

    return [lesson1, lesson2, lesson3, lesson4]


def get_lesson_display(lessons: List[Lesson]) -> str:
    """
    获取四课的显示字符串

    Args:
        lessons: 四课列表

    Returns:
        格式化的四课字符串
    """
    lines = []
    lines.append("  一课  二课  三课  四课")
    lines.append(f"  {lessons[0].heaven}    {lessons[1].heaven}    {lessons[2].heaven}    {lessons[3].heaven}")
    lines.append(f"  {lessons[0].earth}    {lessons[1].earth}    {lessons[2].earth}    {lessons[3].earth}")
    return '\n'.join(lines)
