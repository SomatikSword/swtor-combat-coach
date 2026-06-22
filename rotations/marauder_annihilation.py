import re
from analyzers.dot_analysis import analyze_dot_uptime


def analyze_marauder_annihilation(player_name, encounter_lines):

    result = "\nAnnihilation Marauder Analysis:\n\n"

    rupture_uptime = analyze_dot_uptime(
        encounter_lines,
        player_name,
        "Rupture"
    )

    if rupture_uptime is not None:
        result += f"Rupture uptime: {rupture_uptime}%\n"

        if rupture_uptime < 90:
            result += "⚠ Rupture uptime low (target 95%+)\n"

    berserk_count = 0

    for line in encounter_lines:
        if f"@{player_name}#" in line and "Berserk" in line and "AbilityActivate" in line:
            berserk_count += 1

    result += f"Berserk uses: {berserk_count}\n"

    if berserk_count < 3:
        result += "⚠ Low Berserk usage\n"

    return result