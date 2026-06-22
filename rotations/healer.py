from analyzers.healing import calculate_ehps, _parse_heal_value
from analyzers.dot_analysis import analyze_dot_uptime


def _calculate_heal_breakdown(encounter, player_name):
    """
    Считает суммарный raw и effective heal игрока по энкаунтеру.
    Возвращает кортеж (raw_heal, effective_heal).
    """
    lines = encounter.lines if hasattr(encounter, "lines") else encounter

    raw_total = 0.0
    effective_total = 0.0

    for line in lines:
        if "ApplyEffect" not in line or ": Heal " not in line:
            continue

        if f"@{player_name}#" not in line:
            continue

        raw, effective = _parse_heal_value(line)
        raw_total += raw
        effective_total += effective

    return raw_total, effective_total


def analyze_healer(player_name, encounter, config):

    lines = encounter.lines if hasattr(encounter, "lines") else encounter

    result = "\nДополнительный анализ (Healer):\n\n"

    # ✅ Raw HPS + EHPS
    ehps_data = calculate_ehps(encounter)
    heal = ehps_data.get(player_name)

    if heal:
        result += f"Raw HPS: {heal['raw_hps']}\n"
        result += f"Effective HPS: {heal['ehps']}\n"

    # ✅ Overheal %
    raw_heal, effective_heal = _calculate_heal_breakdown(encounter, player_name)

    if raw_heal > 0:
        overheal_percent = 100 - (effective_heal / raw_heal * 100)
        result += f"Overheal: {round(overheal_percent, 2)}%\n"

        if overheal_percent > 40:
            result += "⚠ Overheal слишком высокий (цель <30%).\n"

    # ✅ HoT uptime
    for hot in config.get("hots", []):
        uptime = analyze_dot_uptime(lines, player_name, hot)

        if uptime is not None:
            result += f"{hot} uptime: {uptime}%\n"

            if uptime < 90:
                result += f"⚠ Низкий uptime {hot}.\n"

    # ✅ Cooldown usage
    for cd in config.get("cooldowns", []):
        count = 0

        for line in lines:
            if f"@{player_name}#" in line and cd in line and "AbilityActivate" in line:
                count += 1

        result += f"{cd} uses: {count}\n"

    return result