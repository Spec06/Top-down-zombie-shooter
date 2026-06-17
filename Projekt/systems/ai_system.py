"""AI system scaffold."""

class AISystem:
    def update(self, entities, dt):
        # simple placeholder: iterate enemies and run behaviour
        for e in entities:
            if hasattr(e, 'ai') or e.get('ai'):
                # implement behaviour here
                pass
