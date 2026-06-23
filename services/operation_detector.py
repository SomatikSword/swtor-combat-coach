from services.boss_catalog import normalize_name, iter_catalog_entries


def detect_operation(bosses):
    """
    Определяет операцию по списку канонических боссов.

    Теперь сюда должны попадать не адды, а нормальные имена:
    Tyth, Scyva, Izax, Bonethrasher и т.д.
    """

    if not bosses:
        return "Не удалось определить"

    scores = {}

    for boss in bosses:
        normalized_boss = normalize_name(boss)

        for operation_name, catalog_boss_name, data in iter_catalog_entries():
            names = [catalog_boss_name]
            names.extend(data.get("boss_aliases", []))
            names.extend(data.get("encounter_aliases", []))

            for name in names:
                normalized_name = normalize_name(name)

                if not normalized_name:
                    continue

                if normalized_boss == normalized_name:
                    scores[operation_name] = scores.get(operation_name, 0) + 1
                    break

    if not scores:
        return "Не удалось определить"

    return max(scores, key=scores.get)