# renderer3d/turtle.py
# Decorative 3D turtle beneath the plate (天圆地方/龟背图)

import math
import numpy as np
from pyrr import matrix44, Vector3

from .geometry import (
    create_turtle_shell_mesh,
    create_turtle_neck_mesh,
    create_turtle_head_mesh,
    create_turtle_leg_mesh,
    create_turtle_tail_mesh,
    create_turtle_scute_pattern,
    create_turtle_plastron_mesh,
    create_turtle_bridge_mesh,
)
from .shaders import PLATE_VERTEX_SHADER, PLATE_FRAGMENT_SHADER
from .shaders import LINE_VERTEX_SHADER, LINE_FRAGMENT_SHADER

# --- New turtle dimensions ---
SHELL_RADIUS = 2.8
SHELL_HEIGHT = 1.25        # dome height (height/radius ≈ 0.45)
SHELL_RIM = 0.08
SHELL_Z_SCALE = 1.05       # slight oval

# Shell apex at Y = -1.50, so Y_OFFSET places shell base (Y=0 local) at -2.75
Y_OFFSET = -2.75

PLASTRON_RX = 2.4
PLASTRON_RZ = 2.7
BRIDGE_HEIGHT = 0.55       # gap between shell base and plastron

# --- Per-part colors ---
COLOR_CARAPACE = np.array([0.30, 0.25, 0.12], dtype='f4')   # warm brown-green
COLOR_PLASTRON = np.array([0.45, 0.38, 0.20], dtype='f4')   # lighter yellowish-tan
COLOR_BRIDGE = np.array([0.22, 0.20, 0.10], dtype='f4')     # dark body sides
COLOR_LEG = np.array([0.18, 0.16, 0.08], dtype='f4')        # dark olive
COLOR_NECK = np.array([0.20, 0.18, 0.09], dtype='f4')
COLOR_HEAD = np.array([0.22, 0.20, 0.10], dtype='f4')
COLOR_TAIL = np.array([0.18, 0.16, 0.08], dtype='f4')

SHININESS = 6.0

# Light (same as plate_renderer)
LIGHT_DIR = np.array([-0.5, -1.0, -0.3], dtype='f4')
LIGHT_DIR = LIGHT_DIR / np.linalg.norm(LIGHT_DIR)
LIGHT_COLOR = np.array([1.0, 0.95, 0.85], dtype='f4')
AMBIENT = np.array([0.15, 0.12, 0.10], dtype='f4')

# Leg placement: (translate_x, translate_y, translate_z, rotation_deg around Y)
LEG_PLACEMENTS = [
    (+1.8, -0.30, +2.0, -30.0),    # front-right
    (-1.8, -0.30, +2.0, +210.0),   # front-left
    (+1.8, -0.30, -1.8, -150.0),   # back-right
    (-1.8, -0.30, -1.8, +150.0),   # back-left
]


class TurtleRenderer3D:
    """Renders a decorative turtle beneath the 3D plate."""

    def __init__(self, ctx):
        self.ctx = ctx

        # Compile shaders
        self.solid_prog = ctx.program(
            vertex_shader=PLATE_VERTEX_SHADER,
            fragment_shader=PLATE_FRAGMENT_SHADER,
        )
        self.line_prog = ctx.program(
            vertex_shader=LINE_VERTEX_SHADER,
            fragment_shader=LINE_FRAGMENT_SHADER,
        )

        # Collect all VAOs for cleanup
        self._vaos = []

        # --- 1. Carapace (shell) ---
        shell_verts, shell_idx = create_turtle_shell_mesh(
            SHELL_RADIUS, SHELL_HEIGHT, SHELL_RIM,
            z_scale=SHELL_Z_SCALE
        )
        self.shell_vao, self.shell_idx_count = self._make_solid_vao(
            shell_verts, shell_idx)
        self.shell_model = matrix44.create_from_translation(
            Vector3([0.0, Y_OFFSET, 0.0]), dtype='f4')

        # --- 2. Plastron (belly) ---
        plast_verts, plast_idx = create_turtle_plastron_mesh(
            rx=PLASTRON_RX, rz=PLASTRON_RZ, concavity=0.15)
        self.plastron_vao, self.plastron_idx_count = self._make_solid_vao(
            plast_verts, plast_idx)
        self.plastron_model = matrix44.create_from_translation(
            Vector3([0.0, Y_OFFSET - BRIDGE_HEIGHT, 0.0]), dtype='f4')

        # --- 3. Bridge (flanks) ---
        bridge_verts, bridge_idx = create_turtle_bridge_mesh(
            SHELL_RADIUS, SHELL_Z_SCALE, PLASTRON_RX, PLASTRON_RZ,
            bridge_height=BRIDGE_HEIGHT)
        self.bridge_vao, self.bridge_idx_count = self._make_solid_vao(
            bridge_verts, bridge_idx)
        self.bridge_model = matrix44.create_from_translation(
            Vector3([0.0, Y_OFFSET, 0.0]), dtype='f4')

        # --- 4. Legs (4x articulated) ---
        leg_verts, leg_idx = create_turtle_leg_mesh(segments=12)
        self.leg_vao, self.leg_idx_count = self._make_solid_vao(
            leg_verts, leg_idx)

        self.leg_models = []
        for lx, ly, lz, rot_deg in LEG_PLACEMENTS:
            rot = matrix44.create_from_y_rotation(
                math.radians(rot_deg), dtype='f4')
            trans = matrix44.create_from_translation(
                Vector3([lx, Y_OFFSET + ly, lz]), dtype='f4')
            model = matrix44.multiply(rot, trans)
            self.leg_models.append(model)

        # --- 5. Neck ---
        neck_verts, neck_idx = create_turtle_neck_mesh(segments=12)
        self.neck_vao, self.neck_idx_count = self._make_solid_vao(
            neck_verts, neck_idx)
        neck_y = Y_OFFSET - 0.30
        neck_z = SHELL_RADIUS * SHELL_Z_SCALE * 0.85
        self.neck_model = matrix44.create_from_translation(
            Vector3([0.0, neck_y, neck_z]), dtype='f4')

        # --- 6. Head (ellipsoid at neck tip) ---
        head_verts, head_idx = create_turtle_head_mesh()
        self.head_vao, self.head_idx_count = self._make_solid_vao(
            head_verts, head_idx)
        # Position at the tip of the neck S-curve (relative to neck origin)
        head_x = 0.0
        head_y = neck_y + 0.25   # neck tip Y offset
        head_z = neck_z + 1.2    # neck tip Z offset
        self.head_model = matrix44.create_from_translation(
            Vector3([head_x, head_y, head_z]), dtype='f4')

        # --- 7. Tail ---
        tail_verts, tail_idx = create_turtle_tail_mesh(segments=8)
        self.tail_vao, self.tail_idx_count = self._make_solid_vao(
            tail_verts, tail_idx)
        tail_y = Y_OFFSET - 0.30
        tail_z = -(SHELL_RADIUS * SHELL_Z_SCALE * 0.85)
        self.tail_model = matrix44.create_from_translation(
            Vector3([0.0, tail_y, tail_z]), dtype='f4')

        # --- 8. Scute pattern lines ---
        scute_verts = create_turtle_scute_pattern(
            SHELL_RADIUS, SHELL_HEIGHT, z_scale=SHELL_Z_SCALE)
        self.scute_vertex_count = len(scute_verts)
        if self.scute_vertex_count > 0:
            scute_vbo = ctx.buffer(scute_verts.tobytes())
            self.scute_vao = ctx.vertex_array(
                self.line_prog,
                [(scute_vbo, '3f 4f', 'in_position', 'in_color')],
            )
            self._vaos.append(self.scute_vao)
        else:
            self.scute_vao = None
        self.scute_model = matrix44.create_from_translation(
            Vector3([0.0, Y_OFFSET, 0.0]), dtype='f4')

    def _make_solid_vao(self, verts, idx):
        """Create a solid VAO from vertices and indices."""
        vbo = self.ctx.buffer(verts.tobytes())
        ibo = self.ctx.buffer(idx.tobytes())
        vao = self.ctx.vertex_array(
            self.solid_prog,
            [(vbo, '3f 3f 2f', 'in_position', 'in_normal', 'in_uv')],
            ibo,
        )
        self._vaos.append(vao)
        return vao, len(idx)

    def _render_solid(self, vao, index_count, model, vp_matrix, camera_pos,
                      color, shininess=SHININESS):
        """Render a solid turtle part with Blinn-Phong lighting."""
        self.solid_prog['u_model'].write(model.tobytes())
        self.solid_prog['u_vp'].write(vp_matrix.astype('f4').tobytes())
        self.solid_prog['u_light_dir'].write(LIGHT_DIR.tobytes())
        self.solid_prog['u_light_color'].write(LIGHT_COLOR.tobytes())
        self.solid_prog['u_ambient'].write(AMBIENT.tobytes())
        self.solid_prog['u_camera_pos'].write(camera_pos.astype('f4').tobytes())
        self.solid_prog['u_shininess'].value = shininess
        self.solid_prog['u_unlit'].value = 0
        self.solid_prog['u_use_texture'].value = 0
        self.solid_prog['u_side_color'].write(color.tobytes())
        vao.render(vertices=index_count)

    def render(self, vp_matrix, camera_pos):
        """Render the complete turtle."""
        # 1. Carapace
        self._render_solid(self.shell_vao, self.shell_idx_count,
                           self.shell_model, vp_matrix, camera_pos,
                           COLOR_CARAPACE)

        # 2. Plastron
        self._render_solid(self.plastron_vao, self.plastron_idx_count,
                           self.plastron_model, vp_matrix, camera_pos,
                           COLOR_PLASTRON)

        # 3. Bridge (flanks)
        self._render_solid(self.bridge_vao, self.bridge_idx_count,
                           self.bridge_model, vp_matrix, camera_pos,
                           COLOR_BRIDGE)

        # 4. Legs
        for leg_model in self.leg_models:
            self._render_solid(self.leg_vao, self.leg_idx_count,
                               leg_model, vp_matrix, camera_pos,
                               COLOR_LEG)

        # 5. Neck
        self._render_solid(self.neck_vao, self.neck_idx_count,
                           self.neck_model, vp_matrix, camera_pos,
                           COLOR_NECK)

        # 6. Head
        self._render_solid(self.head_vao, self.head_idx_count,
                           self.head_model, vp_matrix, camera_pos,
                           COLOR_HEAD)

        # 7. Tail
        self._render_solid(self.tail_vao, self.tail_idx_count,
                           self.tail_model, vp_matrix, camera_pos,
                           COLOR_TAIL)

        # 8. Scute pattern lines
        if self.scute_vao and self.scute_vertex_count > 0:
            self.ctx.blend_func = self.ctx.SRC_ALPHA, self.ctx.ONE_MINUS_SRC_ALPHA
            self.line_prog['u_vp'].write(vp_matrix.astype('f4').tobytes())
            self.line_prog['u_model'].write(self.scute_model.tobytes())
            self.line_prog['u_rise'].value = 1.0
            self.line_prog['u_alpha'].value = 1.0
            self.scute_vao.render(mode=self.ctx.LINES,
                                  vertices=self.scute_vertex_count)

    def release(self):
        """Clean up GL resources."""
        for vao in self._vaos:
            vao.release()
        self.solid_prog.release()
        self.line_prog.release()
