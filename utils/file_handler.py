from pathlib import Path
from uuid import uuid4
from datetime import datetime, timedelta
import shutil
import zipfile


DATA_DIR = Path("data")
UPLOADS_DIR = DATA_DIR / "uploads"

ALLOWED_EXTENSIONS = {".txt", ".zip"}


def ensure_uploads_dir() -> None:
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


def validate_attachment(filename: str) -> None:
    suffix = Path(filename).suffix.lower()

    if suffix not in ALLOWED_EXTENSIONS:
        raise ValueError("Поддерживаются только файлы .txt и .zip")


async def save_uploaded_file(attachment):
    ensure_uploads_dir()
    validate_attachment(attachment.filename)

    upload_id = uuid4().hex
    upload_dir = UPLOADS_DIR / upload_id
    upload_dir.mkdir(parents=True, exist_ok=True)

    safe_filename = Path(attachment.filename).name
    saved_path = upload_dir / safe_filename

    await attachment.save(saved_path)

    return saved_path, upload_dir


def safe_extract_zip(zip_path: Path, extract_to: Path) -> None:
    extract_to = extract_to.resolve()

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        for member in zip_ref.infolist():
            member_path = (extract_to / member.filename).resolve()

            if not str(member_path).startswith(str(extract_to)):
                raise ValueError("ZIP содержит небезопасный путь файла")

        zip_ref.extractall(extract_to)


def find_log_txt(upload_dir: Path) -> Path:
    txt_files = [
        path
        for path in upload_dir.rglob("*.txt")
        if path.is_file() and "__MACOSX" not in path.parts
    ]

    if not txt_files:
        raise ValueError("В загрузке не найден .txt лог")

    combat_logs = [
        path
        for path in txt_files
        if path.name.lower().startswith("combat_")
    ]

    candidates = combat_logs if combat_logs else txt_files

    return max(candidates, key=lambda path: path.stat().st_size)


async def prepare_uploaded_log(attachment):
    saved_path, upload_dir = await save_uploaded_file(attachment)

    if saved_path.suffix.lower() == ".zip":
        safe_extract_zip(saved_path, upload_dir)
        log_path = find_log_txt(upload_dir)

    elif saved_path.suffix.lower() == ".txt":
        log_path = saved_path

    else:
        raise ValueError("Поддерживаются только файлы .txt и .zip")

    debug_info = {
        "uploaded_file": saved_path.name,
        "log_file": log_path.name,
        "upload_dir": str(upload_dir),
    }

    return log_path, upload_dir, debug_info


def cleanup_old_uploads(max_age_hours: int = 24) -> None:
    ensure_uploads_dir()

    now = datetime.now()
    max_age = timedelta(hours=max_age_hours)

    for upload_dir in UPLOADS_DIR.iterdir():
        if not upload_dir.is_dir():
            continue

        modified_time = datetime.fromtimestamp(upload_dir.stat().st_mtime)

        if now - modified_time > max_age:
            shutil.rmtree(upload_dir, ignore_errors=True)