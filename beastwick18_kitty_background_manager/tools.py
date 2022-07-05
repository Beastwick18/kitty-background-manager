import re
from pathlib import Path
from pixcat import Image as PixImage
from PIL import ImageColor, Image, ImageEnhance, ImageOps
import typer
import beastwick18_kitty_background_manager.config as cfg
import beastwick18_kitty_background_manager.output as out

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

def preview_image(img: Path, size: int, fill: bool, a: str):
    file = str(img.resolve())
    if fill:
        PixImage(file).fit_screen(enlarge=True).show()
    else:
        PixImage(file).thumbnail(size).show(align=a)

def resolve_name_conflict(file: Path):
    n = 1
    while (file.with_stem(f'{file.stem}_{n}')).exists() and n < 1000:
        n += 1
    if n == 1000:
        return None
    return file.with_stem(f'{file.stem}_{n}')

def valid_color(property_name: str, hex: str):
    try:
        ImageColor.getrgb(hex)
    except ValueError:
        out.error(f'"{property_name}" cannot be set to value "{hex}": The given value is not a valid color')
        return False
    return True

def valid_dimensions(property_name: str, dim: str):
    w_h = dim.split('x')
    if len(w_h) != 2:
        out.error(f'"{property_name}" cannot be set to value "{dim}": The string must be of format "WxH" (example: "1920x1080")')
        return False
    w, h = w_h
    try:
        w = int(w)
        h = int(h)
    except:
        out.error(f'"{property_name}" cannot be set to value "{dim}": The width and height of the string must be integers')
        return False
    
    if w == 0 or h == 0:
        out.error(f'"{property_name}" cannot be set to value "{dim}": The width and height of the string cannot be 0')
        return False
    
    return True

def assert_range(property_name: str, low, high, value):
    if value < low or value > high:
        out.error(f'"{property_name}" cannot be set to value "{value}": The value must be within the range {low}-{high}')
        return False
    return True

def assert_type(property_name: str, value, valid_type):
    value_type = type(value)
    if isinstance(valid_type, tuple):
        if value_type not in valid_type:
            readable_types = tuple((str(x).split("\'")[1] for x in valid_type))
            out.error(f'"{property_name}" cannot be set to value "{value}": Expected value of type {readable_types} but got value of type {out.readable_type(value)}')
            return False
    elif value_type is not valid_type:
        readable = str(valid_type).split("'")[1]
        out.error(f'"{property_name}" cannot be set to value "{value}": Expected value of type {readable} but got value of type {out.readable_type(value)}')
        return False
    return True

def assert_in(property_name: str, value, values):
    if value not in values:
        out.error(f'{property_name} cannot be set to value "{value}": Possible values are {values}')
        return False
    return True

def set_brightness(img: Image, brightness: float):
    enhancer = ImageEnhance.Brightness(img)
    return enhancer.enhance(brightness)

def set_contrast(img: Image, contrast: float):
    enhancer = ImageEnhance.Contrast(img)
    return enhancer.enhance(contrast)

def scale_image(img: Image, scale_type: str, crop_w: int, crop_h: int, background_color: str):
    if not cfg.conf['scale_type'].validate(scale_type):
        out.error(f'{scale_type} is not a valid value for property "scale_type"')
        return
    elif scale_type == 'fit':
        bgcol = ImageColor.getrgb(background_color)
        img = ImageOps.pad(img, (crop_w, crop_h), color=bgcol)
        img = img.resize((crop_w, crop_h))
    elif scale_type == 'fill':
        img = ImageOps.fit(img, (crop_w, crop_h))
        img = img.resize((crop_w, crop_h))
    return img

