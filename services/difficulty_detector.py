import re


def detect_difficulty(encounter_lines):
    """
    Определяет сложность по максимальному HP босса.
    """

    max_hp = 0

    for line in encounter_lines:

        # Ищем HP босса в формате (currentHP/totalHP)
        hp_match = re.search(r'\((\d+)/(\d+)\)', line)

        if hp_match:
            total_hp = int(hp_match.group(2))

            if total_hp > max_hp:
                max_hp = total_hp

    # Примерные пороги (можно уточнять позже)
    if max_hp == 0:
        return "Не удалось определить"

    if max_hp < 5_000_000:
        return "Story"

    if max_hp < 20_000_000:
        return "Veteran"

    return "Master"