# liuren/derivation.py
# 详细推导过程生成器

from typing import List
from config import (
    STEM_JIGONG, STEM_WUXING, BRANCH_WUXING, WUXING_KE,
    STEM_YINYANG, BRANCH_YINYANG, EARTHLY_BRANCHES,
    BRANCH_CHONG, MOON_GENERALS
)
from liuren.plate import LiurenPlate, Lesson, Pass
from liuren.constants import (
    MOON_GENERAL_NAMES, ZHONGQI_MOON_GENERAL,
    STEM_GUIREN, GENERAL_ORDER
)


def generate_detailed_derivation(plate: LiurenPlate,
                                  lessons: List[Lesson],
                                  passes: List[Pass],
                                  lesson_type: str) -> List[str]:
    """
    Generate comprehensive step-by-step derivation of the 四课三传.

    Returns:
        List of text lines for display in the overlay.
    """
    lines = []

    def add(text):
        lines.append(text)

    def blank():
        lines.append("")

    # ===== Header =====
    add(f"日干支：{plate.day_stem}{plate.day_branch}")
    add(f"时  支：{plate.hour_branch}")
    blank()

    # ===== 1. 月将确定 =====
    add("━━━━━ 一、月将确定 ━━━━━")
    moon_name = MOON_GENERAL_NAMES.get(plate.moon_general, "")
    add(f"月将：{plate.moon_general}（{moon_name}）")
    # Show zhongqi mapping
    for zq, br in ZHONGQI_MOON_GENERAL.items():
        if br == plate.moon_general:
            add(f"中气「{zq}」后用{br}将")
            break
    blank()

    # ===== 2. 天盘旋转 =====
    add("━━━━━ 二、天盘旋转 ━━━━━")
    add(f"口诀：月将{plate.moon_general}加临时支{plate.hour_branch}")
    moon_idx = EARTHLY_BRANCHES.index(plate.moon_general)
    hour_idx = EARTHLY_BRANCHES.index(plate.hour_branch)
    offset = moon_idx - hour_idx
    add(f"偏移量：{plate.moon_general}({moon_idx}) - {plate.hour_branch}({hour_idx}) = {offset}")
    blank()
    add("天地盘对应表：")
    earth_row = "地盘：" + " ".join(EARTHLY_BRANCHES)
    add(earth_row)
    heaven_row = "天盘：" + " ".join(
        plate.heaven_plate[b] for b in EARTHLY_BRANCHES
    )
    add(heaven_row)
    blank()

    # ===== 3. 四课推导 =====
    add("━━━━━ 三、四课推导 ━━━━━")
    jigong = STEM_JIGONG[plate.day_stem]
    add(f"日干{plate.day_stem}的寄宫：{jigong}")
    add(f"  口诀：甲寅乙辰丙巳丁未戊巳己未庚申辛戌壬亥癸丑")
    blank()

    if len(lessons) >= 4:
        # Lesson 1
        add(f"一课：地盘{lessons[0].earth}（日干寄宫）")
        add(f"      天盘上神：{lessons[0].earth}位上天盘为{lessons[0].heaven}")
        if lessons[0].general:
            add(f"      天将：{lessons[0].general}")
        blank()

        # Lesson 2
        add(f"二课：地盘{lessons[1].earth}（一课天盘{lessons[0].heaven}）")
        add(f"      天盘上神：{lessons[1].earth}位上天盘为{lessons[1].heaven}")
        if lessons[1].general:
            add(f"      天将：{lessons[1].general}")
        blank()

        # Lesson 3
        add(f"三课：地盘{lessons[2].earth}（日支{plate.day_branch}）")
        add(f"      天盘上神：{lessons[2].earth}位上天盘为{lessons[2].heaven}")
        if lessons[2].general:
            add(f"      天将：{lessons[2].general}")
        blank()

        # Lesson 4
        add(f"四课：地盘{lessons[3].earth}（三课天盘{lessons[2].heaven}）")
        add(f"      天盘上神：{lessons[3].earth}位上天盘为{lessons[3].heaven}")
        if lessons[3].general:
            add(f"      天将：{lessons[3].general}")
        blank()

        # Summary table
        add("      一课  二课  三课  四课")
        generals = [l.general[:2] if l.general else "  " for l in lessons[:4]]
        add(f" 将：  {generals[0]}  {generals[1]}  {generals[2]}  {generals[3]}")
        add(f" 天：  {lessons[0].heaven}    {lessons[1].heaven}    {lessons[2].heaven}    {lessons[3].heaven}")
        add(f" 地：  {lessons[0].earth}    {lessons[1].earth}    {lessons[2].earth}    {lessons[3].earth}")
        blank()

    # ===== 4. 三传推导 =====
    add("━━━━━ 四、三传推导 ━━━━━")
    add(f"课体：{lesson_type}")
    blank()

    # Check fuyin/fanyin
    is_fuyin = plate.moon_general == plate.hour_branch
    is_fanyin = BRANCH_CHONG.get(plate.moon_general) == plate.hour_branch

    if is_fuyin:
        add("判断：月将等于时支 → 伏吟")
        add("（伏吟：天地盘完全重合，上下一体不动）")
    elif is_fanyin:
        add("判断：月将冲时支 → 返吟")
        add("（返吟：天地盘六冲对照，阴阳相对）")
    else:
        # Show ke relations
        add("查找四课中的克关系：")
        ke_found = []
        for i, lesson in enumerate(lessons[:4]):
            h_wx = BRANCH_WUXING.get(lesson.heaven, "")
            e_wx = BRANCH_WUXING.get(lesson.earth, "")
            # Check 下克上 (earth ke heaven)
            if WUXING_KE.get(e_wx) == h_wx:
                add(f"  第{lesson.index}课：{lesson.earth}({e_wx})克{lesson.heaven}({h_wx}) ← 下克上")
                ke_found.append(lesson.index)
            else:
                add(f"  第{lesson.index}课：{lesson.earth}({e_wx})与{lesson.heaven}({h_wx}) 无克")

        blank()
        if len(ke_found) == 0:
            add("无下克上 → 检查特殊课体")
        elif len(ke_found) == 1:
            add(f"仅第{ke_found[0]}课有下克上 → 元首课")
            add("取被克者（天盘上神）为初传")
        elif len(ke_found) > 1:
            add(f"有{len(ke_found)}个下克上 → 需进一步判断")
            day_yy = STEM_YINYANG[plate.day_stem]
            add(f"日干{plate.day_stem}为{day_yy}，比用法：取被克者阴阳与日干相同者")

    blank()

    # Show passes
    if len(passes) >= 3:
        add(f"初传：{passes[0].branch}")
        if passes[0].general:
            add(f"  天将：{passes[0].general}")

        add(f"中传：初传{passes[0].branch}位上天盘 → {passes[1].branch}")
        if passes[1].general:
            add(f"  天将：{passes[1].general}")

        add(f"末传：中传{passes[1].branch}位上天盘 → {passes[2].branch}")
        if passes[2].general:
            add(f"  天将：{passes[2].general}")

        blank()
        add(f"三传：{passes[0].branch} → {passes[1].branch} → {passes[2].branch}")
    blank()

    # ===== 5. 天将推导 =====
    add("━━━━━ 五、天将推导 ━━━━━")
    if plate.guiren_branch:
        yang_gui, yin_gui = STEM_GUIREN.get(plate.day_stem, ("", ""))
        add(f"日干{plate.day_stem}的贵人：")
        add(f"  阳贵人：{yang_gui}  阴贵人：{yin_gui}")
        add(f"  口诀：甲戊庚牛羊，乙己鼠猴乡，")
        add(f"        丙丁猪鸡位，壬癸兔蛇藏，六辛逢马虎")

        from liuren.generals import DAY_BRANCHES
        is_day = plate.hour_branch in DAY_BRANCHES
        add(f"  时支{plate.hour_branch}为{'昼' if is_day else '夜'}时")
        add(f"  取{'阳' if is_day else '阴'}贵人 → {plate.guiren_branch}")
        blank()

        # Shun/Ni
        SHUN = {'亥', '子', '丑', '寅', '卯', '辰'}
        is_shun = plate.guiren_branch in SHUN
        add(f"贵人临{plate.guiren_branch}{'（顺布）' if is_shun else '（逆布）'}")

        # Show generals plate
        add("天将盘：")
        for branch in EARTHLY_BRANCHES:
            gen = plate.generals_plate.get(branch, "")
            if gen:
                add(f"  {branch}位：{gen}")

    return lines
