import os
import click
from os.path import isdir, dirname, exists
import shutil
import random as rand
import typer
from typing import Optional

enabled_path = '/home/brad/Pictures/kittyWallpapers/'
disabled_path = enabled_path + 'disabled/'
app = typer.Typer()

def remove_next_file():
    for f in os.listdir(enabled_path):
        currfile = enabled_path + f
        if not isdir(currfile):
            # Remove file extension
            file = f.rsplit('.', 1)
            
            if len(file) >= 2:
                name, ext = file
                if not name == '' and ext == 'next':
                    os.remove(currfile)


def to_link(label: str, link: str):
    return f'\u001b]8;;file://{link}\a{label}\u001b]8;;\a'

def list_next():
    for f in os.listdir(enabled_path):
        currfile = enabled_path + f
        if not isdir(currfile):
            # Remove file extension
            file = f.rsplit('.', 1)
            
            if len(file) >= 2:
                name, ext = file
                if not name == '' and ext == 'next':
                    typer.secho(to_link(name, enabled_path + name + '.png'), fg=typer.colors.BLUE)
                    return

def list_images(path):
    list = []
    for f in os.listdir(path):
        currfile = path + f
        if not isdir(currfile):
            # Remove file extension
            file = f.rsplit('.', 1)
            
            if len(file) >= 2:
                name, ext = file
                if not name == '' and ext == 'png':
                    list.append(name)
    return list

@app.callback()
def callback():
    """
    A cli background manager for the Kitty terminal
    """


@app.command()
def list():
    """
    List all enabled and disabled backgrounds, as well as the next background
    """
    
    typer.secho('Next:', fg=typer.colors.WHITE, bold=True, underline=True)
    list_next()
    
    typer.secho('\nEnabled ' + to_link('(📁)', enabled_path) + ':', fg=typer.colors.WHITE, bold=True, underline=True)
    for i in list_images(enabled_path):
        typer.secho(to_link(i, enabled_path + i + '.png'), fg=typer.colors.GREEN)
    
    typer.echo(typer.style('\nDisabled ' + to_link('(📁)', disabled_path) + ':', fg=typer.colors.WHITE, bold=True, underline=True))
    for i in list_images(disabled_path):
        typer.secho(to_link(i, disabled_path + i + '.png'), fg=typer.colors.RED)

def silent_callback(silent: bool):
    bg = rand.choice(list_images(enabled_path))
    
    file = enabled_path + bg + '.png'
    if not exists(file) or isdir(file):
        file = disabled_path + bg + '.png'
        if not exists(file) or isdir(file):
            # TODO: Throw error
            typer.echo('PP')
            return
    
    remove_next_file()
    
    with open(enabled_path + bg + '.next', 'w') as _:
        pass
    
    shutil.copy(file, enabled_path + 'current/current.png')
    
    if not silent:
        typer.secho('Next:', fg=typer.colors.WHITE, bold=True, underline=True)
        list_next()

@app.command()
# @click.option("--silent", help="If present, there will be no output to stdout")
def random(s: Optional[bool] = typer.Option(None, "--silent", help="If present, there will be no output to stdout", callback=silent_callback)):
    """
    Set next background to a random one
    """

@app.command()
def enable(bg: str = typer.Argument("Background", help="The name of the background to be enabled", autocompletion=(lambda: list_images(disabled_path)))):
    """
    Enable a background that is currently disabled
    """
    
    file = disabled_path + bg + '.png'
    if exists(file) and not isdir(file):
        typer.echo(f'Enabled {bg}.png')
        shutil.move(file, enabled_path + bg + '.png')
    else:
        # TODO: Throw error
        typer.echo("PP")

@app.command()
def disable(bg: str = typer.Argument("Background", help="The name of the background to be enabled", autocompletion=(lambda: list_images(enabled_path)))):
    """
    Disable a background that is currently enabled
    """
    
    file = enabled_path + bg + '.png'
    if exists(file) and not isdir(file):
        typer.echo(f'Disabled {bg}.png')
        shutil.move(file, disabled_path + bg + '.png')
    else:
        # TODO: Throw error
        typer.echo("PP")

@app.command()
def set(bg: str = typer.Argument("Background", help="The name of the background to be enabled", autocompletion=(lambda: list_images(enabled_path) + list_images(disabled_path)))):
    """
    Set next background to a specific background (can be an enabled or disabled background)
    """
    
    file = enabled_path + bg + '.png'
    if not exists(file) or isdir(file):
        file = disabled_path + bg + '.png'
        if not exists(file) or isdir(file):
            # TODO: Throw error
            typer.echo('PP')
            return
    
    remove_next_file()
    
    with open(enabled_path + bg + '.next', 'w') as _:
        pass
    
    shutil.copy(file, enabled_path + 'current/current.png')
    
    typer.secho('Next:', fg=typer.colors.WHITE, bold=True, underline=True)
    list_next()

@app.command()
def add():
    """
    Add an image to the background folder
    """
    # TODO: Implement this

@app.command()
def delete():
    """
    Delete an image from the background folder
    """
    # TODO: Implement this
