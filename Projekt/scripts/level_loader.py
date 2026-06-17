"""Level loader scaffold (placeholder)."""

def load_level(path):
    # read TMX or other map format; placeholder returns path
    with open(path, 'r', encoding='utf-8') as f:
        data = f.read()
    return data
