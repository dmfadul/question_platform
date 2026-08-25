def shuffle_disciplines(disciplines: list, seed: int) -> list:
    import random
    
    if seed == 0:
        return disciplines

    rng = random.Random(seed)
    shuffled = disciplines.copy()
    rng.shuffle(shuffled)
    return shuffled