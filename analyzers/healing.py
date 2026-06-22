import re
from collections import defaultdict
from analyzers.combat_duration import get_combat_duration


def _parse_heal_value(line):
    """
    Разбирает поле значения heal-строки SWTOR.

    Формат строки: ... [ApplyEffect {...}: Heal {...}] (VALUE) <THREAT>
    Где VALUE имеет вид: ( RAW[*] [~ EFFECTIVE] )
      RAW        — общий (сырой) хил, присутствует всегда
      *          — признак крита (на расчёт не влияет)
      ~ EFFECTIVE — эффективный хил; появляется ТОЛЬКО когда effective < raw
                    (т.е. часть ушла в оверхил). Если поля нет — effective = raw.

    Проверено по реальным строкам лога: threat == effective × 0.45 (коэффициент
    генерации угрозы хилером), что подтверждает интерпретацию ~EFFECTIVE.

    Возвращает кортеж (raw, effective). При ошибке парсинга — (0.0, 0.0).
    """
    # Значение всегда в круглых скобках сразу после закрывающей квадратной
    # (названия эффектов вроде "Crushed (Eradicate)" могут содержать скобки,
    # но они находятся ВНУТРИ [...], поэтому привязываемся к "] (").
    value_match = re.search(r'\]\s*\(([^)]*)\)', line)
    if not value_match:
        return 0.0, 0.0

    inside = value_match.group(1).strip()

    # Разделяем raw и optional ~effective по тильде
    parts = inside.split('~')
    raw_str = parts[0].strip().rstrip('*').strip()

    try:
        raw = float(raw_str)
    except ValueError:
        return 0.0, 0.0

    if len(parts) > 1:
        effective_str = parts[1].strip()
        try:
            effective = float(effective_str)
        except ValueError:
            effective = raw
    else:
        effective = raw

    return raw, effective


def calculate_ehps(encounter):
    """
    Считает Raw HPS и Effective HPS по каждому игроку-хилеру в энкаунтере.

    Возвращает словарь вида:
        { player_name: {"raw_hps": float, "ehps": float} }

    EHPS совпадает с Parsely/StarParse: effective heal берётся прямо из лога
    (поле ~EFFECTIVE), а длительность — по combat-событиям (Damage/Heal/Death),
    как в Parsely, а не по строке ExitCombat.
    """
    lines = encounter.lines if hasattr(encounter, "lines") else encounter
    duration = get_combat_duration(encounter)

    if not duration:
        return {}

    raw_heal = defaultdict(float)
    effective_heal = defaultdict(float)

    for line in lines:

        # Только реальные heal-эвенты (ApplyEffect: Heal).
        # Строки накидывания зарядов ("Kolto Shell (6 charges)") сюда не попадают.
        if "ApplyEffect" not in line or ": Heal " not in line:
            continue

        source_match = re.search(r'\[@([^#]+)#', line)
        if not source_match:
            continue

        player_name = source_match.group(1).strip()

        raw, effective = _parse_heal_value(line)
        if raw == 0.0 and effective == 0.0:
            continue

        raw_heal[player_name] += raw
        effective_heal[player_name] += effective

    result = {}

    for player in raw_heal:
        result[player] = {
            "raw_hps": round(raw_heal[player] / duration, 2),
            "ehps": round(effective_heal[player] / duration, 2),
        }

    return result
