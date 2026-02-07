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
    # Long sinuous body with claws and horns
    'dragon': BeastOutline(
        name='青龙',
        vertices=[
            # head (horns + snout)
            (1.15, -38.0),   # 0  horn tip left
            (1.10, -35.0),   # 1  horn base left
            (1.18, -33.0),   # 2  horn tip right
            (1.10, -31.0),   # 3  horn base right
            (1.05, -33.0),   # 4  forehead
            (0.98, -36.0),   # 5  snout
            (1.00, -31.0),   # 6  jaw
            # neck
            (1.02, -26.0),   # 7  neck top
            (0.95, -20.0),   # 8  neck curve
            # body (serpentine)
            (1.00, -14.0),   # 9  body crest 1
            (0.92, -7.0),    # 10 body trough 1
            (1.02, 0.0),     # 11 body crest 2
            (0.90, 7.0),     # 12 body trough 2
            (1.00, 14.0),    # 13 body crest 3
            (0.93, 20.0),    # 14 body trough 3
            # tail
            (1.02, 26.0),    # 15 tail base
            (0.95, 32.0),    # 16 tail mid
            (1.05, 38.0),    # 17 tail tip
            # front claws (from body crest 1)
            (1.12, -12.0),   # 18 front claw upper
            (1.18, -15.0),   # 19 front claw tip
            (0.82, -16.0),   # 20 front claw lower
            (0.78, -19.0),   # 21 front claw tip
            # rear claws (from body crest 3)
            (1.12, 12.0),    # 22 rear claw upper
            (1.18, 15.0),    # 23 rear claw tip
            (0.82, 16.0),    # 24 rear claw lower
            (0.78, 19.0),    # 25 rear claw tip
            # whiskers
            (0.92, -38.0),   # 26 whisker tip
        ],
        lines=[
            # horns
            (0, 1), (2, 3),
            # head outline
            (1, 4), (3, 4), (4, 5), (5, 6), (6, 4),
            # whisker
            (5, 26),
            # neck
            (7, 4), (7, 8),
            # body serpentine
            (8, 9), (9, 10), (10, 11), (11, 12), (12, 13), (13, 14),
            # tail
            (14, 15), (15, 16), (16, 17),
            # front claws
            (9, 18), (18, 19), (9, 20), (20, 21),
            # rear claws
            (13, 22), (22, 23), (13, 24), (24, 25),
        ],
        color=(0.3, 0.65, 1.0, 0.85),
    ),

    # ═══ 玄武 (Black Tortoise with Snake) ═══
    # Turtle shell + entwined snake
    'tortoise': BeastOutline(
        name='玄武',
        vertices=[
            # turtle shell (hexagonal)
            (1.05, -15.0),   # 0  shell front-left
            (1.12, -5.0),    # 1  shell left
            (1.08, 5.0),     # 2  shell back-left
            (0.92, 10.0),    # 3  shell back-right
            (0.85, 0.0),     # 4  shell right
            (0.90, -10.0),   # 5  shell front-right
            # turtle head
            (1.02, -22.0),   # 6  neck
            (1.05, -27.0),   # 7  head top
            (0.98, -28.0),   # 8  snout
            (0.95, -25.0),   # 9  jaw
            # turtle legs
            (1.15, -8.0),    # 10 front-left leg
            (1.18, -12.0),   # 11 front-left foot
            (0.80, -5.0),    # 12 front-right leg
            (0.75, -8.0),    # 13 front-right foot
            (1.15, 8.0),     # 14 back-left leg
            (1.18, 12.0),    # 15 back-left foot
            (0.80, 8.0),     # 16 back-right leg
            (0.75, 12.0),    # 17 back-right foot
            # turtle tail
            (0.95, 15.0),    # 18 tail
            # snake body (entwining)
            (0.88, -30.0),   # 19 snake head
            (0.82, -25.0),   # 20 snake neck
            (0.90, -18.0),   # 21 snake body 1
            (1.10, -10.0),   # 22 snake body 2
            (0.88, -2.0),    # 23 snake body 3
            (1.08, 8.0),     # 24 snake body 4
            (0.85, 18.0),    # 25 snake body 5
            (1.00, 25.0),    # 26 snake body 6
            (0.92, 32.0),    # 27 snake tail tip
            (0.85, -32.0),   # 28 snake tongue
        ],
        lines=[
            # shell
            (0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0),
            # head
            (0, 6), (6, 7), (7, 8), (8, 9), (9, 6),
            # legs
            (1, 10), (10, 11), (5, 12), (12, 13),
            (2, 14), (14, 15), (4, 16), (16, 17),
            # tail
            (3, 18),
            # snake
            (19, 28), (19, 20), (20, 21), (21, 22), (22, 23),
            (23, 24), (24, 25), (25, 26), (26, 27),
        ],
        color=(0.45, 0.35, 0.8, 0.85),
    ),

    # ═══ 白虎 (White Tiger) ═══
    # Four-legged walking tiger
    'tiger': BeastOutline(
        name='白虎',
        vertices=[
            # head
            (1.05, -35.0),   # 0  ear left
            (1.10, -32.0),   # 1  crown
            (1.05, -29.0),   # 2  ear right
            (1.02, -32.0),   # 3  forehead
            (0.95, -35.0),   # 4  nose
            (0.92, -32.0),   # 5  chin
            # body
            (1.00, -25.0),   # 6  neck top
            (0.90, -26.0),   # 7  throat
            (1.05, -18.0),   # 8  shoulder
            (1.08, -10.0),   # 9  back peak
            (1.05, 0.0),     # 10 mid back
            (1.02, 10.0),    # 11 hip
            (0.88, -15.0),   # 12 chest
            (0.85, 0.0),     # 13 belly
            (0.88, 12.0),    # 14 rear belly
            # tail
            (1.05, 18.0),    # 15 tail base
            (1.12, 25.0),    # 16 tail mid
            (1.08, 33.0),    # 17 tail curve
            (1.15, 38.0),    # 18 tail tip
            # front legs
            (0.82, -20.0),   # 19 front leg top
            (0.75, -22.0),   # 20 front knee
            (0.72, -18.0),   # 21 front paw
            (0.82, -12.0),   # 22 front leg top 2
            (0.75, -14.0),   # 23 front knee 2
            (0.72, -10.0),   # 24 front paw 2
            # rear legs
            (0.82, 8.0),     # 25 rear leg top
            (0.75, 6.0),     # 26 rear knee
        ],
        lines=[
            # head
            (0, 1), (1, 2), (1, 3), (3, 4), (4, 5), (5, 3),
            # neck-body top
            (3, 6), (6, 8), (8, 9), (9, 10), (10, 11),
            # neck-body bottom
            (5, 7), (7, 12), (12, 13), (13, 14), (14, 11),
            # tail
            (11, 15), (15, 16), (16, 17), (17, 18),
            # front legs
            (12, 19), (19, 20), (20, 21),
            (12, 22), (22, 23), (23, 24),
            # rear legs
            (14, 25), (25, 26),
        ],
        color=(0.95, 0.95, 1.0, 0.85),
    ),

    # ═══ 朱雀 (Vermilion Bird) ═══
    # Bird with spread wings in flight
    'bird': BeastOutline(
        name='朱雀',
        vertices=[
            # head + beak
            (1.02, -5.0),    # 0  crown
            (0.95, -8.0),    # 1  beak tip
            (0.98, -3.0),    # 2  throat
            # neck
            (1.00, 0.0),     # 3  neck base
            # body
            (1.02, 5.0),     # 4  chest
            (1.00, 12.0),    # 5  body center
            (0.95, 18.0),    # 6  rump
            # tail feathers (fan)
            (0.98, 24.0),    # 7  tail center
            (1.05, 28.0),    # 8  tail left
            (0.88, 28.0),    # 9  tail right
            (1.10, 32.0),    # 10 tail far left
            (0.82, 32.0),    # 11 tail far right
            # left wing (upper in view)
            (1.08, 2.0),     # 12 wing root left
            (1.15, -5.0),    # 13 wing mid left
            (1.22, -12.0),   # 14 wing outer left
            (1.28, -20.0),   # 15 wing tip left
            (1.25, -28.0),   # 16 wing far tip left
            (1.18, -15.0),   # 17 wing feather left 1
            (1.20, -22.0),   # 18 wing feather left 2
            # right wing (lower in view)
            (0.90, 2.0),     # 19 wing root right
            (0.82, -5.0),    # 20 wing mid right
            (0.75, -12.0),   # 21 wing outer right
            (0.68, -20.0),   # 22 wing tip right
            (0.65, -28.0),   # 23 wing far tip right
            (0.72, -15.0),   # 24 wing feather right 1
            (0.70, -22.0),   # 25 wing feather right 2
            # legs
            (0.92, 14.0),    # 26 leg top
            (0.85, 18.0),    # 27 leg mid
            (0.82, 22.0),    # 28 talon
            (0.88, 14.0),    # 29 leg 2
        ],
        lines=[
            # head
            (0, 1), (0, 2), (1, 2),
            # neck
            (2, 3), (0, 3),
            # body
            (3, 4), (4, 5), (5, 6),
            # tail fan
            (6, 7), (7, 8), (7, 9), (8, 10), (9, 11),
            # left wing
            (4, 12), (12, 13), (13, 14), (14, 15), (15, 16),
            (14, 17), (15, 18),
            # right wing
            (4, 19), (19, 20), (20, 21), (21, 22), (22, 23),
            (21, 24), (22, 25),
            # legs
            (5, 26), (26, 27), (27, 28),
            (5, 29),
        ],
        color=(1.0, 0.35, 0.25, 0.85),
    ),
}
