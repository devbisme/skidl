I'm going to attempt to remake this video from Phil's Lab with SKiDL

https://www.youtube.com/watch?v=C7-8nUU6e3E

To locally develop a python package:
https://stackoverflow.com/questions/52248505/how-to-locally-develop-a-python-package

$ virtualenv dev_env
$ source dev_env/bin/activate
$ cd ~/project_folder
$ pip install -e .
$ python examples/stm32_usb_buck/main.py

Useful link on schematic components:
https://resources.altium.com/p/guidelines-creating-useful-schematic-symbols


Known Bugs:
* All nets must be unique except stubs!  Otherwise the schematic layout tool will not properly layout parts

Features to add:
* Edit the schematic itself and place images
** https://docs.kicad.org/5.0/en/pl_editor/pl_editor.pdf
* Add images and other information to schematic
** Link to external dashboard, perhaps with testing data
* Generate default circuit board like https://github.com/jvestman/skimibowi

TODO
* https://github.com/xesscorp/zyc
