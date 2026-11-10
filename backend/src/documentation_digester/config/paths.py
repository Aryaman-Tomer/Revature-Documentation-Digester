from pathlib import Path


class PATHS:
    CURRENT_FILE_PATH: Path = Path(__file__)
    SRC_DIRECTORY: Path = CURRENT_FILE_PATH.parents[2]
    ROOT_DIRECTORY: Path = CURRENT_FILE_PATH.parents[3]
