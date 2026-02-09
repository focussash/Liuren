# renderer3d/xiu_data.py
# Star map data for 28 lunar mansions and 4 sacred beast outlines

from typing import NamedTuple, List, Tuple


class MansionData(NamedTuple):
    name: str                                # 星宿名 ('角','亢',...)
    star_offsets: List[Tuple[float, float]]  # (dr, dtheta) per star
    lines: List[Tuple[int, int]]             # internal connections (from_idx, to_idx)


class BeastOutline(NamedTuple):
    name: str                                          # '青龙','白虎',...
    vertices: List[Tuple[float, float]]                # (r_fraction, theta_deg)
    lines: List[Tuple[int, int]]                       # line segments
    color: Tuple[float, float, float, float]           # RGBA


# ─────────────────────────────────────────────────────────────────────
# 28 Mansions star data
# Offset coordinate system:
#   dr:     radial offset as fraction of ring radius (-0.15 ~ +0.15)
#   dtheta: angular offset in degrees relative to mansion center (~±3.5°)
# Each mansion's first star (index 0) is the anchor/main star.
# ─────────────────────────────────────────────────────────────────────

# ═══════════════════════════════════════════════════════════════════
# 东方青龙 (Eastern Azure Dragon)
# ═══════════════════════════════════════════════════════════════════

_JIAO = MansionData(  # 角 - 2 stars (horn tips)
    name='角',
    star_offsets=[
        (0.0, 0.0),       # 角宿一 (α Vir / Spica)
        (0.05, 2.5),      # 角宿二 (ζ Vir)
    ],
    lines=[(0, 1)],
)

_KANG = MansionData(  # 亢 - 4 stars (neck)
    name='亢',
    star_offsets=[
        (0.0, 0.0),       # 亢宿一
        (0.04, 1.8),      # 亢宿二
        (0.08, 0.5),      # 亢宿三
        (0.03, -1.5),     # 亢宿四
    ],
    lines=[(0, 1), (1, 2), (2, 3), (3, 0)],  # quadrilateral
)

_DI = MansionData(  # 氐 - 4 stars (root/base)
    name='氐',
    star_offsets=[
        (0.0, 0.0),
        (0.06, 1.5),
        (0.10, 0.8),
        (0.04, -1.2),
    ],
    lines=[(0, 1), (1, 2), (2, 3), (3, 0)],
)

_FANG = MansionData(  # 房 - 4 stars (room/chamber)
    name='房',
    star_offsets=[
        (0.0, 0.0),
        (0.0, 1.5),
        (0.07, 0.0),
        (0.07, 1.5),
    ],
    lines=[(0, 1), (2, 3), (0, 2), (1, 3)],  # rectangle
)

_XIN = MansionData(  # 心 - 3 stars (heart, Antares center)
    name='心',
    star_offsets=[
        (0.0, 0.0),       # 心宿二 (Antares) - anchor
        (-0.05, 2.0),     # 心宿一
        (0.05, -2.0),     # 心宿三
    ],
    lines=[(1, 0), (0, 2)],  # line through center
)

_WEI = MansionData(  # 尾 - 6 stars (tail)
    name='尾',
    star_offsets=[
        (0.0, 0.0),
        (0.03, 1.2),
        (0.06, 2.2),
        (0.08, 3.0),
        (0.04, -1.0),
        (-0.02, -2.2),
    ],
    lines=[(5, 4), (4, 0), (0, 1), (1, 2), (2, 3)],  # curved tail
)

_JI = MansionData(  # 箕 - 4 stars (winnowing basket)
    name='箕',
    star_offsets=[
        (0.0, 0.0),
        (0.08, 0.0),
        (-0.02, 2.5),
        (0.10, 2.5),
    ],
    lines=[(0, 1), (0, 2), (1, 3), (2, 3)],  # trapezoid
)

# ═══════════════════════════════════════════════════════════════════
# 北方玄武 (Northern Black Tortoise)
# ═══════════════════════════════════════════════════════════════════

_DOU = MansionData(  # 斗 - 6 stars (dipper/ladle)
    name='斗',
    star_offsets=[
        (0.0, 0.0),
        (0.04, 1.5),
        (0.08, 2.8),
        (0.10, 1.0),
        (0.06, -0.5),
        (0.02, -1.8),
    ],
    lines=[(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0)],  # hexagon
)

_NIU = MansionData(  # 牛 - 6 stars (ox)
    name='牛',
    star_offsets=[
        (0.0, 0.0),
        (0.04, 1.2),
        (0.08, 2.0),
        (0.03, -1.0),
        (0.07, -1.8),
        (0.11, -0.5),
    ],
    lines=[(0, 1), (1, 2), (0, 3), (3, 4), (4, 5)],
)

_NV = MansionData(  # 女 - 4 stars (maiden)
    name='女',
    star_offsets=[
        (0.0, 0.0),
        (0.06, 1.5),
        (0.03, -1.5),
        (0.09, 0.0),
    ],
    lines=[(0, 1), (0, 2), (1, 3), (2, 3)],  # diamond
)

_XU = MansionData(  # 虚 - 2 stars (emptiness)
    name='虚',
    star_offsets=[
        (0.0, 0.0),
        (0.06, 2.0),
    ],
    lines=[(0, 1)],
)

_WEI2 = MansionData(  # 危 - 3 stars (rooftop)
    name='危',
    star_offsets=[
        (0.0, 0.0),
        (0.05, 2.0),
        (0.08, -1.0),
    ],
    lines=[(0, 1), (0, 2)],  # V-shape
)

_SHI = MansionData(  # 室 - 2 stars (encampment)
    name='室',
    star_offsets=[
        (0.0, 0.0),
        (0.06, 2.2),
    ],
    lines=[(0, 1)],
)

_BI2 = MansionData(  # 壁 - 2 stars (wall)
    name='壁',
    star_offsets=[
        (0.0, 0.0),
        (0.05, 1.8),
    ],
    lines=[(0, 1)],
)

# ═══════════════════════════════════════════════════════════════════
# 西方白虎 (Western White Tiger)
# ═══════════════════════════════════════════════════════════════════

_KUI = MansionData(  # 奎 - 8 stars (legs, stride - simplified from 16)
    name='奎',
    star_offsets=[
        (0.0, 0.0),
        (0.04, 1.5),
        (0.08, 2.8),
        (0.12, 1.5),
        (0.10, -0.5),
        (0.06, -2.0),
        (-0.02, -1.5),
        (0.02, 0.8),
    ],
    lines=[(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 0), (7, 0)],
)

_LOU = MansionData(  # 娄 - 3 stars (bond/tie)
    name='娄',
    star_offsets=[
        (0.0, 0.0),
        (0.05, 1.8),
        (0.03, -1.5),
    ],
    lines=[(0, 1), (0, 2)],
)

_WEI3 = MansionData(  # 胃 - 3 stars (stomach)
    name='胃',
    star_offsets=[
        (0.0, 0.0),
        (0.04, 1.6),
        (0.06, -1.0),
    ],
    lines=[(0, 1), (1, 2), (2, 0)],  # triangle
)

_MAO = MansionData(  # 昴 - 6 stars (Pleiades cluster, simplified)
    name='昴',
    star_offsets=[
        (0.0, 0.0),       # central star
        (0.03, 1.2),
        (0.04, -0.8),
        (0.06, 0.5),
        (0.02, -1.5),
        (0.05, 2.0),
    ],
    lines=[(0, 1), (0, 2), (0, 3), (0, 4), (0, 5)],  # radial cluster
)

_BI3 = MansionData(  # 毕 - 6 stars (net, Hyades V-shape)
    name='毕',
    star_offsets=[
        (0.0, 0.0),       # vertex of V
        (0.04, 1.5),
        (0.08, 2.8),
        (0.04, -1.5),
        (0.08, -2.8),
        (0.12, 0.0),
    ],
    lines=[(0, 1), (1, 2), (0, 3), (3, 4), (0, 5)],  # V + spike
)

_ZI = MansionData(  # 觜 - 3 stars (beak)
    name='觜',
    star_offsets=[
        (0.0, 0.0),
        (0.04, 1.5),
        (0.04, -1.5),
    ],
    lines=[(0, 1), (0, 2), (1, 2)],  # small triangle
)

_SHEN = MansionData(  # 参 - 7 stars (Orion's belt region)
    name='参',
    star_offsets=[
        (0.0, 0.0),       # center (belt middle)
        (0.0, 1.2),       # belt left
        (0.0, -1.2),      # belt right
        (0.08, 2.5),      # top-left shoulder
        (0.08, -2.5),     # top-right shoulder
        (-0.08, 2.0),     # bottom-left foot
        (-0.08, -2.0),    # bottom-right foot
    ],
    lines=[(1, 0), (0, 2), (3, 1), (2, 4), (3, 5), (4, 6)],
)

# ═══════════════════════════════════════════════════════════════════
# 南方朱雀 (Southern Vermilion Bird)
# ═══════════════════════════════════════════════════════════════════

_JING = MansionData(  # 井 - 8 stars (well - rectangular frame)
    name='井',
    star_offsets=[
        (0.0, 0.0),
        (0.06, 0.0),
        (0.0, 2.0),
        (0.06, 2.0),
        (0.0, -2.0),
        (0.06, -2.0),
        (0.03, 3.0),
        (0.03, -3.0),
    ],
    lines=[(0, 1), (0, 2), (1, 3), (2, 3), (0, 4), (1, 5), (4, 5), (2, 6), (4, 7)],
)

_GUI = MansionData(  # 鬼 - 4 stars (ghost, boxy shape)
    name='鬼',
    star_offsets=[
        (0.0, 0.0),
        (0.05, 1.5),
        (0.05, -1.5),
        (0.10, 0.0),
    ],
    lines=[(0, 1), (1, 3), (3, 2), (2, 0)],  # box
)

_LIU = MansionData(  # 柳 - 6 stars (willow, curved arc)
    name='柳',
    star_offsets=[
        (0.0, 0.0),
        (0.02, 1.2),
        (0.05, 2.2),
        (0.03, -1.0),
        (0.06, -2.0),
        (0.08, 0.5),
    ],
    lines=[(2, 1), (1, 0), (0, 3), (3, 4), (0, 5)],
)

_XING = MansionData(  # 星 - 7 stars (star, Alphard region)
    name='星',
    star_offsets=[
        (0.0, 0.0),       # α Hya (Alphard)
        (0.04, 1.5),
        (0.07, 2.5),
        (0.03, -1.2),
        (0.06, -2.2),
        (0.09, 0.8),
        (0.05, -0.3),
    ],
    lines=[(0, 1), (1, 2), (0, 3), (3, 4), (0, 6), (6, 5)],
)

_ZHANG = MansionData(  # 张 - 6 stars (extended net)
    name='张',
    star_offsets=[
        (0.0, 0.0),
        (0.04, 1.5),
        (0.08, 2.5),
        (0.04, -1.5),
        (0.08, -2.5),
        (0.06, 0.0),
    ],
    lines=[(0, 1), (1, 2), (0, 3), (3, 4), (0, 5)],
)

_YI = MansionData(  # 翼 - 6 stars (wings, simplified from 22)
    name='翼',
    star_offsets=[
        (0.0, 0.0),
        (0.04, 1.5),
        (0.08, 3.0),
        (0.04, -1.5),
        (0.08, -3.0),
        (0.12, 0.0),
    ],
    lines=[(0, 1), (1, 2), (0, 3), (3, 4), (0, 5)],  # spread wings
)

_ZHEN = MansionData(  # 轸 - 4 stars (chariot crossbar)
    name='轸',
    star_offsets=[
        (0.0, 0.0),
        (0.06, 1.5),
        (0.06, -1.5),
        (0.10, 0.0),
    ],
    lines=[(0, 1), (1, 3), (3, 2), (2, 0)],  # box
)


# ─────────────────────────────────────────────────────────────────────
# Ordered list matching ORDERED_XIU_R in config.py
# Index i here corresponds to index i in ORDERED_XIU_R
# [0]虚, [1]女, [2]牛, [3]斗, [4]箕, [5]尾, [6]心, [7]房, [8]氐, [9]亢,
# [10]角, [11]轸, [12]翼, [13]张, [14]星, [15]柳, [16]鬼, [17]井,
# [18]参, [19]觜, [20]毕, [21]昴, [22]胃, [23]娄, [24]奎,
# [25]壁, [26]室, [27]危
# ─────────────────────────────────────────────────────────────────────

ALL_MANSIONS_ORDERED = [
    _XU,      # 0  虚
    _NV,      # 1  女
    _NIU,     # 2  牛
    _DOU,     # 3  斗
    _JI,      # 4  箕
    _WEI,     # 5  尾
    _XIN,     # 6  心
    _FANG,    # 7  房
    _DI,      # 8  氐
    _KANG,    # 9  亢
    _JIAO,    # 10 角
    _ZHEN,    # 11 轸
    _YI,      # 12 翼
    _ZHANG,   # 13 张
    _XING,    # 14 星
    _LIU,     # 15 柳
    _GUI,     # 16 鬼
    _JING,    # 17 井
    _SHEN,    # 18 参
    _ZI,      # 19 觜
    _BI3,     # 20 毕
    _MAO,     # 21 昴
    _WEI3,    # 22 胃
    _LOU,     # 23 娄
    _KUI,     # 24 奎
    _BI2,     # 25 壁
    _SHI,     # 26 室
    _WEI2,    # 27 危
]

# Quick name list for validation
ORDERED_NAMES = [m.name for m in ALL_MANSIONS_ORDERED]

# Beast quadrant indices (into ALL_MANSIONS_ORDERED)
BEAST_QUADRANTS = {
    'dragon':   {'indices': [10, 9, 8, 7, 6, 5, 4]},     # 角亢氐房心尾箕
    'tortoise': {'indices': [3, 2, 1, 0, 27, 26, 25]},    # 斗牛女虚危室壁
    'tiger':    {'indices': [24, 23, 22, 21, 20, 19, 18]}, # 奎娄胃昴毕觜参
    'bird':     {'indices': [17, 16, 15, 14, 13, 12, 11]}, # 井鬼柳星张翼轸
}


# ─────────────────────────────────────────────────────────────────────
# 四圣兽 simplified outline data
# Coordinate system:
#   r_fraction: relative to XIU_RING_RADIUS (0.7~1.2)
#   theta_deg:  offset from quadrant center angle (±42° for 7-mansion span)
# ─────────────────────────────────────────────────────────────────────

BEAST_OUTLINES = {
    # ═══ 青龙 (Azure Dragon) ═══
    # Double-contour serpentine body with mane, three-toed claws, open jaws
    'dragon': BeastOutline(
        name='青龙',
        vertices=[
            # --- Head (open jaws, double contour) ---
            (1.14, -37.0),   # 0  upper skull back
            (1.12, -39.0),   # 1  upper snout
            (1.08, -40.0),   # 2  snout tip (upper jaw)
            (1.04, -39.5),   # 3  snout tip (lower jaw)
            (1.02, -38.0),   # 4  lower jaw mid
            (1.04, -36.0),   # 5  lower jaw back
            (1.08, -35.5),   # 6  jaw hinge
            (1.10, -36.5),   # 7  eye (short mark)
            # --- Horns ---
            (1.18, -38.5),   # 8  left horn tip
            (1.13, -37.5),   # 9  left horn base
            (1.20, -35.5),   # 10 right horn tip
            (1.13, -36.0),   # 11 right horn base
            # --- Whiskers (two) ---
            (1.06, -42.0),   # 12 whisker 1 tip
            (1.00, -41.5),   # 13 whisker 2 tip
            # --- Neck + mane ---
            (1.10, -33.0),   # 14 neck dorsal 1
            (1.08, -29.0),   # 15 neck dorsal 2
            (1.02, -33.5),   # 16 neck ventral 1
            (1.00, -29.5),   # 17 neck ventral 2
            (1.14, -32.0),   # 18 mane tuft 1
            (1.13, -30.0),   # 19 mane tuft 2
            (1.12, -28.0),   # 20 mane tuft 3
            # --- Body dorsal line (S-curve, 6 pts) ---
            (1.06, -24.0),   # 21 body dorsal 1
            (0.98, -16.0),   # 22 body dorsal 2
            (1.06, -8.0),    # 23 body dorsal 3
            (0.96, 0.0),     # 24 body dorsal 4
            (1.06, 8.0),     # 25 body dorsal 5
            (0.98, 16.0),    # 26 body dorsal 6
            # --- Body ventral line (parallel, 6 pts) ---
            (0.98, -24.5),   # 27 body ventral 1
            (0.90, -16.5),   # 28 body ventral 2
            (0.98, -8.5),    # 29 body ventral 3
            (0.88, -0.5),    # 30 body ventral 4
            (0.98, 7.5),     # 31 body ventral 5
            (0.90, 15.5),    # 32 body ventral 6
            # --- Dorsal fin spines (4 short lines from dorsal) ---
            (1.10, -20.0),   # 33 fin 1
            (1.10, -12.0),   # 34 fin 2
            (1.10, -4.0),    # 35 fin 3
            (1.10, 4.0),     # 36 fin 4
            # --- Front claws (3 toes each) ---
            (1.12, -14.0),   # 37 front upper arm
            (1.18, -16.0),   # 38 front upper elbow
            (1.22, -14.0),   # 39 toe 1
            (1.22, -16.5),   # 40 toe 2
            (1.20, -18.0),   # 41 toe 3
            (0.82, -18.0),   # 42 front lower arm
            (0.76, -20.0),   # 43 front lower elbow
            (0.72, -18.0),   # 44 toe 1
            (0.73, -20.5),   # 45 toe 2
            (0.74, -22.0),   # 46 toe 3
            # --- Rear claws (3 toes each) ---
            (1.12, 10.0),    # 47 rear upper arm
            (1.18, 12.0),    # 48 rear upper elbow
            (1.22, 10.0),    # 49 toe 1
            (1.22, 12.5),    # 50 toe 2
            (1.20, 14.0),    # 51 toe 3
            (0.82, 12.0),    # 52 rear lower arm
            (0.76, 14.0),    # 53 rear lower elbow
            (0.72, 12.0),    # 54 toe 1
            (0.73, 14.5),    # 55 toe 2
            (0.74, 16.0),    # 56 toe 3
            # --- Tail (double contour, fire fork) ---
            (1.04, 22.0),    # 57 tail dorsal 1
            (0.96, 28.0),    # 58 tail dorsal 2
            (1.02, 34.0),    # 59 tail dorsal 3
            (0.96, 21.5),    # 60 tail ventral 1
            (0.88, 27.5),    # 61 tail ventral 2
            (0.94, 33.5),    # 62 tail ventral 3
            (1.06, 38.0),    # 63 flame fork upper
            (0.90, 37.5),    # 64 flame fork lower
        ],
        lines=[
            # Upper skull
            (0, 1), (1, 2),
            # Lower jaw
            (3, 4), (4, 5), (5, 6),
            # Jaw hinge connects to skull
            (6, 0),
            # Eye
            (0, 7),
            # Horns
            (8, 9), (10, 11), (9, 0), (11, 6),
            # Whiskers
            (2, 12), (3, 13),
            # Neck dorsal
            (0, 14), (14, 15),
            # Neck ventral
            (5, 16), (16, 17),
            # Mane tufts
            (14, 18), (14, 19), (15, 20),
            # Body dorsal
            (15, 21), (21, 22), (22, 23), (23, 24), (24, 25), (25, 26),
            # Body ventral
            (17, 27), (27, 28), (28, 29), (29, 30), (30, 31), (31, 32),
            # Dorsal fin spines
            (22, 33), (22, 34), (23, 35), (25, 36),
            # Front claws upper
            (22, 37), (37, 38), (38, 39), (38, 40), (38, 41),
            # Front claws lower
            (28, 42), (42, 43), (43, 44), (43, 45), (43, 46),
            # Rear claws upper
            (25, 47), (47, 48), (48, 49), (48, 50), (48, 51),
            # Rear claws lower
            (31, 52), (52, 53), (53, 54), (53, 55), (53, 56),
            # Tail dorsal
            (26, 57), (57, 58), (58, 59),
            # Tail ventral
            (32, 60), (60, 61), (61, 62),
            # Flame fork
            (59, 63), (62, 64),
        ],
        color=(0.4, 0.75, 1.0, 1.0),
    ),

    # ═══ 玄武 (Black Tortoise with Snake) ═══
    # Shell with cross-hatch pattern, webbed feet, snake with double contour
    'tortoise': BeastOutline(
        name='玄武',
        vertices=[
            # --- Shell outline (8 pts elliptical) ---
            (1.10, -12.0),   # 0  shell front
            (1.14, -6.0),    # 1  shell front-left
            (1.14, 0.0),     # 2  shell left
            (1.12, 6.0),     # 3  shell back-left
            (1.06, 10.0),    # 4  shell back
            (0.92, 6.0),     # 5  shell back-right
            (0.88, 0.0),     # 6  shell right
            (0.92, -6.0),    # 7  shell front-right
            # --- Shell pattern: spine + cross hatching ---
            (1.10, -9.0),    # 8  spine front
            (1.02, 0.0),     # 9  spine mid
            (1.02, 8.0),     # 10 spine back
            (1.14, -3.0),    # 11 cross 1 left
            (0.90, -3.0),    # 12 cross 1 right
            (1.13, 3.0),     # 13 cross 2 left
            (0.90, 3.0),     # 14 cross 2 right
            (1.10, 7.0),     # 15 cross 3 left
            (0.93, 7.0),     # 16 cross 3 right
            (1.06, -6.0),    # 17 diag 1 (spine to shell)
            (0.96, -6.0),    # 18 diag 2
            (1.06, 4.0),     # 19 diag 3
            (0.96, 4.0),     # 20 diag 4
            # --- Turtle head (double contour) ---
            (1.06, -18.0),   # 21 head dorsal back
            (1.08, -22.0),   # 22 head dorsal mid
            (1.06, -25.0),   # 23 snout top
            (1.02, -25.5),   # 24 snout tip
            (1.00, -24.5),   # 25 beak line
            (0.99, -22.0),   # 26 head ventral mid
            (1.00, -18.5),   # 27 head ventral back
            (1.04, -23.0),   # 28 eye
            # --- Four legs (3-segment + 2-toe webbed) ---
            (1.16, -8.0),    # 29 FL upper
            (1.20, -10.0),   # 30 FL mid
            (1.22, -8.5),    # 31 FL toe 1
            (1.23, -11.0),   # 32 FL toe 2
            (0.84, -8.0),    # 33 FR upper
            (0.80, -10.0),   # 34 FR mid
            (0.78, -8.5),    # 35 FR toe 1
            (0.77, -11.0),   # 36 FR toe 2
            (1.16, 8.0),     # 37 BL upper
            (1.20, 10.0),    # 38 BL mid
            (1.22, 8.5),     # 39 BL toe 1
            (1.23, 11.0),    # 40 BL toe 2
            (0.84, 8.0),     # 41 BR upper
            (0.80, 10.0),    # 42 BR mid
            (0.78, 8.5),     # 43 BR toe 1
            (0.77, 11.0),    # 44 BR toe 2
            # --- Turtle tail ---
            (0.98, 13.0),    # 45 tail tip
            # --- Snake dorsal line (7 pts, winding around shell) ---
            (0.90, -28.0),   # 46 snake head dorsal
            (0.86, -24.0),   # 47 snake neck dorsal
            (0.92, -16.0),   # 48 snake body d1
            (1.12, -8.0),    # 49 snake body d2
            (0.90, 0.0),     # 50 snake body d3
            (1.10, 10.0),    # 51 snake body d4
            (0.88, 20.0),    # 52 snake body d5
            (1.02, 28.0),    # 53 snake body d6
            (0.94, 34.0),    # 54 snake tail tip
            # --- Snake ventral line (parallel, 7 pts) ---
            (0.86, -27.5),   # 55 snake head ventral
            (0.82, -23.5),   # 56 snake neck ventral
            (0.88, -15.5),   # 57 snake body v1
            (1.08, -7.5),    # 58 snake body v2
            (0.86, 0.5),     # 59 snake body v3
            (1.06, 10.5),    # 60 snake body v4
            (0.84, 20.5),    # 61 snake body v5
            (0.98, 28.5),    # 62 snake body v6
            # --- Snake head detail ---
            (0.92, -29.5),   # 63 snake snout
            (0.94, -31.0),   # 64 tongue fork 1
            (0.88, -31.0),   # 65 tongue fork 2
            (0.89, -26.0),   # 66 snake eye
            # --- Snake scale marks ---
            (0.91, -12.0),   # 67 scale mark 1
            (1.11, -4.0),    # 68 scale mark 2
            (0.89, 4.0),     # 69 scale mark 3
        ],
        lines=[
            # Shell outline
            (0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 0),
            # Shell spine
            (8, 9), (9, 10),
            # Shell cross hatching
            (11, 12), (13, 14), (15, 16),
            # Shell diagonals
            (8, 17), (8, 18), (10, 19), (10, 20),
            # Turtle head dorsal
            (0, 21), (21, 22), (22, 23), (23, 24),
            # Turtle head ventral
            (24, 25), (25, 26), (26, 27), (27, 7),
            # Eye + beak
            (22, 28),
            # Front-left leg
            (1, 29), (29, 30), (30, 31), (30, 32),
            # Front-right leg
            (7, 33), (33, 34), (34, 35), (34, 36),
            # Back-left leg
            (3, 37), (37, 38), (38, 39), (38, 40),
            # Back-right leg
            (5, 41), (41, 42), (42, 43), (42, 44),
            # Turtle tail
            (4, 45),
            # Snake dorsal
            (63, 46), (46, 47), (47, 48), (48, 49), (49, 50),
            (50, 51), (51, 52), (52, 53), (53, 54),
            # Snake ventral
            (63, 55), (55, 56), (56, 57), (57, 58), (58, 59),
            (59, 60), (60, 61), (61, 62),
            # Snake tongue fork
            (63, 64), (63, 65),
            # Snake eye
            (46, 66),
            # Snake scale marks
            (48, 67), (49, 68), (50, 69),
        ],
        color=(0.55, 0.45, 0.9, 1.0),
    ),

    # ═══ 白虎 (White Tiger) ═══
    # Muscular body with double contour, stripes, four complete legs
    'tiger': BeastOutline(
        name='白虎',
        vertices=[
            # --- Head (double contour, wide round face) ---
            (1.10, -34.0),   # 0  forehead top
            (1.12, -36.0),   # 1  skull left
            (1.08, -37.5),   # 2  cheek left
            (1.02, -38.0),   # 3  nose bridge
            (0.97, -37.5),   # 4  nose tip
            (0.95, -36.0),   # 5  chin
            (0.97, -34.0),   # 6  jaw right
            (1.02, -33.0),   # 7  cheek right
            (1.08, -33.5),   # 8  skull right
            # Ears (triangular)
            (1.16, -36.5),   # 9  left ear tip
            (1.16, -33.0),   # 10 right ear tip
            # Eye
            (1.06, -35.5),   # 11 eye
            # --- Body dorsal (shoulder hump → waist dip → hip rise, 6 pts) ---
            (1.06, -30.0),   # 12 neck dorsal
            (1.10, -24.0),   # 13 shoulder peak
            (1.08, -16.0),   # 14 upper back
            (1.04, -8.0),    # 15 mid back (waist dip)
            (1.06, 2.0),     # 16 lower back
            (1.08, 10.0),    # 17 hip rise
            # --- Body ventral (chest → tucked belly, 6 pts) ---
            (0.96, -30.5),   # 18 throat
            (0.92, -24.5),   # 19 chest
            (0.88, -16.5),   # 20 lower chest
            (0.86, -8.5),    # 21 belly front
            (0.88, 1.5),     # 22 belly mid
            (0.90, 9.5),     # 23 belly rear
            # --- Tiger stripes (4 diagonal marks between dorsal/ventral) ---
            (1.06, -21.0),   # 24 stripe 1 top
            (0.92, -22.0),   # 25 stripe 1 bottom
            (1.06, -14.0),   # 26 stripe 2 top
            (0.90, -15.0),   # 27 stripe 2 bottom
            (1.04, -5.0),    # 28 stripe 3 top
            (0.88, -6.0),    # 29 stripe 3 bottom
            (1.06, 5.0),     # 30 stripe 4 top
            (0.90, 4.0),     # 31 stripe 4 bottom
            # --- Front left leg (shoulder-elbow-wrist-paw + 2 toes) ---
            (0.86, -22.0),   # 32 FL hip
            (0.80, -24.0),   # 33 FL elbow
            (0.76, -22.0),   # 34 FL wrist
            (0.73, -21.0),   # 35 FL toe 1
            (0.73, -23.0),   # 36 FL toe 2
            # --- Front right leg ---
            (0.86, -14.0),   # 37 FR hip
            (0.80, -16.0),   # 38 FR elbow
            (0.76, -14.0),   # 39 FR wrist
            (0.73, -13.0),   # 40 FR toe 1
            (0.73, -15.0),   # 41 FR toe 2
            # --- Rear left leg (hip-knee-hock-paw + 2 toes) ---
            (0.88, 6.0),     # 42 RL hip
            (0.82, 4.0),     # 43 RL knee
            (0.78, 6.0),     # 44 RL hock
            (0.74, 5.0),     # 45 RL toe 1
            (0.74, 7.0),     # 46 RL toe 2
            # --- Rear right leg ---
            (0.90, 12.0),    # 47 RR hip
            (0.84, 10.0),    # 48 RR knee
            (0.78, 12.0),    # 49 RR hock
            (0.74, 11.0),    # 50 RR toe 1
            (0.74, 13.0),    # 51 RR toe 2
            # --- Tail (S-curve + dark tip fork) ---
            (1.08, 16.0),    # 52 tail base
            (1.14, 22.0),    # 53 tail mid 1
            (1.10, 28.0),    # 54 tail mid 2
            (1.14, 34.0),    # 55 tail curve
            (1.18, 38.0),    # 56 tail tip fork 1
            (1.10, 38.5),    # 57 tail tip fork 2
        ],
        lines=[
            # Head outline
            (0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 8), (8, 0),
            # Ears
            (1, 9), (9, 0), (8, 10), (10, 0),
            # Eye
            (1, 11),
            # Body dorsal
            (0, 12), (12, 13), (13, 14), (14, 15), (15, 16), (16, 17),
            # Body ventral
            (6, 18), (18, 19), (19, 20), (20, 21), (21, 22), (22, 23),
            # Connect dorsal/ventral at hip
            (17, 23),
            # Tiger stripes
            (24, 25), (26, 27), (28, 29), (30, 31),
            # Front left leg
            (19, 32), (32, 33), (33, 34), (34, 35), (34, 36),
            # Front right leg
            (20, 37), (37, 38), (38, 39), (39, 40), (39, 41),
            # Rear left leg
            (22, 42), (42, 43), (43, 44), (44, 45), (44, 46),
            # Rear right leg
            (23, 47), (47, 48), (48, 49), (49, 50), (49, 51),
            # Tail
            (17, 52), (52, 53), (53, 54), (54, 55), (55, 56), (55, 57),
        ],
        color=(1.0, 1.0, 1.0, 1.0),
    ),

    # ═══ 朱雀 (Vermilion Bird) ═══
    # Phoenix with crest plumes, layered wing feathers, fan tail with eye spots
    'bird': BeastOutline(
        name='朱雀',
        vertices=[
            # --- Head (double contour + crest) ---
            (1.04, -6.0),    # 0  crown top
            (1.00, -4.0),    # 1  crown back
            (0.98, -7.0),    # 2  forehead
            (0.94, -9.0),    # 3  beak upper
            (0.92, -9.5),    # 4  beak tip
            (0.94, -8.0),    # 5  beak lower
            (0.97, -5.5),    # 6  throat
            (1.02, -5.5),    # 7  eye
            # Crest plumes (4 feathers flowing back)
            (1.08, -4.5),    # 8  crest 1 tip
            (1.10, -2.5),    # 9  crest 2 tip
            (1.12, -0.5),    # 10 crest 3 tip
            (1.08, 1.0),     # 11 crest 4 tip
            # --- Body (double contour, puffed chest) ---
            (1.04, -2.0),    # 12 back upper
            (1.06, 4.0),     # 13 back mid
            (1.04, 10.0),    # 14 back lower
            (0.98, 15.0),    # 15 rump
            (0.96, -2.5),    # 16 chest upper
            (0.94, 4.0),     # 17 chest mid
            (0.92, 10.0),    # 18 chest lower
            (0.93, 15.5),    # 19 belly rear
            # --- Left wing (upper, 6-pt arc + 3 feather layers) ---
            (1.10, 1.0),     # 20 wing root L
            (1.16, -4.0),    # 21 wing mid1 L
            (1.22, -10.0),   # 22 wing mid2 L
            (1.28, -17.0),   # 23 wing outer L
            (1.30, -24.0),   # 24 wing tip L
            (1.26, -30.0),   # 25 wing far tip L
            # Left wing primary feathers (3 lines)
            (1.24, -14.0),   # 26 primary 1
            (1.28, -20.0),   # 27 primary 2
            (1.26, -26.0),   # 28 primary 3
            # Left wing secondary feathers (2 lines)
            (1.18, -7.0),    # 29 secondary 1
            (1.22, -13.0),   # 30 secondary 2
            # Left wing coverts (2 short lines)
            (1.14, -2.5),    # 31 covert 1
            (1.18, -8.0),    # 32 covert 2
            # --- Right wing (lower, 6-pt arc + 3 feather layers) ---
            (0.88, 1.0),     # 33 wing root R
            (0.82, -4.0),    # 34 wing mid1 R
            (0.76, -10.0),   # 35 wing mid2 R
            (0.70, -17.0),   # 36 wing outer R
            (0.68, -24.0),   # 37 wing tip R
            (0.66, -30.0),   # 38 wing far tip R
            # Right wing primary feathers
            (0.72, -14.0),   # 39 primary 1
            (0.70, -20.0),   # 40 primary 2
            (0.68, -26.0),   # 41 primary 3
            # Right wing secondary feathers
            (0.78, -7.0),    # 42 secondary 1
            (0.74, -13.0),   # 43 secondary 2
            # Right wing coverts
            (0.84, -2.5),    # 44 covert 1
            (0.78, -8.0),    # 45 covert 2
            # --- Tail fan (7 feathers + 2 eye spots) ---
            (0.98, 20.0),    # 46 tail base center
            (1.06, 24.0),    # 47 tail feather 1 (leftmost)
            (1.02, 26.0),    # 48 tail feather 2
            (0.98, 28.0),    # 49 tail feather 3 (center)
            (0.94, 26.0),    # 50 tail feather 4
            (0.90, 24.0),    # 51 tail feather 5
            (1.10, 30.0),    # 52 tail tip 1 (longest)
            (0.86, 30.0),    # 53 tail tip 5 (longest)
            (1.04, 32.0),    # 54 tail tip 2
            (0.98, 34.0),    # 55 tail tip 3
            (0.92, 32.0),    # 56 tail tip 4
            # Eye spots (on longest feathers)
            (1.09, 28.5),    # 57 eye spot 1 mark
            (0.87, 28.5),    # 58 eye spot 2 mark
            # --- Legs + talons ---
            (0.90, 12.0),    # 59 leg 1 top
            (0.84, 16.0),    # 60 leg 1 mid
            (0.80, 19.0),    # 61 leg 1 foot
            (0.82, 18.0),    # 62 talon 1
            (0.78, 20.0),    # 63 talon 2
            (0.86, 12.0),    # 64 leg 2 top
            (0.82, 16.5),    # 65 leg 2 foot
        ],
        lines=[
            # Head outline
            (0, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 1), (1, 0),
            # Eye
            (0, 7),
            # Crest plumes
            (0, 8), (1, 9), (1, 10), (12, 11),
            # Body dorsal
            (1, 12), (12, 13), (13, 14), (14, 15),
            # Body ventral
            (6, 16), (16, 17), (17, 18), (18, 19),
            # Connect at rump
            (15, 19),
            # Left wing
            (13, 20), (20, 21), (21, 22), (22, 23), (23, 24), (24, 25),
            # Left primaries
            (23, 26), (24, 27), (25, 28),
            # Left secondaries
            (22, 29), (22, 30),
            # Left coverts
            (21, 31), (21, 32),
            # Right wing
            (17, 33), (33, 34), (34, 35), (35, 36), (36, 37), (37, 38),
            # Right primaries
            (36, 39), (37, 40), (38, 41),
            # Right secondaries
            (35, 42), (35, 43),
            # Right coverts
            (34, 44), (34, 45),
            # Tail fan
            (15, 46), (46, 47), (46, 48), (46, 49), (46, 50), (46, 51),
            (47, 52), (48, 54), (49, 55), (50, 56), (51, 53),
            # Eye spots
            (52, 57), (53, 58),
            # Legs
            (18, 59), (59, 60), (60, 61), (61, 62), (61, 63),
            (18, 64), (64, 65),
        ],
        color=(1.0, 0.45, 0.35, 1.0),
    ),
}
