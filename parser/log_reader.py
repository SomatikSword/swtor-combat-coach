def read_log(file_path):

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        lines = file.readlines()

    return lines