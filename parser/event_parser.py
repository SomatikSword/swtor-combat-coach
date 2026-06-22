import re


def parse_line(line):
    # Оставляем проверку на начало и конец боя
    if "EnterCombat" in line:
        return {"type": "enter_combat"}
    if "ExitCombat" in line:
        return {"type": "exit_combat"}

    # 1. Вытаскиваем все данные из квадратных скобок [ ]
    brackets = re.findall(r"\[(.*?)\]", line)

    # 2. Улучшенный поиск числа: берем первые цифры, игнорируя криты (*) и угрозу (~...)
    value_match = re.search(r"\((\d+)[^\)]*\)", line)

    # Проверяем: если скобок меньше 5 или числа нет — эта строка нам не интересна
    if len(brackets) < 5 or not value_match:
        return None

    value = int(value_match.group(1))
    action_info = brackets[4]  # В 5-й скобке (индекс 4) написано, урон это или хил

    # DAMAGE
    if "Damage" in action_info:
        return {
            "type": "damage",
            "source": brackets[1],  # Кто бил
            "target": brackets[2],  # Кого бил
            "ability": brackets[3],  # Чем бил
            "value": value
        }

    # HEAL
    if "Heal" in action_info:
        return {
            "type": "heal",
            "source": brackets[1],
            "target": brackets[2],
            "ability": brackets[3],
            "value": value
        }

    return None