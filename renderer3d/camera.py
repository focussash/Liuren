# renderer3d/camera.py
# Orbit camera using spherical coordinates

import math
import numpy as np
from pyrr import matrix44, Vector3


class OrbitCamera:
    """
    Spherical-coordinate orbit camera.

    Orbits around a target point. Controlled by:
    - Right-click drag: orbit (theta/phi)
    - Scroll wheel: zoom (distance)
    """

    def __init__(self, distance=12.0, theta=0.0, phi=45.0):
        """
        Args:
            distance: Distance from target point
            theta: Azimuth angle in degrees (horizontal rotation)
            phi: Elevation angle in degrees (10-80, where 90 would be straight down)
        """
        self.distance = distance
        self.theta = theta  # azimuth (degrees)
        self.phi = phi      # elevation (degrees)
        self.target = np.array([0.0, 0.0, 0.0], dtype='f4')

        # Limits
        self.phi_min = 10.0
        self.phi_max = 80.0
        self.distance_min = 5.0
        self.distance_max = 30.0

        # Sensitivity
        self.orbit_sensitivity = 0.3
        self.zoom_sensitivity = 1.0

    def get_eye_position(self):
        """Calculate eye position from spherical coordinates."""
        theta_rad = math.radians(self.theta)
        phi_rad = math.radians(self.phi)

        # Spherical to Cartesian (Y-up coordinate system)
        x = self.distance * math.cos(phi_rad) * math.sin(theta_rad)
        y = self.distance * math.sin(phi_rad)
        z = self.distance * math.cos(phi_rad) * math.cos(theta_rad)

        return np.array([
            self.target[0] + x,
            self.target[1] + y,
            self.target[2] + z
        ], dtype='f4')

    def get_view_matrix(self):
        """Build look-at view matrix."""
        eye = Vector3(self.get_eye_position())
        target = Vector3(self.target)
        up = Vector3([0.0, 1.0, 0.0], dtype='f4')
        return matrix44.create_look_at(eye, target, up, dtype='f4')

    def get_projection_matrix(self, aspect=1.0):
        """Build perspective projection matrix."""
        return matrix44.create_perspective_projection(
            45.0, aspect, 0.1, 100.0, dtype='f4'
        )

    def get_vp_matrix(self, aspect=1.0):
        """Return combined view-projection matrix."""
        view = self.get_view_matrix()
        proj = self.get_projection_matrix(aspect)
        return matrix44.multiply(view, proj)

    def orbit(self, dx, dy):
        """
        Adjust camera orbit from mouse delta.

        Args:
            dx: Horizontal mouse movement (pixels)
            dy: Vertical mouse movement (pixels)
        """
        self.theta -= dx * self.orbit_sensitivity
        self.phi += dy * self.orbit_sensitivity
        self.phi = max(self.phi_min, min(self.phi_max, self.phi))

    def zoom(self, delta):
        """
        Adjust camera distance.

        Args:
            delta: Positive = zoom in, negative = zoom out
        """
        self.distance -= delta * self.zoom_sensitivity
        self.distance = max(self.distance_min, min(self.distance_max, self.distance))

    def reset(self):
        """Reset camera to default position."""
        self.distance = 12.0
        self.theta = 0.0
        self.phi = 45.0
