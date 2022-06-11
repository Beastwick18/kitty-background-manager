from PIL import Image, ImageEnhance
import json
from pathlib import Path
import builtins
import imghdr
import os
import click
from os.path import isdir, dirname, exists
import shutil
import random as rand
import typer
from typing import Optional

APP_NAME = "kittybg"

enabled_path = os.path.expandvars('/home/$USER/Pictures/kittyWallpapers/')
disabled_path = os.path.expandvars(enabled_path + 'disabled/')
app = typer.Typer()
brightness = 0.1
contrast = 1.0

def init_dirs():
    e: Path = Path(enabled_path)
    d: Path = Path(disabled_path)
    if not e.is_dir():
        e.mkdir(parents=True)
    if not d.is_dir():
        d.mkdir(parents=True)

def load_config():
    app_dir = typer.get_app_dir(APP_NAME)
    app_path: Path = Path(app_dir)
    config_path: Path = app_path / "config.json"
    if not app_path.is_dir():
        app_path.mkdir(parents=True)
    if not config_path.is_file():
        with config_path.open('w') as _:
            pass
        typer.echo(f'Config file does not exist, {typer.style(to_link("creating it...", app_dir), fg=typer.colors.BLUE)}')
        return
    with open(config_path) as f:
        data = json.load(f)
        options = data.get('options')
        if options is None:
            return
        
        if b := options.get('brightness'):
            global brightness
            brightness = b
        
        if c := options.get('contrast'):
            global contrast
            contrast = c
        
        if e := options.get('enabled_path'):
            global enabled_path
            enabled_path = os.path.expandvars(e)
        
        if d := options.get('disabled_path'):
            global disabled_path
            disabled_path = os.path.expandvars(d)
        

def folder_contains_file(folder: str, file: str):
    for f in os.listdir(folder):
        if not isdir(f) and exists(folder + file):
            return True
    return False

def get_ext_in_path(path: str, ext: str):
    for f in os.listdir(path):
        currfile = path + f
        if not isdir(currfile):
            # Split at file extension
            file = f.rsplit('.', 1)
            
            if len(file) >= 2:
                name, e = file
                if not name == '' and e == ext:
                    yield name

def remove_next_file():
    for name in get_ext_in_path(enabled_path, 'next'):
        os.remove(enabled_path + name + '.next')


def to_link(label: str, path: str):
    return f'\u001b]8;;file://{path}\a{label}\u001b]8;;\a'

def list_next():
    name = next(get_ext_in_path(enabled_path, 'next'), None)
    if name:
        typer.secho(to_link(name, enabled_path + name + '.png'), fg=typer.colors.BLUE)
    else:
        typer.secho("There is no next file, cannot determine which background is next", fg=typer.colors.RED, err=True)

@app.command()
def list():
    """
    List all enabled and disabled backgrounds, as well as the next background
    """
    
    typer.secho('Next:', fg=typer.colors.WHITE, bold=True, underline=True)
    list_next()
    
    typer.secho('\nEnabled ' + to_link('(📁)', enabled_path) + ':', fg=typer.colors.WHITE, bold=True, underline=True)
    for i in get_ext_in_path(enabled_path, 'png'):
        typer.secho(to_link(i, enabled_path + i + '.png'), fg=typer.colors.GREEN)
    
    typer.echo(typer.style('\nDisabled ' + to_link('(📁)', disabled_path) + ':', fg=typer.colors.WHITE, bold=True, underline=True))
    for i in get_ext_in_path(disabled_path, 'png'):
        typer.secho(to_link(i, disabled_path + i + '.png'), fg=typer.colors.RED)

def silent_callback(silent: bool):
    bg = rand.choice(builtins.list(get_ext_in_path(enabled_path, 'png')))
    
    file = enabled_path + bg + '.png'
    if not exists(file) or isdir(file):
        file = disabled_path + bg + '.png'
        if not exists(file) or isdir(file):
            typer.secho('Could not set a random background', fg=typer.colors.RED, err=True)
            return
    
    remove_next_file()
    
    with open(enabled_path + bg + '.next', 'w') as _:
        pass
    
    shutil.copy(file, enabled_path + 'current/current.png')
    
    if not silent:
        typer.secho('Next:', fg=typer.colors.WHITE, bold=True, underline=True)
        list_next()

@app.command()
def random(s: Optional[bool] = typer.Option(None, "--silent", help="If present, there will be no output to stdout", callback=silent_callback)):
    """
    Set next background to a random one
    """

@app.command()
def enable(bg: str = typer.Argument("Background", help="The name of the background to be enabled", autocompletion=(lambda: get_ext_in_path(disabled_path, 'png')))):
    """
    Enable a background that is currently disabled
    """
    
    file = disabled_path + bg + '.png'
    if not exists(file):
        typer.secho(f'Cannot enable background: {bg}.png does not exist', fg=typer.colors.RED, err=True)
    elif isdir(file):
        typer.secho(f'Cannot enable background: {bg}.png is a directory', fg=typer.colors.RED, err=True)
    elif not folder_contains_file(disabled_path, bg+'.png'):
        typer.secho(f'Cannot enable background: {bg}.png is not present within the disabled background path', fg=typer.colors.RED, err=True)
    else:
        typer.echo(f'Enabled {bg}.png')
        shutil.move(file, enabled_path + bg + '.png')

@app.command()
def disable(bg: str = typer.Argument("Background", help="The name of the background to be enabled", autocompletion=(lambda: get_ext_in_path(enabled_path, 'png')))):
    """
    Disable a background that is currently enabled
    """
    
    file = enabled_path + bg + '.png'
    if not exists(file):
        typer.secho(f'Cannot enable background: {bg}.png does not exist', fg=typer.colors.RED, err=True)
    elif isdir(file):
        typer.secho(f'Cannot enable background: {bg}.png is a directory', fg=typer.colors.RED, err=True)
    elif not folder_contains_file(enabled_path, bg+'.png'):
        typer.secho(f'Cannot enable background: {bg}.png is not present within the disabled background path', fg=typer.colors.RED, err=True)
    else:
        typer.echo(f'Disabled {bg}.png')
        shutil.move(file, disabled_path + bg + '.png')

def set_autocomplete():
    e = builtins.list(get_ext_in_path(enabled_path, 'png'))
    d = builtins.list(get_ext_in_path(disabled_path, 'png'))
    return e + d

@app.command()
def set(bg: str = typer.Argument("Background", help="The name of the background to be set", autocompletion=set_autocomplete)):
    """
    Set next background to a specific background (can be an enabled or disabled background)
    """
    
    file = enabled_path + bg + '.png'
    if not exists(file) or isdir(file):
        file = disabled_path + bg + '.png'
        if not exists(file) or isdir(file):
            typer.secho(f'Could not set background: {file} is not a valid background', fg=typer.colors.RED, err=True)
            return
    
    remove_next_file()
    
    with open(enabled_path + bg + '.next', 'w') as _:
        pass
    
    shutil.copy(file, enabled_path + 'current/current.png')
    
    typer.secho('Next:', fg=typer.colors.WHITE, bold=True, underline=True)
    list_next()

@app.command()
def add(path_to_file: str = typer.Argument("Path to image", help="The path to the image to be added to the background folder")):
    """
    Add an image to the background folder
    """
    file = os.path.basename(path_to_file)
    props = file.rsplit('.', 1)
    
    if not exists(path_to_file):
        typer.secho(f'Could not add {path_to_file}: The file does not exist', fg=typer.colors.RED, err=True)
    elif isdir(path_to_file):
        typer.secho(f'Could not add {path_to_file}: The given path points to a directory', fg=typer.colors.RED, err=True)
    elif not len(props) >= 2 or props[0] == '' or props[1] == '':
        typer.secho(f'Could not add {path_to_file}: {file} is not a valid filename', fg=typer.colors.RED, err=True)
    # elif not len(props) >= 2 or not props[1] == 'png':
    #     typer.secho(f'Could not add {path_to_file}: {file} is not of type ".png"', fg=typer.colors.RED, err=True)
    elif imghdr.what(path_to_file) == None:
        # Given file is not an image
        typer.secho(f'Could not add {path_to_file}: The file is not an image', fg=typer.colors.RED, err=True)
    else:
        out_path = enabled_path + props[0] + '.png'
        img = Image.open(path_to_file)
        enhancer = ImageEnhance.Contrast(img)
        img_out = enhancer.enhance(contrast)
        enhancer = ImageEnhance.Brightness(img_out)
        img_out = enhancer.enhance(brightness)
        img_out.save(out_path)
        # img_out.save(out_path+'.png')
        typer.echo('Added ' + typer.style(to_link(props[0], out_path), fg=typer.colors.GREEN))

@app.command()
def delete(bg: str = typer.Argument("Background", help="The name of the background to be deleted from either the enabled or disabled folder")):
    """
    Delete an image from the background folder
    """

@app.command()
def init():
    """
    Initialize all required directories and create a config.json file if one does not exist
    """
    # TODO: Implement this

@app.callback(invoke_without_command=True)
def default(ctx: typer.Context):
    """
    A cli background manager for the Kitty terminal
    """
    load_config()
    init_dirs()
    
    if ctx.invoked_subcommand is not None:
        return
    
    list()
