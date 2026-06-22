import re


def time_to_seconds(timestamp):
    parts = timestamp.split(":")
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = float(parts[2])
    return hours * 3600 + minutes * 60 + seconds


def analyze_gcd_gaps(encounter_lines, player_name):

    action_times = []
    player_pattern = f"@{player_name}#"

    for line in encounter_lines:

        if player_pattern not in line:
            continue

        # ✅ считаем только реальные нажатия
        if "AbilityActivate" not in line:
            continue

        time_match = re.search(r'\[(\d+:\d+:\d+\.\d+)\]', line)
        if not time_match:
            continue

        action_times.append(
            time_to_seconds(time_match.group(1))
        )

    if len(action_times) < 2:
        return None

    gaps = []

    for i in range(1, len(action_times)):
        gap = action_times[i] - action_times[i - 1]

        # игнорируем конец боя и долгие механики
        if gap > 5:
            continue

        gaps.append(gap)

    if not gaps:
        return None

    return {
        "avg_gap": round(sum(gaps) / len(gaps), 2),
        "max_gap": round(max(gaps), 2),
        "long_gaps_count": len([g for g in gaps if g > 2])
    }