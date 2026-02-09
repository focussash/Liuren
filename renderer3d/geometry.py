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


def _swept_tube(path_points, radii, segments=12):
    """
    Generate a tube mesh swept along a path with varying radius.

    Args:
        path_points: list of (x,y,z) centerline points
        radii: list of radii at each point (same length as path_points)
        segments: angular segments per ring
    Returns:
        (vertices, indices) in [pos(3)+normal(3)+uv(2)] format
    """
    path = [np.array(p, dtype='f4') for p in path_points]
    n = len(path)

    # Compute tangent at each point
    tangents = []
    for i in range(n):
        if i == 0:
            t = path[1] - path[0]
        elif i == n - 1:
            t = path[-1] - path[-2]
        else:
            t = path[i + 1] - path[i - 1]
        ln = np.linalg.norm(t)
        if ln < 1e-8:
            t = np.array([0, 1, 0], dtype='f4')
        else:
            t = t / ln
        tangents.append(t)

    # Build stable reference frames using parallel transport
    # Initial reference: pick a vector not parallel to first tangent
    t0 = tangents[0]
    if abs(t0[1]) < 0.9:
        ref = np.array([0, 1, 0], dtype='f4')
    else:
        ref = np.array([1, 0, 0], dtype='f4')

    normals_list = []  # (normal, binormal) per point
    n0 = np.cross(t0, ref)
    n0 = n0 / np.linalg.norm(n0)
    b0 = np.cross(t0, n0)
    normals_list.append((n0, b0))

    for i in range(1, n):
        prev_n, prev_b = normals_list[-1]
        # Rotate previous frame to align with new tangent
        t_prev = tangents[i - 1]
        t_curr = tangents[i]
        v = np.cross(t_prev, t_curr)
        c = np.dot(t_prev, t_curr)
        if np.linalg.norm(v) < 1e-8:
            normals_list.append((prev_n.copy(), prev_b.copy()))
        else:
            # Rodrigues rotation of prev_n around axis v by angle
            v_norm = v / np.linalg.norm(v)
            # Rotate prev_n
            new_n = prev_n * c + np.cross(v_norm, prev_n) * np.linalg.norm(v) + \
                    v_norm * np.dot(v_norm, prev_n) * (1 - c)
            ln = np.linalg.norm(new_n)
            if ln < 1e-8:
                new_n = prev_n.copy()
            else:
                new_n = new_n / ln
            new_b = np.cross(t_curr, new_n)
            ln = np.linalg.norm(new_b)
            if ln > 1e-8:
                new_b = new_b / ln
            normals_list.append((new_n, new_b))

    vertices = []
    indices = []

    for i in range(n):
        p = path[i]
        r = radii[i]
        frame_n, frame_b = normals_list[i]
        v_coord = i / max(n - 1, 1)

        for j in range(segments):
            angle = 2 * np.pi * j / segments
            cos_a = np.cos(angle)
            sin_a = np.sin(angle)

            # Position on ring
            offset = r * (cos_a * frame_n + sin_a * frame_b)
            pos = p + offset
            # Normal = outward from centerline
            nrm = cos_a * frame_n + sin_a * frame_b
            ln = np.linalg.norm(nrm)
            if ln > 1e-8:
                nrm = nrm / ln

            u_coord = j / segments
            vertices.append([pos[0], pos[1], pos[2],
                             nrm[0], nrm[1], nrm[2],
                             u_coord, v_coord])

    # Indices: connect rings
    for i in range(n - 1):
        for j in range(segments):
            next_j = (j + 1) % segments
            r0 = i * segments + j
            r1 = i * segments + next_j
            r2 = (i + 1) * segments + j
            r3 = (i + 1) * segments + next_j
            indices.extend([r0, r2, r3])
            indices.extend([r0, r3, r1])

    # End caps
    # Start cap (close the beginning)
    cap_idx = len(vertices)
    t0 = tangents[0]
    vertices.append([path[0][0], path[0][1], path[0][2],
                     -t0[0], -t0[1], -t0[2], 0.5, 0.5])
    for j in range(segments):
        next_j = (j + 1) % segments
        indices.extend([cap_idx, next_j, j])  # reversed winding

    # End cap
    cap_idx2 = len(vertices)
    tn = tangents[-1]
    vertices.append([path[-1][0], path[-1][1], path[-1][2],
                     tn[0], tn[1], tn[2], 0.5, 0.5])
    last_ring = (n - 1) * segments
    for j in range(segments):
        next_j = (j + 1) % segments
        indices.extend([cap_idx2, last_ring + j, last_ring + next_j])

    vertices = np.array(vertices, dtype='f4')
    indices = np.array(indices, dtype='i4')
    return vertices, indices


def _ellipsoid_mesh(rx, ry, rz, rings=10, segments=16):
    """
    Generate an ellipsoid mesh centered at origin.

    Args:
        rx, ry, rz: radii along X, Y, Z axes
        rings: latitude rings
        segments: longitude segments
    Returns:
        (vertices, indices) in [pos(3)+normal(3)+uv(2)] format
    """
    vertices = []
    indices = []

    for i in range(rings + 1):
        phi = np.pi * i / rings  # 0 to pi (top to bottom)
        cos_phi = np.cos(phi)
        sin_phi = np.sin(phi)

        for j in range(segments + 1):
            theta = 2 * np.pi * j / segments
            cos_theta = np.cos(theta)
            sin_theta = np.sin(theta)

            # Position
            x = rx * sin_phi * cos_theta
            y = ry * cos_phi
            z = rz * sin_phi * sin_theta

            # Normal (gradient of x²/rx² + y²/ry² + z²/rz² = 1)
            nx = x / (rx * rx) if rx > 0 else 0
            ny = y / (ry * ry) if ry > 0 else 0
            nz = z / (rz * rz) if rz > 0 else 0
            ln = np.sqrt(nx*nx + ny*ny + nz*nz)
            if ln > 1e-8:
                nx /= ln; ny /= ln; nz /= ln

            u = j / segments
            v = i / rings
            vertices.append([x, y, z, nx, ny, nz, u, v])

    # Indices
    for i in range(rings):
        for j in range(segments):
            r0 = i * (segments + 1) + j
            r1 = i * (segments + 1) + j + 1
            r2 = (i + 1) * (segments + 1) + j
            r3 = (i + 1) * (segments + 1) + j + 1
            indices.extend([r0, r2, r3])
            indices.extend([r0, r3, r1])

    vertices = np.array(vertices, dtype='f4')
    indices = np.array(indices, dtype='i4')
    return vertices, indices


def create_turtle_shell_mesh(radius, dome_height, rim_height=0.1,
                              rings=20, segments=48, z_scale=1.05):
    """
    Create a turtle shell (carapace) mesh: fuller dome + flat bottom.

    The dome apex is at Y=dome_height, base at Y=0, bottom at Y=-rim_height.
    z_scale makes the shell slightly oval (longer front-to-back).

    Returns:
        (vertices, indices) with format [pos(3) + normal(3) + uv(2)]
    """
    vertices = []
    indices = []

    def dome_y(t):
        """Fuller dome profile: (1-t²)^0.7"""
        val = max(1.0 - t * t, 0.0)
        return dome_height * val ** 0.7

    # --- Dome cap surface ---
    for i in range(rings + 1):
        t = i / rings  # 0=center, 1=edge
        rho = radius * t
        y = dome_y(t)

        for j in range(segments):
            angle = 2 * np.pi * j / segments
            cos_a = np.cos(angle)
            sin_a = np.sin(angle)

            x = rho * cos_a
            z = rho * sin_a * z_scale

            # Numerical normal via finite differences
            if t < 0.001:
                nx, ny, nz = 0.0, 1.0, 0.0
            else:
                dt = 0.001
                y_here = dome_y(t)
                y_dr = dome_y(t + dt)
                dy_dt = (y_dr - y_here) / dt
                # Surface: P(t,theta) = (R*t*cos, dome_y(t), R*t*sin*z_scale)
                # dP/dt = (R*cos, dy_dt * R, R*sin*z_scale)  [chain rule]
                # dP/dtheta = (-R*t*sin, 0, R*t*cos*z_scale)
                dPdt = np.array([radius * cos_a, dy_dt * radius, radius * sin_a * z_scale])
                dPdth = np.array([-rho * sin_a, 0.0, rho * cos_a * z_scale])
                normal = np.cross(dPdth, dPdt)
                ln = np.linalg.norm(normal)
                if ln > 1e-8:
                    normal /= ln
                    nx, ny, nz = normal[0], normal[1], normal[2]
                else:
                    nx, ny, nz = 0.0, 1.0, 0.0

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
        z = radius * sin_a * z_scale
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
        z = radius * sin_a * z_scale
        # Normal pointing outward
        out_x = cos_a
        out_z = sin_a * z_scale
        ln = np.sqrt(out_x*out_x + out_z*out_z)
        if ln > 1e-8:
            out_x /= ln; out_z /= ln
        vertices.append([x, 0, z, out_x, 0, out_z, 0, 0])
        vertices.append([x, bottom_y, z, out_x, 0, out_z, 0, 0])
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


def create_turtle_plastron_mesh(rx=2.4, rz=2.7, concavity=0.15,
                                 rings=12, segments=48):
    """
    Create a turtle plastron (belly plate) mesh: elliptical disc with
    slight upward concavity.

    Centered at origin in XZ plane.

    Returns:
        (vertices, indices) with format [pos(3) + normal(3) + uv(2)]
    """
    vertices = []
    indices = []

    for i in range(rings + 1):
        t = i / rings  # 0=center, 1=edge
        for j in range(segments):
            angle = 2 * np.pi * j / segments
            cos_a = np.cos(angle)
            sin_a = np.sin(angle)

            x = rx * t * cos_a
            z = rz * t * sin_a
            # Slight upward concavity: bowl shape
            y = concavity * (1.0 - t * t)

            # Normal: mostly +Y with slight inward tilt from concavity
            if t < 0.001:
                nx, ny, nz = 0.0, 1.0, 0.0
            else:
                nx = 2.0 * concavity * x / (rx * rx)
                nz = 2.0 * concavity * z / (rz * rz)
                ny = 1.0
                ln = np.sqrt(nx*nx + ny*ny + nz*nz)
                nx /= ln; ny /= ln; nz /= ln

            u = 0.5 + 0.5 * cos_a * t
            v = 0.5 + 0.5 * sin_a * t
            vertices.append([x, y, z, nx, ny, nz, u, v])

    # Triangles (same pattern as dome)
    for i in range(rings):
        for j in range(segments):
            next_j = (j + 1) % segments
            r0 = i * segments + j
            r1 = i * segments + next_j
            r2 = (i + 1) * segments + j
            r3 = (i + 1) * segments + next_j
            if i == 0:
                indices.extend([r0, r2, r3])
            else:
                indices.extend([r0, r2, r3])
                indices.extend([r0, r3, r1])

    # Bottom face (flat underside)
    bottom_center = len(vertices)
    vertices.append([0, 0, 0, 0, -1, 0, 0.5, 0.5])
    for j in range(segments):
        angle = 2 * np.pi * j / segments
        cos_a = np.cos(angle)
        sin_a = np.sin(angle)
        x = rx * cos_a
        z = rz * sin_a
        vertices.append([x, 0, z, 0, -1, 0,
                         0.5 + 0.5 * cos_a, 0.5 + 0.5 * sin_a])
    for j in range(segments):
        next_j = (j + 1) % segments
        indices.extend([bottom_center, bottom_center + 1 + next_j,
                        bottom_center + 1 + j])

    vertices = np.array(vertices, dtype='f4')
    indices = np.array(indices, dtype='i4')
    return vertices, indices


def create_turtle_bridge_mesh(shell_radius, shell_z_scale, plastron_rx, plastron_rz,
                               bridge_height=0.55, segments=48):
    """
    Create a body bridge (flank) mesh connecting carapace rim to plastron edge.

    Quad strip from shell base (Y=0) down to plastron top (Y=-bridge_height).

    Returns:
        (vertices, indices) with format [pos(3) + normal(3) + uv(2)]
    """
    vertices = []
    indices = []

    for j in range(segments):
        angle = 2 * np.pi * j / segments
        cos_a = np.cos(angle)
        sin_a = np.sin(angle)

        # Top edge: shell rim
        x_top = shell_radius * cos_a
        z_top = shell_radius * sin_a * shell_z_scale

        # Bottom edge: plastron rim
        x_bot = plastron_rx * cos_a
        z_bot = plastron_rz * sin_a

        # Outward normal (average of top and bottom positions)
        mx = (x_top + x_bot) * 0.5
        mz = (z_top + z_bot) * 0.5
        ln = np.sqrt(mx*mx + mz*mz)
        if ln > 1e-8:
            nx = mx / ln
            nz = mz / ln
        else:
            nx, nz = cos_a, sin_a

        u = j / segments
        vertices.append([x_top, 0, z_top, nx, 0, nz, u, 1])
        vertices.append([x_bot, -bridge_height, z_bot, nx, 0, nz, u, 0])

    for j in range(segments):
        next_j = (j + 1) % segments
        t1 = j * 2
        b1 = j * 2 + 1
        t2 = next_j * 2
        b2 = next_j * 2 + 1
        indices.extend([t1, b1, b2, t1, b2, t2])

    vertices = np.array(vertices, dtype='f4')
    indices = np.array(indices, dtype='i4')
    return vertices, indices


def create_turtle_neck_mesh(segments=12):
    """
    Create a turtle neck mesh using swept tube with S-curve path.

    The neck extends along +Z with a gentle upward S-curve.

    Returns:
        (vertices, indices) with format [pos(3) + normal(3) + uv(2)]
    """
    path = [(0, 0, 0), (0, -0.15, 0.5), (0, 0.05, 0.9), (0, 0.25, 1.2)]
    radii = [0.25, 0.22, 0.20, 0.18]
    return _swept_tube(path, radii, segments=segments)


def create_turtle_head_mesh():
    """
    Create a turtle head mesh as an ellipsoid.

    Returns:
        (vertices, indices) with format [pos(3) + normal(3) + uv(2)]
    """
    return _ellipsoid_mesh(0.22, 0.20, 0.28, rings=10, segments=16)


def create_turtle_leg_mesh(segments=12):
    """
    Create an articulated turtle leg using swept tube with bent path.

    Path goes: shoulder → elbow (outward+slightly down) → foot (mostly down).

    Returns:
        (vertices, indices) with format [pos(3) + normal(3) + uv(2)]
    """
    path = [(0, 0, 0), (0.85, -0.23, 0), (1.1, -0.95, 0)]
    radii = [0.28, 0.22, 0.18]
    return _swept_tube(path, radii, segments=segments)


def create_turtle_tail_mesh(segments=8):
    """
    Create a small turtle tail using swept tube extending along -Z.

    Returns:
        (vertices, indices) with format [pos(3) + normal(3) + uv(2)]
    """
    path = [(0, 0, 0), (0, -0.1, -0.5)]
    radii = [0.12, 0.03]
    return _swept_tube(path, radii, segments=segments)


def create_turtle_scute_pattern(radius, dome_height, z_scale=1.05):
    """
    Create line vertices for a realistic turtle shell scute pattern.

    Layout:
    - 5 vertebral hexagons along center (Z axis)
    - Marginal ring at r_frac=0.90
    - Radial costal lines connecting vertebral corners to marginal ring
    - 24 short marginal radial lines from ring to rim

    Returns numpy array of line vertices [pos(3) + color(4)] for GL_LINES.
    """
    line_color = (0.22, 0.20, 0.10, 0.7)
    cr, cg, cb, ca = line_color

    def dome_y_func(t):
        """Same dome profile as shell mesh."""
        t = min(max(t, 0.0), 1.0)
        return dome_height * (1.0 - t * t) ** 0.7

    def pos_on_dome(r_frac, angle_rad):
        rho = radius * r_frac
        x = rho * np.cos(angle_rad)
        z = rho * np.sin(angle_rad) * z_scale
        y = dome_y_func(r_frac) + 0.008
        return (x, y, z)

    def pos_on_dome_xz(x, z):
        """Get dome position from x, z coordinates."""
        rho = np.sqrt((x / 1.0)**2 + (z / z_scale)**2)
        t = min(rho / radius, 1.0)
        y = dome_y_func(t) + 0.008
        return (x, y, z)

    lines = []

    def add_line(p0, p1):
        lines.append([p0[0], p0[1], p0[2], cr, cg, cb, ca])
        lines.append([p1[0], p1[1], p1[2], cr, cg, cb, ca])

    def add_arc(p0, p1, n_steps=8):
        """Add a line as a series of small segments projected onto dome."""
        for s in range(n_steps):
            t0 = s / n_steps
            t1 = (s + 1) / n_steps
            x0 = p0[0] + (p1[0] - p0[0]) * t0
            z0 = p0[2] + (p1[2] - p0[2]) * t0
            x1 = p0[0] + (p1[0] - p0[0]) * t1
            z1 = p0[2] + (p1[2] - p0[2]) * t1
            add_line(pos_on_dome_xz(x0, z0), pos_on_dome_xz(x1, z1))

    # --- 5 vertebral hexagons along Z axis (center spine) ---
    hex_r = 0.50
    vertebral_hex_corners = []
    for k in range(5):
        cz = radius * (k - 2) * 0.16 * z_scale  # spread along Z
        hex_pts = []
        for h in range(6):
            ha = h * np.pi / 3 + np.pi / 6  # rotate 30° for flat-top hex
            hx = hex_r * np.cos(ha)
            hz = cz + hex_r * np.sin(ha) * z_scale
            hex_pts.append(pos_on_dome_xz(hx, hz))
        for h in range(6):
            add_line(hex_pts[h], hex_pts[(h + 1) % 6])
        vertebral_hex_corners.append(hex_pts)

    # --- Marginal ring at r_frac=0.90 ---
    n_ring = 24
    ring_r = 0.90
    ring_pts = []
    for i in range(n_ring):
        angle = 2 * np.pi * i / n_ring
        ring_pts.append(pos_on_dome(ring_r, angle))
    for i in range(n_ring):
        add_line(ring_pts[i], ring_pts[(i + 1) % n_ring])

    # --- Costal lines: connect outermost vertebral hex corners to nearest ring points ---
    for hex_pts in vertebral_hex_corners:
        for hp in hex_pts:
            # Find nearest ring point
            best_dist = float('inf')
            best_rp = ring_pts[0]
            for rp in ring_pts:
                dx = rp[0] - hp[0]
                dz = rp[2] - hp[2]
                dist = dx*dx + dz*dz
                if dist < best_dist:
                    best_dist = dist
                    best_rp = rp
            # Only draw if the hex corner is significantly inside the ring
            hp_r = np.sqrt(hp[0]**2 + (hp[2] / z_scale)**2) / radius
            if hp_r < ring_r - 0.05:
                add_arc(hp, best_rp, n_steps=6)

    # --- Marginal radial lines from ring to rim ---
    rim_r = 0.98
    for i in range(n_ring):
        angle = 2 * np.pi * i / n_ring
        rim_pt = pos_on_dome(rim_r, angle)
        add_line(ring_pts[i], rim_pt)

    return np.array(lines, dtype='f4') if lines else np.zeros((0, 7), dtype='f4')
