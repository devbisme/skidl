# -*- coding: utf-8 -*-

# MIT license
#
# Copyright (C) 2018 by XESS Corp.
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
GUI for finding/displaying parts.
"""

from __future__ import print_function

import collections
import os
import re

import wx
import wx.lib.agw.hyperlink as hl

from common import *
from skidl import KICAD, lib_search_paths, search_parts_iter, skidl_cfg

APP_TITLE = "SKiDL Part Search"

APP_EXIT = 1
SHOW_HELP = 3
SHOW_ABOUT = 4
SEARCH_PATH = 5
SEARCH_PARTS = 6
COPY_PART = 7


# Named tuple for parts found by library search.
LibPart = collections.namedtuple("LibPart", "lib_name part part_name")


class SkidlPartSearch(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

        self.InitUI()

    def InitUI(self):

        self.InitMenus()
        self.InitMainPanels()

        # This flag is used to set focus on the table of found parts
        # after a search is completed.
        self.focus_on_found_parts = False
        self.Bind(wx.EVT_IDLE, self.OnIdle)

        self.SetSize(APP_SIZE)
        self.SetTitle(APP_TITLE)
        self.Center()
        self.Show(True)

    def OnIdle(self, EnvironmentError):
        if self.focus_on_found_parts:
            self.found_parts.SelectRow(0)
            self.found_parts.GoToCell(0, 1)
            self.found_parts.SetFocus()
            self.focus_on_found_parts = False
            # self.SendSizeEvent()
            # self.Refresh()
            # self.Update()

    def InitMainPanels(self):
        # Create main splitter window to hold both subpanels.
        self.main_panel = wx.SplitterWindow(self)

        # Subpanel for search text box and lib/part table.
        self.search_panel = self.InitSearchPanel(self.main_panel)

        # Subpanel for part/pin data.
        self.part_panel = self.InitPartPanel(self.main_panel)

        # Split subpanels left/right.
        self.main_panel.SplitVertically(self.search_panel, self.part_panel, sashPosition=0)
        self.main_panel.SetSashGravity(0.5)  # Both subpanels expand/contract equally.
        self.main_panel.SetMinimumPaneSize((APP_SIZE[0] - 3*SPACING) / 2)

        # Create sizer with border around splitter. 
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.main_panel, 1, wx.ALL|wx.EXPAND, border=SPACING)
        self.SetSizer(sizer)

        # Keep border same color as background of main splitter window.
        self.SetBackgroundColour(self.main_panel.GetBackgroundColour())


    def InitSearchPanel(self, parent):
        # Subpanel for search text box and lib/part table.
        search_panel = wx.Panel(parent)
        vbox = wx.BoxSizer(wx.VERTICAL)
        search_panel.SetSizer(vbox)

        # Text box for part search string.
        self.search_text = wx.TextCtrl(
            search_panel, size=(TEXT_BOX_WIDTH, -1), style=wx.TE_PROCESS_ENTER
        )
        self.search_text.Bind(wx.EVT_TEXT_ENTER, self.OnSearch)
        tip = wx.ToolTip("Enter text or regular expression to select parts.")
        self.search_text.SetToolTip(tip)

        # Button to initiate search for parts containing search string.
        search_btn = wx.Button(search_panel, label="Search", size=BTN_SIZE)
        search_btn.Bind(wx.EVT_BUTTON, self.OnSearch)
        tip = wx.ToolTip("Search for parts containing the text or regular expression.")
        search_btn.SetToolTip(tip)

        # Table (grid) for holding libs and parts that match search string.
        self.found_parts = MyGrid(search_panel, ("Library", "Part"), CELL_BCK_COLOUR)
        self.found_parts.Resize(10)
        self.found_parts.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.OnSelectCell)
        self.found_parts.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.OnCopy)

        # Button to copy selected lib/part to clipboard.
        copy_btn = wx.Button(search_panel, label="Copy", size=BTN_SIZE)
        copy_btn.Bind(wx.EVT_BUTTON, self.OnCopy)
        tip = wx.ToolTip("Copy the selected library and part to the clipboard.")
        copy_btn.SetToolTip(tip)

        # Grid for arranging text box, grid and buttons.
        fgs = wx.FlexGridSizer(rows=2, cols=2, vgap=SPACING, hgap=SPACING)
        fgs.AddMany(
            [
                search_btn,
                (self.search_text, 1, wx.EXPAND),
                copy_btn,
                (self.found_parts, 1, wx.EXPAND),
            ]
        )
        fgs.AddGrowableCol(1, 1)  # widths of text box and grid are adjustable.
        fgs.AddGrowableRow(1, 1)  # height of grid is adjustable.

        vbox.Add(fgs, proportion=1, flag=wx.ALL | wx.EXPAND, border=0)

        return search_panel

    def InitPartPanel(self, parent):
        # Subpanel for part/pin data.
        part_panel = wx.Panel(parent)
        vbox = wx.BoxSizer(wx.VERTICAL)
        part_panel.SetSizer(vbox)

        # Text box for displaying description of part highlighted in grid.
        self.part_desc = Description(part_panel, "Part Description/Tags")
        vbox.Add(self.part_desc, proportion=0, flag=wx.ALL, border=0)
        # Hide the inactive description *after* adding it to the sizer so it's placed correctly.
        self.part_desc.Hide()

        # Hyperlink for highlighted part datasheet.
        self.datasheet_link = HyperLink(part_panel, label="Datasheet")
        vbox.Add(self.datasheet_link, proportion=0, flag=wx.ALL, border=0)
        # Hide the inactive link *after* adding it to the sizer so it's placed correctly.
        self.datasheet_link.Hide()

        # Table (grid) of part pin numbers, names, I/O types.
        vbox.Add(
            wx.StaticText(part_panel, label="Pin List"),
            proportion=0,
            flag=wx.ALL,
            border=SPACING,
        )
        self.pin_info = MyGrid(part_panel, ("Pin", "Name", "Type"), CELL_BCK_COLOUR)
        self.pin_info.Resize(10)
        self.pin_info.SetSortFunc(0, natural_sort_key)  # Natural sort pin numbers.
        self.pin_info.SetSortFunc(1, natural_sort_key)  # Natural sort pin names.
        vbox.Add(self.pin_info, proportion=1, flag=wx.ALL | wx.EXPAND, border=SPACING)

        return part_panel

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
        self.Bind(wx.EVT_MENU, self.OnSearch, id=SEARCH_PARTS)
        
        copyMenuItem = wx.MenuItem(srchMenu, COPY_PART, "Copy\tCtrl+C")
        srchMenu.Append(copyMenuItem)
        self.Bind(wx.EVT_MENU, self.OnCopy, id=COPY_PART)

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

    def OnSearch(self, event):

        # Setup indicators to show progress while scanning libraries.
        wx.BeginBusyCursor()
        progress = wx.ProgressDialog(
            "Searching Part Libraries", "Loading parts from libraries.",
            style=wx.PD_CAN_ABORT | wx.PD_AUTO_HIDE
        )

        # Scan libraries looking for parts that match search string.
        self.lib_parts = set()
        search_text = self.search_text.GetLineText(0)
        for lib_part in search_parts_iter(search_text):
            if lib_part[0] == "LIB":
                lib_name, lib_idx, num_libs = lib_part[1:4]
                progress.SetRange(num_libs)
                if not progress.Update(lib_idx, "Reading library {}...".format(lib_name)):
                    # Cancel button was pressed, so abort.
                    progress.Destroy()
                    wx.EndBusyCursor()
                    return
            elif lib_part[0] == "PART":
                self.lib_parts.add(LibPart(*lib_part[1:]))

        # Remove progress indicators after search is done.
        progress.Destroy()
        wx.EndBusyCursor()

        # Sort parts by libraries and part names.
        self.lib_parts = sorted(
            list(self.lib_parts), key=lambda x: "/".join([x.lib_name, x.part_name])
        )

        # place libraries and parts into a table.
        grid = self.found_parts

        # Clear any existing grid cells and add/sub rows to hold search results.
        grid.Resize(len(self.lib_parts))

        # Places libs and part names into table.
        for row, lib_part in enumerate(self.lib_parts):
            grid.SetCellValue(row, 0, lib_part.lib_name)
            grid.SetCellValue(row, 1, lib_part.part_name)

        # Initially sort table by part library in ascending order.
        grid.SortTable(0, 1)

        # Size the columns for their new contents.
        grid.AutoSizeColumns()

        # Focus on the first part in the list.
        self.focus_on_found_parts = True

    def OnSelectCell(self, event):
        # When a row of the lib/part table is selected, display the data for that part.

        # Get the selected row in the lib/part table and translate it to the row in the data table.
        row = self.found_parts.GetDataRow(event.GetRow())

        # Fully instantiate the selected part.
        try:
            part = self.lib_parts[row].part
        except (AttributeError, IndexError):
            return  # Nothing in the lib_parts table.

        part.parse()  # Instantiate pins.

        # Show the part description.
        desc = part.description
        # if part.aliases:
        #     desc += "\nAliases: " + ", ".join(list(part.aliases))
        if part.keywords:
            desc += "\nKeywords: " + part.keywords
        self.part_desc.SetDescription(desc)

        # Display the link to the part datasheet.
        self.datasheet_link.SetURL(part.datasheet)
        if part.datasheet and part.datasheet not in ("~",):
            self.datasheet_link.SetURL(part.datasheet)
            self.datasheet_link.Show()
        else:
            self.datasheet_link.Hide()
        # Re-layout the panel to account for link hide/show.
        self.part_panel.Layout()

        # Place pin data into a table.
        grid = self.pin_info

        # Clear any existing pin data and add/sub rows to hold results.
        grid.Resize(len(part))

        # Sort pins by pin number.
        pins = sorted(part, key=lambda p: natural_sort_key(p.get_pin_info()[0]))

        # Place pin data into the table.
        for row, pin in enumerate(pins):
            num, names, func = pin.get_pin_info()
            grid.SetCellValue(row, 0, num)
            grid.SetCellValue(row, 1, names)
            grid.SetCellValue(row, 2, func)

        # Size the columns for their new contents.
        grid.AutoSizeColumns()

    def OnCopy(self, event):
        # Copy the lib/part for the selected part onto the clipboard.

        # Get any selected rows in the lib/part table plus wherever the cell cursor is.
        selection = self.found_parts.GetSelectedRows()
        selection.append(self.found_parts.GetGridCursorRow())

        # Only process the part in the first selected row and ignore the rest.
        for row in selection:
            # Deselect all rows but the first.
            self.found_parts.SelectRow(row)

            # Create a SKiDL part instantiation.
            lib = self.found_parts.GetCellValue(row, 0)
            part = self.found_parts.GetCellValue(row, 1)
            part_inst = "Part(lib='{lib}', name='{part}')".format(lib=lib, part=part)

            # Make a data object to hold the SKiDL part instantiation.
            dataObj = wx.TextDataObject()
            dataObj.SetText(part_inst)

            # Place the SKiDL part instantiation on the clipboard.
            if wx.TheClipboard.Open():
                wx.TheClipboard.SetData(dataObj)
                wx.TheClipboard.Flush()
            else:
                Feedback("Unable to open clipboard!", "Error")

            # Place only one part on the clipboard.
            return

    def ShowHelp(self, e):
        Feedback(
            """
1. Enter text to search for in the part descriptions.
2. Start the search by pressing Return or clicking on the Search button.
3. Matching parts will appear in the lib/part table in the left-hand pane.
4. Select a row in the lib/part table to display part info in the right-hand pane.
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


def main():

    ex = wx.App()
    SkidlPartSearch(None)
    ex.MainLoop()


if __name__ == "__main__":
    main()
