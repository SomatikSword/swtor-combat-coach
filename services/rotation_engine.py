import re

from analyzers.dot_analysis import analyze_dot_uptime
from rotations.config import ROTATION_CONFIG


def clean_log_name(value: str) -> str:
    if not value:
        return ""

    return value.split("{", 1)[0].strip()


def normalize_ability_name(value: str) -> str:
    value = clean_log_name(value)
    value = value.lower()
    value = re.sub(r"[^a-z0-9' ]+", " ", value)
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def get_log_blocks(line: str) -> list[str]:
    return re.findall(r"\[(.*?)\]", line)


def is_player_source(line: str, player_name: str) -> bool:
    blocks = get_log_blocks(line)

    if len(blocks) < 2:
        return False

    source_block = blocks[1]

    return f"@{player_name}#" in source_block


def get_ability_from_line(line: str) -> str:
    blocks = get_log_blocks(line)

    if len(blocks) < 5:
        return ""

    ability_block = blocks[3]

    return clean_log_name(ability_block)


def is_ability_activate_line(line: str) -> bool:
    blocks = get_log_blocks(line)

    if len(blocks) < 5:
        return False

    event_block = blocks[4]

    return "AbilityActivate" in event_block


def count_ability_activations(encounter_lines, player_name: str, ability_name: str) -> int:
    target_ability = normalize_ability_name(ability_name)

    count = 0

    for line in encounter_lines:
        if not is_player_source(line, player_name):
            continue

        if not is_ability_activate_line(line):
            continue

        used_ability = get_ability_from_line(line)

        if normalize_ability_name(used_ability) == target_ability:
            count += 1

    return count


def get_rotation_config(player_class: str, discipline: str):
    key = (player_class, discipline)

    return ROTATION_CONFIG.get(key)


def analyze_rotation(player_name, encounter_lines, player_class, discipline):
    config = get_rotation_config(player_class, discipline)

    if not config:
        return ""

    result = "\n**Rotation analysis:**\n\n"

    # -----------------------------
    # DoT / effect uptime
    # -----------------------------
    dots = config.get("dots", [])

    if dots:
        result += "**DoT / effect uptime:**\n"

        for dot in dots:
            uptime = analyze_dot_uptime(
                encounter_lines,
                player_name,
                dot
            )

            if uptime is None:
                result += f"• {dot}: 0%\n"
            else:
                result += f"• {dot}: {uptime}%\n"

        result += "\n"

    # -----------------------------
    # Cooldown usage
    # -----------------------------
    cooldowns = config.get("cooldowns", [])

    if cooldowns:
        result += "**Cooldown usage:**\n"

        for ability in cooldowns:
            uses = count_ability_activations(
                encounter_lines,
                player_name,
                ability
            )

            result += f"• {ability}: {uses}\n"

        result += "\n"

    # -----------------------------
    # Core ability usage
    # -----------------------------
    core_abilities = config.get("core_abilities", [])

    if core_abilities:
        result += "**Core ability usage:**\n"

        for ability in core_abilities:
            uses = count_ability_activations(
                encounter_lines,
                player_name,
                ability
            )

            result += f"• {ability}: {uses}\n"

        result += "\n"

    return result

# ---------------------------------------------------
# Ability activation parser
# Used by discipline-specific analyzers
# ---------------------------------------------------
import re


def clean_log_name(value: str) -> str:
    if not value:
        return ""

    return value.split("{", 1)[0].strip()


def normalize_ability_name(value: str) -> str:
    value = clean_log_name(value)
    value = value.lower()
    value = re.sub(r"[^a-z0-9' ]+", " ", value)
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def get_log_blocks(line: str) -> list[str]:
    return re.findall(r"\[(.*?)\]", line)


def is_player_source(line: str, player_name: str) -> bool:
    blocks = get_log_blocks(line)

    if len(blocks) < 2:
        return False

    source_block = blocks[1]

    return f"@{player_name}#" in source_block


def get_ability_from_line(line: str) -> str:
    blocks = get_log_blocks(line)

    if len(blocks) < 5:
        return ""

    ability_block = blocks[3]

    return clean_log_name(ability_block)


def is_ability_activate_line(line: str) -> bool:
    blocks = get_log_blocks(line)

    if len(blocks) < 5:
        return False

    event_block = blocks[4]

    return "AbilityActivate" in event_block


def count_ability_activations(encounter_lines, player_name: str, ability_name: str) -> int:
    target_ability = normalize_ability_name(ability_name)

    count = 0

    for line in encounter_lines:
        if not is_player_source(line, player_name):
            continue

        if not is_ability_activate_line(line):
            continue

        used_ability = get_ability_from_line(line)

        if normalize_ability_name(used_ability) == target_ability:
            count += 1

    return count