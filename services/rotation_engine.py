from rotations.config import ROTATION_CONFIG
from rotations.universal_rotation import analyze_universal


def analyze_rotation(
    player_name,
    encounter_lines,
    player_class,
    discipline
):
    key = (
        player_class,
        discipline
    )

    if key not in ROTATION_CONFIG:
        return (
            "\n**Ротационный анализ:**\n"
            f"Для {player_class} / {discipline} "
            "подробная ротация пока не настроена.\n"
            "Базовый GCD / downtime анализ выше всё равно работает.\n"
        )

    return analyze_universal(
        player_name,
        encounter_lines,
        player_class,
        discipline
    )