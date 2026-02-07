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


def create_dome_mesh(radius, dome_height, rim_height, rings=24, segments=64):
    """
    Create a dome mesh (spherical-cap top + cylindrical rim + flat bottom).

    The dome base sits at Y=0, dome apex at Y=dome_height.
    The rim extends from Y=0 down to Y=-rim_height.
    Bottom face at Y=-rim_height.

    Args:
        radius: Radius of the dome base
        dome_height: Height of the dome cap above the base
        rim_height: Height of the cylindrical rim below the base
        rings: Number of concentric rings for the dome surface
        segments: Number of angular segments

    Returns:
        (vertices, indices, dome_index_count) where dome_index_count
        is the number of indices for the textured dome cap.
    """
    vertices = []
    indices = []
    r2 = radius * radius

    # --- Dome cap surface (textured) ---
    # Concentric rings from center (ring 0) to edge (ring=rings)
    for i in range(rings + 1):
        t = i / rings  # 0 = center, 1 = edge
        rho = radius * t
        y = dome_height * (1.0 - t * t)  # parabolic: h*(1-t²)

        for j in range(segments):
            angle = 2 * np.pi * j / segments
            cos_a = np.cos(angle)
            sin_a = np.sin(angle)

            x = rho * cos_a
            z = rho * sin_a

            # Normal from parabolic surface gradient:
            # Surface: y = h*(1 - (x²+z²)/r²)
            # dy/dx = -2*h*x/r², dy/dz = -2*h*z/r²
            # Unnormalized normal: (2*h*x/r², 1, 2*h*z/r²)
            if t < 0.001:
                nx, ny, nz = 0.0, 1.0, 0.0
            else:
                grad_x = 2.0 * dome_height * x / r2
                grad_z = 2.0 * dome_height * z / r2
                length = np.sqrt(grad_x * grad_x + 1.0 + grad_z * grad_z)
                nx = grad_x / length
                ny = 1.0 / length
                nz = grad_z / length

            # UV: orthographic projection (same as cylinder top face)
            u = 0.5 + 0.5 * cos_a * t
            v = 0.5 + 0.5 * sin_a * t

            vertices.append([x, y, z, nx, ny, nz, u, v])

    # Dome cap triangles (quads between rings)
    for i in range(rings):
        for j in range(segments):
            next_j = (j + 1) % segments
            r0 = i * segments + j
            r1 = i * segments + next_j
            r2_idx = (i + 1) * segments + j
            r3 = (i + 1) * segments + next_j

            if i == 0:
                # First ring: triangles from center ring
                indices.extend([r0, r2_idx, r3])
            else:
                indices.extend([r0, r2_idx, r3])
                indices.extend([r0, r3, r1])

    dome_index_count = len(indices)

    # --- Cylindrical rim (side color, not textured) ---
    rim_base = len(vertices)
    for j in range(segments):
        angle = 2 * np.pi * j / segments
        cos_a = np.cos(angle)
        sin_a = np.sin(angle)
        x = radius * cos_a
        z = radius * sin_a

        # Top edge (dome base, y=0)
        vertices.append([x, 0, z, cos_a, 0, sin_a, 0, 0])
        # Bottom edge (y=-rim_height)
        vertices.append([x, -rim_height, z, cos_a, 0, sin_a, 0, 0])

    for j in range(segments):
        next_j = (j + 1) % segments
        top1 = rim_base + j * 2
        bot1 = rim_base + j * 2 + 1
        top2 = rim_base + next_j * 2
        bot2 = rim_base + next_j * 2 + 1
        indices.extend([top1, bot1, bot2, top1, bot2, top2])

    # --- Bottom face (flat disc at y=-rim_height) ---
    bottom_center = len(vertices)
    vertices.append([0, -rim_height, 0, 0, -1, 0, 0.5, 0.5])

    for j in range(segments):
        angle = 2 * np.pi * j / segments
        cos_a = np.cos(angle)
        sin_a = np.sin(angle)
        x = radius * cos_a
        z = radius * sin_a
        u = 0.5 + 0.5 * cos_a
        v = 0.5 + 0.5 * sin_a
        vertices.append([x, -rim_height, z, 0, -1, 0, u, v])

    for j in range(segments):
        next_j = (j + 1) % segments
        # Reversed winding for bottom face
        indices.extend([bottom_center, bottom_center + 1 + next_j, bottom_center + 1 + j])

    vertices = np.array(vertices, dtype='f4')
    indices = np.array(indices, dtype='i4')

    return vertices, indices, dome_index_count


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
