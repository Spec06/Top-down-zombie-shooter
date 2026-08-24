import settings
from entities.player import Player
from OpenGL.GL import glTranslatef

class Camera:
    def __init__(self, target_entity, distance: float = settings.CAMERA_DISTANCE, pitch: float = settings.CAMERA_PITCH):
        self.target_entity = target_entity
        self.distance = distance
        self.pitch = pitch
        self.x = target_entity.x
        self.z = target_entity.z

    def update(self, player: Player) -> None:
        self.x = player.x
        self.z = player.z

    def apply(self) -> None:
        glTranslatef(-self.x, -self.z, 0.0)