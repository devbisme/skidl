===============================
skidl
===============================

.. image:: https://img.shields.io/pypi/v/skidl.svg
        :target: https://pypi.python.org/pypi/skidl
.. image:: https://travis-ci.com/xesscorp/skidl.svg?branch=master
    :target: https://travis-ci.com/xesscorp/skidl


SKiDL is a module that allows you to compactly describe the interconnection of 
electronic circuits and components using Python.
The resulting Python program performs electrical rules checking
for common mistakes and outputs a netlist that serves as input to
a PCB layout tool.

* Free software: MIT license
* Documentation: http://xesscorp.github.io/skidl
* User Forum: https://github.com/xesscorp/skidl/discussions


==================================
This repo fork is to develop schematic generation features.
I'm going to attempt to remake this video from Phil's Lab with SKiDL

https://www.youtube.com/watch?v=C7-8nUU6e3E

To test:
* Install KiCad
* clone repo
* source the virtual environent
$ source repo_dir/examples/STM32_USB_BUCK/dev_env/bin/activate
$ cd ~/repo_dir
$ pip install -e .
$ python examples/stm32_usb_buck/main.py