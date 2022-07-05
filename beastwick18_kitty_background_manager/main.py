import os
import json
import imghdr
import shutil
import random
from typing import Optional, List
from enum import Enum
from pathlib import Path
from PIL import Image, ImageEnhance, ImageOps, ImageColor
from pixcat import Image as PixImage
import typer
import beastwick18_kitty_background_manager.config as cfg
import beastwick18_kitty_background_manager.output as out
import beastwick18_kitty_background_manager.tools as tools

app = typer.Typer(help='A cli background manager for the Kitty terminal')

cfg.load_config()
cfg.set_paths()

@app.command('list', short_help='List all enabled and disabled backgrounds, as well as the next background')
def cli_list(
    next: Optional[bool] = typer.Option(None, '--next', '-n', help='Show the next background'),
    prev: Optional[bool] = typer.Option(None, '--previous', '-p', help='Show the previous background'),
    enabled: Optional[bool] = typer.Option(None, '--enabled', '-e', help='Show the enabled backgrounds'),
    disabled: Optional[bool] = typer.Option(None, '--disabled', '-d', help='Show the disabled backgrounds')
):
    # Show all if use does not specify any category
    if next is None and prev is None and enabled is None and disabled is None:
        next = True
        prev = True
        enabled = True
        disabled = True
    
    if next and (n := cfg.get_next()) is not None:
        typer.secho('Next:', fg=typer.colors.WHITE, bold=True, underline=True)
        out.to_link_secho(n, cfg.next, fg=typer.colors.BLUE)
        typer.echo()
        
    
    if prev and (p := cfg.get_previous()) is not None:
        typer.secho('Previous:', fg=typer.colors.WHITE, bold=True, underline=True)
        out.to_link_secho(p, cfg.previous, fg=typer.colors.MAGENTA)
        typer.echo()
    
    if enabled:
        typer.secho(f'Enabled {out.to_link("(📁)", cfg.enabled_path)}:', fg=typer.colors.WHITE, bold=True, underline=True)
        for name in tools.get_ext_in_path(cfg.enabled_path, '.png'):
            out.to_link_secho(name, cfg.enabled_path / (name + '.png'), fg=typer.colors.GREEN)
        typer.echo()
    
    if disabled:
        typer.secho(f'Disabled {out.to_link("(📁)", cfg.disabled_path)}:', fg=typer.colors.WHITE, bold=True, underline=True)
        for name in tools.get_ext_in_path(cfg.disabled_path, '.png'):
            out.to_link_secho(name, cfg.disabled_path / (name + '.png'), fg=typer.colors.RED)

@app.command('random', short_help='Set next background to a random enabled background')
def cli_random(
    silent: bool = typer.Option(False, '--silent', '-s', help='If present, there will be no output to stdout'),
    disabled: bool = typer.Option(False, '--disabled', '-d', help='Select a random background from the disabled folder')
):
    if disabled:
        path: Path = cfg.disabled_path
    else:
        path: Path = cfg.enabled_path
    files = list(tools.get_ext_in_path(path, '.png'))
    if len(files) <= 0:
        return
    bg = random.choice(files)
    file: Path = path / (bg + '.png')
    if not file.exists() or file.is_dir():
        out.error('Could not set a random background')
        return
    
    cfg.set_next(file)
    
    shutil.copy(file, cfg.current_path / cfg.CURRENT_FILE)
    
    if not silent:
        typer.secho('Next:', fg=typer.colors.WHITE, bold=True, underline=True)
        out.to_link_secho(cfg.next.stem, cfg.next, fg=typer.colors.BLUE)

@app.command(short_help='Enable a background that is currently disabled')
def enable(bg: str = typer.Argument(..., help='The name of the background to be enabled', autocompletion=(lambda: tools.get_ext_in_path(cfg.disabled_path, '.png')))):
    file = cfg.disabled_path / (bg + '.png')
    if not file.exists():
        out.error(f'Cannot enable background: {bg}.png does not exist')
    elif file.is_dir():
        out.error(f'Cannot enable background: {bg}.png is a directory')
    else:
        typer.echo(f'Enabled {bg}.png')
        out_path = cfg.enabled_path / (bg + '.png')
        if out_path.exists():
            new_path = tools.resolve_name_conflict(out_path)
            if new_path is None:
                out.error('Unable to add image: Cannot find an unused filename')
                return
            out_path = new_path
        
        file.rename(out_path)

@app.command(short_help='Disable a background that is currently enabled')
def disable(bg: str = typer.Argument(..., help='The name of the background to be enabled', autocompletion=(lambda: tools.get_ext_in_path(cfg.enabled_path, '.png')))):
    file = cfg.enabled_path / (bg + '.png')
    if not file.exists():
        out.error(f'Cannot disable background: {bg}.png does not exist')
    elif file.is_dir():
        out.error(f'Cannot disable background: {bg}.png is a directory')
    else:
        typer.echo(f'Disabled {bg}.png')
        out_path = cfg.disabled_path / (bg + '.png')
        if out_path.exists():
            new_path = tools.resolve_name_conflict(out_path)
            if new_path is None:
                out.error('Unable to add image: Cannot find an unused filename')
                return
            out_path = new_path
        
        file.rename(out_path)

def set_autocomplete(ctx: typer.Context, incomplete: str):
    enabled = ctx.params.get('enabled')
    if enabled is None:
        e = list(tools.get_ext_in_path(cfg.enabled_path, '.png'))
        d = list(tools.get_ext_in_path(cfg.disabled_path, '.png'))
        return e + d
    elif enabled:
        return [i for i in tools.get_ext_in_path(cfg.enabled_path, '.png')]
    return tools.get_ext_in_path(cfg.disabled_path, '.png')

@app.command(short_help='Set next background to a specific background (can be an enabled or disabled background)')
def set(
    bg: str = typer.Argument(..., help='The name of the background to be set', autocompletion=set_autocomplete),
    enabled: Optional[bool] = typer.Option(None, '--enabled/--disabled', '-e/-d', help='Only search through the enabled/disabled path for the background'),
    silent: bool = typer.Option(False, '--silent', '-s', help='If present, there will be no output to stdout')
):
    
    file = tools.search_enabled_disabled(enabled, bg)
    
    if file is None:
        out.error(f'Could not set background {bg}.png')
        return
    
    cfg.set_next(file)
    
    shutil.copy(file, cfg.current_path / cfg.CURRENT_FILE)
    
    if not silent:
        typer.secho('Next:', fg=typer.colors.WHITE, bold=True, underline=True)
        out.to_link_secho(cfg.next.stem, cfg.next, fg=typer.colors.BLUE)

@app.command(short_help='Add an image to the background folder')
def add(
    path_to_file: str = typer.Argument(..., help='The path to the image to be added to the background folder'),
    brightness: float = typer.Option(cfg.conf['brightness'].value, '--brightness', '-b', help='Overrides the set value for brightness defined in the config file'),
    contrast: float = typer.Option(cfg.conf['contrast'].value, '--contrast', '-c', help='Overrides the set value for brightness defined in the config file'),
    enabled: bool = typer.Option(True, '--enabled/--disabled', '-e/-d', help='Add the new image to the enabled/disabled folder'),
    preview: bool = typer.Option(cfg.conf['preview_on_add'].value, help='Overrides the set value for showing preview after adding an image'),
    size: int = typer.Option(cfg.conf['preview_size'].value, '--size', help='Set the size for the outputted preview (value must be > 0 and <= 4096'),
    fill: bool = typer.Option(cfg.conf['preview_fill'].value, help='Fill the screen with the image'),
    align: str = typer.Option(cfg.conf['preview_align'].value, '--align', '-a', help='Choose how to align the preview image. Valid values are ("left", "center", "right")'),
    crop_size: str = typer.Option(cfg.conf['crop_size'].value, '--crop-size', help='Determines the size of the cropped image. Should be in the format "WxH"'),
    scale_type: str = typer.Option(cfg.conf['scale_type'].value, '--scale-type', help='Determines how the image should be positioned once resized'),
    out_opt: Optional[str] = typer.Option(None, '--out', '-o', help='Set the output filename'),
    force: bool = typer.Option(False, '--force', '-f', help='Overwrite any existing file that has the same name'),
    background_color: str = typer.Option(cfg.conf['background_color'].value, '--background-color', '-b', help='Overrides the configured color to fill the background with')
):
    if not cfg.conf['preview_align'].validate(align):
        out.error(f'{align} is not a valid value for align option. Valid values are ("left", "center", "right")')
        return
    if not fill and (size <= 0 or size > 4096):
        out.error(f'The given value of {size} is outside the range of 0<n<=4096')
        return
        
    file = Path(path_to_file)
    if not file.exists():
        out.error(f'Could not add {path_to_file}: The file does not exist')
        return
    if file.stem == '':
        out.error(f'Could not add {path_to_file}: {file.stem} is not a valid filename')
        return
    if imghdr.what(path_to_file) is None:
        out.error(f'Could not add {path_to_file}: The file is not an image')
        return
    if file.is_dir():
        out.error(f'Could not add {path_to_file}: The given path points to a directory')
        return
    
    if enabled:
        col = typer.colors.GREEN
        path = cfg.enabled_path
    else:
        col = typer.colors.RED
        path = cfg.disabled_path
    
    if out_opt is None:
        out_path = path / file.with_suffix('.png').name
    else:
        out_path = path / file.with_stem(out_opt).with_suffix('.png').name
    
    if not force and out_path.exists():
        new_path = tools.resolve_name_conflict(out_path)
        if new_path is None:
            out.error('Unable to add image: Cannot find an unused filename')
            return
        
        can_rename = typer.confirm(f'"{out_path.stem}" already exists. Rename "{out_path.stem}" to "{new_path.stem}" instead?')
        if not can_rename:
            return
        out_path = new_path
    
    img = Image.open(path_to_file)
    
    crop_props = crop_size.strip().split('x')
    if len(crop_props) != 2:
        out.error(f'crop_size\'s value of "{crop_size}" is incorrect. Should be in the format "WxH"')
        return
    crop_w, crop_h = (int(crop_props[0]), int(crop_props[1]))
    img = tools.scale_image(img, scale_type, crop_w, crop_h, background_color)
    
    if contrast != 1:
        img = tools.set_contrast(img, contrast)
    if brightness != 1:
        img = tools.set_brightness(img, brightness)
    
    img.save(str(out_path.resolve()))
    
    typer.echo(f'Added {out.to_link_style(out_path.name, out_path, fg=col)}')
    if preview:
        tools.preview_image(out_path, size, fill, align)

@app.command(short_help='Looks for the first occurence of a background in the disabled and enabled folder in that order and deletes it.')
def delete(
        bg: str = typer.Argument(..., help='The name of the background to be deleted from either the enabled or disabled folder', autocompletion=set_autocomplete),
        enabled: Optional[bool] = typer.Option(None, '--enabled/--disabled', '-e/-d', help='Search for the background in the enabled/disabled folder'),
        force: bool = typer.Option(False, '--force', '-f', help='Force the file to be deleted without asking for confimation')
        ):
    if (file := tools.search_enabled_disabled(enabled, bg)) is not None:
        if not force:
            if file.parent.resolve() == cfg.enabled_path.resolve():
                col = typer.colors.GREEN
                path_name = 'enabled'
            else:
                col = typer.colors.RED
                path_name = 'disabled'
            can_delete = typer.confirm(f'Are you sure you want to delete {out.to_link_style(bg, file, fg=col)} from the {path_name} folder')
            if not can_delete:
                return
        file.unlink()
        typer.secho(f'Deleted "{file.name}"')
    else:
        out.error(f'Unable to find background "{bg}.png"')

@app.command(short_help='Rename a background in the enabled/disabled folder to a new name')
def rename(
        bg: str = typer.Argument(..., help='The name of the background to be renamed from either the enabled or disabled folder', autocompletion=set_autocomplete),
        new_name: str = typer.Argument(..., help='The new name of the background', autocompletion=set_autocomplete),
        enabled: Optional[bool] = typer.Option(None, '--enabled/--disabled', '-e/-d', help='Search for the background in the enabled/disabled folder'),
        force: bool = typer.Option(False, '--force', '-f', help='Force the file to be renamed (without naming conflicts) without asking for confimation'),
        overwrite: bool = typer.Option(False, '--overwrite', '-o', help='In the case that the renamed file already exists, it will be overwritten')
        ):
    if (file := tools.search_enabled_disabled(enabled, bg)) is not None:
        new_file = file.with_stem(new_name)
        if not overwrite and new_file.exists():
            new_file = tools.resolve_name_conflict(new_file)
            if not force:
                if new_file is None:
                    out.error(f'Unable to rename {bg} to {new_name}')
                    return
                
                can_rename = typer.confirm(f'"{new_name}" already exists. Rename "{bg}" to "{new_file.stem}" instead?')
                if not can_rename:
                    return
            
        file.replace(new_file)
        typer.secho(f'Renamed "{bg}" to "{new_file.stem}"')
    else:
        out.error(f'Unable to find background "{bg}.png"')

@app.command(short_help='Looks for the first occurence of a background in the disabled and enabled folder in that order and shows a preview')
def preview(
        bg: str = typer.Argument(..., help='The name of the background to be deleted from either the enabled or disabled folder', autocompletion=set_autocomplete),
        enabled: Optional[bool] = typer.Option(None, '--enabled/--disabled', '-e/-d', help='Search for the background in the enabled folder'),
        size: int = typer.Option(cfg.conf['preview_size'].value, '--size', '-s', help='Set the size for the outputted preview (value must be > 0 and <= 4096'),
        fill: bool = typer.Option(cfg.conf['preview_fill'].value, '--fill/--thumbnail', '-f', help='Show the image as a thumbnail or fill the screen'),
        align: str = typer.Option(cfg.conf['preview_align'].value, '--align', '-a', help='Choose how to align the preview image. Valid values are ("left", "center", "right")')
        ):
    if not fill and (size <= 0 or size > 4096):
        out.error(f'The given value of {size} is outside the range of 0<n<=4096')
        return
    if align not in ('left', 'center', 'right'):
        out.error(f'{align} is not a valid value for align option. Valid values are ("left", "center", "right")')
        return
    
    if (file := tools.search_enabled_disabled(enabled, bg)) is not None:
        typer.echo(f'Previewing {out.to_link_style(file.name, file, fg=typer.colors.BLUE)}:')
        tools.preview_image(file, size, fill, align)
    else:
        out.error(f'Unable to find background "{bg}.png"')

def value_completion(ctx: typer.Context):
    property = ctx.params.get('property')
    if property is None or property not in cfg.conf:
        return ['']
    
    val = cfg.conf[property].value
    if type(val) == type(True):
        return ['False', 'True']
    else:
        return [str(val)]

@app.command(short_help='Quickly find and set properties in the config file')
def config(
        property: str = typer.Argument(..., help='The name of the property to configure. This name is the same as the one in your config.json file', autocompletion=(lambda: cfg.conf.keys())),
        value: Optional[str] = typer.Argument(None, help='The value you wish to set the property to', autocompletion=value_completion)
        ):
    if property not in cfg.conf:
        out.error(f'Unknown property: "{property}"')
        return
    
    if value is None:
        typer.echo(f'{property} = {cfg.conf[property].value}')
        return
    
    try:
        new_value = type(cfg.conf[property].value)(value)
    except (TypeError, ValueError):
        out.error(f'Cannot set property "{property}" to value "{value}": Cannot convert to type "{out.readable_type(cfg.conf[property].value)}"')
    else:
        if not cfg.conf[property].validate(new_value):
            out.error(f'Cannot set property "{property}" to value "{value}": The given value is not valid')
            return
        cfg.conf[property].value = new_value
        cfg.save_config()
        typer.echo(f'Set "{property}" to "{new_value}"')


@app.command(short_help='Initialize all required directories and create a config.json file if one does not exist')
def init():
    if not cfg.enabled_path.is_dir():
        cfg.enabled_path.mkdir(parents=True)
    if not cfg.disabled_path.is_dir():
        cfg.disabled_path.mkdir(parents=True)
    if not cfg.current_path.is_dir():
        cfg.current_path.mkdir(parents=True)

@app.callback(invoke_without_command=True)
def default(ctx: typer.Context):
    init()
    
    if ctx.invoked_subcommand is not None:
        return
    
    cli_list()
