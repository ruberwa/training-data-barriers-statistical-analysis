from pathlib import Path


def open_log(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("", encoding="utf-8")


def record(path: Path, message: str) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(message + "\n")
