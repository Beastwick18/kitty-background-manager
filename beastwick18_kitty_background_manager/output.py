from pathlib import Path
import beastwick18_kitty_background_manager.config as cfg
import typer

def to_link(label: str, path: Path):
    return f'\u001b]8;;file://{path}\a{label}\u001b]8;;\a'

def to_link_style(label: str, path: Path, **kwargs):
    return typer.style(to_link(label, path), **kwargs)

def to_link_secho(label: str, path: Path, **kwargs):
    typer.secho(to_link(label, path), **kwargs)

def error(msg: str):
    typer.secho(msg, fg=typer.colors.RED, err=True)

def readable_type(o):
    return str(type(o)).split("'")[1]

def print_previous():
    if cfg.previous is None:
        return
    typer.secho('Previous:', fg=typer.colors.WHITE, bold=True, underline=True)
    to_link_secho(cfg.previous.stem, cfg.previous, fg=typer.colors.MAGENTA)

def print_next():
    if cfg.next is None:
        return
    typer.secho('Next:', fg=typer.colors.WHITE, bold=True, underline=True)
    to_link_secho(cfg.next.stem, cfg.next, fg=typer.colors.BLUE)
