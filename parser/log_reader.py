from pathlib import Path


def read_log(log_path) -> list[str]:
    """
    Читает конкретный лог-файл и возвращает список строк.

    Важно:
    сюда должен приходить уже точный путь к файлу,
    а не папка data.
    """
    log_path = Path(log_path)

    if not log_path.exists():
        raise FileNotFoundError(f"Файл лога не найден: {log_path}")

    if not log_path.is_file():
        raise ValueError(f"Ожидался файл, но получено нечто другое: {log_path}")

    encodings = ["utf-8-sig", "utf-8", "cp1251"]

    last_error = None

    for encoding in encodings:
        try:
            text = log_path.read_text(encoding=encoding)
            return text.splitlines()
        except UnicodeDecodeError as error:
            last_error = error

    raise UnicodeDecodeError(
        "unknown",
        b"",
        0,
        1,
        f"Не удалось прочитать файл ни в одной кодировке: {last_error}",
    )