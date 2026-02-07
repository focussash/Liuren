# renderer3d/celestial.py
# Renders floating celestial decorations above the heaven dome

import math
import numpy as np
import moderngl

from .shaders import (
    BILLBOARD_VERTEX_SHADER, GLOW_FRAGMENT_SHADER,
    LINE_VERTEX_SHADER, LINE_FRAGMENT_SHADER,
)
from .xiu_data import ALL_MANSIONS_ORDERED, BEAST_OUTLINES, BEAST_QUADRANTS


# 北斗七星 pixel coords (relative to 420px diameter heaven surface center)
BEIDOU_PIXELS = [
    (-90, -22),   # 0 - handle start
    (-63, -13),   # 1
    (-32, -9),    # 2
    (0, 0),       # 3 - bowl center (brightest)
    (18, 22),     # 4
    (50, 9),      # 5
    (45, -32),    # 6
]

# Constellation line segments: (from_idx, to_idx)
BEIDOU_LINES = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6)]

# Visual parameters
STAR_FLOAT_HEIGHT = 0.35   # height above dome surface
BEIDOU_STAR_SIZE = 0.14    # billboard half-size
BEIDOU_CENTER_SIZE = 0.20  # center star (idx 3) larger
BEIDOU_STAR_COLOR = (1.0, 0.95, 0.8)      # warm white-gold
BEIDOU_LINE_COLOR = (0.8, 0.3, 0.3, 0.7)  # semi-transparent red
BEIDOU_INTENSITY = 1.8

# 二十八星宿 parameters (expanded ring outside dome)
XIU_RING_RADIUS = 3.8       # star ring radius (well outside dome r=2.1)
XIU_RING_HEIGHT = 0.6       # base float height above heaven_y
XIU_HEIGHT_SLOPE = 0.8      # height drop per unit of dr (cone slope: inner=higher)
XIU_STAR_SIZE = 0.07        # component star size
XIU_ANCHOR_SIZE = 0.10      # anchor/main star per mansion (larger)
XIU_STAR_COLOR = (0.95, 0.95, 1.0)   # bright white
XIU_LINE_COLOR = (0.6, 0.6, 0.7, 0.5)  # internal lines (cool grey)
XIU_INTENSITY = 1.4
XIU_ANCHOR_INTENSITY = 1.8  # anchor stars brighter
XIU_STAR_LIFT = 0.45        # lift stars above beast outlines

# 四圣兽 3D cone draping: vertices at r_frac < 1 are higher, > 1 are lower
BEAST_HEIGHT_RANGE = 0.8    # max height variation across beast outline

# Billboard quad corner offsets
QUAD_OFFSETS = np.array([
    [-1, -1],
    [1, -1],
    [1, 1],
    [-1, 1],
], dtype='f4')

QUAD_INDICES = np.array([0, 1, 2, 0, 2, 3], dtype='i4')


class CelestialRenderer3D:
    """Renders floating celestial objects above the heaven dome."""

    def __init__(self, ctx, dome_height, heaven_radius):
        self.ctx = ctx
        self.dome_height = dome_height
        self.heaven_radius = heaven_radius

        # Compile shader programs
        self.star_prog = ctx.program(
            vertex_shader=BILLBOARD_VERTEX_SHADER,
            fragment_shader=GLOW_FRAGMENT_SHADER,
        )
        self.line_prog = ctx.program(
            vertex_shader=LINE_VERTEX_SHADER,
            fragment_shader=LINE_FRAGMENT_SHADER,
        )

        # Storage for star groups and line groups
        self.star_groups = []  # list of (vao, index_count, color, size, intensity)
        self.line_groups = []  # list of (vao, vertex_count)
        self.beast_line_groups = []  # beast outlines (rendered thicker)

        # Build 北斗七星
        self._build_beidou()

        # Build 二十八星宿 (multi-star constellations)
        self._build_xiu_28()

        # Build 四圣兽 outlines
        self._build_beast_outlines()

    def _dome_y(self, x, z):
        """Get dome surface Y at position (x, z) in local space."""
        rho = math.sqrt(x * x + z * z)
        t = min(rho / self.heaven_radius, 1.0)
        return self.dome_height * (1.0 - t * t)

    def _build_beidou(self):
        """Build 北斗七星 star billboards and constellation lines."""
        scale = self.heaven_radius / 210.0  # pixels to world units

        # Compute 3D positions for each star
        positions = []
        for px, py in BEIDOU_PIXELS:
            x = px * scale
            z = -py * scale  # negate: Pygame Y-down flipped in texture upload
            y = self._dome_y(x, z) + STAR_FLOAT_HEIGHT
            positions.append((x, y, z))

        # --- Star billboards ---
        # Build per-star quads (4 verts each, 6 indices each)
        star_verts = []   # [in_position(3), in_offset(2)] per vertex
        star_indices = []

        for i, (x, y, z) in enumerate(positions):
            base = i * 4
            for ox, oy in QUAD_OFFSETS:
                star_verts.append([x, y, z, ox, oy])
            for idx in QUAD_INDICES:
                star_indices.append(base + idx)

        star_verts = np.array(star_verts, dtype='f4')
        star_indices = np.array(star_indices, dtype='i4')

        vbo = self.ctx.buffer(star_verts.tobytes())
        ibo = self.ctx.buffer(star_indices.tobytes())
        vao = self.ctx.vertex_array(
            self.star_prog,
            [(vbo, '3f 2f', 'in_position', 'in_offset')],
            ibo,
        )

        self.star_groups.append({
            'vao': vao,
            'index_count': len(star_indices),
            'color': BEIDOU_STAR_COLOR,
            'size': BEIDOU_STAR_SIZE,
            'intensity': BEIDOU_INTENSITY,
        })

        # Build a second star group for the center star (idx 3) - larger
        cx, cy, cz = positions[3]
        center_verts = []
        center_indices = []
        for j, (ox, oy) in enumerate(QUAD_OFFSETS):
            center_verts.append([cx, cy, cz, ox, oy])
        for idx in QUAD_INDICES:
            center_indices.append(idx)

        center_verts = np.array(center_verts, dtype='f4')
        center_indices = np.array(center_indices, dtype='i4')

        cvbo = self.ctx.buffer(center_verts.tobytes())
        cibo = self.ctx.buffer(center_indices.tobytes())
        cvao = self.ctx.vertex_array(
            self.star_prog,
            [(cvbo, '3f 2f', 'in_position', 'in_offset')],
            cibo,
        )

        self.star_groups.append({
            'vao': cvao,
            'index_count': len(center_indices),
            'color': BEIDOU_STAR_COLOR,
            'size': BEIDOU_CENTER_SIZE,
            'intensity': BEIDOU_INTENSITY * 1.3,  # brighter
        })

        # --- Constellation lines ---
        line_verts = []  # [in_position(3), in_color(4)]
        r, g, b, a = BEIDOU_LINE_COLOR
        for i0, i1 in BEIDOU_LINES:
            x0, y0, z0 = positions[i0]
            x1, y1, z1 = positions[i1]
            line_verts.append([x0, y0, z0, r, g, b, a])
            line_verts.append([x1, y1, z1, r, g, b, a])

        line_verts = np.array(line_verts, dtype='f4')
        lvbo = self.ctx.buffer(line_verts.tobytes())
        lvao = self.ctx.vertex_array(
            self.line_prog,
            [(lvbo, '3f 4f', 'in_position', 'in_color')],
        )

        self.line_groups.append({
            'vao': lvao,
            'vertex_count': len(line_verts),
        })

    def _build_xiu_28(self):
        """Build 二十八星宿 multi-star constellations at expanded ring radius."""
        step_angle = 360.0 / 28.0

        # Collect all component star positions and anchor positions
        all_star_positions = []   # every star in every mansion
        anchor_positions = []     # first star (anchor) of each mansion
        all_line_verts = []       # internal constellation lines

        lr, lg_c, lb, la = XIU_LINE_COLOR

        for i, mansion in enumerate(ALL_MANSIONS_ORDERED):
            center_angle = 90.0 + i * step_angle
            mansion_positions = []

            for dr, dtheta in mansion.star_offsets:
                star_angle = center_angle + dtheta
                star_radius = XIU_RING_RADIUS * (1.0 + dr)
                angle_rad = math.radians(star_angle)
                x = star_radius * math.cos(angle_rad)
                z = -star_radius * math.sin(angle_rad)
                # Cone slope: stars closer to center (negative dr) sit higher
                # XIU_STAR_LIFT raises stars above beast outlines
                y = XIU_RING_HEIGHT - dr * XIU_HEIGHT_SLOPE + XIU_STAR_LIFT
                mansion_positions.append((x, y, z))

            # First star is the anchor
            anchor_positions.append(mansion_positions[0])
            all_star_positions.extend(mansion_positions)

            # Internal constellation lines
            for a_idx, b_idx in mansion.lines:
                x0, y0, z0 = mansion_positions[a_idx]
                x1, y1, z1 = mansion_positions[b_idx]
                all_line_verts.append([x0, y0, z0, lr, lg_c, lb, la])
                all_line_verts.append([x1, y1, z1, lr, lg_c, lb, la])

        # --- Star group: all component stars (dim, small) ---
        star_verts = []
        star_indices = []
        for i, (x, y, z) in enumerate(all_star_positions):
            base = i * 4
            for ox, oy in QUAD_OFFSETS:
                star_verts.append([x, y, z, ox, oy])
            for idx in QUAD_INDICES:
                star_indices.append(base + idx)

        star_verts = np.array(star_verts, dtype='f4')
        star_indices = np.array(star_indices, dtype='i4')
        vbo = self.ctx.buffer(star_verts.tobytes())
        ibo = self.ctx.buffer(star_indices.tobytes())
        vao = self.ctx.vertex_array(
            self.star_prog,
            [(vbo, '3f 2f', 'in_position', 'in_offset')],
            ibo,
        )
        self.star_groups.append({
            'vao': vao,
            'index_count': len(star_indices),
            'color': XIU_STAR_COLOR,
            'size': XIU_STAR_SIZE,
            'intensity': XIU_INTENSITY,
        })

        # --- Star group: 28 anchor stars (brighter, larger) ---
        anchor_verts = []
        anchor_indices = []
        for i, (x, y, z) in enumerate(anchor_positions):
            base = i * 4
            for ox, oy in QUAD_OFFSETS:
                anchor_verts.append([x, y, z, ox, oy])
            for idx in QUAD_INDICES:
                anchor_indices.append(base + idx)

        anchor_verts = np.array(anchor_verts, dtype='f4')
        anchor_indices = np.array(anchor_indices, dtype='i4')
        avbo = self.ctx.buffer(anchor_verts.tobytes())
        aibo = self.ctx.buffer(anchor_indices.tobytes())
        avao = self.ctx.vertex_array(
            self.star_prog,
            [(avbo, '3f 2f', 'in_position', 'in_offset')],
            aibo,
        )
        self.star_groups.append({
            'vao': avao,
            'index_count': len(anchor_indices),
            'color': XIU_STAR_COLOR,
            'size': XIU_ANCHOR_SIZE,
            'intensity': XIU_ANCHOR_INTENSITY,
        })

        # --- Line group: internal constellation lines ---
        if all_line_verts:
            all_line_verts = np.array(all_line_verts, dtype='f4')
            lvbo = self.ctx.buffer(all_line_verts.tobytes())
            lvao = self.ctx.vertex_array(
                self.line_prog,
                [(lvbo, '3f 4f', 'in_position', 'in_color')],
            )
            self.line_groups.append({
                'vao': lvao,
                'vertex_count': len(all_line_verts),
            })

    def _build_beast_outlines(self):
        """Build 四圣兽 simplified outline drawings."""
        step_angle = 360.0 / 28.0

        for beast_key, outline in BEAST_OUTLINES.items():
            quadrant = BEAST_QUADRANTS[beast_key]
            # Center angle = middle (4th) mansion of the 7
            middle_idx = quadrant['indices'][3]
            center_angle = 90.0 + middle_idx * step_angle

            # Compute vertex positions with 3D cone draping
            positions = []
            for r_frac, theta_deg in outline.vertices:
                abs_angle = center_angle + theta_deg
                radius = XIU_RING_RADIUS * r_frac
                angle_rad = math.radians(abs_angle)
                x = radius * math.cos(angle_rad)
                z = -radius * math.sin(angle_rad)
                # Cone profile: r_frac < 1 → higher, r_frac > 1 → lower
                y = XIU_RING_HEIGHT + (1.0 - r_frac) * BEAST_HEIGHT_RANGE
                positions.append((x, y, z))

            # Build line segments
            r, g, b, a = outline.color
            line_verts = []
            for a_idx, b_idx in outline.lines:
                x0, y0, z0 = positions[a_idx]
                x1, y1, z1 = positions[b_idx]
                line_verts.append([x0, y0, z0, r, g, b, a])
                line_verts.append([x1, y1, z1, r, g, b, a])

            if line_verts:
                line_verts = np.array(line_verts, dtype='f4')
                lvbo = self.ctx.buffer(line_verts.tobytes())
                lvao = self.ctx.vertex_array(
                    self.line_prog,
                    [(lvbo, '3f 4f', 'in_position', 'in_color')],
                )
                self.beast_line_groups.append({
                    'vao': lvao,
                    'vertex_count': len(line_verts),
                })

    def render(self, vp_matrix, model_matrix, camera_right, camera_up):
        """Render all celestial objects.

        Args:
            vp_matrix: View-projection matrix (f4)
            model_matrix: Heaven plate model matrix (f4)
            camera_right: Camera right vector in world space (f4, len 3)
            camera_up: Camera up vector in world space (f4, len 3)
        """
        ctx = self.ctx

        # Save state, disable depth write for transparent objects
        ctx.depth_func = '<='
        prev_depth_mask = ctx.fbo.depth_mask
        ctx.fbo.depth_mask = False

        vp_bytes = vp_matrix.astype('f4').tobytes()
        model_bytes = model_matrix.astype('f4').tobytes()

        # --- Render constellation lines (standard alpha blend) ---
        ctx.blend_func = ctx.SRC_ALPHA, ctx.ONE_MINUS_SRC_ALPHA
        self.line_prog['u_vp'].write(vp_bytes)
        self.line_prog['u_model'].write(model_bytes)

        for lg in self.line_groups:
            lg['vao'].render(moderngl.LINES, vertices=lg['vertex_count'])

        # --- Render beast outline lines (thicker) ---
        ctx.line_width = 2.5
        for lg in self.beast_line_groups:
            lg['vao'].render(moderngl.LINES, vertices=lg['vertex_count'])
        ctx.line_width = 1.0

        # --- Render star billboards (additive blend for glow) ---
        ctx.blend_func = ctx.SRC_ALPHA, ctx.ONE
        self.star_prog['u_vp'].write(vp_bytes)
        self.star_prog['u_model'].write(model_bytes)
        self.star_prog['u_camera_right'].write(
            np.array(camera_right, dtype='f4').tobytes()
        )
        self.star_prog['u_camera_up'].write(
            np.array(camera_up, dtype='f4').tobytes()
        )

        for sg in self.star_groups:
            self.star_prog['u_size'].value = sg['size']
            self.star_prog['u_color'].write(
                np.array(sg['color'], dtype='f4').tobytes()
            )
            self.star_prog['u_intensity'].value = sg['intensity']
            sg['vao'].render(vertices=sg['index_count'])

        # Restore state
        ctx.fbo.depth_mask = prev_depth_mask
        ctx.depth_func = '<'
        ctx.blend_func = ctx.SRC_ALPHA, ctx.ONE_MINUS_SRC_ALPHA

    def release(self):
        """Clean up all GL resources."""
        for sg in self.star_groups:
            sg['vao'].release()
        for lg in self.line_groups:
            lg['vao'].release()
        for lg in self.beast_line_groups:
            lg['vao'].release()
        self.star_prog.release()
        self.line_prog.release()
