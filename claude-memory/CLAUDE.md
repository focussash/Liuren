# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Important**: Always check the `claude-memory/` folder for project context, plans, and progress tracking before starting any work.

## Development Guidelines

- **Follow the plan**: Always refer to `DEVELOPMENT_PLAN.md` before writing any code. The plan defines the implementation order and specifications.
- **Plan changes require approval**: Even with auto-accept enabled, **you MUST ask the user for explicit permission** before modifying DEVELOPMENT_PLAN.md. Never silently iterate on the plan.
- **Modularity is mandatory**: Avoid monolith code at all costs. Split functionality into small, focused modules. Each file should have a single responsibility.
- **Progress tracking**: After completing any sub-step from the development plan, always update `achievements.md` with what was accomplished.

## Project Overview

赛博大六壬 (Cyber Da Liu Ren) - A visualization of the ancient Chinese divination system "Da Liu Ren" styled after the Ruyin Marquis lacquer artifact. Built with Pygame, featuring an interactive rotating celestial plate (天盘) over a fixed earth plate (地盘).

## Commands

```bash
# Run the application
python main.py

# Install dependencies
pip install pygame>=2.1.0 sxtwl>=1.0.0 pytest

# Run tests (when implemented)
python -m pytest tests/ -v
```

## Architecture

### Current Structure

- **config.py**: All constants - color palette (COLOR_*), celestial data (MOON_GENERALS, EARTHLY_BRANCHES, HEAVENLY_STEMS), and 28 lunar mansions (XIU_*)
- **core.py**: Time calculations - `get_chinese_hour()` converts to Chinese time system, `get_moon_general()` determines current month general
- **main.py**: `CyberLiuren` class handles all rendering via pre-rendered surfaces for performance:
  - `earth_surf`: Static square earth plate with 干支, 星宿, 卦象
  - `heaven_surf`: Rotatable circular heaven plate with 月将 and 北斗七星
  - `shadow_surf`: Drop shadow for 3D effect
  - Physics system for drag rotation with inertia

### Key Concepts (六壬 Domain)

- **天盘/地盘**: Heaven plate rotates over fixed earth plate; alignment determined by 月将 (month general) and 时支 (hour branch)
- **月将加临**: "Month general positioned at hour" - core positioning rule: `target_angle = -(hour_idx + general_idx) * 30`
- **地支 (Earthly Branches)**: 子丑寅卯辰巳午未申酉戌亥 - 12 positions at 30° intervals
- **上神 (Upper Spirit)**: The heaven plate branch at a given earth plate position

### Planned Expansion (see DEVELOPMENT_PLAN.md)

The system will expand to include:
- **liuren/**: Core algorithms (four_lessons.py, three_passes.py, plate.py)
- **calendar/**: Solar term calculation via sxtwl library for precise month general determination
- **ui/**: Input panel, sidebar, highlights
- **export/**: Screenshot and text export

### Four Lessons Algorithm (四课)
```
一课: 日干寄宫上神 / 日干寄宫
二课: 一课天盘上神 / 一课天盘
三课: 日支上神 / 日支
四课: 三课天盘上神 / 三课天盘
```

### Heaven Plate Calculation
```python
# Offset = moon_general_index - hour_branch_index
# heaven_branch = (earth_branch_index + offset) % 12
```

## Interaction

- **Drag** the heaven plate to rotate
- **Space** auto-aligns to current time
- Rotation has momentum/friction physics
