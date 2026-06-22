import re

from utils.time_utils import time_to_seconds


def _last_combat_action_time(lines):
    """
    Возвращает timestamp (в секундах) последнего реального combat-события
    в энкаунтере. Parsely/StarParse считают длительность боя именно так —
    по последнему Damage/Heal/Death, а не по строке ExitCombat (которая
    может сработать на 1–2 минуты позже смерти босса и «размазать» HPS/EHPS).

    Возвращает None, если combat-событий нет.
    """
    last_seconds = None

    for line in lines:
        # combat-события: нанесён урон, лечение или смерть участника/NPC
        if "Damage" not in line and "Heal" not in line and "Death" not in line:
            continue

        time_match = re.search(r'\[(\d+:\d+:\d+\.\d+)\]', line)
        if not time_match:
            continue

        last_seconds = time_to_seconds(time_match.group(1))

    return last_seconds


def get_combat_duration(encounter):
    """
    Длительность боя: от EnterCombat до последнего combat-события.
    Возвращает None, если границы определить нельзя.
    """
    if not encounter.start_time:
        return None

    start = time_to_seconds(encounter.start_time)

    lines = encounter.lines if hasattr(encounter, "lines") else encounter
    end = _last_combat_action_time(lines)

    # Запасной вариант: если combat-событий нет, используем end_time энкаунтера
    if end is None and getattr(encounter, "end_time", None):
        end = time_to_seconds(encounter.end_time)

    if end is None:
        return None

    duration = end - start
    if duration <= 0:
        return None

    return duration
