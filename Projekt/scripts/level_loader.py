"""Level loader scaffold (placeholder)."""
from pytmx.util_pygame import load_pygame

def get_player_spawn(tmx_path):
    tmx = load_pygame(tmx_path)
    for obj in tmx.objects:
        if obj.name == "player_spawn":
            return (obj.x, obj.y)
        
    map_w = tmx.width * tmx.tilewidth
    map_h = tmx.height * tmx.tileheight
    return (map_w // 2, map_h // 2)

def load_level(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = f.read()
    return data
