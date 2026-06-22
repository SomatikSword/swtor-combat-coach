from analyzers.dot_analysis import analyze_dot_uptime
from rotations.config import ROTATION_CONFIG


def count_ability_uses(encounter_lines, player_name, ability_name):
    count = 0

    for line in encounter_lines:
        if (
            f"@{player_name}#" in line
            and ability_name in line
            and "AbilityActivate" in line
        ):
            count += 1

    return count


def analyze_universal(
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
            "конфиг не найден.\n"
        )

    config = ROTATION_CONFIG[key]

    result = "\n**Ротационный анализ:**\n"

    dots = config.get("dots", [])
    cooldowns = config.get("cooldowns", [])
    core_abilities = config.get("core_abilities", [])

    # ---------------------------------------------------
    # DoT / effect uptime
    # ---------------------------------------------------
    if dots:
        result += "\n**DoT / effect uptime:**\n"

        for dot in dots:
            uptime = analyze_dot_uptime(
                encounter_lines,
                player_name,
                dot
            )

            if uptime is None:
                result += f"• {dot}: нет данных\n"
                continue

            result += f"• {dot}: {uptime}%\n"

            if uptime < 85:
                result += f"  ⚠ Низкий uptime {dot}\n"

            elif uptime < 95:
                result += f"  ⚠ Можно улучшить uptime {dot}\n"

    else:
        result += "\n**DoT / effect uptime:**\n"
        result += "• У этого спека нет обязательных DoT в базовом конфиге.\n"

    # ---------------------------------------------------
    # Cooldown usage
    # ---------------------------------------------------
    result += "\n**Cooldown usage:**\n"

    if cooldowns:
        for cooldown in cooldowns:
            uses = count_ability_uses(
                encounter_lines,
                player_name,
                cooldown
            )

            result += f"• {cooldown}: {uses}\n"

            if uses == 0:
                result += f"  ⚠ {cooldown} не найден в бою\n"
    else:
        result += "• Нет cooldown-списка для этого спека.\n"

    # ---------------------------------------------------
    # Core ability usage
    # ---------------------------------------------------
    result += "\n**Core ability usage:**\n"

    if core_abilities:
        for ability in core_abilities:
            uses = count_ability_uses(
                encounter_lines,
                player_name,
                ability
            )

            result += f"• {ability}: {uses}\n"

            if uses == 0:
                result += f"  ⚠ {ability} не найден в бою\n"
    else:
        result += "• Нет core ability списка для этого спека.\n"

    return result