import click
from datetime import datetime
from importlib.resources import files
from pathlib import Path
import os
import shutil
import vinery


DIRECTORIES = {
    'tmp': '/tmp/vinery',
    'output': f'{Path().resolve()}/outputs'
}
LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "SUCCESS", "ERROR"]


def setup_directories(directories: str = DIRECTORIES) -> None:
    for dir in directories.values():
        Path(dir).mkdir(parents=True, exist_ok=True)


def set_log_level(log_level: str) -> None:
    if log_level not in LOG_LEVELS:
        raise ValueError(f"Invalid log level: {log_level}. Accepted values: {LOG_LEVELS}")
    os.environ["VINE_LOG_LEVEL"] = os.getenv("VINE_LOG_LEVEL", log_level)


def find_library_path() -> str:
    """
    Locate vinery's 'library' directory in both installed and development modes.

    Returns:
        str: Absolute path to the 'library' directory.
    """
    # Try using importlib for installed mode
    try:
        path = str(files(vinery).joinpath("library"))
        if os.path.isdir(path):
            return path
    except ModuleNotFoundError:
        pass  # Fallback to manual lookup

    # Fallback to development mode directory structure
    # library/ and src/ are siblings
    vinery_root = os.path.dirname(vinery.__file__)
    abs_path = os.path.abspath(os.path.join(vinery_root, "..", "..", "library"))
    if os.path.isdir(abs_path):
        return abs_path
    else:
        raise FileNotFoundError("Could not locate 'library' in either installed or development mode.")


def setup_library(path_to_library: str) -> None:
    if not os.path.isdir(path_to_library):
        raise FileNotFoundError(f"Library path {path_to_library} does not exist!")
    # Copy files from package to user-specified directory
    shutil.copytree(find_library_path(), path_to_library, dirs_exist_ok=True)


def read_file(filename: str, dir: str = 'tmp') -> set[str]:
    try:
        with open(os.path.join(DIRECTORIES[dir], filename), "r") as f:
            return set(line.strip() for line in f.readlines() if line.strip())
    except FileNotFoundError:
        echo(f"File {filename} not found in {DIRECTORIES[dir]}.", log_level="WARNING")
        return set()


def update_file(filename: str, new_lines: list[str], dir: str = 'tmp') -> set[str]:
    contents = read_file(filename, dir)

    for line in new_lines:
        contents.add(line)
    
    with open(os.path.join(DIRECTORIES[dir], filename), "w") as f:
        f.writelines(line + '\n' for line in contents)


def read_deps_conf(directory: str) -> set[str]:
    with open(f"{directory}/_deps.conf", "r") as f:
        return [line.strip().strip("/") for line in f if (
            line.strip().strip("/")
            and not line.startswith("#")  # Ignore comments
        )]


def echo(message: str, log_level: str = "INFO") -> None:
    """
    Custom logging function with color-coded output.
    """
    if LOG_LEVELS.index(log_level) < LOG_LEVELS.index(os.getenv("VINE_LOG_LEVEL", "INFO")):
        return  # Suppress messages below the global log level

    message = f"{datetime.now().time().isoformat(timespec='seconds')} vinery: [{log_level}] {message}"

    if log_level == "DEBUG":
        click.secho(message)
    elif log_level == "INFO":
        click.secho(message, fg="blue", bold=True)
    elif log_level == "WARNING":
        click.secho(message, fg="yellow")
    elif log_level == "SUCCESS":
        click.secho(message, fg="green", bold=True)
    elif log_level == "ERROR":
        click.secho(message, fg="red", bold=True, err=True)
    else:
        click.secho(message, err=True)
        click.secho(f"Log level '{log_level}' is not supported.", fg="red", bold=True, err=True)
