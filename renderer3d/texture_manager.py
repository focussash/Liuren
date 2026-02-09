# renderer3d/texture_manager.py
# Convert Pygame surfaces to ModernGL textures

import pygame
import numpy as np


class TextureManager:
    """Manages Pygame surface to ModernGL texture conversion."""

    def __init__(self, ctx):
        self.ctx = ctx
        self._cache = {}  # name -> texture

    def surface_to_texture(self, surface, name=None):
        """
        Convert a Pygame surface to a ModernGL RGBA texture.

        Pygame is top-down, OpenGL is bottom-up, so we flip vertically.

        Args:
            surface: Pygame Surface (any format, will be converted to RGBA)
            name: Optional cache key

        Returns:
            moderngl.Texture
        """
        # Convert surface to RGBA format
        if surface.get_bitsize() != 32 or not surface.get_flags() & pygame.SRCALPHA:
            rgba_surface = surface.convert_alpha()
        else:
            rgba_surface = surface

        w, h = rgba_surface.get_size()

        # Get raw pixel data as string
        raw = pygame.image.tostring(rgba_surface, 'RGBA')

        # Flip vertically (Pygame top-down -> OpenGL bottom-up)
        arr = np.frombuffer(raw, dtype=np.uint8).reshape((h, w, 4))
        arr = np.flip(arr, axis=0).copy()

        texture = self.ctx.texture((w, h), 4, arr.tobytes())
        texture.filter = (self.ctx.LINEAR, self.ctx.LINEAR)

        if name:
            # Release old texture if it exists
            if name in self._cache:
                self._cache[name].release()
            self._cache[name] = texture

        return texture

    def update_texture(self, texture, surface):
        """
        Update an existing texture with new surface data.

        Args:
            texture: Existing moderngl.Texture
            surface: New Pygame Surface
        """
        if surface.get_bitsize() != 32 or not surface.get_flags() & pygame.SRCALPHA:
            rgba_surface = surface.convert_alpha()
        else:
            rgba_surface = surface

        w, h = rgba_surface.get_size()
        raw = pygame.image.tostring(rgba_surface, 'RGBA')
        arr = np.frombuffer(raw, dtype=np.uint8).reshape((h, w, 4))
        arr = np.flip(arr, axis=0).copy()

        texture.write(arr.tobytes())

    def release_all(self):
        """Release all cached textures."""
        for tex in self._cache.values():
            tex.release()
        self._cache.clear()
