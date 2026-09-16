try:
    import settings
except ModuleNotFoundError:  # package import
    from Projekt import settings
import math
try:
    from entities.player import Player
except ModuleNotFoundError:  # package import
    from Projekt.entities.player import Player
from OpenGL.GLU import gluLookAt

class Camera:
    def __init__(self, target_entity, distance: float = settings.CAMERA_DISTANCE, pitch: float = settings.CAMERA_PITCH):
        self.target_entity = target_entity
        self.distance = distance
        self.pitch = math.radians(pitch)
        self.yaw = 0.0
        self.camera_position = (0.0, 0.0, 0.0)

    def update(self, player: Player) -> None:
        target_y = getattr(player, "y", 0.0)
        camera_x = player.x + self.distance * math.cos(self.pitch) * math.sin(self.yaw)
        camera_y = target_y + self.distance * math.sin(self.pitch)
        camera_z = player.z + self.distance * math.cos(self.pitch) * math.cos(self.yaw)
        self.camera_position = (camera_x, camera_y, camera_z)

    def apply(self) -> None:
        camera_x, camera_y, camera_z = self.camera_position
        target_y = getattr(self.target_entity, "y", 0.0)
        gluLookAt(
            camera_x,
            camera_y,
            camera_z,
            self.target_entity.x,
            target_y,
            self.target_entity.z,
            0.0,
            1.0,
            0.0,
        )

    def world_from_screen(self, mouse_pos, width: int, height: int):
        """Map the screen cursor to the ground plane for top-down aiming."""
        world_width = 24.0
        world_height = world_width * height / max(1, width)
        x = self.target_entity.x + (mouse_pos[0] / width - 0.5) * world_width
        z = self.target_entity.z + (mouse_pos[1] / height - 0.5) * world_height
        return x, z