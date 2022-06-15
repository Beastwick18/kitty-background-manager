from pathlib import Path
from pixcat import Image as PixImage
import typer
import beastwick18_kitty_background_manager.config as cfg

def get_app_file(file: str):
    app_dir = typer.get_app_dir(cfg.APP_NAME)
    app_path: Path = Path(app_dir)
    if not app_path.is_dir():
        app_path.mkdir(parents=True)
    path: Path = app_path / file
    return path.resolve()

def get_ext_in_path(path: Path, ext: str):
    if not path.is_dir():
        return
    
    for f in path.iterdir():
        if f.is_file() and f.suffix == ext and not f.stem == '':
            yield f.stem

def search_enabled_disabled(enabled, bg):
    if enabled or enabled is None:
        path1 = cfg.enabled_path
        path2 = cfg.disabled_path
    else:
        path1 = cfg.disabled_path
        path2 = cfg.enabled_path
    
    file = (path1 / (bg + '.png'))
    if file.exists():
        return file

    if enabled is None:
        file = (path2 / (bg + '.png'))
        if file.exists():
            return file

def preview_image(img: Path, size: int, fill: bool):
    file = str(img.resolve())
    if fill:
        PixImage(file).fit_screen(enlarge=True).show()
    else:
        PixImage(file).thumbnail(size).show(align='left')

def resolve_name_conflict(file: Path):
    n = 1
    while (file.with_stem(f'{file.stem}_{n}')).exists() and n < 1000:
        n += 1
    if n == 1000:
        return None
    return file.with_stem(f'{file.stem}_{n}')
