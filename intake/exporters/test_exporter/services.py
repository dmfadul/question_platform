def _shuffle_disciplines(disciplines: list, seed: int) -> list:
    import random

    seed = abs(seed)
    
    if seed in (0, 1):
        return disciplines

    rng = random.Random(seed)
    shuffled = disciplines.copy()
    rng.shuffle(shuffled)
    return shuffled