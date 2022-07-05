import os
from enum import Enum
from pathlib import Path
import json
import typer
from PIL import ImageColor
import beastwick18_kitty_background_manager.tools as tools
import beastwick18_kitty_background_manager.output as out
from dataclasses import dataclass
from typing import Any, Callable

APP_NAME = 'kittybg'
CONFIG_FILE = 'config.json'
CURRENT_FILE = 'current.png'

enabled_path: Path = None
disabled_path: Path = None
current_path: Path = None

previous: Path = None
next: Path = None

@dataclass
class ConfProperty:
    name: str
    value: Any
    validate_method: Callable
    
    def validate(self, x):
        return self.validate_method(self.name, x)

conf = {}

def add_property(name: str, value: Any, validate_method: Callable):
    conf[name] = ConfProperty(name, value, validate_method)

add_property('brightness', 0.1, lambda n, x: tools.assert_type(n, x, (float, int)))
add_property('contrast', 1.0, lambda n, x: tools.assert_type(n, x, (float, int)))
add_property('enabled_path', '/home/$USER/Pictures/kittyWallpapers/', lambda n, x: tools.assert_type(n, x, str))
add_property('disabled_path', '/home/$USER/Pictures/kittyWallpapers/disabled/', lambda n, x: tools.assert_type(n, x, str))
add_property('current_path', '/home/$USER/Pictures/kittyWallpapers/current/', lambda n, x: tools.assert_type(n, x, str))
add_property('preview_size', 512, lambda n, x: tools.assert_type(n, x, int) and tools.assert_range('preview_size', 0, 4096, x))
add_property('preview_align', 'left', lambda n, x: tools.assert_type(n, x, str) and tools.assert_in(n, x, ('left', 'center', 'right')))
add_property('crop_and_scale', True, lambda n, x: tools.assert_type(n, x, bool))
add_property('crop_size', '1920x1080', lambda n, x: tools.assert_type(n, x, str) and tools.valid_dimensions(n, x))
add_property('scale_type', 'fill', lambda n, x: tools.assert_type(n, x, str) and tools.assert_in(n, x, ('fill', 'fit', 'none')))
add_property('background_color', '#000000', lambda n, x: tools.valid_color(n, x))
add_property('preview_on_add', True, lambda n, x: tools.assert_type(n, x, bool))
add_property('preview_fill', False, lambda n, x: tools.assert_type(n, x, bool))

def generate_default_config():
    data = {}
    data['options'] = {name: data.value for name, data in conf.items()}
    
    data['background'] = {}
    data['background']['next'] = ''
    data['background']['previous'] = ''
    
    config_path: Path = tools.get_app_file(CONFIG_FILE)
    with config_path.open('w') as f:
        json_str = json.dumps(data, indent=4)
        f.write(json_str)

def set_paths():
    global enabled_path, disabled_path, current_path
    enabled_path = Path(os.path.expandvars(conf['enabled_path'].value))
    disabled_path = Path(os.path.expandvars(conf['disabled_path'].value))
    current_path = Path(os.path.expandvars(conf['current_path'].value))

def load_options(options):
    for name, data in conf.items():
        value = data.value
        if (o := options.get(name)) is not None:
            if data.validate(o):
                conf[name].value = o
            else:
                out.error(f'Setting "{name}" to default value of {value}')

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
        
        data.update({'options': {name: data.value for name, data in conf.items()}})
        
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
        conf[property].value = value
        
        data.update({'options': {name: data.value for name, data in conf.items()}})
        
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

def get_next():
    if next is None or next.stem == '':
        return
    return next.stem

def get_previous():
    if previous is None or previous.stem == '':
        return
    return previous.stem
