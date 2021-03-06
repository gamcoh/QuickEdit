# QuickEdit
This is a Sublime Text package that allows you to edit css code directly into html code using the tag class names, like QuickEdit on the Brackets IDE.

Since the 2nd version, the plugin also allows you to use it with php variables and functions

## Installation
To install this plugin, you have two options:

1. If you have Package Control installed, simply search for `QuickEdit` to install.

2. Clone source code to Sublime Text packages folder. (not recommended)

## Usage
<kbd>super + alt + h</kbd> near a class name in order to open a frame with the corresponding css styles into it

<img width="1076" alt="QuickEdit" src="https://user-images.githubusercontent.com/18115514/28502479-8864de10-6ff3-11e7-9a8e-cfa5620b38aa.png">

## Settings
- You can disable the errors report by changing to false the `show_errors` entry in the QuickEdit settings
- You can change the font of the report by changing the `font_face` attribut in your user settings

## Challenges
 - Make it work for IDs too
 - Show errors in the phantom (Could not load the file, Could not find the file, Could not find any css style for this class, id, or other)
 - Many files are included implicitly, we need to find some kind of autoload function that check those files too, maybe by including all the css files that are in the project, or checking if there is a header file somewhere in the project
 - Know the line where we found the css styles even in another file
 - Do not include the comment css styles
