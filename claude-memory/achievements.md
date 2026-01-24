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

---

## In Progress

_(None - awaiting confirmation to proceed to Subproject 4)_

---

## Pending

- Subproject 4: Plate State Classes
- Subproject 5: Four Lessons
- Subproject 6-9: Three Passes System
- Subproject 10-12: UI Components
- Subproject 13: Main Program Integration
- Subproject 14: Export Functionality

---

## Log

| Date | Sub-project | Item | Notes |
|------|-------------|------|-------|
| 2025-01-24 | 1 | Constants system | 20 tests passed |
| 2025-01-24 | 2 | Calendar module | 17 tests passed, using cnlunar instead of sxtwl |
| 2025-01-24 | 3 | Moon general | 14 tests passed |
