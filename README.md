# QuickEdit
This is a Sublime Text package that allows you to edit css code directly into html code using the tag class names, like QuickEdit on the Brackets IDE.

## Installation
To install this plugin, you have two options:

1. If you have Package Control installed, simply search for `QuickEdit` to install.

2. Clone source code to Sublime Text packages folder. (not recommended)

## Usage
<kbd>super + alt + h</kbd> near a class name in order to open a frame with the corresponding css styles into it

<img width="1175" alt="QuickEdit frame example" src="https://user-images.githubusercontent.com/18115514/28253184-dd46559c-6aa0-11e7-996e-5fd3bb5bdd0e.png">

## Challenges
 - Make it work for IDs too
 - Show errors in the phantom (Could not load the file, Could not find the file, Could not find any css style for this class, id, or other)
 - Many files are included implicitly, we need to find some kind of autoload function that check those files too, maybe by including all the css files that are in the project, or checking if there is a header file somewhere in the project
 - Know the line where we found the css styles even in another file
 - Do not include the comment css styles
