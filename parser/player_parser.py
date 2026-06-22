import re

def parse_players(log_lines):
    players = {}

    for line in log_lines:
        if "DisciplineChanged" not in line:
            continue

        # 1️⃣ Имя игрока
        name_match = re.search(r'\[@([^#]+)#', line)
        if not name_match:
            continue

        name = name_match.group(1).strip()

        # 2️⃣ Берём именно содержимое блока [DisciplineChanged ...]
        discipline_block_match = re.search(r'\[DisciplineChanged.*?\]', line)
        if not discipline_block_match:
            continue

        discipline_block = discipline_block_match.group(0)

        # 3️⃣ Убираем всё до двоеточия внутри этого блока
        if ":" not in discipline_block:
            continue

        after_colon = discipline_block.split(":", 1)[1]

        # 4️⃣ Удаляем {числа}
        cleaned = re.sub(r'\{[^}]+\}', '', after_colon)

        # 5️⃣ Убираем лишние символы
        cleaned = cleaned.replace("]", "").strip()

        # Теперь должно быть: Marauder/Annihilation
        if "/" in cleaned:
            parts = cleaned.split("/")
            p_class = parts[0].strip()
            p_spec = parts[1].strip()

            players[name] = {
                "class": p_class,
                "discipline": p_spec
            }

    return players