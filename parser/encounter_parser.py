import re

from utils.time_utils import time_to_seconds


# ──────────────────────────────────────────────────────────────
# Параметры разбиения энкаунтеров.
# Вынесены наверх, чтобы легко менять в PyCharm без правки логики.
# ──────────────────────────────────────────────────────────────

# Если после последнего Damage/Heal/Death прошло больше этого числа секунд,
# а явного ExitCombat не было — считаем бой законченным.
# 120с безопасно для многофазных боссов (Soa, Styrak): фазовые переходы
# между фазами обычно короче 2 минут.
INACTIVITY_TIMEOUT_SEC = 120.0

# Энкаунтеры короче этого порога отбрасываются как мусор (агро мобов,
# переходы, микро-вайпы). Реализует идею из README: «только боссы».
MIN_ENCOUNTER_DURATION_SEC = 30.0


class Encounter:
    """
    Описание одного боя.

    Поля start_time/end_time/lines сохранены для обратной совместимости —
    весь код, делающий encounter.lines и encounter.start_time, работает как прежде.
    Новые опциональные поля (boss_name, duration_sec) добавлены для удобства.
    """

    def __init__(self, start_time):
        self.start_time = start_time
        self.end_time = None
        self.lines = []
        self.boss_name = None      # определяется позже (get_boss_name)
        self.duration_sec = None   # выставляется при закрытии

    def add_line(self, line):
        self.lines.append(line)


def _timestamp_seconds(line):
    """Достаём timestamp строки лога и переводим в секунды. None, если нет."""
    m = re.search(r'\[(\d+:\d+:\d+\.\d+)\]', line)
    if not m:
        return None
    return time_to_seconds(m.group(1))


def _is_combat_event(line):
    """Является ли строка реальным combat-событием (урон/лечение/смерть)."""
    return "Damage" in line or "Heal" in line or "Death" in line


def _area_id(line):
    """
    ID локации из строки AreaEntered, либо None.
    Формат: [AreaEntered {...}: Имя {ID}] → берём последний {ID}.
    """
    if "AreaEntered" not in line:
        return None
    m = re.findall(r'\{(\d+)\}', line)
    return m[-1] if m else None


def _close(encounter, end_time, duration_end_seconds):
    """
    Закрываем энкаунтер: фиксируем end_time и duration.

    end_time              — строка timestamp из ExitCombat (или None).
    duration_end_seconds  — секунды, ДО которых считать длительность боя.
            • при ExitCombat это время самой строки ExitCombat (честная граница);
            • при таймауте/смене зоны/хвосте — время последнего combat-события,
              чтобы не втягивать «мёртвое» время.
    """
    if end_time is not None:
        encounter.end_time = end_time
    elif encounter.start_time:
        # нет явного end_time — точное значение не критично для парсеров,
        # они считают длительность сами; оставляем запас.
        encounter.end_time = encounter.start_time

    if encounter.start_time and duration_end_seconds is not None:
        start_sec = time_to_seconds(encounter.start_time)
        encounter.duration_sec = max(0.0, duration_end_seconds - start_sec)


def split_encounters(log_lines):
    """
    Разбивает лог на отдельные энкаунтеры по 4 критериям:

      1. EnterCombat               → открыть новый бой
      2. ExitCombat                → закрыть текущий бой
      3. Таймаут бездействия 120с  → закрыть текущий бой (нет Damage/Heal/Death)
      4. AreaEntered в дРУГУЮ зону → закрыть текущий бой (смена операции/локации)

    Короткие энкаунтеры (< MIN_ENCOUNTER_DURATION_SEC) отбрасываются как мусор.

    Возвращает список объектов Encounter.
    """
    encounters = []
    current = None
    last_activity_seconds = None        # время последнего Damage/Heal/Death
    current_area_id = None              # ID текущей зоны (для отслеживания смены)

    for raw_line in log_lines:
        line = raw_line if isinstance(raw_line, str) else raw_line.rstrip("\n")
        now = _timestamp_seconds(line)

        # ── 4. Смена зоны AreaEntered ──────────────────────────
        area = _area_id(line)
        if area is not None:
            if current is not None and current_area_id is not None and area != current_area_id:
                # ушли в другую локацию — закрываем бой по последней активности
                _close(current, None, last_activity_seconds)
                encounters.append(current)
                current = None
                last_activity_seconds = None
            current_area_id = area

        # ── 1. EnterCombat → открыть бой ───────────────────────
        if "EnterCombat" in line:
            # Если уже есть открытый бой, который «протух» (давно не было
            # активности), закрываем его по последней активности. Это ловит
            # вайпы без ExitCombat между попытками.
            if current is not None and last_activity_seconds is not None and now is not None:
                if now - last_activity_seconds > INACTIVITY_TIMEOUT_SEC:
                    _close(current, None, last_activity_seconds)
                    encounters.append(current)
                    current = None
                    last_activity_seconds = None

            brackets = re.findall(r"\[(.*?)\]", line)
            start_ts = brackets[0] if brackets else "00:00:00.000"
            current = Encounter(start_ts)
            last_activity_seconds = now
            continue

        # ── 2. ExitCombat → закрыть бой ────────────────────────
        if "ExitCombat" in line:
            if current is not None:
                brackets = re.findall(r"\[(.*?)\]", line)
                end_ts = brackets[0] if brackets else current.start_time
                # длительность до строки ExitCombat — честная граница боя
                _close(current, end_ts, now)
                encounters.append(current)
                current = None
                last_activity_seconds = None
            continue

        # ── сбор строк + отслеживание активности ──────────────
        if current is not None:
            if _is_combat_event(line):
                # ── 3. Проверка таймаута перед обновлением активности ──
                # Если пауза с прошлого combat-события больше порога —
                # старый бой уже «протух», закрываем его и открываем новый
                # (кейс Soa: хвост revive/logout без ExitCombat;
                #  кейс вайпов: несколько попыток подряд без ExitCombat).
                if (last_activity_seconds is not None
                        and now is not None
                        and now - last_activity_seconds > INACTIVITY_TIMEOUT_SEC):
                    # длительность протухшего боя — по последней активности
                    _close(current, None, last_activity_seconds)
                    encounters.append(current)
                    brackets = re.findall(r"\[(.*?)\]", line)
                    current = Encounter(brackets[0] if brackets else "00:00:00.000")

                current.add_line(line)
                last_activity_seconds = now if now is not None else last_activity_seconds
            else:
                current.add_line(line)

    # ── хвост: бой не закрыт ExitCombat ──────────────────────
    if current is not None:
        # длительность по последней активности, не по концу файла
        _close(current, None, last_activity_seconds)
        encounters.append(current)

    # ── фильтр коротких энкаунтеров ──────────────────────────
    filtered = [
        e for e in encounters
        if e.duration_sec is None or e.duration_sec >= MIN_ENCOUNTER_DURATION_SEC
    ]

    return filtered
