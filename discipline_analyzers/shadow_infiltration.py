from services.rotation_engine import count_ability_activations


def analyze_shadow_infiltration(
    player_name,
    encounter_lines,
    player_class,
    discipline
):
    clairvoyant_strike = count_ability_activations(
        encounter_lines,
        player_name,
        "Clairvoyant Strike"
    )

    shadow_strike = count_ability_activations(
        encounter_lines,
        player_name,
        "Shadow Strike"
    )

    psychokinetic_blast = count_ability_activations(
        encounter_lines,
        player_name,
        "Psychokinetic Blast"
    )

    force_breach = count_ability_activations(
        encounter_lines,
        player_name,
        "Force Breach"
    )

    force_potency = count_ability_activations(
        encounter_lines,
        player_name,
        "Force Potency"
    )

    result = "\n**Shadow / Infiltration advanced analysis:**\n\n"

    result += "**Core usage:**\n"
    result += f"• Clairvoyant Strike: {clairvoyant_strike}\n"
    result += f"• Shadow Strike: {shadow_strike}\n"
    result += f"• Psychokinetic Blast: {psychokinetic_blast}\n"
    result += f"• Force Breach: {force_breach}\n"
    result += f"• Force Potency: {force_potency}\n"

    result += "\n**Что будет добавлено дальше:**\n"
    result += "• Infiltration Tactics proc usage\n"
    result += "• потерянные / переписанные проки Shadow Strike\n"
    result += "• Breaching Shadows overcap\n"
    result += "• Force Potency charge usage\n"
    result += "• estimated Force overcap\n"

    result += "\n"

    return result