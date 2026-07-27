def load_text_file(file) -> str:
    """
    Reads uploaded text file and returns content as string.
    """
    return file.read().decode("utf-8")
