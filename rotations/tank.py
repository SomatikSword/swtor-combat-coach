def analyze_tank(player_name, encounter_lines, config):

    result = "\nДополнительный анализ (Tank):\n\n"

    # ✅ Defensive cooldown usage
    for cd in config.get("defensives", []):
        count = 0

        for line in encounter_lines:
            if f"@{player_name}#" in line and cd in line and "AbilityActivate" in line:
                count += 1

        result += f"{cd} uses: {count}\n"

        if count < 2:
            result += f"⚠ {cd} используется редко.\n"

    # ✅ Taunt usage
    taunt_count = 0

    for line in encounter_lines:
        if f"@{player_name}#" in line and "Taunt" in line:
            taunt_count += 1

    result += f"Taunt uses: {taunt_count}\n"

    return result