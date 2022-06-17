import os
from enum import Enum
from pathlib import Path
import json
import typer
import beastwick18_kitty_background_manager.tools as tools
import beastwick18_kitty_background_manager.output as out

APP_NAME = 'kittybg'
CONFIG_FILE = 'config.json'
CURRENT_FILE = 'current.png'

enabled_path: Path = None
disabled_path: Path = None
current_path: Path = None

previous: Path = None
next: Path = None

conf = {
    'brightness': 0.1,
    'contrast': 1.0,
    'enabled_path': '/home/$USER/Pictures/kittyWallpapers/',
    'disabled_path': '/home/$USER/Pictures/kittyWallpapers/disabled/',
    'current_path': '/home/$USER/Pictures/kittyWallpapers/current/',
    'preview_size': 512,
    'preview_align': 'left',
    'crop_and_scale': True,
    'crop_size': '1920x1080',
    'scale_type': 'fill',
    'background_color': '#FF8800',
    'preview_on_add': True,
    'preview_fill': False
}

def generate_default_config():
    data = {}
    data['options'] = conf
    
    data['background'] = {}
    data['background']['next'] = ''
    data['background']['previous'] = ''
    
    config_path: Path = tools.get_app_file(CONFIG_FILE)
    with config_path.open('w') as f:
        json_str = json.dumps(data, indent=4)
        f.write(json_str)

def set_paths():
    global enabled_path, disabled_path, current_path
    enabled_path = Path(os.path.expandvars(conf['enabled_path']))
    disabled_path = Path(os.path.expandvars(conf['disabled_path']))
    current_path = Path(os.path.expandvars(conf['current_path']))

def load_options(options):
    err = False
    for name, value in conf.items():
        if (o := options.get(name)) is not None:
            if type(o) == type(value):
                conf[name] = o
            else:
                err = True
                out.error(f'Cannot read option "{name}" (value={o}): Expected value of type "{out.readable_type(value)}", got type "{out.readable_type(o)}"')
                out.error(f'Setting "{name}" to default value of {value}')
        else:
            err = True
    if err:
        save_config()

def load_background(background):
    if (n := background.get('next')) is not None:
        global next
        next = Path(os.path.expandvars(n))
    
    if (p := background.get('previous')) is not None:
        global previous
        previous = Path(os.path.expandvars(p))

def load_config():
    config_path: Path = tools.get_app_file(CONFIG_FILE)
    if not config_path.is_file():
        typer.echo(f'Config file does not exist, {out.to_link_style("creating it...", config_path.parent, fg=typer.colors.BLUE)}')
        generate_default_config()
        return
    
    with config_path.open('r') as f:
        data = json.load(f)
        if (options := data.get('options')) is not None:
            load_options(options)
        if (background := data.get('background')) is not None:
            load_background(background)

def save_config():
    config_path: Path = tools.get_app_file(CONFIG_FILE)
    
    with config_path.open('r+') as f:
        data = json.load(f)
        
        data.update({'options': conf})
        
        json_str = json.dumps(data, indent=4)
        
        f.seek(0)
        f.write(json_str)
        f.truncate()

def update_property(property: str, value):
    config_path: Path = tools.get_app_file(CONFIG_FILE)
    if not config_path.is_file():
        out.error('Cannot save config file: config.json does not exist')
        return
    if property not in conf:
        out.error(f'Property "{property}" does not exist')
        return
    
    with config_path.open('r+') as f:
        data = json.load(f)
        conf[property] = value
        
        data.update({'options': conf})
        
        json_str = json.dumps(data, indent=4)
        
        f.seek(0)
        f.write(json_str)
        f.truncate()

def set_next(n: Path):
    if n is None:
        return
    global next
    next = n
    config_path: Path = tools.get_app_file(CONFIG_FILE)
    
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

