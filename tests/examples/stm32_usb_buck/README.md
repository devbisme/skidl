Attempting to recreate this video from Phil's Lab with SKiDL: https://www.youtube.com/watch?v=C7-8nUU6e3E


To run the STM32 example with new schematic generation code:
* Clone project
* Activate the virtual environment
* Install this repo's skidl
* Run example
```
$ git clone https://github.com/shanemmattner/skidl
$ cd skidl/examples/stm32_usb_buck
$ source dev_env/bin/activate
$ cd ../.. && pip install -e .
$ python examples/stm32_usb_buck/main.py
```
* Open KiCAD to view files

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
* Can't do multiple part instanciation

Features to add:
* Edit the schematic itself and place images
** https://docs.kicad.org/5.0/en/pl_editor/pl_editor.pdf
* Add images and other information to schematic
** Link to external dashboard, perhaps with testing data
* Generate default circuit board like https://github.com/jvestman/skimibowi

TODO
* https://github.com/xesscorp/zyc
* Try to implement Rect/Point logic
** https://wiki.python.org/moin/PointsAndRectangles

