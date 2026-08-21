# ============================================================
# Shaders
# ============================================================
# Shader sind kleine Programme, die auf der GPU laufen.
# Sie werden in zwei Teile aufgeteilt:
# - Vertex Shader: verarbeitet Vertices / Punkte des 3D-Modells
# - Fragment Shader: berechnet die Farbe jedes Pixels
#
# Die Matrizen uModel, uView und uProj werden hier verwendet, um die Welt,
# die Kamera und die Projektion korrekt auf den Bildschirm zu bringen.

# PHONG_VS = Phong-Vertex-Shader
# Dieser Shader berechnet für jedes Vertex die Position im Weltkoordinatensystem
# und die Normalen, damit anschließend eine Beleuchtung berechnet werden kann.
PHONG_VS = """
#version 330 core
layout(location=0) in vec3 aPos;
layout(location=1) in vec3 aNormal;
uniform mat4 uModel, uView, uProj;
out vec3 vNormal, vWorldPos;
void main() {
    vec4 wp = uModel * vec4(aPos, 1.0);
    vWorldPos = wp.xyz;
    vNormal = mat3(uModel) * aNormal;
    gl_Position = uProj * uView * wp;
}
"""

# PHONG_FS = Phong-Fragment-Shader
# Hier wird die Farbe eines Pixels basierend auf Licht, Normalen und Kamera
# berechnet. Dadurch wirken Objekte räumlich und schattig statt flach gefärbt.
PHONG_FS = """
#version 330 core
in vec3 vNormal, vWorldPos;
uniform vec3 uColor, uLightDir, uViewPos, uPlayerPos, uEmissive;
uniform float uSpotlight, uAlpha;
out vec4 FragColor;
void main() {
    vec3 N = normalize(vNormal);
    vec3 L = normalize(-uLightDir);
    float ambient = 0.45;
    float diff = max(dot(N, L), 0.0);
    vec3 V = normalize(uViewPos - vWorldPos);
    vec3 R = reflect(-L, N);
    float spec = pow(max(dot(V, R), 0.0), 32.0) * 0.4;
    vec3 color = uColor * (ambient + diff * 0.7) + vec3(spec);
    color += uEmissive;
    if (uSpotlight > 0.5) {
        float d = length(vWorldPos.xz - uPlayerPos.xz);
        float s = 1.0 - smoothstep(12.0, 25.0, d);
        color *= (0.35 + 0.65 * s);
    }
    FragColor = vec4(color, uAlpha);
}
"""

# FLAT_VS = einfacher Vertex-Shader ohne Beleuchtung
# Dieser Shader transformiert nur die Position eines Objekts mit Model- und
# Projektionsmatrix. Es gibt keine Normalen oder Lichtberechnung.
FLAT_VS = """
#version 330 core
layout(location=0) in vec3 aPos;
uniform mat4 uModel, uProj;
void main() { gl_Position = uProj * uModel * vec4(aPos, 1.0); }
"""

# FLAT_FS = einfacher Fragment-Shader
# Malt das Objekt in einer festen Farbe ohne Schattierung.
FLAT_FS = """
#version 330 core
uniform vec4 uColor;
out vec4 FragColor;
void main() { FragColor = uColor; }
"""

# TEXT_VS = Shader für Texturen / 2D-Objekte
# Zusätzlich zu Positionen werden UV-Koordinaten übergeben, damit ein Bild
# auf ein Objekt gemappt werden kann.
TEXT_VS = """
#version 330 core
layout(location=0) in vec3 aPos;
layout(location=1) in vec2 aTexCoord;
uniform mat4 uModel, uProj;
out vec2 vTexCoord;
void main() { gl_Position = uProj * uModel * vec4(aPos, 1.0); vTexCoord = aTexCoord; }
"""

# TEXT_FS = Fragment-Shader für Textur-Rendering
# Liest die Texturfarbe aus uTex und kombiniert sie mit der übergebenen Farbe.
# Alpha (= Transparenz) wird dabei berücksichtigt.
TEXT_FS = """
#version 330 core
in vec2 vTexCoord;
uniform sampler2D uTex;
uniform vec4 uColor;
out vec4 FragColor;
void main() {
    float a = texture(uTex, vTexCoord).a;
    FragColor = vec4(uColor.rgb, a * uColor.a);
}
"""
