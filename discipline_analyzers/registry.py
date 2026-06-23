from discipline_analyzers.base import normalize_key
from discipline_analyzers.shadow_infiltration import analyze_shadow_infiltration
from discipline_analyzers.assassin_deception import analyze_assassin_deception


ANALYZERS = {
    ("shadow", "infiltration"): analyze_shadow_infiltration,
    ("assassin", "deception"): analyze_assassin_deception,
}


def analyze_discipline_specific(
    player_name,
    encounter_lines,
    player_class,
    discipline
):
    key = normalize_key(player_class, discipline)

    analyzer = ANALYZERS.get(key)

    if not analyzer:
        return ""

    return analyzer(
        player_name=player_name,
        encounter_lines=encounter_lines,
        player_class=player_class,
        discipline=discipline,
    )