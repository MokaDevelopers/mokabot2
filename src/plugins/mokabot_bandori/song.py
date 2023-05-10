from .BandoriChartRender.model import DifficultyInt


def parse_song_difficulty(args: str) -> tuple[int, DifficultyInt]:
    difficulty_suffixes = {
        'ez': DifficultyInt.Easy,
        'nm': DifficultyInt.Normal,
        'hd': DifficultyInt.Hard,
        'ex': DifficultyInt.Expert,
        'sp': DifficultyInt.Special,
        'easy': DifficultyInt.Easy,
        'normal': DifficultyInt.Normal,
        'hard': DifficultyInt.Hard,
        'expert': DifficultyInt.Expert,
        'special': DifficultyInt.Special
    }

    for suffix, difficulty in difficulty_suffixes.items():
        if args.endswith(suffix):
            return int(args.removesuffix(suffix).strip()), difficulty

    return int(args), DifficultyInt.Expert
