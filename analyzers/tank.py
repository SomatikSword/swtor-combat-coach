import re
from collections import defaultdict

from analyzers.combat_duration import get_combat_duration


TANK_CONFIG = {
    # Republic tanks
    ("Shadow", "Kinetic Combat"): {
        "taunts": [
            "Mind Control",
            "Mass Mind Control",
        ],
        "defensives": [
            "Kinetic Ward",
            "Deflection",
            "Battle Readiness",
            "Resilience",
            "Force Cloak",
            "Force Speed",
        ],
        "tracked_effects": [
            "Kinetic Ward",
            "Deflection",
            "Battle Readiness",
            "Resilience",
        ],
        "maintenance_effects": [
            "Kinetic Ward",
        ],
    },

    ("Guardian", "Defense"): {
        "taunts": [
            "Taunt",
            "Challenging Call",
        ],
        "defensives": [
            "Saber Ward",
            "Warding Call",
            "Enure",
            "Saber Reflect",
            "Focused Defense",
        ],
        "tracked_effects": [
            "Saber Ward",
            "Warding Call",
            "Enure",
            "Saber Reflect",
            "Focused Defense",
        ],
        "maintenance_effects": [],
    },

    ("Vanguard", "Shield Specialist"): {
        "taunts": [
            "Neural Jolt",
            "Sonic Round",
        ],
        "defensives": [
            "Reactive Shield",
            "Adrenaline Rush",
            "Riot Gas",
            "Hold the Line",
            "Power Yield",
        ],
        "tracked_effects": [
            "Reactive Shield",
            "Adrenaline Rush",
            "Riot Gas",
            "Hold the Line",
            "Power Yield",
        ],
        "maintenance_effects": [],
    },

    # Empire tanks
    ("Assassin", "Darkness"): {
        "taunts": [
            "Mind Control",
            "Mass Mind Control",
        ],
        "defensives": [
            "Dark Ward",
            "Deflection",
            "Overcharge Saber",
            "Force Shroud",
            "Force Cloak",
            "Force Speed",
        ],
        "tracked_effects": [
            "Dark Ward",
            "Deflection",
            "Overcharge Saber",
            "Force Shroud",
        ],
        "maintenance_effects": [
            "Dark Ward",
        ],
    },

    ("Juggernaut", "Immortal"): {
        "taunts": [
            "Taunt",
            "Threatening Scream",
        ],
        "defensives": [
            "Saber Ward",
            "Invincible",
            "Endure Pain",
            "Saber Reflect",
            "Enraged Defense",
        ],
        "tracked_effects": [
            "Saber Ward",
            "Invincible",
            "Endure Pain",
            "Saber Reflect",
            "Enraged Defense",
        ],
        "maintenance_effects": [],
    },

    ("Powertech", "Shield Tech"): {
        "taunts": [
            "Neural Dart",
            "Sonic Missile",
        ],
        "defensives": [
            "Energy Shield",
            "Kolto Overload",
            "Oil Slick",
            "Hydraulic Overrides",
            "Power Yield",
        ],
        "tracked_effects": [
            "Energy Shield",
            "Kolto Overload",
            "Oil Slick",
            "Hydraulic Overrides",
            "Power Yield",
        ],
        "maintenance_effects": [],
    },
}


def get_lines(encounter):
    return encounter.lines if hasattr(encounter, "lines") else encounter


def get_tank_config(player_class, discipline):
    return TANK_CONFIG.get(
        (player_class, discipline),
        {
            "taunts": [],
            "defensives": [],
            "tracked_effects": [],
            "maintenance_effects": [],
        }
    )


def parse_time_to_seconds(line):
    match = re.search(
        r"\[(\d+):(\d+):(\d+)\.(\d+)\]",
        line
    )

    if not match:
        return None

    hours = int(match.group(1))
    minutes = int(match.group(2))
    seconds = int(match.group(3))
    milliseconds = int(match.group(4))

    return (
        hours * 3600
        + minutes * 60
        + seconds
        + milliseconds / 1000
    )


def extract_blocks(line):
    return re.findall(r"\[(.*?)\]", line)


def clean_entity_name(block):
    block = block.strip()

    if block == "=":
        return "="

    if block.startswith("@"):
        block = block[1:]

    if "#" in block:
        return block.split("#")[0].strip()

    if "{" in block:
        return block.split("{")[0].strip()

    if "|" in block:
        return block.split("|")[0].strip()

    return block.strip()


def clean_ability_name(block):
    block = block.strip()

    if "{" in block:
        return block.split("{")[0].strip()

    return block


def get_source_from_line(line):
    blocks = extract_blocks(line)

    if len(blocks) < 2:
        return None

    return clean_entity_name(blocks[1])


def get_target_from_line(line):
    blocks = extract_blocks(line)

    if len(blocks) < 3:
        return None

    return clean_entity_name(blocks[2])


def get_ability_from_line(line):
    blocks = extract_blocks(line)

    if len(blocks) < 4:
        return None

    return clean_ability_name(blocks[3])


def get_value_block(line):
    match = re.search(
        r"\]\s*\(([^)]*)\)\s*<",
        line
    )

    if not match:
        return ""

    return match.group(1).strip()


def get_first_number(text):
    match = re.search(
        r"(\d+(?:\.\d+)?)",
        text
    )

    if not match:
        return 0.0

    return float(match.group(1))


def get_damage_value(line):
    value_block = get_value_block(line)

    if not value_block:
        return 0.0

    return get_first_number(value_block)


def get_absorbed_value(line):
    value_block = get_value_block(line)

    if not value_block:
        return 0.0

    lower_value = value_block.lower()

    if "absorbed" in lower_value:
        return get_first_number(value_block)

    if "~" in value_block:
        raw_part, effective_part = value_block.split("~", 1)

        raw = get_first_number(raw_part)
        effective = get_first_number(effective_part)

        if raw > effective:
            return raw - effective

    return 0.0


def is_player_related_effect(line, player_name):
    source = get_source_from_line(line)
    target = get_target_from_line(line)

    return (
        source == player_name
        or target == player_name
        or (
            source == player_name
            and target == "="
        )
    )


def calculate_effect_uptimes(lines, player_name, tracked_effects):
    fight_start = None
    fight_end = None

    active_effects = {}
    total_uptime = defaultdict(float)

    for line in lines:
        current_time = parse_time_to_seconds(line)

        if current_time is None:
            continue

        if fight_start is None:
            fight_start = current_time

        fight_end = current_time

        ability = get_ability_from_line(line)

        if not ability:
            continue

        if ability not in tracked_effects:
            continue

        if not is_player_related_effect(line, player_name):
            continue

        if "ApplyEffect" in line:
            if ability not in active_effects:
                active_effects[ability] = current_time

        elif "RemoveEffect" in line:
            if ability in active_effects:
                start_time = active_effects[ability]

                total_uptime[ability] += max(
                    0,
                    current_time - start_time
                )

                del active_effects[ability]

    if fight_start is None or fight_end is None:
        return {}, 0

    fight_duration = max(
        1,
        fight_end - fight_start
    )

    for ability, start_time in active_effects.items():
        total_uptime[ability] += max(
            0,
            fight_end - start_time
        )

    result = {}

    for ability in tracked_effects:
        uptime_seconds = total_uptime.get(
            ability,
            0
        )

        result[ability] = {
            "seconds": round(uptime_seconds, 2),
            "percent": round(
                uptime_seconds / fight_duration * 100,
                2
            ),
        }

    return result, round(fight_duration, 2)


def analyze_tank_encounter(
    encounter,
    player_name,
    player_class,
    discipline
):
    lines = get_lines(encounter)

    config = get_tank_config(
        player_class,
        discipline
    )

    taunts = config["taunts"]
    defensives = config["defensives"]
    tracked_effects = config["tracked_effects"]
    maintenance_effects = config["maintenance_effects"]

    damage_taken = 0.0
    absorbed_total = 0.0

    hits_taken = 0
    shielded_hits = 0
    avoided_hits = 0

    taunt_uses = defaultdict(int)
    defensive_uses = defaultdict(int)

    for line in lines:
        ability = get_ability_from_line(line)

        if not ability:
            continue

        source = get_source_from_line(line)
        target = get_target_from_line(line)

        # Taunts
        if (
            source == player_name
            and ability in taunts
            and "AbilityActivate" in line
        ):
            taunt_uses[ability] += 1

        # Defensives
        if (
            source == player_name
            and ability in defensives
            and "AbilityActivate" in line
        ):
            defensive_uses[ability] += 1

        # Damage taken
        if (
            target == player_name
            and "Damage" in line
            and "ApplyEffect" in line
        ):
            value_block = get_value_block(line)
            lower_line = line.lower()
            lower_value = value_block.lower()

            damage_value = get_damage_value(line)
            absorbed_value = get_absorbed_value(line)

            hits_taken += 1
            damage_taken += damage_value
            absorbed_total += absorbed_value

            if (
                "-shield" in lower_line
                or "shield" in lower_value
            ):
                shielded_hits += 1

            if (
                "-deflect" in lower_line
                or "-parry" in lower_line
                or "-dodge" in lower_line
                or "-resist" in lower_line
                or "-miss" in lower_line
                or "deflect" in lower_value
                or "parry" in lower_value
                or "dodge" in lower_value
                or "resist" in lower_value
                or "miss" in lower_value
            ):
                avoided_hits += 1

    effect_uptimes, uptime_duration = calculate_effect_uptimes(
        lines,
        player_name,
        tracked_effects
    )

    combat_duration = get_combat_duration(encounter)

    if combat_duration:
        fight_duration = round(combat_duration, 2)
    else:
        fight_duration = uptime_duration

    total_incoming = damage_taken + absorbed_total

    if total_incoming > 0:
        absorb_percent = round(
            absorbed_total / total_incoming * 100,
            2
        )
    else:
        absorb_percent = 0

    if hits_taken > 0:
        shield_rate = round(
            shielded_hits / hits_taken * 100,
            2
        )

        avoid_rate = round(
            avoided_hits / hits_taken * 100,
            2
        )
    else:
        shield_rate = 0
        avoid_rate = 0

    recommendations = []

    total_taunts = sum(taunt_uses.values())
    total_defensives = sum(defensive_uses.values())

    if damage_taken > 0 and total_defensives == 0:
        recommendations.append(
            "За бой не найдено использований defensive-способностей."
        )

    if total_taunts == 0:
        recommendations.append(
            "За бой не найдено использований taunt-способностей."
        )

    for effect_name in maintenance_effects:
        uptime = effect_uptimes.get(
            effect_name,
            {}
        ).get(
            "percent",
            0
        )

        if uptime < 80:
            recommendations.append(
                f"Низкий uptime {effect_name}: {uptime}%. "
                f"Старайся держать ближе к 90%+."
            )

    if hits_taken > 20 and shield_rate < 20:
        recommendations.append(
            "Низкий процент shield-срабатываний по логу. "
            "Проверь стойку, экипировку и uptime защитных эффектов."
        )

    return {
        "has_data": (
            damage_taken > 0
            or total_taunts > 0
            or total_defensives > 0
            or bool(effect_uptimes)
        ),

        "fight_duration": fight_duration,

        "damage_taken": round(damage_taken, 2),
        "absorbed_total": round(absorbed_total, 2),
        "absorb_percent": absorb_percent,

        "hits_taken": hits_taken,
        "shielded_hits": shielded_hits,
        "shield_rate": shield_rate,

        "avoided_hits": avoided_hits,
        "avoid_rate": avoid_rate,

        "taunts": dict(taunt_uses),
        "defensives": dict(defensive_uses),
        "effect_uptimes": effect_uptimes,

        "recommendations": recommendations,
    }