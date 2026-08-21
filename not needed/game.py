import pygame as pg # Using the robust Community Edition import
from pygame.locals import *
from OpenGL.GL import *
import numpy as np

# ... (rest of the code) ...
# --- Constants ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
PLAYER_SPEED = 5.0
PLAYER_RADIUS = 0.3 # Player Collision Radius

# --- Global Lists (The Level Manager) ---
WORLD_OBJECTS = [
    {'position': np.array([5.0, 0.0, -3.0]), 'radius': 0.3}, # The Gold Loot Node
]

# --- Projectile Class ---
class Projectile:
    """Represents a fired bullet/tracer."""
    def __init__(self, start_pos, rotation):
        self.position = np.copy(start_pos)
        self.radius = 0.15
        self.speed = 20.0
        self.rotation = rotation
        self.velocity = self._calculate_velocity()

    def _calculate_velocity(self):
        """Calculates vector based on player's current yaw (rotation)."""
        rotation_rad = np.radians(self.rotation)
        vx = np.cos(rotation_rad) * self.speed
        vz = np.sin(rotation_rad) * self.speed
        vy = 0.0
        return np.array([vx, vy, vz], dtype=float)

    def update(self, dt):
        """Updates projectile position based on velocity."""
        self.position += self.velocity * dt

# --- Player Class (The Hero) ---
class Player:
    """Represents the controllable character and handles movement/collision."""
    def __init__(self, x, y):
        self.position = np.array([x, y, 0.0], dtype=float)
        self.rotation = 0.0  # Yaw (horizontal turn)
        self.health = 100
        self.mesh_size = 0.5

    def update(self, dt):
        """Movement handling and collision checks against static world geometry."""
        keys = pg.key.get_pressed()
        rotation_rad = np.radians(self.rotation)
        forward_vector = np.array([np.cos(rotation_rad), np.sin(rotation_rad), 0.0])
        movement = np.array([0.0, 0.0, 0.0], dtype=float)

        if keys[K_w]: movement += forward_vector
        if keys[K_s]: movement -= forward_vector
        elif keys[K_a]: # Strafe Left
            strafe_left = np.array([-np.sin(rotation_rad), np.cos(rotation_rad), 0.0])
            movement += strafe_left
        elif keys[K_d]: # Strafe Right
            strafe_right = np.array([np.sin(rotation_rad), -np.cos(rotation_rad), 0.0])
            movement += strafe_right

        if np.linalg.norm(movement) > 0:
            movement = movement / np.linalg.norm(movement)
            new_position = self.position + movement * PLAYER_SPEED * dt

            collision_occurred = False
            for obj in WORLD_OBJECTS:
                obj_pos = obj['position']
                obj_radius = obj['radius']
                distance = np.linalg.norm(new_position - obj_pos)

                if distance < (PLAYER_RADIUS + obj_radius):
                    collision_occurred = True
                    # Collision Response: Calculate overlap and push player out
                    direction_vector = new_position - obj_pos
                    overlap = (PLAYER_RADIUS + obj_radius) - distance
                    self.position += (direction_vector / np.linalg.norm(direction_vector)) * overlap
                    break

            return collision_occurred
        return False

    def rotate(self, dt):
        """Handle continuous rotation input."""
        keys = pg.key.get_pressed()
        rotation_speed = 150.0 * dt
        if keys[K_LEFT]: self.rotation -= rotation_speed
        elif keys[K_RIGHT]: self.rotation += rotation_speed

# --- Camera Class (The Observer) ---
class Camera:
    def __init__(self, target_x, target_y, distance=8.0):
        self.target = np.array([target_x, target_y, 0.0], dtype=float)
        self.distance = distance
        self.pitch = 30  # Vertical tilt
        self.yaw = 0

    def update(self, player):
        self.target = np.array([player.position[0], player.position[1], 0.0])
        self.yaw = player.rotation

    def get_view_matrix(self):
        pitch_rad = np.radians(self.pitch)
        yaw_rad = np.radians(self.yaw)
        distance = self.distance

        # Calculate offsets
        view_x = distance * np.cos(pitch_rad) * np.sin(yaw_rad)
        view_y = distance * np.sin(pitch_rad)
        view_z = distance * np.cos(pitch_rad) * np.cos(yaw_rad)

        # Rotation Matrices (Pitch then Yaw)
        Ry = np.array([
            [np.cos(yaw_rad), 0, np.sin(yaw_rad), 0], [0, 1, 0, 0], [-np.sin(yaw_rad), 0, np.cos(yaw_rad), 0], [0, 0, 0, 1]
        ])

        Rx = np.array([
            [1, 0, 0, 0], [0, np.cos(pitch_rad), -np.sin(pitch_rad), 0], [0, np.sin(pitch_rad), np.cos(pitch_rad), 0], [0, 0, 0, 1]
        ])

        R = Rx @ Ry

        # Translation Matrix: T * R
        T = np.identity(4)
        T[0, 3] = -view_x
        T[1, 3] = -view_y
        T[2, 3] = -view_z

        return T @ R

# --- Drawing Functions (The Renderer) ---
def draw_cube(location=(0.0, 0.0, 0.0), size=1.0, color=(1.0, 1.0, 1.0)):
    """Draws a simple colored cube at the specified location."""
    glPushMatrix()
    glTranslatef(location[0], location[1], location[2])
    glScalef(size, size, size)

    vertices = [
        # Front (Indices 0-3), Back (4-7), Top (8-11), Bottom (12-15), Right (16-19), Left (20-23)
        (-0.5, -0.5,  0.5), ( 0.5, -0.5,  0.5), ( 0.5,  0.5,  0.5), (-0.5,  0.5,  0.5), # Front
        (-0.5, -0.5, -0.5), ( 0.5, -0.5, -0.5), ( 0.5,  0.5, -0.5), (-0.5,  0.5, -0.5), # Back
        (-0.5,  0.5,  0.5), ( 0.5,  0.5,  0.5), ( 0.5,  0.5, -0.5), (-0.5,  0.5, -0.5), # Top
        (-0.5, -0.5, -0.5), ( 0.5, -0.5, -0.5), ( 0.5, -0.5,  0.5), (-0.5, -0.5,  0.5), # Bottom
        ( 0.5,  0.5,  0.5), ( 0.5, -0.5,  0.5), ( 0.5, -0.5, -0.5), ( 0.5,  0.5, -0.5), # Right
        (-0.5, -0.5,  0.5), (-0.5,  0.5,  0.5), (-0.5,  0.5, -0.5), (-0.5, -0.5, -0.5)  # Left
    ]

    glBegin(GL_QUADS)
    glColor3fv(color); glVertex3fv([vertices[i] for i in [0, 1, 2, 3]]) # Face 1: Front
    glColor3fv(color); glVertex3fv([vertices[i] for i in [4, 5, 6, 7]]) # Face 2: Back
    glColor3fv(color); glVertex3fv([vertices[i] for i in [8, 9, 10, 11]]) # Face 3: Top
    glColor3fv(color); glVertex3fv([vertices[i] for i in [12, 13, 14, 15]]) # Face 4: Bottom (Ground)
    glColor3fv(color); glVertex3fv([vertices[i] for i in [16, 17, 18, 19]]) # Face 5: Right
    glColor3fv(color); glVertex3fv([vertices[i] for i in [20, 21, 22, 23]]) # Face 6: Left
    glEnd()
    glPopMatrix()

def game_loop():
    """Initializes and runs the main Pygame loop."""
    pg.init()
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), DOUBLEBUF | OPENGL)
    pg.display.set_caption("Pygame Top-Down Looter Shooter [3D]")

    # --- Game Objects Initialization ---
    player = Player(x=0.0, y=1.0)
    camera = Camera(target_x=player.position[0], target_y=player.position[1])
    projectiles = []

    clock = pg.time.Clock()

    # --- Main Loop State ---
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        # --- Event Handling (Input) ---
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    running = False
                elif event.key == pg.K_SPACE:
                    new_proj = Projectile(player.position, player.rotation)
                    projectiles.append(new_proj)

        # --- Update Logic ---
        player_collision_occurred = player.update(dt)
        camera.update(player)

        # *** PROJECTILE UPDATE & COLLISION CHECKING (Loot Mechanic) ***
        projectiles_to_remove = []
        for i, proj in enumerate(projectiles):
            proj.update(dt)
            hit_world_object = False
            for obj in WORLD_OBJECTS:
                obj_pos = obj['position']
                obj_radius = obj['radius']
                P_R = proj.radius
                distance = np.linalg.norm(proj.position - obj_pos)

                if distance < (P_R + obj_radius):
                    hit_world_object = True
                    WORLD_OBJECTS.remove(obj)
                    print(">> Loot Node successfully destroyed! COLLECTABLE ACQUIRED! <<")
                    break

            # Boundary check (+/- 50 units on XZ plane)
            is_out_of_bounds = abs(proj.position[0]) > 50 or abs(proj.position[2]) > 50

            if hit_world_object or is_out_of_bounds:
                projectiles_to_remove.append(i)

        # Remove projectiles cleanly
        for index in sorted(projectiles_to_remove, reverse=True):
            projectiles.pop(index)

        # --- Drawing Phase ---
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)

        # Lighting Setup
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        light_position = [1.5, 2.5, 1.5, 0.0]
        glLightfv(GL_LIGHT0, GL_POSITION, light_position)
        glLightfv(GL_LIGHT0, GL_AMBIENT, (0.15, 0.15, 0.15))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.9, 0.9, 0.9))

        glClearColor(0.5, 0.7, 1.0, 1.0) # Sky Blue background
        glEnable(GL_COLOR_MATERIAL)

        # --- Apply Camera/View Transformation & Draw Sequence ---
        glLoadIdentity()
        view_matrix = camera.get_view_matrix()
        glMultMatrixf(view_matrix.flatten())

        # 1. Ground / Level Base (Green)
        draw_cube(location=(0.0, -0.5, 0.0), size=30.0, color=(0.2, 0.7, 0.2))

        # 2. Player Model (Red)
        glPushMatrix()
        glTranslatef(player.position[0], player.position[1] + player.mesh_size/2, player.position[2])
        glRotatef(player.rotation, 0, 1, 0)
        draw_cube(location=(0.0, 0.0, 0.0), size=player.mesh_size, color=(0.8, 0.2, 0.2)) # Player Mesh Color
        glPopMatrix()

        # 3. Render Projectiles (White bullets)
        for proj in projectiles:
            proj_color = (1.0, 1.0, 1.0)
            draw_cube(location=(proj.position[0], proj.position[1] + proj.radius/2, proj.position[2]), size=proj.radius*2, color=proj_color)

        # 4. Render Loot Nodes (Gold targets)
        for obj in WORLD_OBJECTS:
            loot_pos = obj['position']
            draw_cube(location=(loot_pos[0], loot_pos[1] + obj['radius']/2, loot_pos[2]), size=obj['radius']*2, color=(1.0, 1.0, 0.5))

        pg.display.flip()

    pg.quit()

if __name__ == "__main__":
    game_loop()