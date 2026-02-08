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


def create_turtle_shell_mesh(radius, dome_height, rim_height=0.1,
                              rings=20, segments=48):
    """
    Create a turtle shell (carapace) mesh: parabolic dome + flat bottom.

    The dome apex is at Y=dome_height, base at Y=0, bottom at Y=-rim_height.

    Returns:
        (vertices, indices) with format [pos(3) + normal(3) + uv(2)]
    """
    vertices = []
    indices = []
    r2 = radius * radius

    # --- Dome cap surface ---
    for i in range(rings + 1):
        t = i / rings  # 0=center, 1=edge
        rho = radius * t
        y = dome_height * (1.0 - t * t)  # parabolic

        for j in range(segments):
            angle = 2 * np.pi * j / segments
            cos_a = np.cos(angle)
            sin_a = np.sin(angle)

            x = rho * cos_a
            z = rho * sin_a

            if t < 0.001:
                nx, ny, nz = 0.0, 1.0, 0.0
            else:
                grad_x = 2.0 * dome_height * x / r2
                grad_z = 2.0 * dome_height * z / r2
                length = np.sqrt(grad_x * grad_x + 1.0 + grad_z * grad_z)
                nx = grad_x / length
                ny = 1.0 / length
                nz = grad_z / length

            u = 0.5 + 0.5 * cos_a * t
            v = 0.5 + 0.5 * sin_a * t
            vertices.append([x, y, z, nx, ny, nz, u, v])

    # Dome triangles
    for i in range(rings):
        for j in range(segments):
            next_j = (j + 1) % segments
            r0 = i * segments + j
            r1 = i * segments + next_j
            r2_idx = (i + 1) * segments + j
            r3 = (i + 1) * segments + next_j
            if i == 0:
                indices.extend([r0, r2_idx, r3])
            else:
                indices.extend([r0, r2_idx, r3])
                indices.extend([r0, r3, r1])

    # --- Bottom face (flat disc) ---
    bottom_y = -rim_height
    bottom_center = len(vertices)
    vertices.append([0, bottom_y, 0, 0, -1, 0, 0.5, 0.5])
    for j in range(segments):
        angle = 2 * np.pi * j / segments
        cos_a = np.cos(angle)
        sin_a = np.sin(angle)
        x = radius * cos_a
        z = radius * sin_a
        vertices.append([x, bottom_y, z, 0, -1, 0,
                         0.5 + 0.5 * cos_a, 0.5 + 0.5 * sin_a])
    for j in range(segments):
        next_j = (j + 1) % segments
        indices.extend([bottom_center, bottom_center + 1 + next_j,
                        bottom_center + 1 + j])

    # --- Rim (connect dome edge to bottom edge) ---
    rim_base = len(vertices)
    for j in range(segments):
        angle = 2 * np.pi * j / segments
        cos_a = np.cos(angle)
        sin_a = np.sin(angle)
        x = radius * cos_a
        z = radius * sin_a
        vertices.append([x, 0, z, cos_a, 0, sin_a, 0, 0])
        vertices.append([x, bottom_y, z, cos_a, 0, sin_a, 0, 0])
    for j in range(segments):
        next_j = (j + 1) % segments
        t1 = rim_base + j * 2
        b1 = rim_base + j * 2 + 1
        t2 = rim_base + next_j * 2
        b2 = rim_base + next_j * 2 + 1
        indices.extend([t1, b1, b2, t1, b2, t2])

    vertices = np.array(vertices, dtype='f4')
    indices = np.array(indices, dtype='i4')
    return vertices, indices


def create_turtle_head_mesh(length=1.2, radius=0.4, segments=16, rings=8):
    """
    Create a turtle head mesh (tapered tube extending along +Z).

    Returns:
        (vertices, indices) with format [pos(3) + normal(3) + uv(2)]
    """
    vertices = []
    indices = []

    for i in range(rings + 1):
        t = i / rings
        z = length * t
        r = radius * (1.0 - 0.6 * t * t)  # taper toward tip

        for j in range(segments):
            angle = 2 * np.pi * j / segments
            cos_a = np.cos(angle)
            sin_a = np.sin(angle)
            x = r * cos_a
            y = r * sin_a

            nx, ny, nz = cos_a, sin_a, 0.3 * t
            ln = np.sqrt(nx*nx + ny*ny + nz*nz)
            nx /= ln; ny /= ln; nz /= ln

            vertices.append([x, y, z, nx, ny, nz, 0, 0])

    for i in range(rings):
        for j in range(segments):
            next_j = (j + 1) % segments
            r0 = i * segments + j
            r1 = i * segments + next_j
            r2 = (i + 1) * segments + j
            r3 = (i + 1) * segments + next_j
            indices.extend([r0, r2, r3])
            indices.extend([r0, r3, r1])

    # Tip cap
    tip_idx = len(vertices)
    vertices.append([0, 0, length, 0, 0, 1, 0, 0])
    last_ring = rings * segments
    for j in range(segments):
        next_j = (j + 1) % segments
        indices.extend([tip_idx, last_ring + j, last_ring + next_j])

    vertices = np.array(vertices, dtype='f4')
    indices = np.array(indices, dtype='i4')
    return vertices, indices


def create_turtle_leg_mesh(length=0.8, radius=0.35, segments=12):
    """
    Create a stubby turtle leg (tapered cylinder extending along -Y).

    Returns:
        (vertices, indices) with format [pos(3) + normal(3) + uv(2)]
    """
    vertices = []
    indices = []
    rings = 4
    for i in range(rings + 1):
        t = i / rings
        y = -length * t
        r = radius * (1.0 - 0.3 * t)
        for j in range(segments):
            angle = 2 * np.pi * j / segments
            cos_a = np.cos(angle)
            sin_a = np.sin(angle)
            vertices.append([r * cos_a, y, r * sin_a, cos_a, 0, sin_a, 0, 0])

    for i in range(rings):
        for j in range(segments):
            next_j = (j + 1) % segments
            r0 = i * segments + j
            r1 = i * segments + next_j
            r2 = (i + 1) * segments + j
            r3 = (i + 1) * segments + next_j
            indices.extend([r0, r2, r3])
            indices.extend([r0, r3, r1])

    # Bottom cap
    cap_idx = len(vertices)
    vertices.append([0, -length, 0, 0, -1, 0, 0, 0])
    last_ring = rings * segments
    for j in range(segments):
        next_j = (j + 1) % segments
        indices.extend([cap_idx, last_ring + next_j, last_ring + j])

    vertices = np.array(vertices, dtype='f4')
    indices = np.array(indices, dtype='i4')
    return vertices, indices


def create_turtle_tail_mesh(length=0.4, radius=0.15, segments=8):
    """
    Create a small turtle tail (cone extending along -Z).

    Returns:
        (vertices, indices) with format [pos(3) + normal(3) + uv(2)]
    """
    vertices = []
    indices = []

    for j in range(segments):
        angle = 2 * np.pi * j / segments
        cos_a = np.cos(angle)
        sin_a = np.sin(angle)
        vertices.append([radius * cos_a, radius * sin_a, 0,
                         cos_a, sin_a, 0, 0, 0])

    tip_idx = len(vertices)
    vertices.append([0, 0, -length, 0, 0, -1, 0, 0])

    for j in range(segments):
        next_j = (j + 1) % segments
        indices.extend([j, next_j, tip_idx])

    vertices = np.array(vertices, dtype='f4')
    indices = np.array(indices, dtype='i4')
    return vertices, indices


def create_turtle_hex_pattern(radius, dome_height):
    """
    Create line vertices for the turtle shell scute pattern.

    Returns numpy array of line vertices [pos(3) + color(4)] for GL_LINES.
    """
    line_color = (0.25, 0.28, 0.18, 0.8)
    cr, cg, cb, ca = line_color

    def dome_y(rho):
        t = min(rho / radius, 1.0)
        return dome_height * (1.0 - t * t)

    def pos_on_dome(r_frac, angle_rad):
        rho = radius * r_frac
        x = rho * np.cos(angle_rad)
        z = rho * np.sin(angle_rad)
        y = dome_y(rho) + 0.005
        return (x, y, z)

    lines = []

    def add_line(p0, p1):
        lines.append([p0[0], p0[1], p0[2], cr, cg, cb, ca])
        lines.append([p1[0], p1[1], p1[2], cr, cg, cb, ca])

    # Central vertebral scutes: 5 hexagons along Z axis
    vertebral_centers = []
    for k in range(5):
        cz = radius * (k - 2) * 0.18
        c_rho = abs(cz)
        cy = dome_y(c_rho) + 0.005
        vertebral_centers.append((0, cy, cz))

        hex_r = 0.35
        hex_pts = []
        for h in range(6):
            ha = h * np.pi / 3
            hx = hex_r * np.cos(ha)
            hz = cz + hex_r * np.sin(ha)
            h_rho = np.sqrt(hx * hx + hz * hz)
            hy = dome_y(h_rho) + 0.005
            hex_pts.append((hx, hy, hz))
        for h in range(6):
            add_line(hex_pts[h], hex_pts[(h + 1) % 6])

    # Marginal ring near the edge
    n_ring = 24
    ring_r = 0.85
    ring_pts = []
    for i in range(n_ring):
        angle = 2 * np.pi * i / n_ring
        ring_pts.append(pos_on_dome(ring_r, angle))
    for i in range(n_ring):
        add_line(ring_pts[i], ring_pts[(i + 1) % n_ring])

    # Radial connections from vertebral to ring
    for vp in vertebral_centers:
        for rp in ring_pts:
            dx = rp[0] - vp[0]
            dz = rp[2] - vp[2]
            dist = np.sqrt(dx*dx + dz*dz)
            if dist < radius * 0.5:
                add_line(vp, rp)

    return np.array(lines, dtype='f4') if lines else np.zeros((0, 7), dtype='f4')
