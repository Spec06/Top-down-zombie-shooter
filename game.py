import pygame as pg
from pygame.locals import *
from OpenGL.GL import *
import numpy as np

# --- Constants ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
PLAYER_SPEED = 5.0

# --- Player Class (Draft) ---
class Player:
    def __init__(self, x, y):
        """Initializes the player's state."""
        self.position = np.array([x, y, 0.0], dtype=float) # (x, y, z) in world space
        self.rotation = 0.0  # Rotation around Y-axis (yaw) in degrees
        self.health = 100
        self.mesh_size = 0.5 # Size of the cubic player model

    def update(self, dt):
        """Handle movement and rotation based on input."""
        keys = pg.key.get_pressed()

        # Calculate forward vector based on current rotation
        rotation_rad = np.radians(self.rotation)
        forward_vector = np.array([
            np.cos(rotation_rad),
            np.sin(rotation_rad),
            0.0
        ])

        movement = np.array([0.0, 0.0, 0.0], dtype=float)

        # Directional input (W/S for forward/backward, A/D for strafe left/right)
        if keys[K_w]:
            movement += forward_vector
        if keys[K_s]:
            movement -= forward_vector
        if keys[K_a]: # Strafe Left
            # Vector perpendicular to the forward vector (-sin, cos, 0)
            strafe_left = np.array([-np.sin(rotation_rad), np.cos(rotation_rad), 0.0])
            movement += strafe_left
        if keys[K_d]: # Strafe Right
            strafe_right = np.array([np.sin(rotation_rad), -np.cos(rotation_rad), 0.0])
            movement += strafe_right

        # Normalize movement vector (to prevent faster diagonal movement)
        if np.linalg.norm(movement) > 0:
            movement = movement / np.linalg.norm(movement)

            # Apply speed and delta time to movement
            self.position += movement * PLAYER_SPEED * dt

    def rotate(self, dt):
        """Handle continuous rotation input."""
        keys = pg.key.get_pressed()
        rotation_speed = 150.0 * dt # Degrees per second
        if keys[K_LEFT]:
            self.rotation -= rotation_speed
        if keys[K_RIGHT]:
            self.rotation += rotation_speed

# --- Camera Class (Draft) ---
class Camera:
    def __init__(self, target_x, target_y, distance=8.0):
        """Camera orbits around the target player position."""
        self.target = np.array([target_x, target_y, 0.0], dtype=float)
        self.distance = distance
        self.pitch = 30  # Vertical angle (up/down tilt)
        self.yaw = 0   # Horizontal angle (left/right rotation around Y-axis)

    def update(self, player):
        """Updates the camera based on current player position/rotation."""
        self.target = np.array([player.position[0], player.position[1], 0.0]) # Look at X, Y of player
        # Keep yaw aligned with player rotation for simplicity
        self.yaw = player.rotation

    def get_view_matrix(self):
        """Calculates the ModelView matrix (the transformation from world to camera space)."""

        # Convert angles to radians
        pitch_rad = np.radians(self.pitch)
        yaw_rad = np.radians(self.yaw)
        distance = self.distance

        # Calculate spherical coordinates translated into Cartesian offsets
        # X: distance * cos(pitch) * sin(yaw)
        # Y: distance * sin(pitch)
        # Z: distance * cos(pitch) * cos(yaw)

        view_x = distance * np.cos(pitch_rad) * np.sin(yaw_rad)
        view_y = distance * np.sin(pitch_rad)
        view_z = distance * np.cos(pitch_rad) * np.cos(yaw_rad)

        # The camera position is relative to the target
        camera_pos = np.array([view_x, view_y, view_z])
        target_pos = self.target

        # View Matrix components (LookAt implementation: [Rotations] * [Translation])

        # Note: OpenGL uses a column-major matrix representation internally,
        # but we often define it row-wise when setting uniforms/using numpy

        M = np.identity(4) # Start with Identity Matrix

        # 1. Rotation (Yaw and Pitch around the target)
        # Rotation about Y (Yaw)
        Ry = np.array([
            [np.cos(yaw_rad), 0, np.sin(yaw_rad), 0],
            [0, 1, 0, 0],
            [-np.sin(yaw_rad), 0, np.cos(yaw_rad), 0],
            [0, 0, 0, 1]
        ])

        # Rotation about X (Pitch) - Rotate around the *new* X axis after Yaw
        Rx = np.array([
            [1, 0, 0, 0],
            [0, np.cos(pitch_rad), -np.sin(pitch_rad), 0],
            [0, np.sin(pitch_rad), np.cos(pitch_rad), 0],
            [0, 0, 0, 1]
        ])

        # Combine Rotations (Order matters: Rotate Pitch then Yaw)
        R = Rx @ Ry

        # 2. Translation (Move the world opposite to where the camera is placed)
        # Since the view matrix transforms WORLD -> CAMERA, we translate by [-view_x, -view_y, -view_z]
        T = np.identity(4)
        T[0, 3] = -camera_pos[0] # Tx
        T[1, 3] = -camera_pos[1] # Ty
        T[2, 3] = -camera_pos[2] # Tz

        # Final View Matrix: T * R (applied right-to-left)
        return T @ R

# --- Drawing Functions ---

def draw_cube(location=(0.0, 0.0, 0.0), size=1.0):
    """Draws a simple colored cube at the specified location."""
    glPushMatrix()
    glTranslatef(location[0], location[1], location[2])
    glScalef(size, size, size)

    # Define vertices for a unit-sized cube centered at (0,0,0)
    vertices = [
        # Front face (+Z)
        (-0.5, -0.5, 0.5),  (0.5, -0.5, 0.5),  (0.5, 0.5, 0.5),  (-0.5, 0.5, 0.5),
        # Back face (-Z)
        (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (-0.5, 0.5, -0.5),
        # Top face (+Y)
        (-0.5, 0.5, 0.5),  (0.5, 0.5, 0.5),  (0.5, 0.5, -0.5), (-0.5, 0.5, -0.5),
        # Bottom face (-Y)
        (-0.5, -0.5, 0.5), (0.5, -0.5, 0.5),  (0.5, -0.5, -0.5), (-0.5, -0.5, -0.5),
        # Right face (+X)
        (0.5, -0.5, 0.5),  (0.5, 0.5, 0.5),  (0.5, 0.5, -0.5), (0.5, -0.5, -0.5),
        # Left face (-X)
        (-0.5, -0.5, 0.5), (-0.5, 0.5, 0.5),  (-0.5, 0.5, -0.5), (-0.5, -0.5, -0.5)
    ]

    # Define colors (R, G, B) for each vertex
    colors = [
        (1.0, 0.0, 0.0),  # Red: Front
        (0.0, 1.0, 0.0),  # Green: Back
        (0.0, 0.0, 1.0),  # Blue: Top
        (1.0, 1.0, 0.0),  # Yellow: Bottom (Coin/Loot color)
        (0.5, 0.5, 0.5),  # Gray: Right
        (0.8, 0.0, 0.8)   # Magenta: Left
    ]

    # Draw each face using GL_QUADS
    glBegin(GL_QUADS)

    # Front Face (Red)
    glColor3fv(colors[0])
    glVertex3fv(vertices[0])
    glVertex3fv(vertices[1])
    glVertex3fv(vertices[2])
    glVertex3fv(vertices[3])

    # Back Face (Green)
    glColor3fv(colors[1])
    glVertex3fv(vertices[4])
    glVertex3fv(vertices[5])
    glVertex3fv(vertices[6])
    glVertex3fv(vertices[7])

    # Top Face (Blue)
    glColor3fv(colors[2])
    glVertex3fv(vertices[8])
    glVertex3fv(vertices[9])
    glVertex3fv(vertices[10])
    glVertex3fv(vertices[11])

    # Bottom Face (Yellow - Represents the ground/base level)
    glColor3fv(colors[3])
    glVertex3fv(vertices[12]) # Reusing vertices list layout for simplicity: this is actually vertex index 0, but drawn as bottom
    glVertex3fv(vertices[13])
    glVertex3fv(vertices[14])
    glVertex3fv(vertices[15])

    # Right Face (Gray) - *Note: Adjusted the indices to match a contiguous list of 24 vertices*
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_COLOR_ARRAY)
    glVertexPointer(3, GL_FLOAT, 0, np.array(vertices))
    glColorPointer(3, GL_FLOAT, 0, np.array(colors))

    # Redrawing using array commands for better efficiency:
    glBegin(GL_QUADS)

    # Front face (Red)
    glColor3f(*colors[0])
    glVertex3f(*vertices[2*0:2*0+3]) # (-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5)

    # Back face (Green)
    glColor3f(*colors[1])
    glVertex3f(*vertices[2*1+0:2*1+3]) # (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (0.5, 0.5, -0.5)

    # Top face (Blue)
    glColor3f(*colors[2])
    glVertex3f(*vertices[2*2+0:2*2+3]) # (-0.5, 0.5, 0.5), (0.5, 0.5, 0.5), (0.5, 0.5, -0.5)

    # Bottom face (Yellow/Ground Plate)
    glColor3f(*colors[3])
    glVertex3f(*vertices[2*3+0:2*3+3]) # (-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (0.5, -0.5, -0.5)

    # Right face (Gray)
    glColor3f(*colors[4])
    glVertex3f(0.5, -0.5, 0.5) # Note: Need to use explicit vertex coordinates here for clarity when mixing methods
    glVertex3f(0.5, 0.5, 0.5)
    glVertex3f(0.5, 0.5, -0.5)
    glVertex3f(0.5, -0.5, -0.5)

    # Left face (Magenta)
    glColor3f(*colors[5])
    glVertex3f(-0.5, -0.5, 0.5)
    glVertex3f(-0.5, 0.5, 0.5)
    glVertex3f(-0.5, 0.5, -0.5)
    glVertex3f(-0.5, -0.5, -0.5)

    glEnd()
    glPopMatrix()

# --- Main Game Loop Function ---
def game_loop():
    """Initializes and runs the main Pygame loop."""
    pg.init()
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), DOUBLEBUF | OPENGL)
    pg.display.set_caption("Pygame Top-Down Looter Shooter [3D]")

    # --- Game Objects Initialization ---
    player = Player(x=0.0, y=1.0) # Start player slightly above the ground (y=0.5 to 1.0 for cube center)
    camera = Camera(target_x=player.position[0], target_y=player.position[1])

    # --- Clock and Timing ---
    clock = pg.time.Clock()

    running = True
    while running:
        # Calculate Delta Time (Time elapsed since last frame in seconds)
        dt = clock.tick(FPS) / 1000.0

        # --- Event Handling ---
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    running = False
                # Future hook for shooting, abilities, etc.

        # --- Update Logic ---
        player.rotate(dt) # Player rotation happens continuously even if no directional key is held down (for smoother turn)
        player.update(dt)
        camera.update(player)

        # --- Drawing Phase ---

        # Set up OpenGL state for each frame
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST) # Crucial: Ensures closer objects obscure farther ones

        # Setup basic lighting (Phong shading foundation)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        light_position = [1.0, 1.0, 1.0, 0.0] # Directional key point at infinity
        glLightfv(GL_LIGHT0, GL_POSITION, light_position)
        glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2)) # Ambient light level
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (1.0, 1.0, 1.0))  # Brightness of the directional component

        # Set background color (Sky Blue)
        glClearColor(0.5, 0.7, 1.0, 1.0)
        glEnable(GL_COLOR_MATERIAL) # Allows colors set via glColor3fv to be used by OpenGL lighting

        # --- Apply Camera/View Transformation ---
        glLoadIdentity() # Reset the ModelView matrix stack
        view_matrix = camera.get_view_matrix()
        glMultMatrixf(view_matrix.flatten())

        # --- Draw Game World Elements ---

        # 1. The Ground / Level Base (A large cube/plate at height -0.5)
        # We use a larger box to simulate an open plane or initial map area.
        draw_cube(location=(0.0, -0.5, 0.0), size=30.0)

        # 2. Player Model (Drawn at the player's world position/Y-level)
        glPushMatrix()
        glTranslatef(player.position[0], player.position[1] + 0.5, player.position[2]) # Adjust Y to center cube on ground level
        # Optional: Rotate model to match character yaw/rotation
        glRotatef(player.rotation, 0, 1, 0)
        draw_cube(location=(0.0, 0.0, 0.0), size=player.mesh_size)
        glPopMatrix()

        # Optional: Draw a Loot/Resource Node (a smaller cube somewhere else)
        loot_pos = np.array([5.0, 0.0, -3.0])
        draw_cube(location=(loot_pos[0], loot_pos[1] + 0.5, loot_pos[2]), size=0.7, color=(1.0, 1.0, 0.0)) # Gold/Yellow

        # --- Flip the display to show what was rendered ---
        pg.display.flip()

    # Quit Pygame
    pg.quit()

if __name__ == "__main__":
    print("--- Starting Top-Down Looter Shooter Implementation in Pygame (3D) ---")
    game_loop()
    print("\nGame loop terminated successfully.")