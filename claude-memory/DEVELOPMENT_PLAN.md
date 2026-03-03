# 赛博大六壬 - 四课三传系统开发规划

## 项目概述

将现有的六壬式盘可视化程序扩展为完整的排盘系统，支持：
- 手动排盘（输入日干支+时支）
- 自动排盘（按当前时间）
- 四课三传计算与推导过程展示
- 式盘高亮 + 侧边栏文字说明
- 导出截图/文字记录

---

## 目标项目结构

```
Liuren/
├── config.py           # [扩展] 添加五行、寄宫、天将等常量
├── core.py             # [保留] 时辰计算
├── main.py             # [重构] 渲染引擎，集成新UI
├── DEVELOPMENT_PLAN.md # 本开发计划
├── tests/              # [新增] 测试模块
│   ├── __init__.py
│   ├── test_constants.py
│   ├── test_calendar.py
│   ├── test_plate.py
│   ├── test_four_lessons.py
│   └── test_three_passes.py
├── calendar/           # [新增] 万年历模块
│   ├── __init__.py
│   ├── solar_terms.py  # 节气计算（精确月将）
│   └── ganzhi.py       # 干支推算
├── liuren/             # [新增] 六壬核心算法
│   ├── __init__.py
│   ├── constants.py    # 六壬专用常量
│   ├── moon_general.py # 月将计算（基于中气）
│   ├── four_lessons.py # 四课系统
│   ├── three_passes.py # 三传系统
│   └── plate.py        # 式盘状态类
├── ui/                 # [新增] UI组件
│   ├── __init__.py
│   ├── input_panel.py  # 输入面板（干支选择器）
│   ├── sidebar.py      # 结果侧边栏
│   └── highlight.py    # 式盘高亮渲染
└── export/             # [新增] 导出功能
    ├── __init__.py
    ├── screenshot.py   # 截图保存
    └── text_export.py  # 文字导出
```

---

# 子项目 1：六壬常量系统

## 1.1 目标
扩展 `config.py`，新建 `liuren/constants.py`，建立完整的六壬数据常量体系。

## 1.2 实现内容

### 扩展 config.py
```python
# 五行系统
STEM_WUXING = {'甲': '木', '乙': '木', '丙': '火', '丁': '火',
               '戊': '土', '己': '土', '庚': '金', '辛': '金',
               '壬': '水', '癸': '水'}
BRANCH_WUXING = {'寅': '木', '卯': '木', '辰': '土', '巳': '火',
                 '午': '火', '未': '土', '申': '金', '酉': '金',
                 '戌': '土', '亥': '水', '子': '水', '丑': '土'}
WUXING_KE = {'木': '土', '土': '水', '水': '火', '火': '金', '金': '木'}
WUXING_SHENG = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}

# 阴阳
STEM_YINYANG = {'甲': '阳', '乙': '阴', '丙': '阳', '丁': '阴',
                '戊': '阳', '己': '阴', '庚': '阳', '辛': '阴',
                '壬': '阳', '癸': '阴'}
BRANCH_YINYANG = {'子': '阳', '丑': '阴', '寅': '阳', '卯': '阴',
                  '辰': '阳', '巳': '阴', '午': '阳', '未': '阴',
                  '申': '阳', '酉': '阴', '戌': '阳', '亥': '阴'}

# 天干寄宫（六壬核心）
STEM_JIGONG = {'甲': '寅', '乙': '辰', '丙': '巳', '丁': '未',
               '戊': '巳', '己': '未', '庚': '申', '辛': '戌',
               '壬': '亥', '癸': '丑'}

# 地支六冲
BRANCH_CHONG = {'子': '午', '午': '子', '丑': '未', '未': '丑',
                '寅': '申', '申': '寅', '卯': '酉', '酉': '卯',
                '辰': '戌', '戌': '辰', '巳': '亥', '亥': '巳'}

# 驿马
BRANCH_YIMA = {'寅': '申', '卯': '巳', '辰': '寅', '巳': '亥',
               '午': '申', '未': '巳', '申': '寅', '酉': '亥',
               '戌': '申', '亥': '巳', '子': '寅', '丑': '亥'}
```

### 新建 liuren/constants.py
```python
# 中气对应月将
ZHONGQI_MOON_GENERAL = {
    '雨水': '亥', '春分': '戌', '谷雨': '酉', '小满': '申',
    '夏至': '未', '大暑': '午', '处暑': '巳', '秋分': '辰',
    '霜降': '卯', '小雪': '寅', '冬至': '丑', '大寒': '子'
}

# 月将名称 (地支 -> 名称)
MOON_GENERAL_NAMES = {
    '子': '神后', '丑': '大吉', '寅': '功曹', '卯': '太冲',
    '辰': '天罡', '巳': '太乙', '午': '胜光', '未': '小吉',
    '申': '传送', '酉': '从魁', '戌': '河魁', '亥': '登明'
}

# 十二天将
TWELVE_GENERALS = ['贵人', '腾蛇', '朱雀', '六合', '勾陈', '青龙',
                   '天空', '白虎', '太常', '玄武', '太阴', '天后']
```

## 1.3 测试计划

### 测试文件: `tests/test_constants.py`

| 测试ID | 测试名称 | 输入 | 预期输出 | 验证方法 |
|--------|----------|------|----------|----------|
| C001 | 五行克关系完整性 | WUXING_KE | 5个完整映射 | `assert len(WUXING_KE) == 5` |
| C002 | 五行克循环验证 | 木->土->水->火->金->木 | 循环正确 | 从任意元素出发遍历5次回到原点 |
| C003 | 天干五行正确性 | '甲' | '木' | `assert STEM_WUXING['甲'] == '木'` |
| C004 | 地支五行正确性 | '巳' | '火' | `assert BRANCH_WUXING['巳'] == '火'` |
| C005 | 寄宫完整性 | STEM_JIGONG | 10个映射 | `assert len(STEM_JIGONG) == 10` |
| C006 | 寄宫正确性-甲 | '甲' | '寅' | `assert STEM_JIGONG['甲'] == '寅'` |
| C007 | 寄宫正确性-戊 | '戊' | '巳' | `assert STEM_JIGONG['戊'] == '巳'` |
| C008 | 六冲对称性 | 所有地支 | A冲B则B冲A | 遍历验证双向关系 |
| C009 | 阴阳完整性 | 天干+地支 | 各12个 | 验证数量和值域 |
| C010 | 月将名称完整性 | MOON_GENERAL_NAMES | 12个映射 | `assert len(...) == 12` |

### 验证命令
```bash
python -m pytest tests/test_constants.py -v
```

---

# 子项目 2：万年历与节气计算

## 2.1 目标
实现基于 `sxtwl` 的节气计算和干支推算，为月将计算提供基础。

## 2.2 实现内容

### calendar/solar_terms.py
```python
import sxtwl

def get_solar_term(year: int, month: int, day: int) -> tuple[str, datetime]:
    """获取指定日期所在的中气及其时间"""
    # 返回 (中气名称, 中气时间)
    pass

def get_current_zhongqi(dt: datetime) -> str:
    """获取当前生效的中气（用于月将计算）"""
    pass
```

### calendar/ganzhi.py
```python
import sxtwl

def get_day_ganzhi(year: int, month: int, day: int) -> tuple[str, str]:
    """获取日干支"""
    # 返回 (日干, 日支)
    pass

def get_hour_branch(hour: int) -> str:
    """获取时支"""
    pass

def get_full_ganzhi(dt: datetime) -> dict:
    """获取完整四柱"""
    # 返回 {'year': (干,支), 'month': (干,支), 'day': (干,支), 'hour': (干,支)}
    pass
```

## 2.3 测试计划

### 测试文件: `tests/test_calendar.py`

| 测试ID | 测试名称 | 输入 | 预期输出 | 验证方法 |
|--------|----------|------|----------|----------|
| CAL001 | 春分节气验证 | 2024-03-20 | '春分' | 与天文历对照 |
| CAL002 | 夏至节气验证 | 2024-06-21 | '夏至' | 与天文历对照 |
| CAL003 | 秋分节气验证 | 2024-09-22 | '秋分' | 与天文历对照 |
| CAL004 | 冬至节气验证 | 2024-12-21 | '冬至' | 与天文历对照 |
| CAL005 | 中气边界测试 | 春分前一天 | '雨水' | 验证节气切换 |
| CAL006 | 日干支-甲子日 | 已知甲子日 | ('甲', '子') | 查万年历验证 |
| CAL007 | 日干支-连续性 | 连续3天 | 干支顺序正确 | 验证60甲子循环 |
| CAL008 | 时支-子时 | 23:30 | '子' | `assert get_hour_branch(23) == '子'` |
| CAL009 | 时支-午时 | 12:00 | '午' | `assert get_hour_branch(12) == '午'` |
| CAL010 | 时支边界-丑时 | 01:30 | '丑' | 验证时辰边界 |

### 具体测试案例（已知日期）
```python
# 2024年特定日期验证（需查万年历确认）
TEST_DATES = [
    {'date': (2024, 1, 1), 'day_gz': ('甲', '辰')},   # 待确认
    {'date': (2024, 3, 20), 'zhongqi': '春分'},
    {'date': (2024, 6, 21), 'zhongqi': '夏至'},
]
```

### 验证命令
```bash
python -m pytest tests/test_calendar.py -v
```

---

# 子项目 3：月将计算

## 3.1 目标
实现精确的月将计算（基于中气）。

## 3.2 实现内容

### liuren/moon_general.py
```python
from calendar.solar_terms import get_current_zhongqi
from liuren.constants import ZHONGQI_MOON_GENERAL, MOON_GENERAL_NAMES

def get_moon_general(dt: datetime) -> tuple[str, str]:
    """
    获取月将
    返回: (月将地支, 月将名称)
    例如: ('亥', '登明')
    """
    zhongqi = get_current_zhongqi(dt)
    branch = ZHONGQI_MOON_GENERAL[zhongqi]
    name = MOON_GENERAL_NAMES[branch]
    return (branch, name)
```

## 3.3 测试计划

### 测试文件: `tests/test_moon_general.py`

| 测试ID | 测试名称 | 输入日期 | 预期月将 | 验证依据 |
|--------|----------|----------|----------|----------|
| MG001 | 雨水后月将 | 2024-02-20 | ('亥', '登明') | 雨水后用亥将 |
| MG002 | 春分后月将 | 2024-03-25 | ('戌', '河魁') | 春分后用戌将 |
| MG003 | 谷雨后月将 | 2024-04-25 | ('酉', '从魁') | 谷雨后用酉将 |
| MG004 | 小满后月将 | 2024-05-25 | ('申', '传送') | 小满后用申将 |
| MG005 | 夏至后月将 | 2024-06-25 | ('未', '小吉') | 夏至后用未将 |
| MG006 | 大暑后月将 | 2024-07-25 | ('午', '胜光') | 大暑后用午将 |
| MG007 | 处暑后月将 | 2024-08-25 | ('巳', '太乙') | 处暑后用巳将 |
| MG008 | 秋分后月将 | 2024-09-25 | ('辰', '天罡') | 秋分后用辰将 |
| MG009 | 霜降后月将 | 2024-10-25 | ('卯', '太冲') | 霜降后用卯将 |
| MG010 | 小雪后月将 | 2024-11-25 | ('寅', '功曹') | 小雪后用寅将 |
| MG011 | 冬至后月将 | 2024-12-25 | ('丑', '大吉') | 冬至后用丑将 |
| MG012 | 大寒后月将 | 2025-01-25 | ('子', '神后') | 大寒后用子将 |

### 验证命令
```bash
python -m pytest tests/test_moon_general.py -v
```

---

# 子项目 4：天地盘与式盘状态

## 4.1 目标
实现天地盘计算和 `LiurenPlate` 数据类。

## 4.2 实现内容

### liuren/plate.py
```python
from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class Lesson:
    """一课数据"""
    heaven: str  # 天盘（上神）
    earth: str   # 地盘
    index: int   # 第几课 (1-4)

@dataclass
class Pass:
    """一传数据"""
    branch: str  # 地支
    index: int   # 第几传 (1=初传, 2=中传, 3=末传)

@dataclass
class LiurenPlate:
    day_stem: str
    day_branch: str
    hour_branch: str
    moon_general: str
    moon_general_name: str
    heaven_plate: Dict[str, str]  # 地盘位置 -> 天盘地支
    lessons: List[Lesson] = field(default_factory=list)
    passes: List[Pass] = field(default_factory=list)
    lesson_type: str = ""
    derivation_log: List[str] = field(default_factory=list)

def build_heaven_plate(moon_general: str, hour_branch: str) -> Dict[str, str]:
    """
    构建天地盘映射
    月将加临时支：月将地支落在时支位置
    """
    pass

def get_heaven_branch(heaven_plate: Dict[str, str], earth_branch: str) -> str:
    """获取某地盘位置上的天盘地支"""
    return heaven_plate[earth_branch]
```

## 4.3 测试计划

### 测试文件: `tests/test_plate.py`

| 测试ID | 测试名称 | 输入 | 预期输出 | 验证方法 |
|--------|----------|------|----------|----------|
| PL001 | 天盘构建-亥加午 | 月将亥,时支午 | 天盘亥在地盘午位 | 验证映射关系 |
| PL002 | 天盘构建-子加子 | 月将子,时支子 | 天地盘重合(伏吟) | 所有位置相同 |
| PL003 | 天盘构建-子加午 | 月将子,时支午 | 天地盘对冲(返吟) | 所有位置冲关系 |
| PL004 | 上神查询-寅位 | 亥加午,查寅位 | '巳' | 手动计算验证 |
| PL005 | 上神查询-子位 | 亥加午,查子位 | '巳' | 手动计算验证 |
| PL006 | 天盘完整性 | 任意天盘 | 12个映射 | `assert len(heaven_plate) == 12` |
| PL007 | 天盘双射性 | 任意天盘 | 天盘地支不重复 | 验证值的唯一性 |

### 天盘映射验证示例
```
月将亥(登明)加临午时:
地盘: 子丑寅卯辰巳午未申酉戌亥
天盘: 巳午未申酉戌亥子丑寅卯辰

验证: heaven_plate['寅'] == '未' (因为亥->午偏移了5位)
```

### 验证命令
```bash
python -m pytest tests/test_plate.py -v
```

---

# 子项目 5：四课计算

## 5.1 目标
实现四课计算算法。

## 5.2 四课算法说明
```
一课：日干寄宫位置的天盘地支 / 日干寄宫
二课：一课天盘地支位置的天盘地支 / 一课天盘地支
三课：日支位置的天盘地支 / 日支
四课：三课天盘地支位置的天盘地支 / 三课天盘地支
```

## 5.3 实现内容

### liuren/four_lessons.py
```python
from config import STEM_JIGONG
from liuren.plate import LiurenPlate, Lesson, get_heaven_branch

def calculate_four_lessons(plate: LiurenPlate) -> List[Lesson]:
    """
    计算四课
    """
    jigong = STEM_JIGONG[plate.day_stem]

    # 一课: 寄宫上神
    lesson1_heaven = get_heaven_branch(plate.heaven_plate, jigong)
    lesson1 = Lesson(heaven=lesson1_heaven, earth=jigong, index=1)

    # 二课: 一课天盘上神
    lesson2_heaven = get_heaven_branch(plate.heaven_plate, lesson1_heaven)
    lesson2 = Lesson(heaven=lesson2_heaven, earth=lesson1_heaven, index=2)

    # 三课: 日支上神
    lesson3_heaven = get_heaven_branch(plate.heaven_plate, plate.day_branch)
    lesson3 = Lesson(heaven=lesson3_heaven, earth=plate.day_branch, index=3)

    # 四课: 三课天盘上神
    lesson4_heaven = get_heaven_branch(plate.heaven_plate, lesson3_heaven)
    lesson4 = Lesson(heaven=lesson4_heaven, earth=lesson3_heaven, index=4)

    return [lesson1, lesson2, lesson3, lesson4]
```

## 5.4 测试计划

### 测试文件: `tests/test_four_lessons.py`

| 测试ID | 输入 | 预期四课 | 验证依据 |
|--------|------|----------|----------|
| FL001 | 甲子日午时,月将亥 | 一课:未/寅, 二课:子/未, 三课:巳/子, 四课:戌/巳 | 传统算法手算 |
| FL002 | 乙丑日卯时,月将戌 | 待计算 | 传统算法手算 |
| FL003 | 丙寅日申时,月将酉 | 待计算 | 传统算法手算 |
| FL004 | 丁卯日巳时,月将未 | 待计算 | 传统算法手算 |
| FL005 | 戊辰日寅时,月将午 | 待计算 | 传统算法手算 |
| FL006 | 己巳日亥时,月将卯 | 待计算 | 传统算法手算 |
| FL007 | 庚午日子时,月将丑 | 待计算 | 传统算法手算 |
| FL008 | 辛未日酉时,月将辰 | 待计算 | 传统算法手算 |
| FL009 | 壬申日戌时,月将寅 | 待计算 | 传统算法手算 |
| FL010 | 癸酉日未时,月将申 | 待计算 | 传统算法手算 |

### 详细验证案例: 甲子日午时月将亥

```
天盘构建: 亥加临午
地盘: 子 丑 寅 卯 辰 巳 午 未 申 酉 戌 亥
天盘: 巳 午 未 申 酉 戌 亥 子 丑 寅 卯 辰

偏移量计算: 亥(11) - 午(6) = 5, 天盘 = (地盘 + 5) % 12

甲寄宫寅:
一课: 寅上神 = (2+5)%12 = 7 = 未 → 未/寅
二课: 未上神 = (7+5)%12 = 0 = 子 → 子/未
三课: 子上神 = (0+5)%12 = 5 = 巳 → 巳/子
四课: 巳上神 = (5+5)%12 = 10 = 戌 → 戌/巳
```

### 验证命令
```bash
python -m pytest tests/test_four_lessons.py -v
```

---

# 子项目 6：三传计算 - 基础课体

## 6.1 目标
实现贼克、比用、涉害三种基础取初传方法。

## 6.2 算法说明

### 贼克法（元首课）
- 条件：四课中有且仅有一个下克上
- 取法：取被克者（天盘）为初传

### 比用法
- 条件：四课中有多个下克上
- 取法：取与日干阴阳相同的被克者

### 涉害法
- 条件：比用后仍有多个
- 取法：计算各候选从所临位置到本位经过的克数，取最深者
- 涉害深度计算：从天盘地支所临地盘位置，数到天盘地支本位，途中受克次数

## 6.3 实现内容

### liuren/three_passes.py (Part 1)
```python
def find_ke_relations(lessons: List[Lesson], day_stem: str) -> List[tuple]:
    """
    找出四课中的下克上关系
    返回: [(课index, 被克天盘, 克者地盘), ...]
    """
    pass

def select_by_biyon(candidates: List, day_stem: str) -> List:
    """比用法：筛选与日干阴阳相同者"""
    pass

def calculate_shehai_depth(branch: str, heaven_plate: dict) -> int:
    """计算涉害深度"""
    pass

def get_initial_pass_basic(plate: LiurenPlate) -> tuple[str, str]:
    """
    基础取初传: 贼克->比用->涉害
    返回: (初传地支, 课体名称)
    """
    pass
```

## 6.4 测试计划

### 测试文件: `tests/test_three_passes.py` (Part 1)

| 测试ID | 课体 | 输入条件 | 预期初传 | 验证依据 |
|--------|------|----------|----------|----------|
| TP001 | 元首课 | 仅一个下克上 | 被克者 | 《大六壬指南》 |
| TP002 | 重审课 | 两克,阴阳不同 | 与日干同阴阳者 | 比用法规则 |
| TP003 | 知一课 | 两克,阴阳相同 | 涉害最深者 | 涉害法规则 |
| TP004 | 涉害深度 | 特定天盘配置 | 正确深度值 | 手动计算 |

### 具体测试案例

```python
# 元首课示例 (待确认具体数据)
def test_yuanshou():
    """元首课: 仅一个下克上"""
    plate = create_plate('甲', '子', '午', '亥')
    lessons = calculate_four_lessons(plate)
    initial, lesson_type = get_initial_pass_basic(plate)
    assert lesson_type == '元首'
```

### 验证命令
```bash
python -m pytest tests/test_three_passes.py::TestBasicPasses -v
```

---

# 子项目 7：三传计算 - 特殊课体

## 7.1 目标
实现遥克、昴星、别责、八专课体。

## 7.2 算法说明

### 遥克课
- 条件：四课无下克上
- 取法：从十二天盘中找能克日干者
- 分类：蒿矢(一克)、弹射(多克取与日干同阴阳)

### 昴星课
- 条件：无克且无遥克
- 取法：阳日取日支前一位上神，阴日取日支后一位上神

### 别责课
- 条件：日干为阳且时支为阴，或日干为阴且时支为阳
- 取法：日干寄宫上神

### 八专课
- 条件：日干支同位(如甲寅、乙卯等)
- 取法：特殊规则

## 7.3 实现内容

### liuren/three_passes.py (Part 2)
```python
def find_yaoke(heaven_plate: dict, day_stem: str) -> List[str]:
    """遥克法：找天盘中克日干者"""
    pass

def get_mao_xing(plate: LiurenPlate) -> str:
    """昴星法取初传"""
    pass

def get_bie_ze(plate: LiurenPlate) -> str:
    """别责法取初传"""
    pass

def get_ba_zhuan(plate: LiurenPlate) -> str:
    """八专法取初传"""
    pass
```

## 7.4 测试计划

| 测试ID | 课体 | 输入条件 | 预期结果 | 验证依据 |
|--------|------|----------|----------|----------|
| TP101 | 蒿矢课 | 四课无克,天盘一克 | 该克者为初传 | 遥克规则 |
| TP102 | 弹射课 | 四课无克,天盘多克 | 与日干同阴阳者 | 遥克+比用 |
| TP103 | 昴星课-阳日 | 无克无遥克,阳日 | 日支前一位上神 | 昴星规则 |
| TP104 | 昴星课-阴日 | 无克无遥克,阴日 | 日支后一位上神 | 昴星规则 |
| TP105 | 别责课 | 干时阴阳相错 | 寄宫上神 | 别责规则 |
| TP106 | 八专课 | 甲寅日等 | 特殊取法 | 八专规则 |

### 验证命令
```bash
python -m pytest tests/test_three_passes.py::TestSpecialPasses -v
```

---

# 子项目 8：三传计算 - 伏吟返吟

## 8.1 目标
实现伏吟课和返吟课。

## 8.2 算法说明

### 伏吟课
- 条件：天地盘重合（月将等于时支）
- 取法：
  - 有克：按正常规则
  - 无克阳日：日支前一位为初传（阳日自刑）
  - 无克阴日：日干寄宫上神为初传

### 返吟课
- 条件：天地盘对冲（月将冲时支）
- 取法：取驿马为初传

## 8.3 实现内容

### liuren/three_passes.py (Part 3)
```python
def is_fuyin(plate: LiurenPlate) -> bool:
    """判断是否伏吟"""
    return plate.moon_general == plate.hour_branch

def is_fanyin(plate: LiurenPlate) -> bool:
    """判断是否返吟"""
    return BRANCH_CHONG[plate.moon_general] == plate.hour_branch

def get_fuyin_pass(plate: LiurenPlate) -> tuple[str, str]:
    """伏吟课取初传"""
    pass

def get_fanyin_pass(plate: LiurenPlate) -> str:
    """返吟课取初传"""
    # 返回日支的驿马
    return BRANCH_YIMA[plate.day_branch]
```

## 8.4 测试计划

| 测试ID | 课体 | 输入条件 | 预期结果 | 验证依据 |
|--------|------|----------|----------|----------|
| TP201 | 伏吟判定 | 月将=时支 | True | 定义 |
| TP202 | 返吟判定 | 月将冲时支 | True | 六冲关系 |
| TP203 | 伏吟有克 | 伏吟+有下克上 | 正常取被克者 | 伏吟规则 |
| TP204 | 伏吟无克阳日 | 伏吟无克+阳日 | 日支前一位 | 伏吟规则 |
| TP205 | 伏吟无克阴日 | 伏吟无克+阴日 | 寄宫上神 | 伏吟规则 |
| TP206 | 返吟取驿马 | 返吟课 | 日支驿马 | 返吟规则 |

### 验证命令
```bash
python -m pytest tests/test_three_passes.py::TestFuyinFanyin -v
```

---

# 子项目 9：三传计算 - 中末传

## 9.1 目标
实现中传、末传的计算。

## 9.2 算法说明

### 标准规则
- 中传：初传所临地盘位置的上神
- 末传：中传所临地盘位置的上神

### 特殊规则（伏吟）
- 伏吟时三传相同（因为上神等于本位）
- 需按特殊规则处理

### 特殊规则（返吟）
- 返吟时中传=初传冲，末传=初传

## 9.3 实现内容

### liuren/three_passes.py (Part 4)
```python
def calculate_three_passes(plate: LiurenPlate) -> List[Pass]:
    """
    计算完整三传
    1. 确定课体
    2. 取初传
    3. 计算中传、末传
    """
    # 判断特殊课体
    if is_fuyin(plate):
        return calculate_fuyin_passes(plate)
    if is_fanyin(plate):
        return calculate_fanyin_passes(plate)

    # 标准流程
    initial = get_initial_pass(plate)
    middle = get_heaven_branch(plate.heaven_plate, initial)
    final = get_heaven_branch(plate.heaven_plate, middle)

    return [
        Pass(branch=initial, index=1),
        Pass(branch=middle, index=2),
        Pass(branch=final, index=3)
    ]
```

## 9.4 测试计划

| 测试ID | 场景 | 输入 | 预期三传 | 验证依据 |
|--------|------|------|----------|----------|
| TP301 | 标准三传 | 元首课 | 顺序正确 | 上神递推 |
| TP302 | 伏吟三传 | 伏吟课 | 特殊规则 | 伏吟传法 |
| TP303 | 返吟三传 | 返吟课 | 驿马-冲-驿马 | 返吟传法 |
| TP304 | 昴星三传 | 昴星课 | 特殊规则 | 昴星传法 |

### 验证命令
```bash
python -m pytest tests/test_three_passes.py::TestThreePasses -v
```

---

# 子项目 10：UI - 输入面板

## 10.1 目标
实现干支选择器和排盘按钮。

## 10.2 实现内容

### ui/input_panel.py
```python
import pygame
from config import HEAVENLY_STEMS, EARTHLY_BRANCHES

class DropdownSelector:
    """下拉选择器组件"""
    def __init__(self, x, y, width, options, label):
        pass

    def draw(self, screen):
        pass

    def handle_event(self, event) -> bool:
        pass

    def get_value(self) -> str:
        pass

class InputPanel:
    """输入面板：包含日干、日支、时支选择器"""
    def __init__(self, x, y):
        self.day_stem_selector = DropdownSelector(...)
        self.day_branch_selector = DropdownSelector(...)
        self.hour_branch_selector = DropdownSelector(...)
        self.auto_button = Button(...)
        self.paipan_button = Button(...)

    def draw(self, screen):
        pass

    def handle_event(self, event):
        pass

    def get_input(self) -> dict:
        """返回 {'day_stem': str, 'day_branch': str, 'hour_branch': str}"""
        pass
```

## 10.3 测试计划

| 测试ID | 测试名称 | 操作 | 预期结果 | 验证方法 |
|--------|----------|------|----------|----------|
| UI001 | 下拉展开 | 点击选择器 | 显示选项列表 | 视觉验证 |
| UI002 | 选项选择 | 点击选项 | 值被选中,列表收起 | 视觉验证 |
| UI003 | 干支完整 | 展开各选择器 | 显示10干/12支 | 视觉验证 |
| UI004 | 排盘触发 | 点击排盘按钮 | 触发回调 | 回调被调用 |
| UI005 | 自动排盘 | 点击自动按钮 | 填入当前时间干支 | 值正确 |

### 验证方法
```bash
python -c "from ui.input_panel import InputPanel; import pygame; ..."
# 手动交互测试
```

---

# 子项目 11：UI - 式盘高亮

## 11.1 目标
在式盘上高亮显示四课三传涉及的位置。

## 11.2 实现内容

### ui/highlight.py
```python
class PlateHighlighter:
    """式盘高亮渲染器"""

    def __init__(self, center, radius):
        self.center = center
        self.radius = radius

    def highlight_branch(self, screen, branch: str, color, angle_offset: float):
        """高亮某个地支位置"""
        pass

    def highlight_lessons(self, screen, lessons: List[Lesson], angle_offset: float):
        """高亮四课位置"""
        pass

    def highlight_passes(self, screen, passes: List[Pass], angle_offset: float):
        """高亮三传位置"""
        pass
```

## 11.3 测试计划

| 测试ID | 测试名称 | 输入 | 预期结果 | 验证方法 |
|--------|----------|------|----------|----------|
| HL001 | 单位置高亮 | 地支'子' | 子位置发光 | 视觉验证 |
| HL002 | 四课高亮 | 四课数据 | 4个位置高亮 | 视觉验证 |
| HL003 | 三传高亮 | 三传数据 | 3个位置高亮 | 视觉验证 |
| HL004 | 颜色区分 | 四课+三传 | 不同颜色 | 视觉验证 |
| HL005 | 旋转同步 | 旋转天盘 | 高亮跟随旋转 | 视觉验证 |

---

# 子项目 12：UI - 结果侧边栏

## 12.1 目标
显示四课三传结果和推导过程。

## 12.2 实现内容

### ui/sidebar.py
```python
class ResultSidebar:
    """结果显示侧边栏"""

    def __init__(self, x, y, width, height):
        pass

    def set_plate(self, plate: LiurenPlate):
        """设置要显示的盘局"""
        self.plate = plate

    def draw(self, screen):
        """绘制结果面板"""
        # 显示: 日干支、时支、月将、课体
        # 显示: 四课表格
        # 显示: 三传
        # 显示: 推导过程
        pass
```

## 12.3 测试计划

| 测试ID | 测试名称 | 输入 | 预期结果 | 验证方法 |
|--------|----------|------|----------|----------|
| SB001 | 基本信息显示 | LiurenPlate | 显示日干支等 | 视觉验证 |
| SB002 | 四课表格 | 四课数据 | 正确格式显示 | 视觉验证 |
| SB003 | 三传显示 | 三传数据 | 箭头连接显示 | 视觉验证 |
| SB004 | 推导过程 | derivation_log | 逐行显示 | 视觉验证 |
| SB005 | 滚动功能 | 长推导过程 | 可滚动查看 | 交互验证 |

---

# 子项目 13：主程序集成

## 13.1 目标
重构 `main.py`，集成所有组件。

## 13.2 实现内容

### main.py 重构
```python
class CyberLiuren:
    def __init__(self):
        # 调整窗口尺寸 1200x800
        self.screen = pygame.display.set_mode((1200, 800))

        # 初始化组件
        self.input_panel = InputPanel(20, 20)
        self.sidebar = ResultSidebar(850, 20, 330, 760)
        self.highlighter = PlateHighlighter(...)

        # 当前盘局
        self.current_plate = None

    def on_paipan(self, input_data: dict):
        """排盘按钮回调"""
        # 1. 计算月将
        # 2. 创建 LiurenPlate
        # 3. 计算四课三传
        # 4. 更新显示
        pass

    def run(self):
        # 主循环
        pass
```

## 13.3 测试计划

| 测试ID | 测试名称 | 操作 | 预期结果 | 验证方法 |
|--------|----------|------|----------|----------|
| INT001 | 完整排盘流程 | 选干支+排盘 | 显示完整结果 | 端到端测试 |
| INT002 | 式盘高亮 | 排盘后 | 四课三传高亮 | 视觉验证 |
| INT003 | 结果正确性 | 已知案例 | 与传统软件对照 | 对比验证 |
| INT004 | 天盘旋转 | 拖拽/惯性 | 高亮跟随 | 交互验证 |
| INT005 | 自动排盘 | 点击自动 | 当前时间排盘 | 功能验证 |

---

# 子项目 14：导出功能

## 14.1 目标
实现截图保存和文字导出。

## 14.2 实现内容

### export/screenshot.py
```python
def save_screenshot(screen, filename: str = None) -> str:
    """保存当前屏幕截图"""
    if filename is None:
        filename = f"liuren_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    pygame.image.save(screen, filename)
    return filename
```

### export/text_export.py
```python
def export_plate_text(plate: LiurenPlate) -> str:
    """导出盘局文字描述"""
    lines = [
        f"日干支: {plate.day_stem}{plate.day_branch}",
        f"时支: {plate.hour_branch}",
        f"月将: {plate.moon_general}({plate.moon_general_name})",
        f"课体: {plate.lesson_type}",
        "",
        "【四课】",
        "  一课  二课  三课  四课",
        f"天: {' '.join(l.heaven for l in plate.lessons)}",
        f"地: {' '.join(l.earth for l in plate.lessons)}",
        "",
        f"【三传】{plate.passes[0].branch} → {plate.passes[1].branch} → {plate.passes[2].branch}",
        "",
        "【推导过程】",
        *plate.derivation_log
    ]
    return '\n'.join(lines)

def save_to_file(plate: LiurenPlate, filename: str = None) -> str:
    """保存到文件"""
    pass
```

## 14.3 测试计划

| 测试ID | 测试名称 | 输入 | 预期结果 | 验证方法 |
|--------|----------|------|----------|----------|
| EX001 | 截图保存 | 当前屏幕 | PNG文件生成 | 文件存在 |
| EX002 | 文字导出 | LiurenPlate | 格式正确的文本 | 内容验证 |
| EX003 | 文件保存 | 导出文本 | TXT文件生成 | 文件存在 |
| EX004 | 文件名生成 | 无参数 | 时间戳命名 | 格式正确 |

---

# 综合集成测试

## 已知案例验证

以下案例用于端到端验证系统正确性：

| 案例ID | 日干支 | 时支 | 月将 | 课体 | 四课 | 三传 | 来源 |
|--------|--------|------|------|------|------|------|------|
| CASE01 | 甲子 | 午 | 亥 | 元首 | 待验证 | 待验证 | 《大六壬指南》 |
| CASE02 | 丙寅 | 申 | 酉 | 比用 | 待验证 | 待验证 | 待查 |
| CASE03 | 戊辰 | 寅 | 午 | 涉害 | 待验证 | 待验证 | 待查 |
| CASE04 | 伏吟案例 | - | - | 伏吟 | 待验证 | 待验证 | 待查 |
| CASE05 | 返吟案例 | - | - | 返吟 | 待验证 | 待验证 | 待查 |
| CASE06 | 遥克案例 | - | - | 蒿矢 | 待验证 | 待验证 | 待查 |
| CASE07 | 昴星案例 | - | - | 昴星 | 待验证 | 待验证 | 待查 |
| CASE08 | 别责案例 | - | - | 别责 | 待验证 | 待验证 | 待查 |
| CASE09 | 八专案例 | - | - | 八专 | 待验证 | 待验证 | 待查 |
| CASE10 | 当前时间 | 自动 | 自动 | - | - | - | 与其他软件对比 |

---

# 开发顺序与依赖关系

```
子项目1 (常量) ──┬──> 子项目3 (月将)
                │
子项目2 (万年历) ─┘
                      │
                      v
                子项目4 (式盘状态)
                      │
                      v
                子项目5 (四课) ──┬──> 子项目6 (三传基础)
                                │
                                ├──> 子项目7 (三传特殊)
                                │
                                └──> 子项目8 (伏吟返吟)
                                            │
                                            v
                                      子项目9 (中末传)
                                            │
子项目10 (输入面板) ──┐                     │
                      │                     │
子项目11 (高亮) ──────┼──> 子项目13 (集成) <─┘
                      │
子项目12 (侧边栏) ────┘
                            │
                            v
                      子项目14 (导出)
```

---

# 依赖安装

```bash
pip install pygame>=2.1.0 sxtwl>=1.0.0 pytest
```

---

# 运行测试

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定子项目测试
python -m pytest tests/test_constants.py -v
python -m pytest tests/test_calendar.py -v
python -m pytest tests/test_four_lessons.py -v
python -m pytest tests/test_three_passes.py -v

# 运行集成测试
python -m pytest tests/test_integration.py -v
```

---
---

# Main Project 2: 式盘3D化

## 项目概述

在保留全部现有2D功能的基础上，增加3D查看模式：
- 2D/3D模式切换（Tab键）
- 3D漆器实物风格：地盘为有厚度的方形木板，天盘为有厚度的圆盘叠在上面
- 3D视角操控：右键拖拽旋转视角，滚轮缩放
- 3D天盘操控：左键拖拽旋转天盘（保留物理惯性）
- UI面板（侧边栏、输入面板）在3D模式下保持功能

## 技术方案

**ModernGL + Pygame（Framebuffer Readback）**
- 使用 `moderngl.create_standalone_context()` 创建独立GL上下文
- 3D场景渲染到800x800 framebuffer，读回为Pygame surface
- 2D UI组件（sidebar, input panel）继续用Pygame绘制在上层
- 现有2D代码零修改风险
- 矩阵库使用 `pyrr`

## 新增依赖

```bash
pip install moderngl pyrr numpy
```

## 新增项目结构

```
Liuren/
├── renderer3d/
│   ├── __init__.py           # Package exports
│   ├── context.py            # ModernGL上下文 + Pygame集成
│   ├── camera.py             # 轨道相机（球坐标、矩阵）
│   ├── geometry.py           # 网格生成（方盒、圆柱、UV）
│   ├── shaders.py            # GLSL着色器源码
│   ├── plate_renderer.py     # 3D式盘渲染主类
│   └── texture_manager.py    # Pygame Surface -> GL纹理转换
├── main.py                   # [修改] 模式切换、条件渲染
└── config.py                 # [扩展] 3D相关常量
```

---

# 子项目 3D-1: ModernGL上下文与Pygame集成

## 目标
建立 ModernGL + Pygame 桥接管道。在盘区域渲染一个测试图形，验证管线可用。

## 实现内容

### renderer3d/context.py
- `class GLContext`:
  - `__init__(width=800, height=800)`: 创建standalone ModernGL context，创建FBO（颜色+深度附件）
  - `begin_frame()`: 绑定FBO，清屏，设viewport
  - `end_frame() -> pygame.Surface`: 从FBO读像素(`fbo.read()`)，Y轴翻转，转为Pygame surface
  - `release()`: 清理GL资源

### renderer3d/shaders.py
- 最小化vertex/fragment shader对（硬编码三角形，纯色）用于验证

### main.py 修改
- 新增 `self.mode_3d = False`
- `Tab` 键切换
- 渲染分支：3D模式下用GLContext渲染，blit到plate区域(0,0)

## 验证标准
- Tab切换后plate区域显示彩色测试图形
- 2D模式完全不变
- 两种模式均60FPS
- UI面板正常覆盖在3D视口上方

## 关键文件
- 新建: `renderer3d/__init__.py`, `renderer3d/context.py`, `renderer3d/shaders.py`
- 修改: `main.py`

---

# 子项目 3D-2: 轨道相机

## 目标
实现球坐标轨道相机，支持鼠标交互。

## 实现内容

### renderer3d/camera.py
- `class OrbitCamera`:
  - 状态: `theta`(方位角), `phi`(仰角,限10°-80°), `distance`(缩放), `target`(看向点,默认原点)
  - `get_view_matrix() -> mat4`: 从球坐标计算eye位置，构建lookAt矩阵
  - `get_projection_matrix(aspect) -> mat4`: 透视投影(45°FOV)
  - `orbit(dx, dy)`: 鼠标增量调整theta/phi
  - `zoom(delta)`: 调整distance（有范围限制）
  - `get_vp_matrix() -> mat4`: 返回 projection * view

### main.py 事件处理
- 3D模式下:
  - 右键拖拽 → `camera.orbit(dx, dy)`
  - 滚轮 → `camera.zoom(delta)`
  - 左键拖拽 → 仍旋转天盘（物理不变）
- 2D模式: 完全不变

## 验证标准
- 右键拖拽可环绕原点旋转视角
- 滚轮缩放
- 初始视角：约45°仰角俯视
- 无万向锁问题

## 关键文件
- 新建: `renderer3d/camera.py`
- 修改: `main.py`（3D模式事件处理）

---

# 子项目 3D-3: 地盘3D几何体

## 目标
将地盘创建为带纹理的3D方盒（有厚度的漆木板），渲染在3D场景中。

## 实现内容

### renderer3d/geometry.py
- `create_box_mesh(width, height, depth) -> (vertices, indices)`:
  - 6面，每面4顶点，顶点数据：position(3) + normal(3) + UV(2)
  - 顶面UV映射完整地盘纹理
  - 侧面纯色（深朱红漆 COLOR_EARTH_BG暗化）
  - 世界尺寸: 7.0 x 7.0 x 0.5

### renderer3d/texture_manager.py
- `class TextureManager`:
  - `surface_to_texture(ctx, surface) -> moderngl.Texture`: Pygame surface → GL纹理
  - `update_texture(texture, surface)`: 更新已有纹理数据
  - 注意Pygame Y轴翻转

### renderer3d/shaders.py（扩展）
- `PLATE_VERT`: MVP矩阵变换，传递UV和法线
- `PLATE_FRAG`: 采样纹理，基础漫反射光照

### renderer3d/plate_renderer.py
- `class PlateRenderer3D`:
  - `__init__(ctx, earth_surface)`: 创建VAO/VBO/IBO，编译shader，上传地盘纹理
  - `render_earth(vp_matrix)`: 绘制地盘方盒

## 验证标准
- 地盘渲染为有厚度的3D方块
- 顶面显示完整地盘纹理（所有文字、装饰、节点）
- 侧面显示深色漆器颜色
- 轨道相机可从各角度查看3D厚度
- 盘体居中于世界原点

## 关键文件
- 新建: `renderer3d/geometry.py`, `renderer3d/texture_manager.py`, `renderer3d/plate_renderer.py`
- 修改: `renderer3d/shaders.py`

---

# 子项目 3D-4: 天盘3D几何体

## 目标
将天盘创建为带纹理的3D圆柱（有厚度的圆盘），悬浮在地盘上方。

## 实现内容

### renderer3d/geometry.py（扩展）
- `create_cylinder_mesh(radius, height, segments=64) -> (vertices, indices)`:
  - 顶面：扇形展开，UV圆形映射(中心0.5,0.5)
  - 底面：同上，法线朝下
  - 侧面：环形quad strip
  - 世界尺寸: radius=2.1, height=0.3, Y偏移=0.5（与地盘间距）

### 天盘纹理策略
当前 `heaven_surf` 不含月将和二十八宿文字（已移至实时绘制以避免模糊）。3D模式需要创建完整纹理：
- 新增 `create_heaven_plate_3d() -> pygame.Surface`:
  - 基于 `heaven_surf`（北斗、圆环、光影）
  - 在其上绘制所有月将文字（角度=0的默认位置）
  - 绘制二十八宿文字
  - 排盘后追加天将文字
- 此surface在排盘/动画完成时重建，上传为静态纹理
- 3D中几何体旋转，纹理自然随动，无模糊问题

### plate_renderer.py（扩展）
- `render_heaven(vp_matrix, angle)`:
  - 构建model矩阵：Y轴平移 + 绕Y轴旋转angle
  - 绘制带天盘纹理的圆柱

## 验证标准
- 天盘渲染为厚圆盘，悬浮在地盘上方
- 可见两层间隙（漆器物理分离感）
- 顶面显示天盘纹理（北斗、结构圆、光影、月将、二十八宿）
- 天盘以2D模式相同角度旋转

## 关键文件
- 修改: `renderer3d/geometry.py`, `renderer3d/plate_renderer.py`
- 修改: `main.py`（新增 `create_heaven_plate_3d()` 方法）

## 注意
现有 `draw_convex_lighting()` 在纹理中烘焙了高光。3D模式有真实光照后可能过亮。可选择：不在3D纹理中调用 `draw_convex_lighting()`，由shader处理光照。调试时决定。

---

# 子项目 3D-5: 光照与材质（漆器美学）

## 目标
实现3D光照系统，匹配赛博漆器美学。

## 实现内容

### renderer3d/shaders.py（替换测试shader为生产shader）

**Vertex Shader**: MVP变换，传递世界坐标、法线、UV
**Fragment Shader**: Blinn-Phong光照模型
- 漫反射 + 镜面反射 + 环境光
- `u_light_dir`: 方向光，从左上方照射（匹配现有convex lighting方向）
- `u_light_color`: 暖色调 (1.0, 0.95, 0.85)
- `u_ambient`: 暖暗环境光 (0.15, 0.12, 0.10)
- `u_shininess`: 漆器高光值
- `u_use_texture`: 区分纹理面和纯色侧面

**材质参数**:
- 地盘: 低光泽度(8-16)，偏木质感，侧面COLOR_EARTH_BG暗化
- 天盘: 高光泽度(32-64)，漆器光泽，侧面COLOR_HEAVEN_BG暗化

## 验证标准
- 两个盘体有可见3D光照和高光
- 漆器质感：天盘表面微微泛光
- 侧面光照正确
- 整体色温匹配赛博漆器美学

## 关键文件
- 修改: `renderer3d/shaders.py`, `renderer3d/plate_renderer.py`
- 可能修改: `config.py`（3D光照常量）

---

# 子项目 3D-6: 盘间阴影

## 目标
在3D空间中渲染天盘投射在地盘上的阴影。

## 实现内容

### renderer3d/geometry.py（扩展）
- `create_shadow_disc(radius, segments=64)`: 扁平圆盘，Y=0.01（地盘表面微上方）
- UV映射径向渐变纹理（中心暗，边缘透明）

### 渲染
- 复用现有 `shadow_surf` 概念，生成渐变纹理
- 开启alpha混合，在地盘之后、天盘之前渲染
- 阴影不随天盘旋转（形状投影，非标记）

## 验证标准
- 从侧面视角可见盘间阴影
- 阴影外观匹配2D模式
- 阴影不跟随天盘旋转

## 关键文件
- 修改: `renderer3d/geometry.py`, `renderer3d/plate_renderer.py`

---

# 子项目 3D-7: 3D高亮（四课三传）

## 目标
在3D模式下显示四课三传高亮效果。

## 实现内容

### 方案：3D → 2D投影 + 现有Pygame绘制
- 计算高亮地支的3D世界坐标（在天盘上的位置，考虑旋转角度）
- 通过VP矩阵投影到屏幕坐标
- 复用现有 `PlateHighlighter` 在投影位置绘制发光效果

### ui/highlight.py（扩展）
- 新增 `project_3d_to_screen(world_pos, vp_matrix, viewport) -> (screen_x, screen_y)`
- 标准投影：clip = vp * world → ndc = clip.xyz/clip.w → screen

## 验证标准
- 相机旋转时四课高亮跟随正确位置
- 天盘旋转时三传高亮跟随
- 背面不可见时高亮消失
- 连接线在3D下正确绘制

## 关键文件
- 修改: `ui/highlight.py`
- 修改: `main.py`（3D模式高亮渲染路径）

---

# 子项目 3D-8: 操控集成与模式切换完善

## 目标
完善2D/3D模式切换，确保所有操控在两种模式下正确工作。

## 实现内容

### main.py 完善
- `Tab`键切换 + HUD显示当前模式
- 3D模式操控:
  - 左键拖拽plate区域 → 旋转天盘（物理惯性不变）
  - 右键拖拽 → 轨道相机旋转
  - plate区域滚轮 → 缩放
  - sidebar区域滚轮 → 滚动sidebar
- 2D模式: 完全不变
- 所有快捷键两种模式通用（Space, F5, F6）

### 天盘3D拖拽
- 3D模式下左键水平拖拽增量直接映射到旋转角度增量
- 保持惯性/摩擦物理
- 灵敏度与2D模式接近

### 相机默认值
- 初始：仰角45°，方位角0°，distance适配盘体填满视口
- `Home`键或右键双击重置视角

## 验证标准
- 2D↔3D无缝切换（无闪烁、无状态丢失）
- 事件路由正确：UI区域点击给UI，plate区域点击给plate/camera
- 截图(F5)在3D模式下正确捕获
- 所有交互感觉流畅自然

## 关键文件
- 修改: `main.py`

---

# 子项目 3D-9: 性能优化与视觉打磨

## 目标
确保60FPS，视觉打磨，处理边界情况。

## 实现内容

### 性能
- 分析framebuffer readback性能，必要时使用PBO异步读取
- 纹理上传优化：仅在状态变化时重传（dirty flag）
- 地盘纹理只上传一次（完全静态）

### 视觉打磨
- MSAA 4x抗锯齿（ModernGL FBO设samples=4，加resolve步骤）
- 3D模式背景：保持深色或微渐变
- 模式切换动画（可选：从俯视平滑过渡到3D视角）

### 边界情况
- 截图在3D模式下捕获合成画面
- 文字导出不受影响（基于数据非视觉）
- GL资源清理（退出/模式切换时释放）

## 验证标准
- 两种模式稳定60FPS
- 抗锯齿的3D边缘
- 无内存泄漏
- 截图正确

## 关键文件
- 修改: `renderer3d/context.py`（MSAA）, `renderer3d/plate_renderer.py`, `main.py`

---

# Main Project 2 依赖关系

```
3D-1 (上下文) → 3D-2 (相机) → 3D-3 (地盘) → 3D-4 (天盘)
                                                    ↓
3D-5 (光照) → 3D-6 (阴影) → 3D-7 (高亮) → 3D-8 (操控) → 3D-9 (打磨)
```

线性关键路径: 3D-1 → 3D-2 → 3D-3 → 3D-4 → 3D-5 → 3D-6 → 3D-7 → 3D-8 → 3D-9

---

# Main Project 2 设计决策汇总

| 决策 | 选择 | 理由 |
|------|------|------|
| 渲染架构 | Framebuffer Readback | 保留全部2D UI代码；隔离清晰；~2ms开销可接受 |
| GL上下文 | Standalone | 避免Pygame display冲突 |
| 矩阵库 | pyrr | 轻量；提供所需矩阵运算 |
| 3D文字 | 预渲染到纹理 | 无模糊；仅状态变化时更新 |
| 3D高亮 | 投影到2D后用Pygame绘制 | 复用PlateHighlighter；最少新代码 |
| 阴影 | 盘间纹理圆盘 | 匹配2D外观；无shadow map复杂性 |
| 抗锯齿 | MSAA 4x | ModernGL简单开启；视觉提升大 |
| 模式切换 | Tab键 + boolean flag | 简单；状态跨切换保留 |

---

# 更新后的依赖安装

```bash
pip install pygame>=2.1.0 cnlunar pytest moderngl pyrr numpy
```

---

# 更新后的运行测试

```bash
# 运行所有测试
python -m pytest tests/ -v

# 运行特定子项目测试
python -m pytest tests/test_constants.py -v
python -m pytest tests/test_calendar.py -v
python -m pytest tests/test_four_lessons.py -v
python -m pytest tests/test_three_passes.py -v

# 运行集成测试
python -m pytest tests/test_integration.py -v

# 运行应用（验证3D功能）
python main.py
# Tab键切换2D/3D模式
```

---
---

# Main Project 3: 3D视觉美化

## 项目概述

在已完成的3D模式基础上进行视觉美化（**仅3D模式，2D模式不动**）：
1. 天盘从平面圆柱改为穹顶半球（类似出土漆器实物）
2. 北斗七星从平面纹理改为3D空间中悬浮的发光星座
3. 二十八星宿作为发光点环绕在天盘上方
4. 四圣兽（青龙/白虎/朱雀/玄武）以星座连线形式环绕

**设计决策**:
- 穹顶纹理贴弧面（彩绘漆碗风格）
- 星星风格：发光点+星座连线（天象图效果）
- 四圣兽：28宿中每组7星用颜色连线组成轮廓
- 盘面文字全部保留不变（3D装饰是额外叠加）
- 所有天体装饰物随天盘一起旋转

## 新增项目结构

```
Liuren/
├── renderer3d/
│   ├── celestial.py         # [新建] 天体装饰渲染器（星点+星座连线）
│   ├── geometry.py          # [修改] 新增穹顶网格生成
│   ├── shaders.py           # [修改] 新增billboard+line shader
│   ├── plate_renderer.py    # [修改] 天盘改用穹顶
│   └── __init__.py          # [修改] 导出CelestialRenderer3D
├── main.py                  # [修改] 集成天体渲染器, 修复highlight Y坐标
```

---

# 子项目 3D-10: 穹顶天盘几何体

## 目标
将天盘从平面圆柱改为穹顶形状（球冠顶面+短圆柱边缘+平底），纹理通过正交投影UV映射到弧面。

## 实现内容

### renderer3d/geometry.py — 新增 `create_dome_mesh()`
```python
def create_dome_mesh(radius, dome_height, rim_height, rings=24, segments=64):
    """穹顶网格：球冠顶面 + 圆柱边缘 + 平底面。
    Returns: (vertices, indices, dome_index_count)
    """
```

**穹顶面参数化**（抛物面近似 `y = h*(1 - t²)`）：
- 同心环 `i=0..rings`，角度细分 `j=0..segments`
- `t = i / rings`（0=中心, 1=边缘）
- 位置: `(radius*t*cos(θ), dome_height*(1-t²), radius*t*sin(θ))`
- UV正交投影: `u = 0.5 + 0.5*cos(θ)*t`, `v = 0.5 + 0.5*sin(θ)*t`
- 法线: 从抛物面梯度解析计算并归一化

**短圆柱边缘（rim）**：穹顶边缘(y=0)到底面(y=-rim_height)
**平底面**：y=-rim_height
**索引分区**：穹顶面在前（贴纹理），边缘+底面在后（侧色）

### renderer3d/plate_renderer.py — 修改
- 新常量: `DOME_HEIGHT = 0.45`, `RIM_HEIGHT = 0.15`
- 构造函数: `create_cylinder_mesh` → `create_dome_mesh`
- 导出 `DOME_HEIGHT` 供 `_highlight_3d` 使用
- 新增 `get_heaven_model(angle_deg)` 方法（供后续celestial renderer共享模型矩阵）

### main.py — 修改 `_highlight_3d()`
- 高亮Y坐标从平顶 `HEAVEN_DEPTH/2` 改为穹顶面高度:
  `highlight_y = DOME_HEIGHT * (1 - (r/R)²)`

## 关键参数
| 参数 | 值 | 说明 |
|------|-----|------|
| DOME_HEIGHT | 0.45 | 半径21%弧度，文字不过度扭曲 |
| RIM_HEIGHT | 0.15 | 短边缘，漆碗唇口感 |
| rings | 24 | 平滑弧面 |
| segments | 64 | 与现有圆柱一致 |

## 验证标准
- 天盘显示穹顶形状，有可见弧度
- 纹理正确映射到弧面
- Blinn-Phong高光在弧面上正确移动
- `_highlight_3d` 高亮跟随穹顶面
- 2D模式不变，160 tests pass

## 关键文件
- 修改: `renderer3d/geometry.py`, `renderer3d/plate_renderer.py`, `main.py`

---

# 子项目 3D-11: 天体渲染器 + 北斗七星3D星座

## 目标
创建 `CelestialRenderer3D` 类，渲染悬浮在穹顶上方的发光星点和星座连线。首个实现：北斗七星。

## 实现内容

### renderer3d/shaders.py — 新增4个shader
- **BILLBOARD_VERTEX_SHADER**: model变换星点中心位置，camera_right/up展开billboard四边形
- **GLOW_FRAGMENT_SHADER**: 高斯衰减发光 `glow = exp(-dist²*3.0)`
- **LINE_VERTEX_SHADER**: MVP变换 + per-vertex颜色
- **LINE_FRAGMENT_SHADER**: 直通颜色输出

### renderer3d/celestial.py — 新建
```python
class CelestialRenderer3D:
    def __init__(self, ctx, dome_height, heaven_radius):
        # 编译shader，创建北斗VAO/VBO
    def render(self, vp_matrix, model_matrix, camera_right, camera_up):
        # 关闭深度写入，渲染连线(alpha blend)→星点(additive blend)
    def release(self):
```

### 北斗七星3D坐标
2D像素坐标→3D: `scale = HEAVEN_RADIUS / 210px`，Y = 穹顶面高度 + 悬浮间距(0.35)
连线: handle 0→1→2→3, bowl 3→4→5→6

### 渲染管线集成 (main.py)
在 `_render_3d()` 中，render_heaven 之后、end_frame 之前:
```python
heaven_model = self.plate_renderer.get_heaven_model(-self.angle)
view = self.camera.get_view_matrix()
camera_right, camera_up = view[0,:3], view[1,:3]  # pyrr行主序
self.celestial_renderer.render(vp, heaven_model, camera_right, camera_up)
```

混合策略: 关闭深度写入 → 连线(alpha blend) → 星点(additive blend) → 恢复

## 关键参数
| 参数 | 值 | 说明 |
|------|-----|------|
| STAR_FLOAT_HEIGHT | 0.35 | 穹顶上方悬浮高度 |
| 北斗星点半径 | 0.08 | 相机距离12时清晰可见 |
| 中心星(idx 3) | 0.12 | 勺柄-勺身交汇，稍大 |
| 星点颜色 | (0.9, 0.7, 0.3) | 金色 |
| 连线颜色 | (0.7, 0.24, 0.24, 0.6) | 半透明暗红 |

## 验证标准
- 7个金色发光星点悬浮在穹顶上方
- 星座连线可见
- Billboard始终面向相机
- 随天盘旋转，60FPS

## 关键文件
- 新建: `renderer3d/celestial.py`
- 修改: `renderer3d/shaders.py`, `renderer3d/__init__.py`, `main.py`

---

# 子项目 3D-12: 二十八星宿 + 四圣兽星座

## 目标
在穹顶上方添加28个星宿发光点环绕成环，用四色连线将每组7星连成四圣兽星座。

## 实现内容

### 28星宿星点
- 位置: 88%半径处，360/28间距，起始90°
- 浮空高度: 0.25（比北斗0.35低，层次感）
- 星点更小(0.05)更暗(0.8强度)

### 四圣兽连线
ORDERED_XIU_R中每组7星顺序连线:
- 东方青龙(蓝): 角亢氐房心尾箕 → 索引[10,9,8,7,6,5,4]
- 北方玄武(紫): 斗牛女虚危室壁 → 索引[3,2,1,0,27,26,25]
- 西方白虎(白): 奎娄胃昴毕觜参 → 索引[24,23,22,21,20,19,18]
- 南方朱雀(红): 井鬼柳星张翼轸 → 索引[17,16,15,14,13,12,11]

颜色: 青龙(0.2,0.5,0.9) / 白虎(0.85,0.85,0.9) / 朱雀(0.85,0.25,0.2) / 玄武(0.3,0.25,0.6)

### 扩展 CelestialRenderer3D
新增28宿StarGroup + 4个LineGroup

## 验证标准
- 28星点形成均匀环形
- 4组彩色连线连接各自7星
- 与北斗共存，层次分明
- 随天盘旋转，60FPS

## 关键文件
- 修改: `renderer3d/celestial.py`

---

# 子项目 3D-13: 星宿数据模块 + 圣兽轮廓数据

## 目标
创建独立的星图数据模块，包含28宿多星座数据和四圣兽详细轮廓数据，配套完整测试。

## 实现内容

### renderer3d/xiu_data.py — 新建
- `MansionData(NamedTuple)`: 星宿数据（name, star_offsets, lines）
- `BeastOutline(NamedTuple)`: 圣兽轮廓（name, vertices, lines, color）
- 28宿各星座的多星位置和内部连线（锚星+组件星）
- `ALL_MANSIONS_ORDERED`: 按 ORDERED_XIU_R 顺序排列的28宿数据
- `BEAST_QUADRANTS`: 四象限星宿索引
- `BEAST_OUTLINES`: 四圣兽详细轮廓数据（~58-66顶点/58-62线段）

### tests/test_xiu_data.py — 新建
- 28宿数量/名称/星数/线段索引/偏移范围验证
- 四圣兽顶点/线段/颜色/范围验证
- 四象限覆盖完整性验证
- 430 tests total

## 关键文件
- 新建: `renderer3d/xiu_data.py`, `tests/test_xiu_data.py`

---

# 子项目 3D-14: 28宿多星座渲染

## 目标
将28宿从单星点扩展为多星座（每宿2-8星+内部连线），使用 xiu_data 数据。

## 实现内容

### renderer3d/celestial.py — 重写 `_build_xiu_28()`
- 每个星宿按 `star_offsets` 放置多颗组件星（锥面投影高度）
- 锚星（首星）单独渲染更大更亮
- 星宿内部连线（`mansion.lines`）用冷灰色半透明渲染
- 组件星: size=0.07, 暗金色
- 锚星: size=0.10, 更亮 (intensity=1.8)

## 关键文件
- 修改: `renderer3d/celestial.py`, `renderer3d/xiu_data.py`

---

# 子项目 3D-15: 四圣兽精细化轮廓

## 目标
将四圣兽从简单7星连线改为独立的精细轮廓画（双轮廓体积感+内部细节），使用 xiu_data 中的 BEAST_OUTLINES 数据。

## 实现内容

### renderer3d/celestial.py — 新增 `_build_beast_outlines()`
- 从 `BEAST_OUTLINES` 读取顶点和线段数据
- 各顶点通过锥面投影到3D空间（r_frac→高度映射）
- 四色渲染：青龙蓝/玄武紫/白虎白/朱雀红
- 独立 `beast_line_groups` 列表，渲染时 `ctx.line_width=2.5`

### 四圣兽设计
| 圣兽 | 顶点 | 线段 | 关键特征 |
|------|------|------|----------|
| 青龙 | 65 | 58 | 双轮廓蛇身、开口颚、双角、鬃毛、脊鳍、三趾爪×4、火叉尾 |
| 玄武 | 70 | 62 | 8点甲壳+十字网纹、蹼足×4、蛇双轮廓缠绕、分叉舌、鳞纹 |
| 白虎 | 58 | 58 | 圆脸三角耳、肌肉背腹双轮廓、虎纹×4、完整四腿+爪、S形叉尾 |
| 朱雀 | 66 | 62 | 头冠羽×4、鼓胸双轮廓、三层翅羽、七根扇尾、凤眼斑、爪趾 |

## 关键文件
- 修改: `renderer3d/celestial.py`, `renderer3d/xiu_data.py`

---

# 子项目 3D-16: 视觉微调（高亮/天空/亮度）

## 目标
根据视觉反馈进行三项微调。

## 实现内容

### 1. 高亮球缩小
- `ui/highlight.py`: `_draw_glow` 默认 size 25→20（2D微缩）
- `main.py`: 3D高亮传 size=15（3D明显更小）

### 2. 3D背景深蓝星空
- `renderer3d/context.py`: clear_color → (0.04, 0.06, 0.18)（深蓝星空色）

### 3. 四圣兽亮度提升 + 线条加粗
- `renderer3d/xiu_data.py`: 四圣兽颜色alpha 0.85→1.0，RGB提亮
- `renderer3d/celestial.py`: beast_line_groups 独立渲染，ctx.line_width=2.5

## 关键文件
- 修改: `ui/highlight.py`, `main.py`, `renderer3d/context.py`, `renderer3d/xiu_data.py`, `renderer3d/celestial.py`

---

# 子项目 3D-17: 星层分离 + 2D旋转修复 + 北斗增大

## 目标
修复三个视觉/交互问题。

## 实现内容

### 1. 星点浮在圣兽上方
- `renderer3d/celestial.py`: 新增 `XIU_STAR_LIFT = 0.45`
- 28宿星点Y坐标整体抬升0.45，从圣兽轮廓高度范围(0.44~0.84)上方渲染(0.89~1.05)
- 星点不再被圣兽线条遮挡

### 2. 2D天盘旋转方向修复
- **Bug**: `pygame.transform.rotate(surf, -α)` 产生CW视觉旋转，但文字公式 `math.radians(-α)` 在pygame y-down坐标系产生CCW视觉旋转，导致北斗与文字/高亮反向
- **Fix**: 保持surface用 `-self.angle`（拖拽方向正确），将三处文字/高亮的angle_offset从 `math.radians(-self.angle)` 改为 `math.radians(self.angle)`
- 修改: `draw_heaven_text()`, `draw_generals()`, highlight `angle_offset`

### 3. 3D北斗七星增大增亮
- `renderer3d/celestial.py`:
  - BEIDOU_STAR_SIZE: 0.08→0.14 (+75%)
  - BEIDOU_CENTER_SIZE: 0.12→0.20 (+67%)
  - BEIDOU_INTENSITY: 1.2→1.8 (+50%)
  - BEIDOU_STAR_COLOR: 冷白→暖金白 (1.0, 0.95, 0.8)
  - BEIDOU_LINE_COLOR: 更亮红 (0.8, 0.3, 0.3, 0.7)

## 关键文件
- 修改: `renderer3d/celestial.py`, `main.py`

---

# Main Project 3 依赖关系

```
3D-10 (穹顶几何体) → 3D-11 (天体渲染器+北斗) → 3D-12 (28宿+四圣兽基础)
                                                       ↓
3D-13 (星宿数据模块) → 3D-14 (多星座渲染) → 3D-15 (圣兽精细化) → 3D-16 (视觉微调) → 3D-17 (修复)
```

---

# Feature: 3D装饰龟 (天圆地方/龟背图)

## 目标
在3D式盘下方放置一只装饰性的龟，寓意天圆地方、龟背负天。龟由实体壳(抛物面穹顶)、四肢、头、尾和壳面六角纹路组成。

## 实现内容
- `renderer3d/geometry.py`: 新增5个mesh生成函数
  - `create_turtle_shell_mesh()`: 抛物面穹顶+平底+rim
  - `create_turtle_head_mesh()`: 锥形头部
  - `create_turtle_leg_mesh()`: 柱形短腿
  - `create_turtle_tail_mesh()`: 锥形尾巴
  - `create_turtle_hex_pattern()`: 壳面六角线条
- `renderer3d/turtle.py`: TurtleRenderer3D类
  - 复用PLATE_SHADER(Blinn-Phong) + LINE_SHADER
  - 壳色(45,50,30)深橄榄, shininess=6(亚光)
- `main.py`: 渲染管线最前端(depth test处理遮挡)

## 关键文件
- 新增: `renderer3d/turtle.py`
- 修改: `renderer3d/geometry.py`, `renderer3d/__init__.py`, `main.py`

---

# Feature: 详细推导面板

## 目标
在侧边栏增加「详解」按钮，点击后弹出全屏遮罩式面板，显示四课三传的完整推导步骤。

## 实现内容
- `liuren/derivation.py`: `generate_detailed_derivation()`函数
  - 输出月将确定、天盘旋转、四课推导、三传推导、天将推导全过程
- `ui/derivation_overlay.py`: DerivationOverlay类
  - 700x700半透明遮罩面板，滚动条，关闭按钮
- `ui/sidebar.py`: 新增「详解」按钮(推导过程标题栏右侧)
- `main.py`: 事件处理+渲染管线集成

## 关键文件
- 新增: `liuren/derivation.py`, `ui/derivation_overlay.py`
- 修改: `ui/sidebar.py`, `ui/__init__.py`, `main.py`

---
---

# Main Project 4: 自动解盘 (LLM-Based Divination Interpretation)

## 项目概述

排盘完成后，用户可选择历史占卜名家的风格和占卜目的，程序将盘局数据发送给LLM（Claude/OpenAI/Gemini），获取自动解读。

**核心功能**:
- 侧边栏"自动解盘"可折叠区域（人物选择 + 目的选择 + 解盘按钮）
- 多LLM后端支持（先实现Anthropic，预留OpenAI/Gemini接口）
- 后台线程调用API，UI显示"解卦中..."，完成后弹出解读结果遮罩

**技术方案**:
- `LLMBackend` 基类 + 各provider子类（~15行/子类）
- `.env` 配置: `LLM_PROVIDER`, `LLM_MODEL`, provider-specific API key
- 后台线程 + GIL原子性轮询（无需锁），主线程每帧检查结果
- `InterpretationOverlay`（克隆 `DerivationOverlay` 模式，增加loading态+自动换行）

## 新增项目结构

```
Liuren/
├── llm/                         # [新建] LLM集成包
│   ├── __init__.py              # 导出 LLMInterpreter
│   ├── backends.py              # LLMBackend基类 + AnthropicBackend
│   ├── prompts.py               # 人物描述 + 目的模板 + prompt构建
│   └── interpreter.py           # 配置加载、后端选择、异步调用、结果轮询
├── ui/
│   └── interpretation_overlay.py # [新建] LLM解盘结果遮罩面板
├── .env.example                 # [新建] 配置模板
├── .gitignore                   # [新建]
```

## 新增依赖

```bash
# 仅需安装所选provider的SDK
pip install anthropic        # Anthropic (默认)
# pip install openai         # OpenAI (待实现)
# pip install google-genai   # Gemini (待实现)
```

---

# 子项目 LLM-1: llm/ 包（后端抽象 + prompt工程 + 解释器）

## 目标
创建 `llm/` 包，实现多provider后端抽象、prompt构建、异步API调用。

## 实现内容

### llm/backends.py — Provider抽象
```python
class LLMBackend:
    """基类。每个provider实现 call()。"""
    def call(self, system_prompt: str, user_prompt: str, model: str) -> str:
        raise NotImplementedError

class AnthropicBackend(LLMBackend):
    """Anthropic实现。惰性导入anthropic包。默认模型: claude-sonnet-4-6"""
    def call(self, system_prompt, user_prompt, model):
        from anthropic import Anthropic
        client = Anthropic(api_key=self.api_key)
        resp = client.messages.create(model=model, max_tokens=4096,
                                       system=system_prompt,
                                       messages=[{"role": "user", "content": user_prompt}])
        return resp.content[0].text

# PENDING: OpenAIBackend (openai SDK, 默认 gpt-4o)
# PENDING: GeminiBackend (google-genai SDK, 默认 gemini-2.0-flash)
```

### llm/prompts.py — Prompt工程
- `PERSONA_PROFILES` dict:
  - 管辂 (209-256 CE, 三国魏): 直言不讳、分析缜密，擅射覆
  - 贺茂忠行 (~917-977 CE, 平安时代): 庄重仪式感，融合阴阳道
- `PURPOSE_TEMPLATES` dict:
  - 射覆: 推断隐藏之物的材质/颜色/形状
  - 占卜明日运势: 从五行生克/天将吉凶分析运势
- `build_system_prompt(personas: list[str]) -> str`: 单人→一个视角；多人→分段各自解读
- `build_user_prompt(plate_text, purpose, day_stem, day_branch) -> str`: 盘局数据 + 五行注释

### llm/interpreter.py — 异步解释器
- `LLMInterpreter` class:
  - `_load_config()`: 解析 `.env` (简单行读取器，无需python-dotenv)，回退到环境变量
  - `_create_backend()`: 根据 `LLM_PROVIDER` 实例化对应后端
  - `is_busy` / `has_result` / `has_error` 属性（GIL原子性，无需锁）
  - `get_result()` / `get_error()`: 消费式读取（读后清空）
  - `interpret_async(plate_text, personas, purpose, ...)`: 启动daemon线程
  - `_run_interpretation(...)`: 构建prompt → `backend.call()` → 设置 `_result` 或 `_error`

### .env.example
```
LLM_PROVIDER=anthropic
LLM_MODEL=claude-sonnet-4-6
ANTHROPIC_API_KEY=your-key-here
# OPENAI_API_KEY=your-key-here
# GEMINI_API_KEY=your-key-here
```

## 关键文件
- 新建: `llm/__init__.py`, `llm/backends.py`, `llm/prompts.py`, `llm/interpreter.py`
- 新建: `.env.example`, `.gitignore`

---

# 子项目 LLM-2: 解盘结果遮罩面板

## 目标
克隆 `DerivationOverlay` 模式，创建 `InterpretationOverlay`，支持loading态和自动换行。

## 实现内容

### ui/interpretation_overlay.py
- 克隆自 `ui/derivation_overlay.py` (208行)
- 标题: "【LLM解盘】"
- `show_loading()`: `self.loading = True`, `self.visible = True`
- `draw()` loading态: 绘制"解卦中..."并用 `pygame.time.get_ticks()` 做脉冲动画
- `set_result(text: str)`: 按换行符分割 + 自动换行（中文按字符宽度）
- `set_error(error: str)`: 红色调显示错误信息
- `_wrap_text(text) -> List[str]`: 用 `font.size()` 测量像素宽度做字符级换行
- 分区标题检测: 含"━"的行 → 用 COLOR_SECTION 样式

## 关键文件
- 新建: `ui/interpretation_overlay.py`
- 修改: `ui/__init__.py`

---

# 子项目 LLM-3: 侧边栏LLM区域

## 目标
在侧边栏推导过程下方添加可折叠的"自动解盘"区域。

## 实现内容

### ui/sidebar.py 扩展
新增状态:
```python
self.llm_expanded = False
self.persona_options = ['管辂', '贺茂忠行']
self.persona_selected = [True, True]  # 默认全选
self.purpose_options = ['射覆', '占卜明日运势']
self.purpose_selected = 0  # 索引
self.interpret_callback = None
```

新增方法:
- `set_interpret_callback(callback)`: 存储回调
- `get_selected_personas() -> list[str]`: 返回勾选的人物名
- `get_selected_purpose() -> str`: 返回选中的目的名
- `_draw_llm_section(screen, y, clip_rect) -> int`: 绘制区域

UI布局（展开时）:
```
[自动解盘 ▼]                     ← 切换按钮 (70x22)
  解盘人物：                      ← 标签
  [✓] 管辂  [✓] 贺茂忠行         ← 复选框
  占卜目的：                      ← 标签
  (●) 射覆  (○) 占卜明日运势     ← 单选按钮
  [     解  盘     ]              ← 触发按钮 (全宽)
```

**设计决策**: 用复选框+单选按钮（非DropdownSelector），因为sidebar内容在clip区域内滚动，下拉菜单会被裁剪。

## 关键文件
- 修改: `ui/sidebar.py`

---

# 子项目 LLM-4: 主程序集成

## 目标
将LLM解释器和结果遮罩面板集成到main.py。

## 实现内容

### 初始化
```python
from llm.interpreter import LLMInterpreter
from ui.interpretation_overlay import InterpretationOverlay
self.llm_interpreter = LLMInterpreter()
self.interpretation_overlay = InterpretationOverlay(50, 30, 750, 720, self.hud_font)
self.sidebar.set_interpret_callback(self.on_interpret)
```

### on_interpret() 方法
1. 守卫: `if not self.current_plate or self.llm_interpreter.is_busy: return`
2. 从sidebar获取personas/purpose
3. 通过 `export_plate_text_for_llm()` 序列化盘局数据
4. `self.interpretation_overlay.show_loading()`
5. `self.llm_interpreter.interpret_async(...)`

### 主循环轮询（update阶段）
```python
if self.llm_interpreter.has_result:
    self.interpretation_overlay.set_result(self.llm_interpreter.get_result())
elif self.llm_interpreter.has_error:
    self.interpretation_overlay.set_error(self.llm_interpreter.get_error())
```

### 事件优先级
InterpretationOverlay（最高）→ DerivationOverlay → 3D toggle → InputPanel/Sidebar → Plate

### 渲染顺序
InterpretationOverlay 在 DerivationOverlay 之后绘制（最上层遮罩）

## 关键文件
- 修改: `main.py`

---

# 子项目 LLM-5: 增强盘局导出 + 安装依赖

## 目标
为LLM创建增强版盘局文本导出（含天将+五行注释），安装SDK。

## 实现内容

### export/text_export.py — 新增 `export_plate_text_for_llm()`
- 四课表格含天将 (Lesson.general)
- 三传含天将
- 五行注释 (日干五行, 日支五行)
- 天地盘完整12位映射表
- 贵人信息
- 不含时间戳/装饰性分隔线

### 安装（仅需当前provider的SDK）
```bash
"E:\MiniConda\envs\biomotum\python.exe" -m pip install anthropic
```

## 关键文件
- 修改: `export/text_export.py`

---

# Main Project 4 依赖关系

```
LLM-1 (llm/包) ──┬──→ LLM-4 (main.py集成)
                  │
LLM-2 (遮罩面板) ─┤
                  │
LLM-3 (侧边栏) ──┘
                        │
                        v
                  LLM-5 (导出增强+安装)
```

LLM-1/2/3 可并行开发，LLM-4 依赖前三者，LLM-5 可在任意阶段完成。

---

# Main Project 4 Pending Improvements (待实现)

- **OpenAIBackend**: `llm/backends.py` 新增。`openai` SDK, `client.chat.completions.create()`。默认模型 `gpt-4o`。~15行。
- **GeminiBackend**: `llm/backends.py` 新增。`google-genai` SDK, `client.models.generate_content()`。默认模型 `gemini-2.0-flash`。~15行。
- **UI provider选择器**: 在侧边栏LLM区域添加provider下拉，运行时切换（目前仅.env配置）
- **更多人物**: 邵雍、袁天罡、安倍晴明等
- **更多占卜目的**: 占病、占行人、占失物等
- **流式显示**: 从一次性显示改为流式输出，提升长回复的UX
