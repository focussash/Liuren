# Development Achievements

Progress tracking for 赛博大六壬 四课三传系统

---

## Completed

### Subproject 1: Constants System
- Extended `config.py` with:
  - 五行系统 (STEM_WUXING, BRANCH_WUXING, WUXING_KE, WUXING_SHENG)
  - 阴阳 (STEM_YINYANG, BRANCH_YINYANG)
  - 天干寄宫 (STEM_JIGONG)
  - 地支六冲 (BRANCH_CHONG)
  - 驿马 (BRANCH_YIMA)
- Created `liuren/__init__.py`
- Created `liuren/constants.py` with:
  - ZHONGQI_MOON_GENERAL (中气对应月将)
  - MOON_GENERAL_NAMES (月将名称)
  - TWELVE_GENERALS (十二天将)
  - ZHONGQI_LIST, JIEQI_LIST, LESSON_TYPES
- **Tests**: 20/20 passed (`tests/test_constants.py`)

### Subproject 2: Calendar Module
- Created `lunar_calendar/` package (renamed from `calendar/` to avoid stdlib conflict)
- Created `lunar_calendar/solar_terms.py`:
  - `get_solar_terms_dict()` - Get all solar terms for a year
  - `get_current_zhongqi()` - Get current zhongqi for moon general calculation
  - `get_solar_term_of_day()` - Check if date is a solar term day
- Created `lunar_calendar/ganzhi.py`:
  - `get_day_ganzhi()` - Get day stem/branch
  - `get_hour_branch()` - Get hour branch (时支)
  - `get_hour_ganzhi()` - Get hour stem/branch
  - `get_full_ganzhi()` - Get complete four pillars
  - Utility functions for branch/stem index conversion
- **Library**: Using `cnlunar` (pure Python) instead of `sxtwl` (requires C++ build tools)
- **Tests**: 17/17 passed (`tests/test_calendar.py`)

### Subproject 3: Moon General Calculation
- Created `liuren/moon_general.py`:
  - `get_moon_general(dt)` - Get moon general (branch, name) for a datetime
  - `get_moon_general_by_zhongqi(zhongqi)` - Get moon general by zhongqi name
- **Tests**: 14/14 passed (`tests/test_moon_general.py`)
  - Verified all 12 zhongqi periods (雨水→亥将, 春分→戌将, ... 大寒→子将)

### Subproject 4: Plate State Classes
- Created `liuren/plate.py`:
  - `Lesson` dataclass - 一课数据 (heaven, earth, index)
  - `Pass` dataclass - 一传数据 (branch, index)
  - `LiurenPlate` dataclass - 完整式盘状态
  - `build_heaven_plate(moon_general, hour_branch)` - 构建天地盘映射
  - `get_heaven_branch(heaven_plate, earth_branch)` - 获取上神
  - `is_fuyin()`, `is_fanyin()` - 伏吟/返吟判断
- **Tests**: 15/15 passed (`tests/test_plate.py`)
  - Verified 亥加午 example from plan
  - Verified 伏吟(天地盘重合) and 返吟(天地盘对冲)
- **Note**: Plan's PL004 had incorrect expected value (巳 instead of 未); implemented correctly per the example

### Subproject 5: Four Lessons (四课)
- Created `liuren/four_lessons.py`:
  - `calculate_four_lessons(plate)` - 计算四课
  - `get_lesson_display(lessons)` - 获取四课显示字符串
- **Algorithm**:
  - 一课: 日干寄宫上神 / 日干寄宫
  - 二课: 一课天盘上神 / 一课天盘
  - 三课: 日支上神 / 日支
  - 四课: 三课天盘上神 / 三课天盘
- **Tests**: 9/9 passed (`tests/test_four_lessons.py`)
  - FL001-FL006: 6 different day stem/branch combinations
  - 伏吟 case (天地盘重合)
  - 返吟 case (天地盘对冲)
  - Display format test

### Subprojects 6-9: Three Passes System (三传)
- Created `liuren/three_passes.py`:
  - **Helper functions**: `is_ke()`, `is_fuyin()`, `is_fanyin()`
  - **Basic course types (Subproject 6)**:
    - `find_ke_relations()` - 找下克上关系
    - `select_by_biyong()` - 比用法筛选
    - `calculate_shehai_depth()` - 涉害深度计算
    - `get_initial_pass_basic()` - 贼克→比用→涉害
  - **Special course types (Subproject 7)**:
    - `get_yaoke_pass()` - 遥克法（蒿矢/弹射）
    - `get_maoxing_pass()` - 昴星法
    - `get_bieze_pass()` - 别责法
    - `get_bazhuan_pass()` - 八专法
  - **伏吟/返吟 (Subproject 8)**:
    - `get_fuyin_pass()` - 伏吟课取初传
    - `get_fanyin_pass()` - 返吟课取驿马
  - **中末传 (Subproject 9)**:
    - `calculate_standard_passes()` - 标准三传递推
    - `calculate_fuyin_passes()` - 伏吟三传
    - `calculate_fanyin_passes()` - 返吟三传（驿马-冲-驿马）
    - `calculate_three_passes()` - 完整三传计算主函数
- **Course types implemented**: 元首、重审、知一、蒿矢、弹射、昴星、别责、八专、伏吟、返吟
- **Tests**: 27/27 passed (`tests/test_three_passes.py`)

### Subprojects 10-12: UI Components
- Created `ui/__init__.py` - Package exports
- Created `ui/input_panel.py`:
  - `Button` class - 按钮组件 with hover states and callbacks
  - `DropdownSelector` class - 下拉选择器组件
  - `InputPanel` class - 输入面板（日干、日支、时支选择器 + 自动/排盘按钮）
  - Auto-fill callback using `lunar_calendar.ganzhi` for current time
- Created `ui/highlight.py`:
  - `PlateHighlighter` class - 式盘高亮渲染器
  - `get_branch_angle()` - 地支角度计算（子在底部-90度）
  - `get_branch_position()` - 地支屏幕位置计算
  - `highlight_lessons()` - 四课高亮（金黄色）
  - `highlight_passes()` - 三传高亮（初传红色，其他青蓝色）
  - `draw_connection_lines()` - 三传连接线
- Created `ui/sidebar.py`:
  - `ResultSidebar` class - 结果显示侧边栏
  - `set_plate()` - 设置盘局数据
  - `_draw_basic_info()` - 绘制基本信息
  - `_draw_four_lessons()` - 绘制四课表格
  - `_draw_three_passes()` - 绘制三传
  - `_draw_derivation_log()` - 绘制推导过程
  - Scroll support for long content
- **Tests**: 15/15 passed (`tests/test_ui.py`)
  - TestInputPanel: 6 tests (dropdown, selection, stems, branches, get_input, button)
  - TestHighlighter: 5 tests (branch position, lessons, passes, angle calculation)
  - TestSidebar: 4 tests (creation, set_plate, clear, draw_empty)
  - TestUIIntegration: 1 test (all components importable)

---

## In Progress

_(None - proceeding to Subproject 13)_

---

## Pending

- Subproject 13: Main Program Integration
- Subproject 14: Export Functionality

---

## Log

| Date | Sub-project | Item | Notes |
|------|-------------|------|-------|
| 2025-01-24 | 1 | Constants system | 20 tests passed |
| 2025-01-24 | 2 | Calendar module | 17 tests passed, using cnlunar instead of sxtwl |
| 2025-01-24 | 3 | Moon general | 14 tests passed |
| 2025-01-24 | 4 | Plate state | 15 tests passed, fixed PL004 expected value |
| 2025-01-24 | 5 | Four lessons | 9 tests passed |
| 2025-01-24 | 6-9 | Three passes | 27 tests passed, all 10 course types |
| 2025-01-24 | 10-12 | UI Components | 15 tests passed, input panel, highlighter, sidebar |
