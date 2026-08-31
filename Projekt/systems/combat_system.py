"""Combat system: applies attacks to targets using components."""
import math


class CombatSystem:
    def __init__(self, world=None):
        self.world = world or []

    @staticmethod
    def circle_collision(x1, z1, r1, x2, z2, r2):
        dx = x2 - x1
        dz = z2 - z1
        distance = math.hypot(dx, dz)
        return distance < (r1 + r2)

    def perform_melee(self, attacker_entity, attack_comp, targets=None):
        targets = targets if targets is not None else self.world
        hits = []

        ax, _, az = attacker_entity.position
        for target in targets:
            if target is attacker_entity:
                continue
            tx, _, tz = target.position
            if self.circle_collision(ax, az, attack_comp.range, tx, tz, getattr(target, 'radius', 0.0)):
                health = target.get('health') if hasattr(target, 'get') else None
                if health is not None:
                    health.take_damage(attack_comp.damage)
                    hits.append(target)
        return hits

    def handle_projectiles(self, projectiles, targets):
        remaining = []
        for projectile in projectiles:
            px, _, pz = projectile.position
            hit_target = False

            for target in targets:
                tx, _, tz = target.position
                if self.circle_collision(px, pz, getattr(projectile, 'radius', 0.0), tx, tz, getattr(target, 'radius', 0.0)):
                    health = target.get('health') if hasattr(target, 'get') else None
                    if health is not None:
                        health.take_damage(getattr(projectile, 'damage', 1))
                        if hasattr(target, 'alive'):
                            target.alive = not target.is_dead()
                    hit_target = True
                    break

            if not hit_target:
                remaining.append(projectile)

        return remaining


