# Kitty Background Manager
A cli program for managing your backgrounds for kitty terminal

This project is WIP for now.
I plan to add the following features:
- [ ] Config file
- [ ] Option to dim image
- [ ] Option to scale and crop image

## Installation
To install Kitty Background Manager, you will have to clone the repository and run

```
chmod +x ./install.sh
```

from within the repository. After that, you can run the install script. 

The program requires poetry to install correctly. 

## Running the program
Once the program is installed, you can run it by calling the `kittybg` command from your terminal

The current arguments the program accepts are:
- `random`: change to a random background
    - Can be run with `--silent` to hide the output. Useful for randomizing the background when the terminal starts
- `set`: change to a specific background
- `enable`: enable a specific background
- `disable`: disable a specific background
- `list`: list all backgrounds
- `add`: add a background to the background folder
- `delete`: delete a background from the background folder

## Background storage

Backgrounds are stored in `/home/$USER/Pictures/kittyWallpapers/` by defualt

In the near future, there will be an option to change the location
