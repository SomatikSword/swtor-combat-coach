"""
Юнит-тесты разбиения энкаунтеров.

Запуск (на выбор):
    python tests/test_encounter_split.py            # простой запуск с assert
    python -m pytest tests/test_encounter_split.py  # если установлен pytest

Тесты используют синтетические строки лога, построенные по реальному формату
SWTOR CombatLog, и проверяют 4 критерия разбиения + фильтр коротких боёв.
"""
import os
import sys

# чтобы импорт parser.encounter_parser работал при запуске из корня проекта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parser.encounter_parser import (
    split_encounters,
    INACTIVITY_TIMEOUT_SEC,
    MIN_ENCOUNTER_DURATION_SEC,
)


def _line(ts, body):
    """Собирает валидную строку лога: [timestamp] ... body"""
    return f"[{ts}] [@Player#123|...|(100/100)] [Mob {{999}}|...|(100/100)] {body}"


def _enter(ts):
    return _line(ts, "[] [] [Event {836045448945472}: EnterCombat {836045448945489}]")


def _exit(ts):
    return _line(ts, "[] [] [Event {836045448945472}: ExitCombat {836045448945490}]")


def _damage(ts):
    return _line(ts, "[Ability {1}] [ApplyEffect {2}: Damage {3}] (1000 energy)")


def _heal(ts):
    return _line(ts, "[Ability {1}] [ApplyEffect {2}: Heal {3}] (500)")


def _death(ts):
    return _line(ts, "[] [] [Event {836045448945472}: Death {836045448945493}]")


def _area(ts, name, area_id):
    return (f"[{ts}] [@Player#123|...|(100/100)] [] [] "
            f"[AreaEntered {{836045448953664}}: {name} {{{area_id}}}]")


# ──────────────────────────────────────────────────────────────
# Тест 1: обычный бой с ExitCombat — один энкаунтер
# ──────────────────────────────────────────────────────────────
def test_normal_encounter_with_exitcombat():
    lines = [
        _enter("20:00:00.000"),
        _damage("20:00:01.000"),
        _damage("20:00:05.000"),
        _heal("20:00:06.000"),
        _exit("20:02:00.000"),
    ]
    encounters = split_encounters(lines)
    assert len(encounters) == 1, f"ожидал 1 бой, получил {len(encounters)}"
    assert encounters[0].duration_sec is not None
    assert encounters[0].duration_sec >= 30.0, "бой не должен быть отфильтрован"
    print("PASS  test_normal_encounter_with_exitcombat")


# ──────────────────────────────────────────────────────────────
# Тест 2: кейс Soa — бой без ExitCombat + хвост >120с → 1 бой (хвост отваливается)
# ──────────────────────────────────────────────────────────────
def test_soa_tail_split_off():
    # реальный бой 10 минут, затем 3 минуты «мёртвого» хвоста без ExitCombat
    lines = [_enter("21:50:00.000")]
    # 10 минут активного боя
    for i in range(0, 600, 5):
        lines.append(_damage(f"21:{50 + i // 60:02d}:{i % 60:02d}.000"))
    # хвост: revive/logout, 3 минуты тишины (порог 120с)
    lines.append(_death("22:01:00.000"))   # последнее событие боя
    lines.append(_damage("22:04:30.000"))  # через 210с — это уже ДРУГОЙ бой (или мусор)

    encounters = split_encounters(lines)
    # хвост 90с после 22:01 → но следующее событие через 210с > 120с порог
    # значит Soa-бой закрывается по таймауту на 22:01:00
    soa = [e for e in encounters if e.duration_sec and e.duration_sec > 60]
    assert len(soa) >= 1, "ожидал, что Soa-бой сохранится"
    # длительность Soa должна быть ~11 минут (до 22:01), а не ~14.5
    assert soa[0].duration_sec < 12 * 60, (
        f"Soa-бой слишком длинный: {soa[0].duration_sec}с — хвост не отвалился"
    )
    print("PASS  test_soa_tail_split_off")


# ──────────────────────────────────────────────────────────────
# Тест 3: многофазный босс с паузой 90с внутри — НЕ должен разрезаться (порог 120с)
# ──────────────────────────────────────────────────────────────
def test_multiphase_boss_not_split():
    lines = [
        _enter("20:00:00.000"),
        _damage("20:00:05.000"),
        _damage("20:00:10.000"),
        # пауза между фазами 90 секунд (< порога 120с)
        _damage("20:01:40.000"),   # +90с от прошлого
        _damage("20:01:45.000"),
        _exit("20:03:00.000"),
    ]
    encounters = split_encounters(lines)
    assert len(encounters) == 1, (
        f"многофазный босс разрезан на {len(encounters)} — порог {INACTIVITY_TIMEOUT_SEC}с не сработал"
    )
    print("PASS  test_multiphase_boss_not_split")


# ──────────────────────────────────────────────────────────────
# Тест 4: короткий бой 7с отбрасывается фильтром
# ──────────────────────────────────────────────────────────────
def test_short_encounter_filtered():
    lines = [
        _enter("20:00:00.000"),
        _damage("20:00:03.000"),
        _exit("20:00:07.000"),
    ]
    encounters = split_encounters(lines)
    assert len(encounters) == 0, (
        f"короткий бой {MIN_ENCOUNTER_DURATION_SEC}с не должен пройти фильтр"
    )
    print("PASS  test_short_encounter_filtered")


# ──────────────────────────────────────────────────────────────
# Тест 5: AreaEntered в другую зону закрывает текущий бой
# ──────────────────────────────────────────────────────────────
def test_area_change_closes_encounter():
    # реалистично: сначала вход в операцию (area_id A), бой, затем
    # переход в другую локацию (area_id B) → бой закрывается.
    lines = [
        _area("19:59:00.000", "Eternity Vault", "833571547775670"),
        _enter("20:00:00.000"),
        _damage("20:00:05.000"),
        _damage("20:00:40.000"),
        # уход в другую локацию (другой area_id)
        _area("20:01:30.000", "Imperial Fleet", "137438989504"),
        _enter("20:05:00.000"),
        _damage("20:05:05.000"),
        _exit("20:07:00.000"),
    ]
    encounters = split_encounters(lines)
    # первый бой закрывается по смене зоны; второй — полноценный
    assert len(encounters) == 2, f"ожидал 2 боя, получил {len(encounters)}"
    print("PASS  test_area_change_closes_encounter")


# ──────────────────────────────────────────────────────────────
# Тест 6: два боя подряд без ExitCombat между ними → 2 боя
# (пауза между попытками > 120с, но каждая попытка > 30с, чтобы пройти фильтр)
# ──────────────────────────────────────────────────────────────
def test_consecutive_wipes_split():
    lines = [
        _enter("20:00:00.000"),
        _damage("20:00:05.000"),
        _damage("20:00:40.000"),   # попытка 1 длится 40с
        _death("20:00:45.000"),    # смерть — конец попытки 1
        # 3 минуты тишины (вайп, регенерация) → таймаут 120с закроет попытку 1
        _enter("20:03:30.000"),
        _damage("20:03:35.000"),
        _damage("20:04:10.000"),   # попытка 2 длится 40с
        _death("20:04:15.000"),
        _exit("20:04:16.000"),
    ]
    encounters = split_encounters(lines)
    assert len(encounters) == 2, (
        f"ожидал 2 попытки, получил {len(encounters)}"
    )
    print("PASS  test_consecutive_wipes_split")


def main():
    tests = [
        test_normal_encounter_with_exitcombat,
        test_soa_tail_split_off,
        test_multiphase_boss_not_split,
        test_short_encounter_filtered,
        test_area_change_closes_encounter,
        test_consecutive_wipes_split,
    ]
    failed = 0
    for t in tests:
        try:
            t()
        except AssertionError as e:
            print(f"FAIL  {t.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"ERROR {t.__name__}: {type(e).__name__}: {e}")
            failed += 1
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
