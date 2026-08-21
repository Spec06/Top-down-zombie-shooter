"""Combat system: applies attacks to targets using components."""
import math


class CombatSystem:
    def __init__(self, world=None):
        self.world = world

    @staticmethod
    def _distance_xz(a, b):
        """Distance in the XZ plane between two position-like sequences/arrays."""
        dx = float(a[0]) - float(b[0])
        dz = float(a[2]) - float(b[2]) if len(b) > 2 else float(b[1])
        return math.hypot(dx, dz)

    def perform_melee(self, attacker, attack_comp):
        if not attack_comp.can_attack():
            return []
        attack_comp.record_attack()
        hits = []
        if not hasattr(attacker, 'position'):
            return hits
        atk_pos = attacker.position
        for target in (self.world or []):
            if target is attacker:
                continue
            if not target.get('health'):
                continue
            if not hasattr(target, 'position'):
                continue
            # compute distance in XZ plane
            try:
                dist = self._distance_xz(atk_pos, target.position)
            except Exception:
                # fallback to 2D distance if shapes differ
                dist = math.hypot(atk_pos[0] - target.position[0], atk_pos[1] - target.position[1])

            if dist <= attack_comp.range:
                # apply damage
                target.get('health').apply_damage(attack_comp.damage)

                # apply knockback if target has movement component
                kb = getattr(attack_comp, 'knockback', 0)
                mv = target.get('movement')
                if kb and mv:
                    # direction from attacker -> target in XZ
                    dir_x = float(target.position[0]) - float(atk_pos[0])
                    dir_z = float(target.position[2]) - float(atk_pos[2]) if len(atk_pos) > 2 else float(target.position[1]) - float(atk_pos[1])
                    try:
                        mv.apply_knockback((dir_x, dir_z), kb)
                    except Exception:
                        pass

                hits.append(target)
        return hits
