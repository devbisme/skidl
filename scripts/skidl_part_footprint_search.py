# -*- coding: utf-8 -*-

# MIT license
#
# Copyright (C) 2019 by XESS Corp.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
GUI for finding/displaying parts and footprints.
"""

from __future__ import print_function

import wx

from common import *
from skidl_part_search import PartSearchPanel
from skidl_footprint_search import FootprintSearchPanel

APP_TITLE = "SKiDL Part/Footprint Search"
APP_EXIT = 1
SHOW_HELP = 3
SHOW_ABOUT = 4
SEARCH_PATH = 5
SEARCH_PARTS = 6
COPY_PART = 7


class AppFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

        self.panel = PartFootprintSearchPanel(self)
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.panel, proportion=1, flag=wx.ALL | wx.EXPAND, border=SPACING)
        self.SetSizer(box)

        # Keep border same color as background of panel.
        self.SetBackgroundColour(self.panel.GetBackgroundColour())

        self.InitMenus()

        #self.SetSize(APP_SIZE)
        self.SetTitle(APP_TITLE)
        self.Center()
        self.Show(True)

    def InitMenus(self):

        # Top menu.
        menuBar = wx.MenuBar()

        # File submenu containing quit button.
        fileMenu = wx.Menu()
        menuBar.Append(fileMenu, "&File")

        quitMenuItem = wx.MenuItem(fileMenu, APP_EXIT, "Quit\tCtrl+Q")
        fileMenu.Append(quitMenuItem)
        self.Bind(wx.EVT_MENU, self.OnQuit, id=APP_EXIT)

        # Search submenu containing search and copy buttons.
        srchMenu = wx.Menu()
        menuBar.Append(srchMenu, "&Search")

        srchPathItem = wx.MenuItem(srchMenu, SEARCH_PATH, "Set search path...\tCtrl+P")
        srchMenu.Append(srchPathItem)
        self.Bind(wx.EVT_MENU, self.OnSearchPath, id=SEARCH_PATH)

        srchMenuItem = wx.MenuItem(srchMenu, SEARCH_PARTS, "Search\tCtrl+F")
        srchMenu.Append(srchMenuItem)
        #self.Bind(wx.EVT_MENU, self.panel.OnSearch, id=SEARCH_PARTS)

        copyMenuItem = wx.MenuItem(srchMenu, COPY_PART, "Copy\tCtrl+C")
        srchMenu.Append(copyMenuItem)
        #self.Bind(wx.EVT_MENU, self.panel.OnCopy, id=COPY_PART)

        # Help menu containing help and about buttons.
        helpMenu = wx.Menu()
        menuBar.Append(helpMenu, "&Help")

        helpMenuItem = wx.MenuItem(helpMenu, SHOW_HELP, "Help\tCtrl+H")
        helpMenu.Append(helpMenuItem)
        aboutMenuItem = wx.MenuItem(helpMenu, SHOW_ABOUT, "About App\tCtrl+A")
        helpMenu.Append(aboutMenuItem)
        self.Bind(wx.EVT_MENU, self.ShowHelp, id=SHOW_HELP)
        self.Bind(wx.EVT_MENU, self.ShowAbout, id=SHOW_ABOUT)

        self.SetMenuBar(menuBar)

    def OnSearchPath(self, event):
        dlg = TextEntryDialog(
            self,
            title="Set Part Search Path",
            caption="Part Search Path",
            tip="Enter {sep}-separated list of directories in which to search for parts.".format(
                sep=os.pathsep
            ),
        )
        dlg.Center()
        dlg.SetValue(os.pathsep.join(lib_search_paths[KICAD]))
        if dlg.ShowModal() == wx.ID_OK:
            lib_search_paths[KICAD] = dlg.GetValue().split(os.pathsep)
            skidl_cfg.store()  # Stores updated lib search path in file.
        dlg.Destroy()

    def ShowHelp(self, e):
        Feedback(
            """
1. Enter text to search for in the part descriptions.
2. Start the search by pressing Return or clicking on the Search button.
3. Matching parts will appear in the Library/Part table in the left-hand pane.
4. Select a row in the Library/Part table to display part info in the right-hand pane.
5. Click the Copy button to place the selected library and part on the clipboard.
6. Paste the clipboard contents into your SKiDL code.
            """,
            "Help",
        )

    def ShowAbout(self, e):
        Feedback(
            APP_TITLE
            + """
(c) 2019 XESS Corp.
https://github.com/xesscorp/skidl
MIT License
            """,
            "About",
        )

    def OnQuit(self, e):
        self.Close()



class PartFootprintSearchPanel(wx.SplitterWindow):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

        # Subpanel for part search panel.
        self.part_panel = add_border(PartSearchPanel(self), wx.BOTTOM)

        # Subpanel for footprint search.
        self.footprint_panel = add_border(FootprintSearchPanel(self), wx.TOP)

        # Split subpanels left/right.
        self.SplitHorizontally(self.part_panel, self.footprint_panel, sashPosition=0)
        self.SetSashGravity(0.5)  # Both subpanels expand/contract equally.
        #self.SetMinimumPaneSize((APP_SIZE[0] - 3 * SPACING) / 2)

def main():
    # import wx.lib.inspection
    app = wx.App()
    AppFrame(None)
    # wx.lib.inspection.InspectionTool().Show()
    app.MainLoop()


if __name__ == "__main__":
    main()
