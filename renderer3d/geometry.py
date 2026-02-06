# renderer3d/geometry.py
# Mesh generation for 3D plate rendering

import numpy as np


def create_box_mesh(width, height, depth):
    """
    Create a 3D box mesh (for the earth plate slab).

    The box is centered at origin, with Y as up-axis.
    Top face = +Y, bottom face = -Y.

    Args:
        width: X dimension
        height: Z dimension (depth of the square plate)
        depth: Y dimension (thickness of the slab)

    Returns:
        (vertices, indices) where vertices is a numpy array of
        [position(3) + normal(3) + uv(2)] per vertex.
    """
    w, h, d = width / 2, depth / 2, height / 2

    # Each face: 4 vertices with position, normal, UV
    # Top face (+Y) - this gets the plate texture
    top = [
        [-w,  h, -d,  0, 1, 0,  0, 0],  # top-left
        [ w,  h, -d,  0, 1, 0,  1, 0],  # top-right
        [ w,  h,  d,  0, 1, 0,  1, 1],  # bottom-right
        [-w,  h,  d,  0, 1, 0,  0, 1],  # bottom-left
    ]

    # Bottom face (-Y)
    bottom = [
        [-w, -h,  d,  0, -1, 0,  0, 0],
        [ w, -h,  d,  0, -1, 0,  1, 0],
        [ w, -h, -d,  0, -1, 0,  1, 1],
        [-w, -h, -d,  0, -1, 0,  0, 1],
    ]

    # Front face (+Z)
    front = [
        [-w, -h,  d,  0, 0, 1,  0, 0],
        [ w, -h,  d,  0, 0, 1,  1, 0],
        [ w,  h,  d,  0, 0, 1,  1, 1],
        [-w,  h,  d,  0, 0, 1,  0, 1],
    ]

    # Back face (-Z)
    back = [
        [ w, -h, -d,  0, 0, -1,  0, 0],
        [-w, -h, -d,  0, 0, -1,  1, 0],
        [-w,  h, -d,  0, 0, -1,  1, 1],
        [ w,  h, -d,  0, 0, -1,  0, 1],
    ]

    # Right face (+X)
    right = [
        [ w, -h,  d,  1, 0, 0,  0, 0],
        [ w, -h, -d,  1, 0, 0,  1, 0],
        [ w,  h, -d,  1, 0, 0,  1, 1],
        [ w,  h,  d,  1, 0, 0,  0, 1],
    ]

    # Left face (-X)
    left = [
        [-w, -h, -d,  -1, 0, 0,  0, 0],
        [-w, -h,  d,  -1, 0, 0,  1, 0],
        [-w,  h,  d,  -1, 0, 0,  1, 1],
        [-w,  h, -d,  -1, 0, 0,  0, 1],
    ]

    all_faces = [top, bottom, front, back, right, left]
    vertices = []
    indices = []

    for i, face in enumerate(all_faces):
        base = i * 4
        vertices.extend(face)
        indices.extend([base, base+1, base+2, base, base+2, base+3])

    vertices = np.array(vertices, dtype='f4')
    indices = np.array(indices, dtype='i4')

    return vertices, indices


def create_cylinder_mesh(radius, height, segments=64):
    """
    Create a 3D cylinder mesh (for the heaven plate disc).

    The cylinder is centered at origin, with Y as up-axis.
    Top face = +Y/2, bottom face = -Y/2.

    Args:
        radius: Radius of the cylinder
        height: Y dimension (thickness)
        segments: Number of segments around the circumference

    Returns:
        (vertices, indices) - same format as create_box_mesh
    """
    vertices = []
    indices = []
    half_h = height / 2

    # --- Top face (fan from center) ---
    # Center vertex
    top_center_idx = 0
    vertices.append([0, half_h, 0,  0, 1, 0,  0.5, 0.5])

    for i in range(segments):
        angle = 2 * np.pi * i / segments
        x = radius * np.cos(angle)
        z = radius * np.sin(angle)
        # UV: map circle to [0,1] square (circular mapping)
        u = 0.5 + 0.5 * np.cos(angle)
        v = 0.5 + 0.5 * np.sin(angle)
        vertices.append([x, half_h, z,  0, 1, 0,  u, v])

    # Top face triangles (fan)
    for i in range(segments):
        next_i = (i + 1) % segments
        indices.extend([top_center_idx, top_center_idx + 1 + i, top_center_idx + 1 + next_i])

    # --- Bottom face (fan from center) ---
    bottom_center_idx = len(vertices)
    vertices.append([0, -half_h, 0,  0, -1, 0,  0.5, 0.5])

    for i in range(segments):
        angle = 2 * np.pi * i / segments
        x = radius * np.cos(angle)
        z = radius * np.sin(angle)
        u = 0.5 + 0.5 * np.cos(angle)
        v = 0.5 + 0.5 * np.sin(angle)
        vertices.append([x, -half_h, z,  0, -1, 0,  u, v])

    # Bottom face triangles (fan, reversed winding)
    for i in range(segments):
        next_i = (i + 1) % segments
        indices.extend([bottom_center_idx, bottom_center_idx + 1 + next_i, bottom_center_idx + 1 + i])

    # --- Side face (quad strip) ---
    side_base = len(vertices)
    for i in range(segments):
        angle = 2 * np.pi * i / segments
        x = radius * np.cos(angle)
        z = radius * np.sin(angle)
        nx = np.cos(angle)
        nz = np.sin(angle)
        u = i / segments

        # Top edge vertex
        vertices.append([x,  half_h, z,  nx, 0, nz,  u, 1])
        # Bottom edge vertex
        vertices.append([x, -half_h, z,  nx, 0, nz,  u, 0])

    # Side face triangles
    for i in range(segments):
        next_i = (i + 1) % segments
        top1 = side_base + i * 2
        bot1 = side_base + i * 2 + 1
        top2 = side_base + next_i * 2
        bot2 = side_base + next_i * 2 + 1
        indices.extend([top1, bot1, bot2, top1, bot2, top2])

    vertices = np.array(vertices, dtype='f4')
    indices = np.array(indices, dtype='i4')

    return vertices, indices


def create_disc_mesh(radius, segments=64):
    """
    Create a flat disc mesh on the XZ plane at Y=0 (for shadows).

    Normal faces +Y. UV maps circle to [0,1] square.

    Args:
        radius: Radius of the disc
        segments: Number of segments around the circumference

    Returns:
        (vertices, indices) - same format as other mesh functions
    """
    vertices = []
    indices = []

    # Center vertex
    vertices.append([0, 0, 0, 0, 1, 0, 0.5, 0.5])

    for i in range(segments):
        angle = 2 * np.pi * i / segments
        x = radius * np.cos(angle)
        z = radius * np.sin(angle)
        u = 0.5 + 0.5 * np.cos(angle)
        v = 0.5 + 0.5 * np.sin(angle)
        vertices.append([x, 0, z, 0, 1, 0, u, v])

    for i in range(segments):
        next_i = (i + 1) % segments
        indices.extend([0, 1 + i, 1 + next_i])

    vertices = np.array(vertices, dtype='f4')
    indices = np.array(indices, dtype='i4')

    return vertices, indices
