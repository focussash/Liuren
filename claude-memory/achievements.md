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

## Completed (continued)

### Subproject 13-14: Main Program Integration & Export
- Integrated all components into `main.py`
- Export functionality with screenshot (F5) and text export (F6)

### Subproject 15: 天将计算系统
- Extended `liuren/constants.py`:
  - `STEM_GUIREN`: 天干贵人表（阳贵/阴贵地支）
  - `GENERAL_ORDER`: 十二天将顺序
  - Fixed 癸的阳贵/阴贵：阳贵巳，阴贵卯（与壬相反，源自"壬蛇癸兔"口诀）
- Created `liuren/generals.py`:
  - `is_daytime()`: 昼夜判断（卯-申为昼）
  - `get_guiren_branch()`: 获取贵人所临地支
  - `build_generals_plate()`: 构建天将盘
    - 顺逆规则：贵人临亥子丑寅卯辰→顺布，临巳午未申酉戌→逆布
  - `get_general_for_heaven_branch()`: 获取天盘地支对应天将
- Extended data classes (`liuren/plate.py`):
  - `Lesson.general`: 四课天将
  - `Pass.general`: 三传天将
  - `LiurenPlate.generals_plate`: 天将盘
  - `LiurenPlate.guiren_branch`: 贵人所临地支
- Updated `liuren/four_lessons.py`: 计算四课时填充天将
- Updated `liuren/three_passes.py`: 计算三传时填充天将

### Subproject 16: 天将可视化与动画
- Added to `main.py`:
  - `draw_generals()`: 在天盘内圈绘制天将（跟随旋转）
  - `start_generals_animation()` / `update_generals_animation()`: 布将动画
  - 贵人用金色高亮，其他天将用暗红色
- Updated `ui/sidebar.py`:
  - 四课显示增加天将行
  - 三传显示增加天将行
  - 盘局信息显示"贵人：X宫"

### Subproject 17: 空格键行为修复
- 已排盘时：对齐到排盘时的时支（而非当前时间）
- 未排盘时：自动排盘

### Subproject 18: 按钮优化
- "自动"→"当前"：只填充干支不排盘
- 新增"即时起卦"按钮：一键用当前时间排盘

### Subproject 19: 输入面板位置优化
- 输入面板从左上角(20,20)移至右下角(530,650)
- 下拉选择器支持向上展开（`open_upward`参数）
- 避免遮挡盘体中心区域，界面更美观

### Bug Fix: 天盘文字旋转模糊问题
- **问题**: 刚加载时文字清晰，天盘一转就模糊（二次旋转导致）
- **根因**: 预渲染的月将、二十八宿先被`draw_rotated_text()`旋转一次，运行时整个Surface再被`pygame.transform.rotate()`旋转，造成像素插值模糊
- **解决方案**: 将月将和二十八宿改为实时绘制（类似天将的方式）
- **修改**:
  - 从`create_heaven_plate()`移除月将和二十八宿绘制代码
  - 新增`draw_heaven_text()`方法，实时计算位置和角度
  - 在主循环中绘制旋转后的天盘背景后调用`draw_heaven_text()`
- **效果**: 文字只经过一次旋转，无论天盘如何旋转都保持清晰

---

## Completed (Main Project 2: 式盘3D化)

### Subproject 3D-1: ModernGL上下文与Pygame集成
- Created `renderer3d/` package:
  - `renderer3d/__init__.py`: exports GLContext
  - `renderer3d/context.py`: GLContext class (standalone context + FBO readback)
  - `renderer3d/shaders.py`: test vertex/fragment shader pair
- Modified `main.py`:
  - Added `import numpy`, `from renderer3d import GLContext`
  - Added `self.mode_3d` flag, `self.gl_context` initialization
  - `Tab` key toggles 2D/3D mode
  - Extracted `_render_2d()` and `_render_3d()` methods
  - HUD shows current mode `[2D]`/`[3D]`
  - GL resources cleaned up on exit
- **Dependencies**: moderngl, pyrr, numpy installed into biomotum venv
- **Tests**: 160/160 existing tests still pass
- **Pipeline verified**: standalone context → FBO → readback → Pygame surface blit OK

### Subproject 3D-2: 轨道相机
- Created `renderer3d/camera.py`:
  - `OrbitCamera` class: spherical coordinates (theta/phi/distance)
  - `get_eye_position()`, `get_view_matrix()`, `get_projection_matrix()`, `get_vp_matrix()`
  - `orbit(dx, dy)`: mouse drag → theta/phi adjustment (with clamping 10°-80°)
  - `zoom(delta)`: scroll → distance adjustment (clamped 5-30)
  - `reset()`: Home key resets to default view
- Modified `main.py`:
  - Right-click drag in 3D mode → `camera.orbit()`
  - Scroll wheel in 3D mode → `camera.zoom()` (only in plate area)
  - Left-click drag in 3D mode → horizontal delta maps to rotation angle
  - Home key → camera reset
  - `MOUSEWHEEL` event support (cross-platform)
- **Tests**: 160/160 existing tests pass, camera unit tests pass

### Subproject 3D-3: 地盘3D几何体
- Created `renderer3d/geometry.py`:
  - `create_box_mesh(width, height, depth)`: 6面方盒，每面4顶点(pos+normal+uv)
  - `create_cylinder_mesh(radius, height, segments)`: 圆柱体（顶面/底面/侧面）
- Created `renderer3d/texture_manager.py`:
  - `TextureManager`: Pygame Surface → GL RGBA纹理（含Y轴翻转）
  - `surface_to_texture()`, `update_texture()`, cache管理
- Created `renderer3d/plate_renderer.py`:
  - `PlateRenderer3D`: 编译shader，创建VAO/VBO/IBO
  - `render_earth(vp, camera_pos)`: 顶面贴纹理+Blinn-Phong光照，侧面纯色
  - 世界尺寸: 7.0×7.0×0.5
- Updated `renderer3d/shaders.py`: 添加 PLATE_VERTEX/FRAGMENT_SHADER
  - Blinn-Phong: 方向光+镜面反射+环境光
  - 支持纹理/纯色切换 (`u_use_texture`)
- Updated `main.py`: `_render_3d()` 使用 PlateRenderer3D
- **Tests**: 160/160 passed, 3D地盘渲染集成测试通过

### Subproject 3D-4: 天盘3D几何体
- Extended `renderer3d/plate_renderer.py`:
  - Constructor now accepts `heaven_surface` (破坏性API变更)
  - 创建圆柱VAO/VBO/IBO (64段, radius=2.1, depth=0.3)
  - `render_heaven(vp, camera_pos, angle_deg)`: 模型矩阵=Y旋转+Y平移(0.9)，顶面贴纹理，底面/侧面HEAVEN_SIDE_COLOR
  - `update_heaven_texture(surface)`: 排盘后更新天盘纹理
  - 天盘Y位置: EARTH_DEPTH/2 + HEAVEN_Y_OFFSET + HEAVEN_DEPTH/2 = 0.9
  - 天盘材质: shininess=48 (漆器光泽)
- Added `create_heaven_plate_3d()` to `main.py`:
  - 预渲染完整天盘纹理（背景圆+结构线+北斗+月将+二十八宿+天将）
  - 不含convex lighting（由shader Blinn-Phong代替）
  - 排盘前：无天将；布将动画完成后重建纹理含天将
  - `heaven_3d_needs_update` dirty flag控制纹理更新时机
- Updated `_render_3d()`: 地盘渲染后紧接天盘渲染
- Updated `on_paipan()`: 设置dirty flag
- Updated `update_generals_animation()`: 动画完成时触发3D纹理重建
- **Tests**: 160/160 passed, 3D管线烟雾测试通过(多角度渲染+纹理更新)

### Subproject 3D-5: 光照与材质（漆器美学）
- **Already implemented in 3D-3/3D-4**:
  - Blinn-Phong shader (PLATE_FRAGMENT_SHADER): 方向光+镜面反射+环境光
  - 地盘 shininess=12 (木质), 天盘 shininess=48 (漆器光泽)
  - LIGHT_DIR: 左上方暖白光, AMBIENT: 暖暗环境光
  - `u_use_texture`/`u_side_color` 区分纹理面和纯色侧面
  - 地盘侧面: darkened COLOR_EARTH_BG, 天盘侧面: darkened COLOR_HEAVEN_BG

### Subproject 3D-6: 盘间阴影
- Added `create_disc_mesh(radius, segments)` to `renderer3d/geometry.py`:
  - XZ平面圆盘，Y=0，法线+Y，圆形UV映射
- Extended `renderer3d/shaders.py`:
  - Added `uniform int u_unlit` to PLATE_FRAGMENT_SHADER
  - `u_unlit==1` 时直接输出base color (bypass Blinn-Phong)
- Extended `renderer3d/plate_renderer.py`:
  - 阴影圆盘: SHADOW_RADIUS=2.415 (天盘1.15倍), SHADOW_Y=0.26 (地盘表面微上方)
  - `_create_shadow_texture()`: 256px径向渐变 (中心alpha=120, 边缘透明)
  - `render_shadow(vp)`: 无光照渲染阴影圆盘
- Updated `main.py` `_render_3d()`: 地盘→阴影→天盘分层渲染
- **Tests**: 160/160 passed

### Subproject 3D-7: 3D高亮（四课三传）
- Added `_highlight_3d(vp)` to `main.py`:
  - 构建天盘model矩阵 (与render_heaven一致)
  - 计算branch 3D世界坐标: mesh_angle = -(90 + idx*30)° (Pygame Y-flip适配)
  - MVP投影: `clip = local @ mvp` (pyrr row-major)
  - NDC→屏幕坐标转换
  - 复用 `PlateHighlighter._draw_glow()` 绘制四课(金色)/三传(红/青)高亮
  - 绘制三传连接线
  - 背面裁剪: clip.w <= 0 时跳过
- Updated `_render_3d()`: 3D surface blit后调用 `_highlight_3d(vp)`
- **Tests**: 160/160 passed

### Subproject 3D-8: 操控集成与模式切换完善
- **Already implemented in 3D-1/3D-2**:
  - Tab切换 + HUD模式显示
  - 右键拖拽→轨道相机, 滚轮→缩放, 左键拖拽→天盘旋转(物理惯性)
  - Home键→相机重置, Space/F5/F6/F7全模式通用

### Subproject 3D-9: 性能优化与视觉打磨
- Rewrote `renderer3d/context.py` for MSAA 4x:
  - 多重采样渲染缓冲区 (color + depth, samples=4)
  - 独立resolve FBO (非多重采样, 用于像素回读)
  - `ctx.copy_framebuffer()` 执行MSAA resolve
  - 优雅降级: try/except自动回退到标准渲染
  - `end_frame()`: MSAA时先resolve再readback，否则直接readback
- **Tests**: 160/160 passed, MSAA烟雾测试通过 ("MSAA 4x enabled")

---

## Completed (Main Project 3: 3D视觉美化)

### Subproject 3D-10: 穹顶天盘几何体
- Added `create_dome_mesh(radius, dome_height, rim_height, rings, segments)` to `renderer3d/geometry.py`:
  - 抛物面穹顶 `y = h*(1-t²)` + 短圆柱边缘 + 平底面
  - UV正交投影映射（与圆柱顶面UV一致，纹理无缝衔接）
  - 法线从抛物面梯度解析计算
  - 返回 `(vertices, indices, dome_index_count)` 三元组
  - 1793 vertices, 9600 indices (dome: 9024, rim+bottom: 576)
- Modified `renderer3d/plate_renderer.py`:
  - 新常量: `DOME_HEIGHT=0.45`, `RIM_HEIGHT=0.15` (替代 `HEAVEN_DEPTH=0.3`)
  - `create_cylinder_mesh` → `create_dome_mesh`
  - 新增 `get_heaven_model(angle_deg)` 方法（模型矩阵供外部共享）
  - `heaven_y = EARTH_DEPTH/2 + HEAVEN_Y_OFFSET + RIM_HEIGHT = 0.9`
- Modified `main.py` `_highlight_3d()`:
  - 高亮Y坐标从平顶改为穹顶面 `DOME_HEIGHT * (1 - (r/R)²)`
  - 使用 `plate_renderer.get_heaven_model()` 消除重复矩阵计算
- **Tests**: 160/160 passed, 穹顶管线烟雾测试通过

### Subproject 3D-11: 天体渲染器 + 北斗七星3D星座
- Added 4 GLSL shaders to `renderer3d/shaders.py`:
  - `BILLBOARD_VERTEX_SHADER`: u_model变换中心→camera_right/up展开billboard
  - `GLOW_FRAGMENT_SHADER`: 高斯衰减 `exp(-d²*3)` 发光效果
  - `LINE_VERTEX_SHADER/FRAGMENT_SHADER`: MVP变换+per-vertex颜色直通
- Created `renderer3d/celestial.py`:
  - `CelestialRenderer3D(ctx, dome_height, heaven_radius)` 类
  - 北斗七星: 7个冷白色billboard星点 + 6段暗红连线
  - 中心星(idx 3)单独渲染更大更亮 (size=0.12, intensity=1.56)
  - `_dome_y(x,z)` 计算穹顶面高度，星点悬浮其上0.35
  - `render()`: 关闭深度写入→连线(alpha blend)→星点(additive blend)→恢复
  - StarGroup/LineGroup字典存储VAO/参数，支持3D-12扩展
- Modified `main.py`:
  - 初始化 `CelestialRenderer3D` 在 `PlateRenderer3D` 之后
  - `_render_3d()`: 天盘渲染后调用 `celestial_renderer.render()`
  - 从view矩阵列(columns)提取 `camera_right/up` (pyrr create_look_at列主序)
  - 退出时 `celestial_renderer.release()`
- Updated `renderer3d/__init__.py`: 导出 `CelestialRenderer3D`
- **Bug fixes**:
  - Billboard方向: view矩阵基向量在列(columns)而非行(rows)
  - 星点颜色: (0.9,0.7,0.3)金色→(0.95,0.95,1.0)冷白色
  - 坐标翻转: `z = -py * scale` (Pygame Y-down → GL Y-up)
- **Tests**: 160/160 passed, 天体渲染管线烟雾测试通过 (2 star groups + 1 line group)

### Subproject 3D-12: 二十八星宿 + 四圣兽星座
- Extended `renderer3d/celestial.py`:
  - `_build_xiu_28()`: 28个暗金色星点环形排列 + 4组圣兽连线
  - 28宿位置: 88%半径, 每隔12.857°, 起始90° (匹配2D纹理角度)
  - `z = -radius * sin(angle)` (Y-flip pattern与北斗一致)
  - 穹顶面高度 + XIU_FLOAT_HEIGHT(0.25) 悬浮高度(比北斗低)
  - 星点: size=0.05, color=(0.65,0.52,0.32)暗金, intensity=0.8
  - 四圣兽连线 (每组7星6段):
    - 东方青龙: 角亢氐房心尾箕 → 青蓝色(0.2,0.5,0.9)
    - 北方玄武: 斗牛女虚危室壁 → 深紫色(0.3,0.25,0.6)
    - 西方白虎: 奎娄胃昴毕觜参 → 银白色(0.85,0.85,0.9)
    - 南方朱雀: 井鬼柳星张翼轸 → 朱红色(0.85,0.25,0.2)
- No changes to main.py needed (render pipeline handles all groups generically)
- **Tests**: 160/160 passed, 烟雾测试通过 (3 star groups + 5 line groups)

---

## Main Project 2 Checklist (式盘3D化) — ALL COMPLETE

- [x] 3D-1: ModernGL上下文与Pygame集成
- [x] 3D-2: 轨道相机
- [x] 3D-3: 地盘3D几何体
- [x] 3D-4: 天盘3D几何体
- [x] 3D-5: 光照与材质（漆器美学）— 已在3D-3/3D-4中实现
- [x] 3D-6: 盘间阴影
- [x] 3D-7: 3D高亮（四课三传）
- [x] 3D-8: 操控集成与模式切换完善 — 已在3D-1/3D-2中实现
- [x] 3D-9: 性能优化与视觉打磨 — MSAA 4x

## Main Project 3 Checklist (3D视觉美化)

- [x] 3D-10: 穹顶天盘几何体
- [x] 3D-11: 天体渲染器 + 北斗七星3D星座
- [x] 3D-12: 二十八星宿 + 四圣兽星座

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
| 2026-02-05 | 15-18 | 天将系统 | 天将计算、可视化、布将动画、贵人高亮、空格键修复、按钮优化 |
| 2026-02-05 | Bug fix | 天将布法 | 修正癸阳贵/阴贵、顺逆根据贵人位置决定 |
| 2026-02-06 | 19 | UI优化 | 输入面板移至右下角，下拉菜单向上展开 |
| 2026-02-06 | 20 | UI布局 | 输入面板移至侧边栏下方(830,640)，侧边栏高度缩减至600px，盘体完全不被遮挡 |
| 2026-02-06 | Bug fix | 下拉菜单遮挡 | 修复下拉菜单被侧边栏遮挡：交换main.py绘制顺序(先sidebar后input_panel) |
| 2026-02-06 | Bug fix | 天盘文字模糊 | 月将/二十八宿改为实时绘制，避免二次旋转模糊 |
| 2026-02-06 | 3D-1 | GL上下文+Pygame集成 | renderer3d/包，GLContext (standalone+FBO readback)，Tab切换，160 tests pass |
| 2026-02-06 | 3D-2 | 轨道相机 | OrbitCamera (球坐标)，右键拖拽/滚轮缩放/Home重置，160 tests pass |
| 2026-02-06 | 3D-3 | 地盘3D几何体 | geometry/texture_manager/plate_renderer，方盒+纹理+Blinn-Phong，160 tests pass |
| 2026-02-06 | 3D-4 | 天盘3D几何体 | 圆柱体+天盘纹理(月将/二十八宿/天将)+排盘纹理更新，160 tests pass |
| 2026-02-06 | 3D-5 | 光照与材质 | 已在3D-3/3D-4中完成: Blinn-Phong shader, 地盘shininess=12(木), 天盘=48(漆) |
| 2026-02-06 | 3D-6 | 盘间阴影 | disc_mesh+径向渐变纹理+u_unlit shader flag，地盘/阴影/天盘分层渲染，160 tests pass |
| 2026-02-06 | 3D-7 | 3D高亮 | 3D→2D投影(pyrr MVP矩阵)，复用PlateHighlighter glow，四课/三传/连接线，160 tests pass |
| 2026-02-06 | 3D-8 | 操控集成 | 已在3D-1/3D-2中完成: Tab切换/左右键/滚轮/Home/快捷键/物理惯性全部就绪 |
| 2026-02-06 | 3D-9 | MSAA抗锯齿 | 多重采样FBO+resolve回读，4x MSAA优雅降级，160 tests pass |
| 2026-02-06 | 3D-10 | 穹顶天盘 | create_dome_mesh(抛物面+rim+底), 替换圆柱, get_heaven_model(), highlight适配, 160 tests pass |
| 2026-02-06 | 3D-11 | 天体渲染器+北斗 | CelestialRenderer3D, billboard+glow+line shaders, 北斗七星7星+6线, additive blend, 3 bug fixes (billboard方向/颜色/Y-flip), 160 tests pass |
| 2026-02-06 | 3D-12 | 28宿+四圣兽 | 28暗金星点环+4色圣兽连线(青龙蓝/玄武紫/白虎白/朱雀红), 3 star groups + 5 line groups, 160 tests pass |
