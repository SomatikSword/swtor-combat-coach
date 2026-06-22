import re


def time_to_seconds(timestamp):
    parts = timestamp.split(":")
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = float(parts[2])
    return hours * 3600 + minutes * 60 + seconds


def analyze_dot_uptime(encounter_lines, player_name, ability_name):

    active_start = None
    total_dot_time = 0

    fight_start = None
    fight_end = None

    for line in encounter_lines:

        time_match = re.search(r'\[(\d+:\d+:\d+\.\d+)\]', line)
        if not time_match:
            continue

        current_time = time_to_seconds(time_match.group(1))

        if fight_start is None:
            fight_start = current_time

        fight_end = current_time

        if f"@{player_name}#" not in line:
            continue

        if ability_name not in line:
            continue

        # DoT applied
        if "ApplyEffect" in line and active_start is None:
            active_start = current_time

        # DoT removed
        if "RemoveEffect" in line and active_start is not None:
            total_dot_time += current_time - active_start
            active_start = None

    # Если DoT всё ещё активен к концу боя
    if active_start is not None:
        total_dot_time += fight_end - active_start

    if fight_start is None or fight_end is None:
        return None

    fight_duration = fight_end - fight_start

    if fight_duration <= 0:
        return None

    uptime_percent = (total_dot_time / fight_duration) * 100

    if uptime_percent > 100:
        uptime_percent = 100

    return round(uptime_percent, 2)