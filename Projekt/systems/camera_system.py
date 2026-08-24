import settings
import math
from entities.player import Player
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