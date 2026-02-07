# renderer3d/shaders.py
# GLSL shader source strings for 3D plate rendering

# --- Test shaders (3D-1 验证用) ---

TEST_VERTEX_SHADER = """
#version 330

in vec3 in_position;
in vec3 in_color;

out vec3 v_color;

uniform mat4 u_vp;

void main() {
    gl_Position = u_vp * vec4(in_position, 1.0);
    v_color = in_color;
}
"""

TEST_FRAGMENT_SHADER = """
#version 330

in vec3 v_color;
out vec4 fragColor;

void main() {
    fragColor = vec4(v_color, 1.0);
}
"""

# --- Plate shaders (3D-3+) ---

PLATE_VERTEX_SHADER = """
#version 330

uniform mat4 u_model;
uniform mat4 u_vp;

in vec3 in_position;
in vec3 in_normal;
in vec2 in_uv;

out vec3 v_world_pos;
out vec3 v_normal;
out vec2 v_uv;

void main() {
    vec4 world = u_model * vec4(in_position, 1.0);
    v_world_pos = world.xyz;
    v_normal = mat3(u_model) * in_normal;
    v_uv = in_uv;
    gl_Position = u_vp * world;
}
"""

PLATE_FRAGMENT_SHADER = """
#version 330

uniform sampler2D u_texture;
uniform int u_use_texture;       // 1 = sample texture, 0 = use side_color
uniform vec3 u_side_color;       // color for non-textured faces

uniform vec3 u_light_dir;        // directional light direction (normalized)
uniform vec3 u_light_color;      // light color
uniform vec3 u_ambient;          // ambient light
uniform vec3 u_camera_pos;       // for specular
uniform float u_shininess;       // specular exponent
uniform int u_unlit;             // 1 = bypass lighting, output color directly

in vec3 v_world_pos;
in vec3 v_normal;
in vec2 v_uv;

out vec4 fragColor;

void main() {
    // Base color
    vec3 base;
    float alpha = 1.0;
    if (u_use_texture == 1) {
        vec4 tex = texture(u_texture, v_uv);
        base = tex.rgb;
        alpha = tex.a;
        if (alpha < 0.01) discard;
    } else {
        base = u_side_color;
    }

    // Unlit mode: output base color directly (for shadows, overlays)
    if (u_unlit == 1) {
        fragColor = vec4(base, alpha);
        return;
    }

    vec3 N = normalize(v_normal);
    vec3 L = normalize(-u_light_dir);
    vec3 V = normalize(u_camera_pos - v_world_pos);
    vec3 H = normalize(L + V);

    // Diffuse
    float diff = max(dot(N, L), 0.0);

    // Specular (Blinn-Phong)
    float spec = pow(max(dot(N, H), 0.0), u_shininess);

    vec3 color = u_ambient * base + diff * u_light_color * base + spec * u_light_color * 0.3;
    fragColor = vec4(color, alpha);
}
"""

# --- Celestial shaders (3D-11+) ---

BILLBOARD_VERTEX_SHADER = """
#version 330

uniform mat4 u_vp;
uniform mat4 u_model;
uniform vec3 u_camera_right;
uniform vec3 u_camera_up;
uniform float u_size;

in vec3 in_position;
in vec2 in_offset;

out vec2 v_uv;

void main() {
    vec4 world_center = u_model * vec4(in_position, 1.0);
    vec3 world_pos = world_center.xyz
                   + u_camera_right * in_offset.x * u_size
                   + u_camera_up * in_offset.y * u_size;
    gl_Position = u_vp * vec4(world_pos, 1.0);
    v_uv = in_offset * 0.5 + 0.5;
}
"""

GLOW_FRAGMENT_SHADER = """
#version 330

uniform vec3 u_color;
uniform float u_intensity;

in vec2 v_uv;
out vec4 fragColor;

void main() {
    float dist = length(v_uv - 0.5) * 2.0;
    float glow = exp(-dist * dist * 3.0);
    float alpha = glow * u_intensity;
    if (alpha < 0.01) discard;
    fragColor = vec4(u_color * glow, alpha);
}
"""

LINE_VERTEX_SHADER = """
#version 330

uniform mat4 u_vp;
uniform mat4 u_model;

in vec3 in_position;
in vec4 in_color;

out vec4 v_color;

void main() {
    vec4 world = u_model * vec4(in_position, 1.0);
    gl_Position = u_vp * world;
    v_color = in_color;
}
"""

LINE_FRAGMENT_SHADER = """
#version 330

in vec4 v_color;
out vec4 fragColor;

void main() {
    fragColor = v_color;
}
"""
