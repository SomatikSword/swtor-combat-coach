from collections import defaultdict
import re


def time_to_seconds(timestamp):
    parts = timestamp.split(":")
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = float(parts[2])
    return hours * 3600 + minutes * 60 + seconds


def calculate_dps(encounter_lines):

    damage_by_player = defaultdict(float)
    start_time = None
    end_time = None

    for line in encounter_lines:

        # Время
        time_match = re.search(r'\[(\d+:\d+:\d+\.\d+)\]', line)
        if not time_match:
            continue

        current_time = time_to_seconds(time_match.group(1))

        if start_time is None:
            start_time = current_time

        end_time = current_time

        # Только строки с уроном
        if "Damage" not in line:
            continue

        name_match = re.search(r'\[@([^#]+)#', line)
        if not name_match:
            continue

        player_name = name_match.group(1).strip()

        value_match = re.search(r'<([\d\.]+)>', line)
        if not value_match:
            continue

        damage = float(value_match.group(1))

        damage_by_player[player_name] += damage

    if start_time is None or end_time is None:
        return {}

    duration = end_time - start_time
    if duration <= 0:
        return {}

    result = {}

    for player, total_damage in damage_by_player.items():
        result[player] = round(total_damage / duration, 2)

    return result