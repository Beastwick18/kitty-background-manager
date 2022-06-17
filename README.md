# Kitty Background Manager
A cli program for managing your backgrounds for kitty terminal

This project is WIP for now.
I plan to add the following features:
- [X] Config file
- [X] Option to dim image
- [ ] Option to scale and crop image
- [X] Add `config` command for quickly changing the config file without having to open it
- [ ] Add playlists... maybe?

# Simple Demo
Below is a simple demo showing the process of adding, disabling, and changing the background
![Demo](assets/demo.gif)

## Installation
The program requires poetry, python, and pip to install correctly. Make sure you have all three installed before attempting installation.

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

## Post-installation instructions
After installing, there are some steps you should take to get the program working as intended:
1. Run `kittybg init` to create the config file and enabled, disabled, and current folders
    - Optionally, you can also run `kittybg --install-completion` to get autocompletion for kittybg in your terminal. Doing this is recommended as it will autocomplete names of backgrounds, as well as config properties and much more.
3. Configure your `config.json` file to your liking
    - Feel free to mess around with how the program will edit the images once added by changing the `brightness`, `contrast`, and other properties
4. Configure your `kitty.conf` so that the `background_image` properties value is set to the same value as the `current_image` property in your `config.json` file
5. Go ahead and add your backgrounds to the enabled folder. You can either manually add them, or use `kittybg add` to add them.
6. That's it! Everything should now be working. If you run a command like `kittybg set [BG]` or `kittybg random`, you should see a different background once you restart your terminal.

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
- `disable`: Disable a background that is currently enabled
- `enable`: Enable a background that is currently disabled
- `init`: Initialize all required directories and create a config.json file if one does not exist
- `list`: List all enabled and disabled backgrounds, as well as the next background
- `random`: Set next background to a random one
    - Can be run with `--silent` to hide the output. Useful for randomizing the background when the terminal starts
- `set`: Set next background to a specific background (can be an enabled or disabled background)
- `config`: Quickly find and set properties in the config file
    - Takes in a `property` and an optional `value` to set the property to. If no value is given, it will print out the current value of the property

## Config file
The config file for this program is in a json file typically located in `/home/$USER/.config/kittybg/config.json`

An example config.json looks like this
```json
{
    "options": {
        "brightness": 0.1,
        "contrast": 1.0,
        "enabled_path": "/home/$USER/Pictures/kittyWallpapers/",
        "disabled_path": "/home/$USER/Pictures/kittyWallpapers/disabled/",
        "current_path": "/home/$USER/Pictures/kittyWallpapers/current/",
        "preview_size": 512,
        "preview_align": "left",
        "crop_and_scale": true,
        "crop_size": "1920x1080",
        "scale_type": "fill",
        "background_color": "#000000",
        "preview_on_add": true,
        "preview_fill": false
    },
    "background": {
        "next": "",
        "previous": ""
    }
}
```
## Changing the background when kitty starts
The main reason I created this program was so that I could have random backgrounds whenever I created a new kitty instance.

If this is something you also would like to do, then follow the below steps:
1. Open your `.bashrc`, `config.fish`, `.zshrc` or whichever file is appropriate for your terminal.
2. Add the command `kittybg random --silent` to this file and save it.
    - Typically, you can just add the command to the end of the file
3. Restart the terminal twice. The first time you restart, a random background will be set, but it will only show once the next terminal is opened. This is why you have to restart twice.

This is just how kitty works. Since the `.bashrc` file is run after kitty has already started, the background that is show is not the one stored in the `current.png` file, but is actually the one that was stored there before the `.bashrc` was run. Basically, kitty will read the `current.png` file and set the background, and then the command `kittybg random --silent` is run right after, which updates the `current.png` file to a new background. To avoid confusion, the _next_ background is considered to be the `current.png` file, and the _previous_ background is considered to be the previous `current.png`.

## Background storage

Backgrounds are stored in `/home/$USER/Pictures/kittyWallpapers/` by defualt

The current background that is to be displayed is stored in `/home/$USER/Pictures/kittyWallpapers/current/current.png`. You should set the `background_image` property in your `kitty.conf` file to point to this image

All backgrounds should be in PNG format, as that is only what kitty will accept as a valid image
- When using the `add` command, the image will automatically be converted into PNG format. Any images manually added should be already in the correct format.
