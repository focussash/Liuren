# renderer3d/plate_renderer.py
# Main 3D plate renderer - orchestrates earth/heaven plate rendering

import numpy as np
import pygame
from pyrr import matrix44, Vector3

from .geometry import create_box_mesh, create_cylinder_mesh, create_disc_mesh
from .shaders import PLATE_VERTEX_SHADER, PLATE_FRAGMENT_SHADER
from .texture_manager import TextureManager


# World-space dimensions (earth plate is 7x7, heaven disc radius 2.1)
EARTH_WIDTH = 7.0
EARTH_HEIGHT = 7.0
EARTH_DEPTH = 0.5       # thickness of earth plate slab

HEAVEN_RADIUS = 2.1
HEAVEN_DEPTH = 0.3       # thickness of heaven disc
HEAVEN_Y_OFFSET = 0.5    # gap above earth plate top surface

# Light direction: from upper-left-front (matching existing convex lighting)
LIGHT_DIR = np.array([-0.5, -1.0, -0.3], dtype='f4')
LIGHT_DIR = LIGHT_DIR / np.linalg.norm(LIGHT_DIR)

LIGHT_COLOR = np.array([1.0, 0.95, 0.85], dtype='f4')  # warm white
AMBIENT = np.array([0.15, 0.12, 0.10], dtype='f4')       # warm dark

# Material: side colors (normalized from Pygame 0-255 to 0-1)
EARTH_SIDE_COLOR = np.array([40/255, 12/255, 12/255], dtype='f4')  # darkened COLOR_EARTH_BG
HEAVEN_SIDE_COLOR = np.array([8/255, 8/255, 10/255], dtype='f4')   # darkened COLOR_HEAVEN_BG

EARTH_SHININESS = 12.0   # wood-like
HEAVEN_SHININESS = 48.0  # lacquer sheen

SHADOW_RADIUS = HEAVEN_RADIUS * 1.15   # slightly larger for soft spread
SHADOW_Y = EARTH_DEPTH / 2 + 0.01      # just above earth plate surface


class PlateRenderer3D:
    """Renders the earth and heaven plates as 3D textured objects."""

    def __init__(self, ctx, earth_surface, heaven_surface):
        """
        Args:
            ctx: ModernGL context
            earth_surface: Pygame Surface for the earth plate texture
            heaven_surface: Pygame Surface for the heaven plate texture
        """
        self.ctx = ctx
        self.tex_manager = TextureManager(ctx)

        # Compile shader program
        self.prog = ctx.program(
            vertex_shader=PLATE_VERTEX_SHADER,
            fragment_shader=PLATE_FRAGMENT_SHADER,
        )

        # --- Earth plate geometry ---
        earth_verts, earth_idx = create_box_mesh(EARTH_WIDTH, EARTH_HEIGHT, EARTH_DEPTH)
        earth_vbo = ctx.buffer(earth_verts.tobytes())
        earth_ibo = ctx.buffer(earth_idx.tobytes())
        self.earth_vao = ctx.vertex_array(
            self.prog,
            [(earth_vbo, '3f 3f 2f', 'in_position', 'in_normal', 'in_uv')],
            earth_ibo
        )
        self.earth_index_count = len(earth_idx)

        # Earth plate texture
        self.earth_texture = self.tex_manager.surface_to_texture(earth_surface, 'earth')

        # Earth model matrix: centered at origin, top face at Y = EARTH_DEPTH/2
        self.earth_model = matrix44.create_identity(dtype='f4')

        # --- Heaven plate geometry ---
        heaven_segments = 64
        heaven_verts, heaven_idx = create_cylinder_mesh(
            HEAVEN_RADIUS, HEAVEN_DEPTH, heaven_segments
        )
        heaven_vbo = ctx.buffer(heaven_verts.tobytes())
        heaven_ibo = ctx.buffer(heaven_idx.tobytes())
        self.heaven_vao = ctx.vertex_array(
            self.prog,
            [(heaven_vbo, '3f 3f 2f', 'in_position', 'in_normal', 'in_uv')],
            heaven_ibo
        )
        self.heaven_index_count = len(heaven_idx)
        self.heaven_top_index_count = heaven_segments * 3  # top face fan triangles

        # Heaven plate texture
        self.heaven_texture = self.tex_manager.surface_to_texture(heaven_surface, 'heaven')

        # Pre-compute heaven Y position (above earth plate top surface)
        self.heaven_y = EARTH_DEPTH / 2 + HEAVEN_Y_OFFSET + HEAVEN_DEPTH / 2

        # --- Shadow disc ---
        shadow_verts, shadow_idx = create_disc_mesh(SHADOW_RADIUS)
        shadow_vbo = ctx.buffer(shadow_verts.tobytes())
        shadow_ibo = ctx.buffer(shadow_idx.tobytes())
        self.shadow_vao = ctx.vertex_array(
            self.prog,
            [(shadow_vbo, '3f 3f 2f', 'in_position', 'in_normal', 'in_uv')],
            shadow_ibo
        )
        self.shadow_index_count = len(shadow_idx)

        # Shadow texture: radial gradient (dark center → transparent edge)
        self.shadow_texture = self._create_shadow_texture()

        # Shadow model matrix: translate to just above earth surface
        self.shadow_model = matrix44.create_from_translation(
            Vector3([0.0, SHADOW_Y, 0.0]), dtype='f4'
        )

    def _create_shadow_texture(self):
        """Create a radial gradient shadow texture."""
        size = 256
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        center = size // 2
        for r in range(center, 0, -1):
            progress = r / center  # 1.0 at edge, 0.0 at center
            alpha = int(120 * (1 - progress * progress))
            pygame.draw.circle(surf, (0, 0, 0, alpha), (center, center), r)
        return self.tex_manager.surface_to_texture(surf, 'shadow')

    def render_earth(self, vp_matrix, camera_pos):
        """Render the earth plate."""
        self.prog['u_model'].write(self.earth_model.tobytes())
        self.prog['u_vp'].write(vp_matrix.astype('f4').tobytes())
        self.prog['u_light_dir'].write(LIGHT_DIR.tobytes())
        self.prog['u_light_color'].write(LIGHT_COLOR.tobytes())
        self.prog['u_ambient'].write(AMBIENT.tobytes())
        self.prog['u_camera_pos'].write(camera_pos.astype('f4').tobytes())
        self.prog['u_shininess'].value = EARTH_SHININESS
        self.prog['u_unlit'].value = 0

        # Render top face with texture (first 6 indices = top face)
        self.earth_texture.use(0)
        self.prog['u_texture'].value = 0
        self.prog['u_use_texture'].value = 1
        self.earth_vao.render(vertices=6, first=0)

        # Render remaining faces with side color (indices 6 onwards)
        self.prog['u_use_texture'].value = 0
        self.prog['u_side_color'].write(EARTH_SIDE_COLOR.tobytes())
        self.earth_vao.render(vertices=self.earth_index_count - 6, first=6)

    def render_heaven(self, vp_matrix, camera_pos, angle_deg):
        """Render the heaven plate disc at the given rotation angle.

        Args:
            vp_matrix: View-projection matrix
            camera_pos: Camera position for specular
            angle_deg: Rotation angle in degrees (around Y axis)
        """
        # Build model matrix: rotate around Y, then translate up
        angle_rad = float(np.radians(angle_deg))
        rotation = matrix44.create_from_y_rotation(angle_rad, dtype='f4')
        translation = matrix44.create_from_translation(
            Vector3([0.0, self.heaven_y, 0.0]), dtype='f4'
        )
        model = matrix44.multiply(rotation, translation)

        self.prog['u_model'].write(model.tobytes())
        self.prog['u_vp'].write(vp_matrix.astype('f4').tobytes())
        self.prog['u_light_dir'].write(LIGHT_DIR.tobytes())
        self.prog['u_light_color'].write(LIGHT_COLOR.tobytes())
        self.prog['u_ambient'].write(AMBIENT.tobytes())
        self.prog['u_camera_pos'].write(camera_pos.astype('f4').tobytes())
        self.prog['u_shininess'].value = HEAVEN_SHININESS
        self.prog['u_unlit'].value = 0

        # Render top face with texture
        self.heaven_texture.use(0)
        self.prog['u_texture'].value = 0
        self.prog['u_use_texture'].value = 1
        self.heaven_vao.render(vertices=self.heaven_top_index_count, first=0)

        # Render bottom + side faces with side color
        self.prog['u_use_texture'].value = 0
        self.prog['u_side_color'].write(HEAVEN_SIDE_COLOR.tobytes())
        remaining = self.heaven_index_count - self.heaven_top_index_count
        self.heaven_vao.render(vertices=remaining, first=self.heaven_top_index_count)

    def render_shadow(self, vp_matrix):
        """Render the shadow disc on the earth plate surface (unlit)."""
        self.prog['u_model'].write(self.shadow_model.tobytes())
        self.prog['u_vp'].write(vp_matrix.astype('f4').tobytes())
        self.prog['u_unlit'].value = 1
        self.prog['u_use_texture'].value = 1

        self.shadow_texture.use(0)
        self.prog['u_texture'].value = 0
        self.shadow_vao.render()

    def update_heaven_texture(self, surface):
        """Update the heaven plate texture (e.g., after adding generals)."""
        self.tex_manager.update_texture(self.heaven_texture, surface)

    def release(self):
        """Clean up all GL resources."""
        self.earth_vao.release()
        self.heaven_vao.release()
        self.shadow_vao.release()
        self.tex_manager.release_all()
        self.prog.release()
