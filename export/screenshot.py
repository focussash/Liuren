# export/screenshot.py
# 截图保存功能

import pygame
import os
from datetime import datetime


def save_screenshot(screen: pygame.Surface, filename: str = None) -> str:
    """
    Save current screen to PNG file.

    Args:
        screen: pygame screen surface
        filename: Optional filename. Auto-generates timestamped filename if not provided.

    Returns:
        The saved filename.
    """
    # Ensure exports directory exists
    export_dir = "exports"
    if not os.path.exists(export_dir):
        os.makedirs(export_dir)

    # Generate filename if not provided
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"liuren_{timestamp}.png"

    # Ensure .png extension
    if not filename.lower().endswith('.png'):
        filename += '.png'

    # Build full path
    filepath = os.path.join(export_dir, filename)

    # Save screenshot
    pygame.image.save(screen, filepath)

    return filepath
