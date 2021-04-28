from pathlib import Path


def getPath(_file_, *path):
    return Path(_file_).resolve().parent.joinpath(*path)