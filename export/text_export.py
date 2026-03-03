# export/text_export.py
# 文本导出功能

import os
from datetime import datetime
from typing import List

from liuren.plate import LiurenPlate, Lesson, Pass, EARTHLY_BRANCHES
from config import STEM_WUXING, BRANCH_WUXING


def export_plate_text(plate: LiurenPlate) -> str:
    """
    Generate formatted text description of the plate.

    Args:
        plate: LiurenPlate object containing the divination data.

    Returns:
        Formatted text string describing the plate.
    """
    lines = []

    # Header
    lines.append("=" * 40)
    lines.append("赛博大六壬排盘结果")
    lines.append("=" * 40)
    lines.append("")

    # Basic information
    lines.append("【基本信息】")
    lines.append(f"日干支: {plate.day_stem}{plate.day_branch}")
    lines.append(f"时支: {plate.hour_branch}")
    lines.append(f"月将: {plate.moon_general} ({plate.moon_general_name})")
    lines.append(f"课体: {plate.lesson_type}")
    lines.append("")

    # Four lessons
    lines.append("【四课】")
    if plate.lessons:
        # Header row
        lines.append("      一课  二课  三课  四课")

        # Heaven row (上神)
        heaven_row = "天盘: "
        for lesson in plate.lessons:
            heaven_row += f" {lesson.heaven}   "
        lines.append(heaven_row.rstrip())

        # Earth row (地盘)
        earth_row = "地盘: "
        for lesson in plate.lessons:
            earth_row += f" {lesson.earth}   "
        lines.append(earth_row.rstrip())
    else:
        lines.append("(未计算)")
    lines.append("")

    # Three passes
    lines.append("【三传】")
    if plate.passes:
        lines.append("初传 → 中传 → 末传")
        passes_str = f" {plate.passes[0].branch}  →  {plate.passes[1].branch}  →  {plate.passes[2].branch}"
        lines.append(passes_str)
    else:
        lines.append("(未计算)")
    lines.append("")

    # Derivation process
    lines.append("【推导过程】")
    if plate.derivation_log:
        for log_line in plate.derivation_log:
            lines.append(log_line)
    else:
        lines.append("(无推导记录)")
    lines.append("")

    # Footer
    lines.append("=" * 40)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines.append(f"生成时间: {timestamp}")
    lines.append("=" * 40)

    return "\n".join(lines)


def save_to_file(plate: LiurenPlate, filename: str = None) -> str:
    """
    Save plate text to file.

    Args:
        plate: LiurenPlate object containing the divination data.
        filename: Optional filename. Auto-generates timestamped filename if not provided.

    Returns:
        The saved filename.
    """
    # Ensure exports directory exists
    export_dir = "exports"
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)

    # Generate filename if not provided
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"liuren_{timestamp}.txt"

    # Ensure .txt extension
    if not filename.lower().endswith('.txt'):
        filename += '.txt'

    # Build full path
    filepath = os.path.join(export_dir, filename)

    # Generate text content
    content = export_plate_text(plate)

    # Save to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    return filepath


def export_plate_text_for_llm(plate: LiurenPlate) -> str:
    """Generate plate text optimized for LLM interpretation.

    Includes 天将, 五行 annotations, full heaven-earth mapping,
    and 贵人 info. Omits decorative headers and timestamps.
    """
    lines = []

    # Basic info
    stem_wx = STEM_WUXING.get(plate.day_stem, '')
    branch_wx = BRANCH_WUXING.get(plate.day_branch, '')
    lines.append(f"日干支: {plate.day_stem}{plate.day_branch}"
                 f"（{plate.day_stem}属{stem_wx}，{plate.day_branch}属{branch_wx}）")
    lines.append(f"时支: {plate.hour_branch}")
    lines.append(f"月将: {plate.moon_general}（{plate.moon_general_name}）")
    lines.append(f"课体: {plate.lesson_type}")
    if plate.guiren_branch:
        lines.append(f"贵人: {plate.guiren_branch}宫")
    lines.append("")

    # Heaven-Earth plate mapping
    lines.append("【天地盘】")
    if plate.heaven_plate:
        heaven_row = "天盘: "
        earth_row = "地盘: "
        for branch in EARTHLY_BRANCHES:
            heaven = plate.heaven_plate.get(branch, '?')
            heaven_row += f"{heaven} "
            earth_row += f"{branch} "
        lines.append(earth_row.rstrip())
        lines.append(heaven_row.rstrip())
    lines.append("")

    # Four lessons with generals
    lines.append("【四课】")
    if plate.lessons:
        lines.append("      一课  二课  三课  四课")
        generals = [l.general if l.general else "--" for l in plate.lessons]
        lines.append(f"天将: {generals[0]:4s}{generals[1]:4s}{generals[2]:4s}{generals[3]}")
        heavens = [l.heaven for l in plate.lessons]
        lines.append(f"天盘: {heavens[0]:4s}{heavens[1]:4s}{heavens[2]:4s}{heavens[3]}")
        earths = [l.earth for l in plate.lessons]
        lines.append(f"地盘: {earths[0]:4s}{earths[1]:4s}{earths[2]:4s}{earths[3]}")

        # Add wuxing relationships for each lesson
        lines.append("")
        for lesson in plate.lessons:
            h_wx = BRANCH_WUXING.get(lesson.heaven, '?')
            e_wx = BRANCH_WUXING.get(lesson.earth, '?')
            lines.append(f"  第{lesson.index}课: {lesson.heaven}({h_wx})/"
                        f"{lesson.earth}({e_wx}) 天将:{lesson.general}")
    lines.append("")

    # Three passes with generals
    lines.append("【三传】")
    if plate.passes:
        pass_names = ['初传', '中传', '末传']
        for i, p in enumerate(plate.passes):
            p_wx = BRANCH_WUXING.get(p.branch, '?')
            lines.append(f"  {pass_names[i]}: {p.branch}({p_wx}) 天将:{p.general}")
    lines.append("")

    # Generals plate
    if plate.generals_plate:
        lines.append("【天将盘】")
        for branch in EARTHLY_BRANCHES:
            general = plate.generals_plate.get(branch, '')
            if general:
                lines.append(f"  {branch}宫: {general}")

    return "\n".join(lines)
