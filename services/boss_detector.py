import re

from services.boss_catalog import (
    normalize_name,
    iter_catalog_entries,
    TRASH_NAMES,
)


def get_log_blocks(line: str) -> list[str]:
    return re.findall(r"\[(.*?)\]", line)


def clean_entity_name(value: str) -> str:
    if not value:
        return ""

    return value.split("{", 1)[0].strip()


def extract_targets_from_lines(lines) -> list[str]:
    """
    Достаёт цели из строк лога.

    SWTOR combat log обычно:
    [time] [source] [target] [ability] [event]
    """
    targets = []

    for line in lines:
        blocks = get_log_blocks(line)

        if len(blocks) < 3:
            continue

        target = clean_entity_name(blocks[2])

        if not target:
            continue

        # Игроки обычно начинаются с @.
        if target.startswith("@"):
            continue

        targets.append(target)

    return targets


def name_matches(value: str, aliases: list[str]) -> bool:
    normalized_value = normalize_name(value)

    if not normalized_value:
        return False

    for alias in aliases:
        normalized_alias = normalize_name(alias)

        if not normalized_alias:
            continue

        if normalized_value == normalized_alias:
            return True

        if normalized_alias in normalized_value:
            return True

        if normalized_value in normalized_alias:
            return True

    return False


def detect_boss_encounter(lines):
    """
    Определяет, относится ли encounter к настоящему боссу.

    Возвращает:
    {
        "is_boss_fight": True/False,
        "operation": "...",
        "boss_name": "...",
        "matched_name": "...",
        "match_type": "boss" / "encounter_add"
    }
    """

    targets = extract_targets_from_lines(lines)

    if not targets:
        return {
            "is_boss_fight": False,
            "operation": None,
            "boss_name": None,
            "matched_name": None,
            "match_type": None,
        }

    # Считаем, какие цели чаще всего встречались.
    target_counts = {}

    for target in targets:
        normalized_target = normalize_name(target)

        if not normalized_target:
            continue

        target_counts[target] = target_counts.get(target, 0) + 1

    if not target_counts:
        return {
            "is_boss_fight": False,
            "operation": None,
            "boss_name": None,
            "matched_name": None,
            "match_type": None,
        }

    best_match = None
    best_score = 0

    for target, count in target_counts.items():
        normalized_target = normalize_name(target)

        if normalized_target in TRASH_NAMES:
            continue

        for operation_name, boss_name, data in iter_catalog_entries():
            boss_aliases = data.get("boss_aliases", [])
            encounter_aliases = data.get("encounter_aliases", [])

            if name_matches(target, boss_aliases):
                score = count + 1000

                if score > best_score:
                    best_score = score
                    best_match = {
                        "is_boss_fight": True,
                        "operation": operation_name,
                        "boss_name": boss_name,
                        "matched_name": target,
                        "match_type": "boss",
                    }

            elif name_matches(target, encounter_aliases):
                score = count + 100

                if score > best_score:
                    best_score = score
                    best_match = {
                        "is_boss_fight": True,
                        "operation": operation_name,
                        "boss_name": boss_name,
                        "matched_name": target,
                        "match_type": "encounter_add",
                    }

    if best_match:
        return best_match

    return {
        "is_boss_fight": False,
        "operation": None,
        "boss_name": None,
        "matched_name": None,
        "match_type": None,
    }