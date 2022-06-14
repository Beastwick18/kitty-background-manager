# Kitty Background Manager
A cli program for managing your backgrounds for kitty terminal

This project is WIP for now.
I plan to add the following features:
- [X] Config file
- [X] Option to dim image
- [ ] Option to scale and crop image
- [ ] Add `config` command for quickly changing the config file without having to open it
- [ ] Add playlists... maybe?

## Installation
The program requires poetry, python, and pip to install correctly.

To install Kitty Background Manager, you will have to clone the repository and run the following commands to install the program

```
chmod +x ./install.sh
./install.sh
```
The first command you should run after installing is
```
kittybg init
```
This command will create the enabled folder and disabled folder as specified in the `config.json` file

This program uses [typer](https://github.com/tiangolo/typer) for handling the cli portion of the app and [pixcat](https://github.com/mirukana/pixcat) for displaying image previews in the terminal

## Running the program
Once the program is installed, you can run it by calling the `kittybg` command from your terminal

The current arguments the program accepts are:
- `preview`: Looks for the first occurence of a background in the disabled and enabled folder in that order and shows a preview
    - Can be run with `--enabled` or `--disabled` to search through just the enabled or disabled folder
    - Can also be run with `--fill` to make the preview fill the screen or with `--size n` with n being between 0 and 4096 to set the preview images size
- `add`: Add an image to the background folder
    - If `preview_on_add` is set to `true` in `config.json`, then everytime an image is added a preview will be shown in the terminal. This is useful for quickly seeing the effects of any edits made by the program
- `delete`: Looks for the first occurence of a background in the disabled and enabled folder in that order and deletes it.
    - Can be run with `--enabled` or `--disabled` to search through just the enabled or disabled folder
- `disable`:Disable a background that is currently enabled
- `enable`: Enable a background that is currently disabled
- `init`: Initialize all required directories and create a config.json file if one does not exist
- `list`: List all enabled and disabled backgrounds, as well as the next background
- `random`: Set next background to a random one
    - Can be run with `--silent` to hide the output. Useful for randomizing the background when the terminal starts
- `set`: Set next background to a specific background (can be an enabled or disabled background)

## Config file
The config file for this program is in a json file typically located in `/home/$USER/.config/kittybg/config.json`

The editable properties stored in this json are the brightness of the image, the contrast of the image, the enabled folder path, and the disabled folder path

An example config.json looks like this
```json
{
    "options": {
        "brightness": 0.1,
        "contrast": 1.15,
        "enabled_path": "/home/$USER/Pictures/kittyWallpapers/",
        "disabled_path": "/home/$USER/Pictures/kittyWallpapers/disabled/",
        "preview_size": 512,
        "preview_fill": false,
        "preview_on_add": true
    }
}
```

## Background storage

Backgrounds are stored in `/home/$USER/Pictures/kittyWallpapers/` by defualt

The current background that is to be displayed is stored in `/home/$USER/Pictures/kittyWallpapers/current/current.png`. You should set the `background_image` property in your `kitty.conf` file to point to this image

All backgrounds should be in PNG format, as that is only what kitty will accept as a valid image
- When using the `add` command, the image will automatically be converted into PNG format

In the near future, there will be an option to change the location
