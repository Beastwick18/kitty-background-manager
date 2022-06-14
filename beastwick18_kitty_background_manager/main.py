import os
import json
import imghdr
import shutil
import random
from pathlib import Path
from PIL import Image, ImageEnhance
from pixcat import Image as PixImage
import typer
import beastwick18_kitty_background_manager.defaults as df

app = typer.Typer(help="A cli background manager for the Kitty terminal")

enabled_path: Path = Path(os.path.expandvars(df.ENABLED_PATH))
disabled_path: Path = Path(os.path.expandvars(df.DISABLED_PATH))
current_path: Path = Path(os.path.expandvars(df.CURRENT_PATH))

brightness = df.BRIGHTNESS
contrast = df.CONTRAST
preview_size = df.PREVIEW_SIZE
preview_on_add = df.PREVIEW_ON_ADD
preview_fill = df.PREVIEW_FILL
preview_align = df.PREVIEW_ALIGN

previous: Path = None
next: Path = None

def get_app_file(file: str):
    app_dir = typer.get_app_dir(df.APP_NAME)
    app_path: Path = Path(app_dir)
    if not app_path.is_dir():
        app_path.mkdir(parents=True)
    path: Path = app_path / file
    return path.resolve()

def generate_default_config():
    data = {}
    data['options'] = {}
    data['options']['brightness'] = df.BRIGHTNESS
    data['options']['contrast'] = df.CONTRAST
    data['options']['enabled_path'] = df.ENABLED_PATH
    data['options']['disabled_path'] = df.DISABLED_PATH
    data['options']['preview_size'] = df.PREVIEW_SIZE
    data['options']['preview_fill'] = df.PREVIEW_FILL
    data['options']['preview_on_add'] = df.PREVIEW_ON_ADD
    data['options']['preview_align'] = df.PREVIEW_ALIGN
    data['options']['current_path'] = df.CURRENT_PATH
    
    data['background'] = {}
    data['background']['next'] = ""
    data['background']['previous'] = ""
    
    config_path: Path = get_app_file(df.CONFIG_FILE)
    with config_path.open('w') as f:
        json_str = json.dumps(data, indent=4)
        f.write(json_str)

def to_link(label: str, path: Path):
    return f'\u001b]8;;file://{path}\a{label}\u001b]8;;\a'

def to_link_style(label: str, path: Path, **kwargs):
    return typer.style(to_link(label, path), **kwargs)

def to_link_secho(label: str, path: Path, **kwargs):
    typer.secho(to_link(label, path), **kwargs)

def load_options(options):
    if (b := options.get('brightness')) is not None:
        global brightness
        brightness = b
    
    if (c := options.get('contrast')) is not None:
        global contrast
        contrast = c
    
    if (e := options.get('enabled_path')) is not None:
        global enabled_path
        enabled_path = Path(os.path.expandvars(e))
    
    if (d := options.get('disabled_path')) is not None:
        global disabled_path
        disabled_path = Path(os.path.expandvars(d))
    
    if (ps := options.get('preview_size')) is not None:
        global preview_size
        preview_size = ps
    
    if (pf := options.get('preview_fill')) is not None:
        global preview_fill
        preview_fill = pf
    
    if (po := options.get('preview_on_add')) is not None:
        global preview_on_add
        preview_on_add = po
    
    if (cp := options.get('current_path')) is not None:
        global current_path
        current_path = Path(os.path.expandvars(cp))
    
def load_background(background):
    if (n := background.get('next')) is not None:
        global next
        next = Path(os.path.expandvars(n))
    
    if (p := background.get('previous')) is not None:
        global previous
        previous = Path(os.path.expandvars(p))

def load_config():
    config_path: Path = get_app_file(df.CONFIG_FILE)
    if not config_path.is_file():
        typer.echo(f'Config file does not exist, {to_link_style("creating it...", config_path.parent, fg=typer.colors.BLUE)}')
        generate_default_config()
        return
    
    with config_path.open('r') as f:
        data = json.load(f)
        if (options := data.get('options')) is not None:
            load_options(options)
        if (background := data.get('background')) is not None:
            load_background(background)

load_config()

def set_next(n: Path):
    if n is None:
        return
    global next
    next = n
    config_path: Path = get_app_file(df.CONFIG_FILE)
    
    with config_path.open('r+') as f:
        data = json.load(f)
        background = data.get('background')
        bg = {'background': {'next': str(next.resolve())}}
        
        if background is not None and (p := background.get('next')) is not None:
            bg['background']['previous'] = p
        
        data.update(bg)
        
        json_str = json.dumps(data, indent=4)
        
        f.seek(0)
        f.write(json_str)
        f.truncate()

def error(msg: str):
    typer.secho(msg, fg=typer.colors.RED, err=True)

def folder_contains_file(folder: Path, file: str):
    p: Path = folder / file
    return p.exists() and not p.is_dir()

def get_ext_in_path(path: Path, ext: str):
    if not path.is_dir():
        return
    
    for f in path.iterdir():
        if f.is_file() and f.suffix == ext and not f.stem == '':
            yield f.stem

# def remove_next_file():
#     for name in get_ext_in_path(enabled_path, '.next'):
#         (enabled_path / (name + '.next')).unlink()

# def list_next():
#     name = next(get_ext_in_path(enabled_path, '.next'), None)
#     if name is not None:
#         to_link_secho(name, enabled_path / (name + '.png'), fg=typer.colors.BLUE)
#     else:
#         error('There is no next file, cannot determine which background is next')

def print_previous():
    if previous is None:
        return
    typer.secho('Previous:', fg=typer.colors.WHITE, bold=True, underline=True)
    to_link_secho(previous.stem, next, fg=typer.colors.MAGENTA)

def print_next():
    if next is None:
        return
    typer.secho('Next:', fg=typer.colors.WHITE, bold=True, underline=True)
    to_link_secho(next.stem, next, fg=typer.colors.BLUE)

@app.command("list", short_help="List all enabled and disabled backgrounds, as well as the next background")
def cli_list(
        nxt: bool = typer.Option(False, '--next', '-n', help='The next background will be shown'),
        prev: bool = typer.Option(False, '--previous', '-p', help='The previous background will be shown'),
        enabled: bool = typer.Option(False, '--enabled', '-e', help='The enabled backgrounds will be shown'),
        disabled: bool = typer.Option(False, '--disabled', '-d', help='The disabled backgrounds will be shown')
        ):
    if not (nxt or prev or enabled or disabled):
        nxt = True
        prev = True
        enabled = True
        disabled = True
    
    if nxt and next is not None:
        print_next()
        typer.echo()
    
    if prev and previous is not None:
        print_previous()
        typer.echo()
    
    if enabled:
        typer.secho(f'Enabled {to_link("(📁)", enabled_path)}:', fg=typer.colors.WHITE, bold=True, underline=True)
        for name in get_ext_in_path(enabled_path, '.png'):
            to_link_secho(name, enabled_path / (name + '.png'), fg=typer.colors.GREEN)
        typer.echo()
    
    if disabled:
        typer.secho(f'Disabled {to_link("(📁)", disabled_path)}:', fg=typer.colors.WHITE, bold=True, underline=True)
        for name in get_ext_in_path(disabled_path, '.png'):
            to_link_secho(name, disabled_path / (name + '.png'), fg=typer.colors.RED)

@app.command("random", short_help="Set next background to a random enabled background")
def cli_random(
        silent: bool = typer.Option(False, "--silent", "-s", help="If present, there will be no output to stdout"),
        disabled: bool = typer.Option(False, "--disabled", "-d", help="Select a random background from the disabled folder")
        ):
    if disabled:
        path: Path = disabled_path
    else:
        path: Path = enabled_path
    bg = random.choice(list(get_ext_in_path(path, '.png')))
    file: Path = path / (bg + '.png')
    if not file.exists() or file.is_dir():
        error('Could not set a random background')
        return
    
    # remove_next_file()
    
    # (enabled_path / (bg + '.next')).touch()
    set_next(file)
    
    shutil.copy(file, current_path / df.CURRENT_FILE)
    
    if not silent:
        print_next()

@app.command(short_help="Enable a background that is currently disabled")
def enable(bg: str = typer.Argument(..., help="The name of the background to be enabled", autocompletion=(lambda: get_ext_in_path(disabled_path, '.png')))):
    file = disabled_path / (bg + '.png')
    if not file.exists():
        error(f'Cannot enable background: {bg}.png does not exist')
    elif file.is_dir():
        error(f'Cannot enable background: {bg}.png is a directory')
    else:
        typer.echo(f'Enabled {bg}.png')
        file.rename(enabled_path / (bg + '.png'))

@app.command(short_help="Disable a background that is currently enabled")
def disable(bg: str = typer.Argument(..., help="The name of the background to be enabled", autocompletion=(lambda: get_ext_in_path(enabled_path, '.png')))):
    file = enabled_path / (bg + '.png')
    if not file.exists():
        error(f'Cannot disable background: {bg}.png does not exist')
    elif file.is_dir():
        error(f'Cannot disable background: {bg}.png is a directory')
    else:
        typer.echo(f'Disabled {bg}.png')
        file.rename(disabled_path / (bg + '.png'))

def set_autocomplete():
    e = list(get_ext_in_path(enabled_path, '.png'))
    d = list(get_ext_in_path(disabled_path, '.png'))
    return e + d

def search_enabled_disabled(enabled, disabled, bg, op):
    first_occurence = False
    if not enabled and not disabled:
        first_occurence = True

    found = False
    if disabled or first_occurence:
        file = (disabled_path / (bg + '.png'))
        if file.exists():
            found = True
            op(file)

    if enabled or (first_occurence and not found):
        file = (enabled_path / (bg + '.png'))
        if file.exists():
            found = True
            op(file)
    return found

@app.command(short_help="Set next background to a specific background (can be an enabled or disabled background)")
def set(
        bg: str = typer.Argument(..., help="The name of the background to be set", autocompletion=set_autocomplete),
        enabled: bool = typer.Option(False, "--enabled", "-e", help="Only search through the enabled path for the background"),
        disabled: bool = typer.Option(False, "--disabled", "-d", help="Only search through the enabled path for the background"),
        silent: bool = typer.Option(False, "--silent", "-s", help="If present, there will be no output to stdout"),
        ):
    
    if enabled and disabled:
        enabled = False
        disabled = False
    
    file: Path = None
    def op(f: Path):
        nonlocal file
        file = f
    
    search_enabled_disabled(enabled, disabled, bg, op)
    
    if file is None:
        error(f'Could not set background {bg}.png')
        return
    
    # remove_next_file()
    
    # (enabled_path / (bg + '.next')).touch()
    set_next(file)
    
    shutil.copy(file, current_path / df.CURRENT_FILE)
    
    if not silent:
        print_next()

@app.command(short_help="Add an image to the background folder")
def add(
        path_to_file: str = typer.Argument(..., help="The path to the image to be added to the background folder"),
        b: float = typer.Option(brightness, "--brightness", help="Overrides the set value for brightness defined in the config file"),
        c: float = typer.Option(contrast, "--contrast", help="Overrides the set value for brightness defined in the config file"),
        preview: bool = typer.Option(preview_on_add, help="Overrides the set value for showing preview after adding an image")
        ):
    file: Path = Path(path_to_file)
    
    if not file.exists():
        error(f'Could not add {path_to_file}: The file does not exist')
    elif file.stem == '':
        error(f'Could not add {path_to_file}: {file.stem} is not a valid filename')
    elif imghdr.what(path_to_file) is None:
        error(f'Could not add {path_to_file}: The file is not an image')
    elif file.is_dir():
        error(f'Could not add {path_to_file}: The given path points to a directory')
        
    else:
        out_path = enabled_path / (file.stem + '.png')
        img = Image.open(path_to_file)
        enhancer = ImageEnhance.Contrast(img)
        img_out = enhancer.enhance(c)
        enhancer = ImageEnhance.Brightness(img_out)
        img_out = enhancer.enhance(b)
        img_out.save(str(out_path.resolve()))
        typer.echo(f'Added {to_link_style(file.stem, out_path, fg=typer.colors.GREEN)}')
        if preview:
            preview_image(out_path)

@app.command(short_help="Looks for the first occurence of a background in the disabled and enabled folder in that order and deletes it.")
def delete(
        bg: str = typer.Argument(..., help="The name of the background to be deleted from either the enabled or disabled folder", autocompletion=set_autocomplete),
        enabled: bool = typer.Option(False, "--enabled", help="Search for the background in the enabled folder"),
        disabled: bool = typer.Option(False, "--disabled", help="Search for the background in the disabled folder")
        ):
    if not search_enabled_disabled(enabled, disabled, bg, (lambda file: file.unlink())):
        error(f'Unable to find background "{bg}.png"')
    else:
        typer.secho(f'Deleted "{bg}.png"')

def preview_image(img: Path, size: int = preview_size, fill: bool = preview_fill):
    file = str(img.resolve())
    if fill:
        PixImage(file).fit_screen(enlarge=True).show()
    else:
        PixImage(file).thumbnail(size).show(align='left')

@app.command(short_help='Looks for the first occurence of a background in the disabled and enabled folder in that order and shows a preview')
def preview(
        bg: str = typer.Argument(..., help="The name of the background to be deleted from either the enabled or disabled folder", autocompletion=set_autocomplete),
        enabled: bool = typer.Option(False, "--enabled", help="Search for the background in the enabled folder"),
        disabled: bool = typer.Option(False, "--disabled", help="Search for the background in the disabled folder"),
        size: int = typer.Option(preview_size, "--size", help="Set the size for the outputted preview (value must be > 0 and <= 4096"),
        fill: bool = typer.Option(preview_fill, "--fill", help="Fill the screen with the image")
        ):
    if not fill and (size <= 0 or size > 4096):
        error(f'The given value of {size} is outside the range of 0<n<=4096')
        return
    
    def op(file):
        typer.echo(f'Previewing {to_link_style(file.name, file, fg=typer.colors.BLUE)}:')
        preview_image(file, size, fill)
    
    if not search_enabled_disabled(enabled, disabled, bg, op):
        error(f'Unable to find background "{bg}.png"')

@app.command(short_help="Initialize all required directories and create a config.json file if one does not exist")
def init():
    if not enabled_path.is_dir():
        enabled_path.mkdir(parents=True)
    if not disabled_path.is_dir():
        disabled_path.mkdir(parents=True)

@app.callback(invoke_without_command=True)
def default(ctx: typer.Context):
    init()
    
    if ctx.invoked_subcommand is not None:
        return
    
    cli_list()
