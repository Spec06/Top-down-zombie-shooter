import numpy as np
import math

# ============================================================
# Matrix Math
# ============================================================
# Diese Datei enthält 4x4-Matrizen, die im 3D-Rendering verwendet werden.
# Eine Matrix beschreibt eine Transformation im Raum:
# - Verschiebung (Translation)
# - Drehung (Rotation)
# - Skalierung (Scaling)
# - Kameraposition / Blickrichtung (LookAt)
# - Projektion auf den Bildschirm (Orthogonal / Perspektive)
#
# Diese Matrizen werden später mit Vektoren bzw. Punktkoordinaten
# multipliziert, damit Objekte im 3D-Raum korrekt dargestellt werden.

# Gibt die Einheitsmatrix zurück.
# Das ist eine Matrix, die nichts verändert.
def mat4_identity():
    return np.identity(4, dtype=np.float32)

# Erzeugt eine Translationsmatrix.
# Ein Punkt (x, y, z) wird um die übergebenen Werte verschoben.
# In der Matrix werden die Werte in die letzte Spalte geschrieben.
def mat4_translate(x, y, z):
    m = np.identity(4, dtype=np.float32)
    m[0,3], m[1,3], m[2,3] = x, y, z
    return m

# Erzeugt eine Skalierungsmatrix.
# Die x-, y- und z-Koordinaten werden mit den gegebenen Faktoren multipliziert.
def mat4_scale(sx, sy, sz):
    m = np.identity(4, dtype=np.float32)
    m[0,0], m[1,1], m[2,2] = sx, sy, sz
    return m

# Erzeugt eine Rotation um die Y-Achse.
# 'a' ist der Winkel in Radiant.
# cos(a) und sin(a) werden verwendet, um den Punkt um die Y-Achse zu drehen.
def mat4_rotate_y(a):
    c, s = math.cos(a), math.sin(a)
    m = np.identity(4, dtype=np.float32)
    m[0,0], m[0,2] = c, -s
    m[2,0], m[2,2] = s, c
    return m

# Erzeugt eine Rotation um die X-Achse.
# Analog zu mat4_rotate_y(), nur für die X-Richtung.
def mat4_rotate_x(a):
    c, s = math.cos(a), math.sin(a)
    m = np.identity(4, dtype=np.float32)
    m[1,1], m[1,2] = c, -s
    m[2,1], m[2,2] = s, c
    return m

# Erzeugt eine orthografische Projektionsmatrix.
# 'l, r, b, t' = linke, rechte, untere, obere Grenze des Sichtbereichs
# 'n, f' = Nah- und Fernbereich
# Diese Matrix macht Objekte ohne Perspektivverzerrung sichtbar.
# Wird oft für 2D-UI oder technische Ansichten verwendet.
def mat4_ortho(l, r, b, t, n, f):
    m = np.identity(4, dtype=np.float32)
    m[0,0] = 2.0/(r-l); m[1,1] = 2.0/(t-b); m[2,2] = -2.0/(f-n)
    m[0,3] = -(r+l)/(r-l); m[1,3] = -(t+b)/(t-b); m[2,3] = -(f+n)/(f-n)
    return m

# Erzeugt eine LookAt-Kamera-Matrix.
# 'eye' = Position der Kamera
# 'target' = Punkt, auf den die Kamera schaut
# 'up' = Richtung nach oben
#
# Die Funktion berechnet:
# 1. Blickrichtung f = target - eye
# 2. Seitliche Achse s = cross(f, up)
# 3. Hochrichtung u = cross(s, f)
#
# Danach wird eine Matrix aufgebaut, die die Welt aus der Kameraperspektive
# transformiert. Dadurch sieht man die Szene aus dem Blickwinkel der Kamera.
def mat4_look_at(eye, target, up):
    eye = np.array(eye, dtype=np.float32)
    target = np.array(target, dtype=np.float32)
    up = np.array(up, dtype=np.float32)
    f = target - eye; f /= np.linalg.norm(f)
    s = np.cross(f, up); s /= np.linalg.norm(s)
    u = np.cross(s, f)
    m = np.identity(4, dtype=np.float32)
    m[0,0]=s[0]; m[0,1]=s[1]; m[0,2]=s[2]; m[0,3]=-np.dot(s,eye)
    m[1,0]=u[0]; m[1,1]=u[1]; m[1,2]=u[2]; m[1,3]=-np.dot(u,eye)
    m[2,0]=-f[0]; m[2,1]=-f[1]; m[2,2]=-f[2]; m[2,3]=np.dot(f,eye)
    return m

# Multipliziert zwei 4x4-Matrizen miteinander.
# Das ist wichtig, wenn mehrere Transformationen kombiniert werden müssen.
# Beispiel: Objekt drehen + verschieben + Kamera anwenden.
# Die Reihenfolge ist wichtig, da Matrixmultiplikation nicht kommutativ ist.
def mat4_mul(a, b):
    return np.dot(a, b).astype(np.float32)