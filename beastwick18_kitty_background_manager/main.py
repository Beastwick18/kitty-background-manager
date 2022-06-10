from os import listdir
from os.path import isdir, dirname, exists
import shutil
import typer


enabled_path = '/home/brad/Pictures/kittyWallpapers/'
disabled_path = enabled_path + 'disabled/'
app = typer.Typer()

def to_link(label: str, link: str):
    s = "\u001b]8;;file://{}\a{}\u001b]8;;\a"
    return s.format(link, label)

def list_next():
    for f in listdir(enabled_path):
        currfile = enabled_path + f
        if not isdir(currfile):
            # Remove file extension
            file = f.rsplit('.', 1)
            
            if len(file) >= 2:
                name, ext = file
                if not name == '' and ext == 'next':
                    typer.echo(typer.style(to_link(name, enabled_path + name + '.png'), fg=typer.colors.BLUE))
                    return

def list_files_colored(filepath, col):
    for f in listdir(filepath):
        currfile = filepath + f
        if not isdir(currfile):
            # Remove file extension
            file = f.rsplit('.', 1)
            
            if len(file) >= 2:
                name, ext = file
                if not name == '' and not ext == 'next':
                    typer.echo(typer.style(to_link(name, currfile), fg=col))

@app.callback()
def callback():
    """
    A cli background manager for the Kitty terminal
    """


@app.command()
def list():
    """
    List all enabled and disabled backgrounds, as well as the next
    background
    """
    typer.echo(typer.style('Next:', fg=typer.colors.WHITE, bold=True, underline=True))
    list_next()
    
    typer.echo(typer.style('\nEnabled ' + to_link('(📁)', enabled_path) + ':', fg=typer.colors.WHITE, bold=True, underline=True))
    list_files_colored(enabled_path, typer.colors.GREEN)
    
    typer.echo(typer.style('\nDisabled ' + to_link('(📁)', disabled_path) + ':', fg=typer.colors.WHITE, bold=True, underline=True))
    list_files_colored(disabled_path, typer.colors.RED)


@app.command()
def random():
    """
    Set next background to a random one
    """
    typer.echo("Loading portal gun")

@app.command()
def enable(bg: str = typer.Argument(...)):
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
def disable(bg: str = typer.Argument(...)):
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
def set(bg: str = typer.Argument(...)):
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
    
    typer.echo(file)
