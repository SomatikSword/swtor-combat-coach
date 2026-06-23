from services.rotation_engine import count_ability_activations


def analyze_assassin_deception(
    player_name,
    encounter_lines,
    player_class,
    discipline
):
    voltaic_slash = count_ability_activations(
        encounter_lines,
        player_name,
        "Voltaic Slash"
    )

    maul = count_ability_activations(
        encounter_lines,
        player_name,
        "Maul"
    )

    ball_lightning = count_ability_activations(
        encounter_lines,
        player_name,
        "Ball Lightning"
    )

    discharge = count_ability_activations(
        encounter_lines,
        player_name,
        "Discharge"
    )

    recklessness = count_ability_activations(
        encounter_lines,
        player_name,
        "Recklessness"
    )

    result = "\n**Assassin / Deception advanced analysis:**\n\n"

    result += "**Core usage:**\n"
    result += f"• Voltaic Slash: {voltaic_slash}\n"
    result += f"• Maul: {maul}\n"
    result += f"• Ball Lightning: {ball_lightning}\n"
    result += f"• Discharge: {discharge}\n"
    result += f"• Recklessness: {recklessness}\n"

    result += "\n**Что будет добавлено дальше:**\n"
    result += "• Duplicity proc usage\n"
    result += "• потерянные / переписанные проки Maul\n"
    result += "• Static Charge overcap\n"
    result += "• Recklessness charge usage\n"
    result += "• estimated Force overcap\n"

    result += "\n"

    return result