# renderer3d/context.py
# ModernGL standalone context + Pygame framebuffer bridge

import moderngl
import numpy as np
import pygame
from .shaders import TEST_VERTEX_SHADER, TEST_FRAGMENT_SHADER


class GLContext:
    """
    ModernGL standalone context with framebuffer readback to Pygame surface.

    Uses create_standalone_context() to avoid conflicts with Pygame's display.
    Renders to an offscreen FBO (optionally with MSAA), then reads pixels back
    as a Pygame surface.
    """

    def __init__(self, width=800, height=800, samples=4):
        self.width = width
        self.height = height

        # Create standalone OpenGL context (no window needed)
        self.ctx = moderngl.create_standalone_context()

        self._msaa = False
        self._color_ms = None
        self._depth_ms = None
        self._fbo_resolve = None

        if samples > 1:
            try:
                # Multisampled FBO for rendering (anti-aliased edges)
                self._color_ms = self.ctx.renderbuffer(
                    (width, height), 4, samples=samples
                )
                self._depth_ms = self.ctx.depth_renderbuffer(
                    (width, height), samples=samples
                )
                self.fbo = self.ctx.framebuffer(
                    color_attachments=[self._color_ms],
                    depth_attachment=self._depth_ms
                )

                # Resolve FBO (non-multisampled, for pixel readback)
                self._color_resolve = self.ctx.texture((width, height), 4)
                self._fbo_resolve = self.ctx.framebuffer(
                    color_attachments=[self._color_resolve]
                )
                self._msaa = True
                print(f"MSAA {samples}x enabled")
            except Exception as e:
                print(f"MSAA not available ({e}), using standard rendering")
                samples = 0

        if not self._msaa:
            # Standard (non-MSAA) FBO
            self._color_resolve = self.ctx.texture((width, height), 4)
            self._depth = self.ctx.depth_renderbuffer((width, height))
            self.fbo = self.ctx.framebuffer(
                color_attachments=[self._color_resolve],
                depth_attachment=self._depth
            )

        # Build test scene for 3D-1 verification
        self._build_test_scene()

    def _build_test_scene(self):
        """Build a test triangle to verify the GL pipeline works."""
        self.test_prog = self.ctx.program(
            vertex_shader=TEST_VERTEX_SHADER,
            fragment_shader=TEST_FRAGMENT_SHADER,
        )

        # A colored triangle in 3D space (lying on XZ plane, Y=up)
        vertices = np.array([
            # x,     y,    z,    r,   g,   b
             0.0,  0.0,  2.0,  1.0, 0.2, 0.2,   # top (red)
            -2.0,  0.0, -1.5,  0.2, 1.0, 0.2,   # bottom-left (green)
             2.0,  0.0, -1.5,  0.2, 0.2, 1.0,   # bottom-right (blue)
        ], dtype='f4')

        vbo = self.ctx.buffer(vertices.tobytes())
        self.test_vao = self.ctx.vertex_array(
            self.test_prog,
            [(vbo, '3f 3f', 'in_position', 'in_color')]
        )

    def begin_frame(self, clear_color=(0.04, 0.06, 0.18, 1.0)):
        """Bind FBO and clear for a new frame."""
        self.fbo.use()
        self.ctx.clear(*clear_color)
        self.ctx.enable(moderngl.DEPTH_TEST)

    def render_test(self, vp_matrix):
        """Render the test triangle with the given VP matrix."""
        self.test_prog['u_vp'].write(vp_matrix.astype('f4').tobytes())
        self.test_vao.render(moderngl.TRIANGLES)

    def end_frame(self):
        """
        Read framebuffer pixels and return as a Pygame surface.
        If MSAA is active, resolves the multisampled FBO first.
        """
        if self._msaa:
            # Resolve multisampled FBO to regular FBO for readback
            self.ctx.copy_framebuffer(self._fbo_resolve, self.fbo)
            raw = self._fbo_resolve.read(components=4)
        else:
            raw = self.fbo.read(components=4)

        # Convert raw bytes to numpy array, reshape, flip Y axis
        arr = np.frombuffer(raw, dtype=np.uint8).reshape((self.height, self.width, 4))
        arr = np.flip(arr, axis=0).copy()  # flip vertically, make contiguous
        # Create Pygame surface from buffer
        surface = pygame.image.frombuffer(arr.tobytes(), (self.width, self.height), 'RGBA')
        return surface

    def resize(self, width, height):
        """Resize the FBO to a new width/height, releasing old resources."""
        if width == self.width and height == self.height:
            return

        # Release old FBO resources (but NOT test scene or ctx)
        self.fbo.release()
        if self._msaa:
            self._color_ms.release()
            self._depth_ms.release()
            self._fbo_resolve.release()
        else:
            if hasattr(self, '_depth'):
                self._depth.release()
        self._color_resolve.release()

        self.width = width
        self.height = height

        # Recreate FBO at new size
        was_msaa = self._msaa
        self._msaa = False

        if was_msaa:
            try:
                self._color_ms = self.ctx.renderbuffer(
                    (width, height), 4, samples=4
                )
                self._depth_ms = self.ctx.depth_renderbuffer(
                    (width, height), samples=4
                )
                self.fbo = self.ctx.framebuffer(
                    color_attachments=[self._color_ms],
                    depth_attachment=self._depth_ms
                )
                self._color_resolve = self.ctx.texture((width, height), 4)
                self._fbo_resolve = self.ctx.framebuffer(
                    color_attachments=[self._color_resolve]
                )
                self._msaa = True
            except Exception:
                was_msaa = False

        if not self._msaa:
            self._color_resolve = self.ctx.texture((width, height), 4)
            self._depth = self.ctx.depth_renderbuffer((width, height))
            self.fbo = self.ctx.framebuffer(
                color_attachments=[self._color_resolve],
                depth_attachment=self._depth
            )

    def release(self):
        """Clean up all GL resources."""
        self.test_vao.release()
        self.test_prog.release()
        self.fbo.release()
        if self._msaa:
            self._color_ms.release()
            self._depth_ms.release()
            self._fbo_resolve.release()
        else:
            if hasattr(self, '_depth'):
                self._depth.release()
        self._color_resolve.release()
        self.ctx.release()
