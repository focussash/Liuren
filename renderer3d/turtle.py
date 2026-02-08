# renderer3d/turtle.py
# Decorative 3D turtle beneath the plate (天圆地方/龟背图)

import math
import numpy as np
from pyrr import matrix44, Vector3

from .geometry import (
    create_turtle_shell_mesh,
    create_turtle_head_mesh,
    create_turtle_leg_mesh,
    create_turtle_tail_mesh,
    create_turtle_hex_pattern,
)
from .shaders import PLATE_VERTEX_SHADER, PLATE_FRAGMENT_SHADER
from .shaders import LINE_VERTEX_SHADER, LINE_FRAGMENT_SHADER

# Turtle dimensions
TURTLE_SHELL_RADIUS = 4.2
TURTLE_SHELL_HEIGHT = 0.6
TURTLE_SHELL_RIM = 0.1
TURTLE_Y_OFFSET = -0.35   # shell apex Y (below earth bottom at -0.25)

# Colors
TURTLE_SHELL_COLOR = np.array([45/255, 50/255, 30/255], dtype='f4')
TURTLE_LIMB_COLOR = np.array([55/255, 58/255, 35/255], dtype='f4')
TURTLE_SHININESS = 6.0

# Light (same as plate_renderer)
LIGHT_DIR = np.array([-0.5, -1.0, -0.3], dtype='f4')
LIGHT_DIR = LIGHT_DIR / np.linalg.norm(LIGHT_DIR)
LIGHT_COLOR = np.array([1.0, 0.95, 0.85], dtype='f4')
AMBIENT = np.array([0.15, 0.12, 0.10], dtype='f4')

# Leg positions: (x_sign, z_sign, angle_offset)
LEG_POSITIONS = [
    ( 1,  1),  # front-right
    (-1,  1),  # front-left
    ( 1, -1),  # back-right
    (-1, -1),  # back-left
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

        # --- Shell ---
        shell_verts, shell_idx = create_turtle_shell_mesh(
            TURTLE_SHELL_RADIUS, TURTLE_SHELL_HEIGHT, TURTLE_SHELL_RIM
        )
        shell_vbo = ctx.buffer(shell_verts.tobytes())
        shell_ibo = ctx.buffer(shell_idx.tobytes())
        self.shell_vao = ctx.vertex_array(
            self.solid_prog,
            [(shell_vbo, '3f 3f 2f', 'in_position', 'in_normal', 'in_uv')],
            shell_ibo,
        )
        self.shell_index_count = len(shell_idx)

        # Shell model matrix: position shell apex at TURTLE_Y_OFFSET
        self.shell_model = matrix44.create_from_translation(
            Vector3([0.0, TURTLE_Y_OFFSET, 0.0]), dtype='f4'
        )

        # --- Head ---
        head_verts, head_idx = create_turtle_head_mesh(length=1.2, radius=0.4)
        head_vbo = ctx.buffer(head_verts.tobytes())
        head_ibo = ctx.buffer(head_idx.tobytes())
        self.head_vao = ctx.vertex_array(
            self.solid_prog,
            [(head_vbo, '3f 3f 2f', 'in_position', 'in_normal', 'in_uv')],
            head_ibo,
        )
        self.head_index_count = len(head_idx)

        # Head position: front of shell (+Z), slightly below apex
        head_y = TURTLE_Y_OFFSET - 0.15
        head_z = TURTLE_SHELL_RADIUS + 0.3
        self.head_model = matrix44.create_from_translation(
            Vector3([0.0, head_y, head_z]), dtype='f4'
        )

        # --- Legs (4) ---
        leg_verts, leg_idx = create_turtle_leg_mesh(length=0.8, radius=0.35)
        leg_vbo = ctx.buffer(leg_verts.tobytes())
        leg_ibo = ctx.buffer(leg_idx.tobytes())
        self.leg_vao = ctx.vertex_array(
            self.solid_prog,
            [(leg_vbo, '3f 3f 2f', 'in_position', 'in_normal', 'in_uv')],
            leg_ibo,
        )
        self.leg_index_count = len(leg_idx)

        # Leg model matrices
        self.leg_models = []
        leg_spread = TURTLE_SHELL_RADIUS * 0.7
        leg_y = TURTLE_Y_OFFSET - TURTLE_SHELL_RIM
        for x_sign, z_sign in LEG_POSITIONS:
            lx = x_sign * leg_spread
            lz = z_sign * leg_spread * 0.8
            model = matrix44.create_from_translation(
                Vector3([lx, leg_y, lz]), dtype='f4'
            )
            self.leg_models.append(model)

        # --- Tail ---
        tail_verts, tail_idx = create_turtle_tail_mesh(length=0.4, radius=0.15)
        tail_vbo = ctx.buffer(tail_verts.tobytes())
        tail_ibo = ctx.buffer(tail_idx.tobytes())
        self.tail_vao = ctx.vertex_array(
            self.solid_prog,
            [(tail_vbo, '3f 3f 2f', 'in_position', 'in_normal', 'in_uv')],
            tail_ibo,
        )
        self.tail_index_count = len(tail_idx)

        # Tail position: back of shell (-Z)
        tail_y = TURTLE_Y_OFFSET - 0.1
        tail_z = -(TURTLE_SHELL_RADIUS + 0.1)
        self.tail_model = matrix44.create_from_translation(
            Vector3([0.0, tail_y, tail_z]), dtype='f4'
        )

        # --- Hex pattern lines ---
        hex_verts = create_turtle_hex_pattern(
            TURTLE_SHELL_RADIUS, TURTLE_SHELL_HEIGHT
        )
        self.hex_vertex_count = len(hex_verts)
        if self.hex_vertex_count > 0:
            hex_vbo = ctx.buffer(hex_verts.tobytes())
            self.hex_vao = ctx.vertex_array(
                self.line_prog,
                [(hex_vbo, '3f 4f', 'in_position', 'in_color')],
            )
        else:
            self.hex_vao = None

        # Hex line model = same as shell
        self.hex_model = matrix44.create_from_translation(
            Vector3([0.0, TURTLE_Y_OFFSET, 0.0]), dtype='f4'
        )

    def _render_solid(self, vao, index_count, model, vp_matrix, camera_pos,
                      color, shininess=TURTLE_SHININESS):
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
        # 1. Shell
        self._render_solid(self.shell_vao, self.shell_index_count,
                           self.shell_model, vp_matrix, camera_pos,
                           TURTLE_SHELL_COLOR)

        # 2. Head
        self._render_solid(self.head_vao, self.head_index_count,
                           self.head_model, vp_matrix, camera_pos,
                           TURTLE_LIMB_COLOR)

        # 3. Legs
        for leg_model in self.leg_models:
            self._render_solid(self.leg_vao, self.leg_index_count,
                               leg_model, vp_matrix, camera_pos,
                               TURTLE_LIMB_COLOR)

        # 4. Tail
        self._render_solid(self.tail_vao, self.tail_index_count,
                           self.tail_model, vp_matrix, camera_pos,
                           TURTLE_LIMB_COLOR)

        # 5. Hex pattern lines
        if self.hex_vao and self.hex_vertex_count > 0:
            self.ctx.blend_func = self.ctx.SRC_ALPHA, self.ctx.ONE_MINUS_SRC_ALPHA
            identity = matrix44.create_identity(dtype='f4')
            self.line_prog['u_vp'].write(vp_matrix.astype('f4').tobytes())
            self.line_prog['u_model'].write(self.hex_model.tobytes())
            self.line_prog['u_rise'].value = 1.0
            self.line_prog['u_alpha'].value = 1.0
            self.hex_vao.render(mode=self.ctx.LINES,
                                vertices=self.hex_vertex_count)

    def release(self):
        """Clean up GL resources."""
        self.shell_vao.release()
        self.head_vao.release()
        self.leg_vao.release()
        self.tail_vao.release()
        if self.hex_vao:
            self.hex_vao.release()
        self.solid_prog.release()
        self.line_prog.release()
