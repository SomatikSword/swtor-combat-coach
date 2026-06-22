import zipfile
import os


def extract_log_file(file_path):

    # Если TXT — просто вернуть путь
    if file_path.endswith(".txt"):
        return file_path

    # Если ZIP — распаковать
    if file_path.endswith(".zip"):

        extract_folder = "data/extracted"

        os.makedirs(extract_folder, exist_ok=True)

        with zipfile.ZipFile(file_path, "r") as zip_ref:
            zip_ref.extractall(extract_folder)

        # Ищем txt внутри архива
        for file_name in os.listdir(extract_folder):

            if file_name.endswith(".txt"):
                return os.path.join(
                    extract_folder,
                    file_name
                )

    return None