"""Collectible drops created when a zombie dies."""

try:
    from entities.entity import Entity
except ModuleNotFoundError:  # package import
    from Projekt.entities.entity import Entity


class LootItem(Entity):
    def __init__(self, x: float, z: float, loot_type: str, amount: int = 1) -> None:
        super().__init__(position=(float(x), 0.25, float(z)), radius=0.28)
        self.loot_type = loot_type
        self.amount = amount

    def collect(self, player, ammo: dict, magazine: dict, weapons: dict) -> bool:
        if self.loot_type == "medkit":
            health = getattr(player, "health", None)
            if health is None or health.current >= health.max_hp:
                return False
            health.heal(self.amount)
        elif self.loot_type == "stamina":
            player.stamina = min(player.max_stamina, player.stamina + self.amount)
        elif self.loot_type in ammo:
            ammo[self.loot_type] += self.amount
        elif self.loot_type in weapons:
            magazine[self.loot_type] = weapons[self.loot_type]["magazine"]
        else:
            return False
        return True