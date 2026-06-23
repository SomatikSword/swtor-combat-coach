def empty_report():
    return ""


def normalize_key(player_class: str, discipline: str):
    return (
        player_class.strip().lower(),
        discipline.strip().lower()
    )