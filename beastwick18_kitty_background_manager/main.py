import os
import json
import imghdr
import shutil
import random
from typing import Optional
from enum import Enum
from pathlib import Path
from PIL import Image, ImageEnhance
from pixcat import Image as PixImage
import typer
import beastwick18_kitty_background_manager.config as cfg
import beastwick18_kitty_background_manager.output as out
import beastwick18_kitty_background_manager.tools as tools

app = typer.Typer(help="A cli background manager for the Kitty terminal")

if __name__ == 'beastwick18_kitty_background_manager.main':
    cfg.load_config()
    cfg.set_paths()

@app.command("list", short_help="List all enabled and disabled backgrounds, as well as the next background")
def cli_list(
        nxt: bool = typer.Option(False, '--next', '-n', help='Show the next background'),
        prev: bool = typer.Option(False, '--previous', '-p', help='Show the previous background'),
        enabled: bool = typer.Option(False, '--enabled', '-e', help='Show the enabled backgrounds'),
        disabled: bool = typer.Option(False, '--disabled', '-d', help='Show the disabled backgrounds')
        ):
    if not (nxt or prev or enabled or disabled):
        nxt = True
        prev = True
        enabled = True
        disabled = True
    
    if nxt and next is not None:
        out.print_next()
        typer.echo()
    
    if prev and cfg.previous is not None:
        out.print_previous()
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

@app.command("random", short_help="Set next background to a random enabled background")
def cli_random(
        silent: bool = typer.Option(False, "--silent", "-s", help="If present, there will be no output to stdout"),
        disabled: bool = typer.Option(False, "--disabled", "-d", help="Select a random background from the disabled folder")
        ):
    if disabled:
        path: Path = cfg.disabled_path
    else:
        path: Path = cfg.enabled_path
    bg = random.choice(list(tools.get_ext_in_path(path, '.png')))
    file: Path = path / (bg + '.png')
    if not file.exists() or file.is_dir():
        out.error('Could not set a random background')
        return
    
    cfg.set_next(file)
    
    shutil.copy(file, cfg.current_path / cfg.CURRENT_FILE)
    
    if not silent:
        out.print_next()

@app.command(short_help="Enable a background that is currently disabled")
def enable(bg: str = typer.Argument(..., help="The name of the background to be enabled", autocompletion=(lambda: tools.get_ext_in_path(cfg.disabled_path, '.png')))):
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
                out.error("Unable to add image: Cannot find an unused filename")
                return
            out_path = new_path
        
        file.rename(out_path)

@app.command(short_help="Disable a background that is currently enabled")
def disable(bg: str = typer.Argument(..., help="The name of the background to be enabled", autocompletion=(lambda: tools.get_ext_in_path(cfg.enabled_path, '.png')))):
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
                out.error("Unable to add image: Cannot find an unused filename")
                return
            out_path = new_path
        
        file.rename(out_path)

def set_autocomplete():
    e = list(tools.get_ext_in_path(cfg.enabled_path, '.png'))
    d = list(tools.get_ext_in_path(cfg.disabled_path, '.png'))
    return e + d

@app.command(short_help="Set next background to a specific background (can be an enabled or disabled background)")
def set(
        bg: str = typer.Argument(..., help="The name of the background to be set", autocompletion=set_autocomplete),
        enabled: Optional[bool] = typer.Option(None, "--enabled/--disabled", "-e/-d", help="Only search through the enabled/disabled path for the background"),
        silent: bool = typer.Option(False, "--silent", "-s", help="If present, there will be no output to stdout")
        ):
    
    file = tools.search_enabled_disabled(enabled, bg)
    
    if file is None:
        out.error(f'Could not set background {bg}.png')
        return
    
    cfg.set_next(file)
    
    shutil.copy(file, cfg.current_path / cfg.CURRENT_FILE)
    
    if not silent:
        out.print_next()

@app.command(short_help="Add an image to the background folder")
def add(
        path_to_file: str = typer.Argument(..., help="The path to the image to be added to the background folder"),
        b: float = typer.Option(cfg.conf["brightness"], "--brightness", help="Overrides the set value for brightness defined in the config file"),
        c: float = typer.Option(cfg.conf["contrast"], "--contrast", help="Overrides the set value for brightness defined in the config file"),
        enabled: bool = typer.Option(True, "--enabled/--disabled", "-e/-d", help="Add the new image to the enabled/disabled folder"),
        preview: bool = typer.Option(cfg.conf["preview_on_add"], help="Overrides the set value for showing preview after adding an image"),
        size: int = typer.Option(cfg.conf["preview_size"], "--size", help="Set the size for the outputted preview (value must be > 0 and <= 4096"),
        fill: bool = typer.Option(cfg.conf["preview_fill"], help="Fill the screen with the image"),
        crop_size: str = typer.Option(cfg.conf["crop_size"], "--crop-size", help="Determines the size of the cropped image. Should be in the format \"WxH\""),
        scale_type: str = typer.Option(cfg.conf["scale_type"], "--scale-type", help="Determines how the image should be positioned once resized"),
        out_opt: Optional[str] = typer.Option(None, "--out", "-o", help="Set the output filename")
        ):
    file: Path = Path(path_to_file)
    
    if not file.exists():
        out.error(f'Could not add {path_to_file}: The file does not exist')
    elif file.stem == '':
        out.error(f'Could not add {path_to_file}: {file.stem} is not a valid filename')
    elif imghdr.what(path_to_file) is None:
        out.error(f'Could not add {path_to_file}: The file is not an image')
    elif file.is_dir():
        out.error(f'Could not add {path_to_file}: The given path points to a directory')
    else:
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
        
        if out_path.exists():
            new_path = tools.resolve_name_conflict(out_path)
            if new_path is None:
                out.error("Unable to add image: Cannot find an unused filename")
                return
            
            can_rename = typer.confirm(f'"{out_path.stem}" already exists. Rename "{out_path.stem}" to "{new_path.stem}" instead?')
            if not can_rename:
                return
            out_path = new_path
        
        img = Image.open(path_to_file)
        enhancer = ImageEnhance.Contrast(img)
        img_out = enhancer.enhance(c)
        enhancer = ImageEnhance.Brightness(img_out)
        img_out = enhancer.enhance(b)
        
        img_out.save(str(out_path.resolve()))
        
        typer.echo(f'Added {out.to_link_style(out_path.name, out_path, fg=col)}')
        if preview:
            tools.preview_image(out_path, size, fill)

@app.command(short_help="Looks for the first occurence of a background in the disabled and enabled folder in that order and deletes it.")
def delete(
        bg: str = typer.Argument(..., help="The name of the background to be deleted from either the enabled or disabled folder", autocompletion=set_autocomplete),
        enabled: Optional[bool] = typer.Option(None, "--enabled/--disabled", "-e/-d", help="Search for the background in the enabled/disabled folder"),
        force: bool = typer.Option(False, "--force", "-f", help="Force the file to be deleted without asking for confimation")
        ):
    if (file := tools.search_enabled_disabled(enabled, bg)) is not None:
        if not force:
            if file.parent.resolve() == cfg.enabled_path.resolve():
                col = typer.colors.GREEN
                path_name = "enabled"
            else:
                col = typer.colors.RED
                path_name = "disabled"
            can_delete = typer.confirm(f'Are you sure you want to delete {out.to_link_style(bg, file, fg=col)} from the {path_name} folder')
            if not can_delete:
                return
        file.unlink()
        typer.secho(f'Deleted "{file.name}"')
    else:
        out.error(f'Unable to find background "{bg}.png"')

@app.command(short_help="Rename a background in the enabled/disabled folder to a new name")
def rename(
        bg: str = typer.Argument(..., help="The name of the background to be renamed from either the enabled or disabled folder", autocompletion=set_autocomplete),
        new_name: str = typer.Argument(..., help="The new name of the background", autocompletion=set_autocomplete),
        enabled: Optional[bool] = typer.Option(None, "--enabled/--disabled", "-e/-d", help="Search for the background in the enabled/disabled folder"),
        force: bool = typer.Option(False, "--force", "-f", help="Force the file to be renamed (without naming conflicts) without asking for confimation"),
        overwrite: bool = typer.Option(False, "--overwrite", "-o", help="In the case that the renamed file already exists, it will be overwritten")
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
        bg: str = typer.Argument(..., help="The name of the background to be deleted from either the enabled or disabled folder", autocompletion=set_autocomplete),
        enabled: Optional[bool] = typer.Option(None, "--enabled/--disabled", "-e/-d", help="Search for the background in the enabled folder"),
        size: int = typer.Option(cfg.conf["preview_size"], "--size", "-s", help="Set the size for the outputted preview (value must be > 0 and <= 4096"),
        fill: bool = typer.Option(cfg.conf["preview_fill"], "--fill/--thumbnail", "-f", help="Do/Don't fill the screen with the image")
        ):
    if not fill and (size <= 0 or size > 4096):
        out.error(f'The given value of {size} is outside the range of 0<n<=4096')
        return
    
    if (file := tools.search_enabled_disabled(enabled, bg)) is not None:
        typer.echo(f'Previewing {out.to_link_style(file.name, file, fg=typer.colors.BLUE)}:')
        tools.preview_image(file, size, fill)
    else:
        out.error(f'Unable to find background "{bg}.png"')

@app.command(short_help="Initialize all required directories and create a config.json file if one does not exist")
def init():
    if not cfg.enabled_path.is_dir():
        cfg.enabled_path.mkdir(parents=True)
    if not cfg.disabled_path.is_dir():
        cfg.disabled_path.mkdir(parents=True)

@app.callback(invoke_without_command=True)
def default(ctx: typer.Context):
    init()
    
    if ctx.invoked_subcommand is not None:
        return
    
    cli_list()
