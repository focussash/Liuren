# ui/derivation_overlay.py
# Overlay panel for detailed 四课三传 derivation display

import pygame
from typing import List

# Colors (matching sidebar theme)
COLOR_OVERLAY_BG = (20, 20, 25, 200)
COLOR_PANEL_BG = (30, 30, 38)
COLOR_BORDER = (80, 70, 55)
COLOR_TITLE = (220, 190, 100)
COLOR_TEXT = (200, 180, 140)
COLOR_DIM = (150, 130, 100)
COLOR_SECTION = (180, 150, 90)
COLOR_CLOSE_BG = (60, 40, 40)
COLOR_CLOSE_HOVER = (100, 50, 50)
COLOR_CLOSE_TEXT = (220, 180, 140)
COLOR_SCROLLBAR = (80, 70, 55, 150)
COLOR_SCROLLBAR_THUMB = (140, 120, 80, 200)


class DerivationOverlay:
    """Semi-transparent overlay panel showing detailed derivation."""

    def __init__(self, x, y, width, height, font):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.font = font
        self.small_font = pygame.font.SysFont(
            font.get_name() if hasattr(font, 'get_name') else 'simhei', 15
        )

        self.visible = False
        self.lines: List[str] = []
        self.scroll_offset = 0
        self.max_scroll = 0

        self.line_height = 22
        self.padding = 20
        self.title_height = 35
        self.close_size = 25

        # Close button rect
        self.close_rect = pygame.Rect(
            x + width - self.close_size - 8,
            y + 5,
            self.close_size,
            self.close_size,
        )

        # Content area
        self.content_rect = pygame.Rect(
            x + self.padding,
            y + self.title_height + 5,
            width - self.padding * 2 - 12,  # leave room for scrollbar
            height - self.title_height - self.padding - 5,
        )

        # Scrollbar
        self.scrollbar_rect = pygame.Rect(
            x + width - self.padding,
            y + self.title_height + 5,
            8,
            height - self.title_height - self.padding - 5,
        )
        self.scrollbar_dragging = False
        self.scroll_drag_start_y = 0
        self.scroll_drag_start_offset = 0

    def set_content(self, lines: List[str]):
        self.lines = lines
        self.scroll_offset = 0
        self._update_max_scroll()

    def _update_max_scroll(self):
        content_h = len(self.lines) * self.line_height
        self.max_scroll = max(0, content_h - self.content_rect.height)

    def toggle(self):
        self.visible = not self.visible

    def handle_event(self, event) -> bool:
        """Handle events. Returns True if event was consumed."""
        if not self.visible:
            return False

        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if not panel_rect.collidepoint(event.pos):
                # Click outside panel -> close
                self.visible = False
                return True

            if self.close_rect.collidepoint(event.pos):
                self.visible = False
                return True

            # Scrollbar drag
            if self.scrollbar_rect.collidepoint(event.pos):
                self.scrollbar_dragging = True
                self.scroll_drag_start_y = event.pos[1]
                self.scroll_drag_start_offset = self.scroll_offset
                return True

            # Consume click within panel
            return True

        elif event.type == pygame.MOUSEBUTTONUP:
            if self.scrollbar_dragging:
                self.scrollbar_dragging = False
                return True

        elif event.type == pygame.MOUSEMOTION:
            if self.scrollbar_dragging:
                dy = event.pos[1] - self.scroll_drag_start_y
                # Map scrollbar drag to content scroll
                if self.scrollbar_rect.height > 0 and self.max_scroll > 0:
                    ratio = self.max_scroll / self.scrollbar_rect.height
                    self.scroll_offset = self.scroll_drag_start_offset + dy * ratio
                    self.scroll_offset = max(0, min(self.scroll_offset, self.max_scroll))
                return True

        elif event.type == pygame.MOUSEWHEEL:
            if panel_rect.collidepoint(pygame.mouse.get_pos()):
                self.scroll_offset -= event.y * 30
                self.scroll_offset = max(0, min(self.scroll_offset, self.max_scroll))
                return True

        return False

    def draw(self, screen):
        if not self.visible or not self.lines:
            return

        # Semi-transparent background overlay (full screen dim)
        overlay_surf = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay_surf.fill((0, 0, 0, 120))
        screen.blit(overlay_surf, (0, 0))

        # Panel background
        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, COLOR_PANEL_BG, panel_rect, border_radius=8)
        pygame.draw.rect(screen, COLOR_BORDER, panel_rect, width=2, border_radius=8)

        # Title bar
        title_surf = self.font.render("【详细推导】", True, COLOR_TITLE)
        screen.blit(title_surf, (self.x + self.padding, self.y + 8))

        # Title underline
        pygame.draw.line(screen, COLOR_BORDER,
                         (self.x + 10, self.y + self.title_height),
                         (self.x + self.width - 10, self.y + self.title_height), 1)

        # Close button
        mouse_pos = pygame.mouse.get_pos()
        close_color = COLOR_CLOSE_HOVER if self.close_rect.collidepoint(mouse_pos) else COLOR_CLOSE_BG
        pygame.draw.rect(screen, close_color, self.close_rect, border_radius=4)
        close_text = self.font.render("X", True, COLOR_CLOSE_TEXT)
        close_text_rect = close_text.get_rect(center=self.close_rect.center)
        screen.blit(close_text, close_text_rect)

        # Content area with clipping
        clip_prev = screen.get_clip()
        screen.set_clip(self.content_rect)

        y = self.content_rect.y - int(self.scroll_offset)
        for line in self.lines:
            if y + self.line_height >= self.content_rect.y and y < self.content_rect.bottom:
                # Section headers (lines with ━)
                if '━' in line:
                    color = COLOR_SECTION
                    font = self.font
                elif line.startswith("  "):
                    color = COLOR_DIM
                    font = self.small_font
                else:
                    color = COLOR_TEXT
                    font = self.small_font

                text_surf = font.render(line, True, color)
                screen.blit(text_surf, (self.content_rect.x, y))
            y += self.line_height

        screen.set_clip(clip_prev)

        # Scrollbar
        if self.max_scroll > 0:
            content_h = len(self.lines) * self.line_height
            visible_ratio = self.content_rect.height / content_h
            thumb_h = max(20, int(self.scrollbar_rect.height * visible_ratio))
            scroll_ratio = self.scroll_offset / self.max_scroll if self.max_scroll > 0 else 0
            thumb_y = self.scrollbar_rect.y + int((self.scrollbar_rect.height - thumb_h) * scroll_ratio)

            # Track
            track_surf = pygame.Surface((self.scrollbar_rect.width, self.scrollbar_rect.height), pygame.SRCALPHA)
            track_surf.fill((50, 50, 55, 100))
            screen.blit(track_surf, self.scrollbar_rect.topleft)

            # Thumb
            thumb_rect = pygame.Rect(self.scrollbar_rect.x, thumb_y,
                                     self.scrollbar_rect.width, thumb_h)
            thumb_surf = pygame.Surface((thumb_rect.width, thumb_rect.height), pygame.SRCALPHA)
            thumb_surf.fill(COLOR_SCROLLBAR_THUMB)
            screen.blit(thumb_surf, thumb_rect.topleft)
