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
GUI for finding/displaying footprints.
"""

from __future__ import print_function

import math
import os
import string
from collections import defaultdict, namedtuple

import pykicad.module as pym
import wx
import wx.lib.agw.hyperlink as hl

from common import *
from footprint_painter import FootprintPainter
from skidl import (
    KICAD,
    footprint_search_paths,
    rmv_quotes,
    search_footprints_iter,
    skidl_cfg,
)

APP_TITLE = "SKiDL Footprint Search"

APP_EXIT = 1
SHOW_HELP = 3
SHOW_ABOUT = 4
SEARCH_PATH = 5
SEARCH_FOOTPRINTS = 6
COPY_FOOTPRINTS = 7
PAINT_ACTUAL_SIZE_CKBX_ID = 8


class FootprintPaintingPanel(wx.Panel):
    def __init__(self, parent):
        super(self.__class__, self).__init__(parent)
        self.footprint = None

        # Repaint the footprint panel whenever the "show actual size" checkbox changes.
        self.paint_actual_size_ckbx = wx.FindWindowById(
            PAINT_ACTUAL_SIZE_CKBX_ID, parent
        )
        self.paint_actual_size_ckbx.Bind(wx.EVT_CHECKBOX, self.OnSize)

        # Repaint the footprint panel for any paint or windows resize event.
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)

    @property
    def footprint(self):
        return self._footprint

    @footprint.setter
    def footprint(self, fp):
        if not fp:
            self._footprint = None
        else:
            self._footprint = FootprintPainter(fp, wx.ClientDC(self))

    def OnPaint(self, event):
        if self.footprint:
            self.Refresh()  # Causes repaint of the entire footprint panel.
            self.footprint.paint(
                wx.PaintDC(self), self.paint_actual_size_ckbx.GetValue()
            )
        else:
            self.ClearBackground()

    def OnSize(self, event):
        if self.footprint:
            self.Refresh()  # Causes repaint of the entire footprint panel.
            self.footprint.paint(
                wx.ClientDC(self), self.paint_actual_size_ckbx.GetValue()
            )
        else:
            self.ClearBackground()


class SkidlFootprintSearch(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

        # No valid footprint cache upon startup.
        self.cache_invalid = True

        self.InitUI()

    def InitUI(self):

        self.InitMenus()
        self.InitMainPanels()

        # This flag is used to set focus on the table of found footprints
        # after a search is completed.
        self.focus_on_found_footprints = False
        self.Bind(wx.EVT_IDLE, self.OnIdle)

        self.SetSize(APP_SIZE)
        self.SetTitle(APP_TITLE)
        self.Center()
        self.Show(True)

    def OnIdle(self, event):
        if self.focus_on_found_footprints:
            self.found_footprints.SelectRow(0)
            self.found_footprints.GoToCell(0, 1)
            self.found_footprints.SetFocus()
            self.focus_on_found_footprints = False
            # self.SendSizeEvent()
            # self.Refresh()
            # self.Update()

    def InitMainPanels(self):
        # Create main splitter window to hold both subpanels.
        self.main_panel = wx.SplitterWindow(self)

        # Subpanel for search text box and lib/part table.
        self.search_panel = self.InitSearchPanel(self.main_panel)

        # Subpanel for part/pin data.
        self.fp_panel = self.InitFootprintPanel(self.main_panel)

        # Split subpanels left/right.
        self.main_panel.SplitVertically(
            self.search_panel, self.fp_panel, sashPosition=0
        )
        self.main_panel.SetSashGravity(0.5)  # Both subpanels expand/contract equally.
        self.main_panel.SetMinimumPaneSize((APP_SIZE[0] - 3 * SPACING) / 2)

        # Create sizer with border around splitter.
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.main_panel, 1, wx.ALL | wx.EXPAND, border=SPACING)
        self.SetSizer(sizer)

        # Keep border same color as background of main splitter window.
        self.SetBackgroundColour(self.main_panel.GetBackgroundColour())

    def InitSearchPanel(self, parent):
        # Subpanel for search text box and footprint table.
        search_panel = wx.Panel(parent)
        vbox = wx.BoxSizer(wx.VERTICAL)
        search_panel.SetSizer(vbox)

        # Text box for footprint search string.
        self.search_text = wx.TextCtrl(
            search_panel, size=(TEXT_BOX_WIDTH, -1), style=wx.TE_PROCESS_ENTER
        )
        self.search_text.Bind(wx.EVT_TEXT_ENTER, self.OnSearch)
        tip = wx.ToolTip("Enter text or regular expression to select footprints.")
        self.search_text.SetToolTip(tip)

        # Button to initiate search for footprints containing search string.
        search_btn = wx.Button(search_panel, label="Search", size=BTN_SIZE)
        search_btn.Bind(wx.EVT_BUTTON, self.OnSearch)
        tip = wx.ToolTip(
            "Search for footprints containing the text or regular expression."
        )
        search_btn.SetToolTip(tip)

        # Table (grid) for holding footprints that match search string.
        self.found_footprints = MyGrid(
            search_panel, ("Library", "Footprint"), CELL_BCK_COLOUR
        )
        self.found_footprints.Resize(10)
        self.found_footprints.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.OnSelectCell)
        self.found_footprints.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.OnCopy)

        # Button to copy selected footprint to clipboard.
        copy_btn = wx.Button(search_panel, label="Copy", size=BTN_SIZE)
        copy_btn.Bind(wx.EVT_BUTTON, self.OnCopy)
        tip = wx.ToolTip("Copy the selected footprint to the clipboard.")
        copy_btn.SetToolTip(tip)

        # Grid for arranging text box, grid and buttons.
        fgs = wx.FlexGridSizer(rows=2, cols=2, vgap=SPACING, hgap=SPACING)
        fgs.AddMany(
            [
                search_btn,
                (self.search_text, 1, wx.EXPAND),
                copy_btn,
                (self.found_footprints, 1, wx.EXPAND),
            ]
        )
        fgs.AddGrowableCol(1, 1)  # widths of text box and grid are adjustable.
        fgs.AddGrowableRow(1, 1)  # height of grid is adjustable.

        vbox.Add(fgs, proportion=1, flag=wx.ALL | wx.EXPAND, border=0)

        return search_panel

    def InitFootprintPanel(self, parent):
        # Subpanel for footprint painting.
        fp_panel = wx.Panel(parent)
        vbox = wx.BoxSizer(wx.VERTICAL)
        fp_panel.SetSizer(vbox)

        # Text box for displaying description of footprint highlighted in grid.
        self.fp_desc = Description(fp_panel, "Footprint Description/Tags")
        vbox.Add(self.fp_desc, proportion=0, flag=wx.ALL, border=0)
        # Hide the inactive description *after* adding it to the sizer so it's placed correctly.
        self.fp_desc.Hide()

        # Hyperlink for highlighted footprint datasheet.
        self.datasheet_link = HyperLink(fp_panel, label="Datasheet")
        vbox.Add(self.datasheet_link, proportion=0, flag=wx.ALL, border=0)
        # Hide the inactive link *after* adding it to the sizer so it's placed correctly.
        self.datasheet_link.Hide()

        # Footprint painting.
        self.painting_title_panel = wx.Panel(fp_panel)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.painting_title_panel.SetSizer(hbox)
        hbox.Add(
            wx.StaticText(self.painting_title_panel, label="Footprint"),
            proportion=0,
            flag=wx.ALL,
            border=0,
        )
        hbox.AddSpacer(3 * SPACING)
        self.actual_size_ckbx = wx.CheckBox(
            self.painting_title_panel,
            id=PAINT_ACTUAL_SIZE_CKBX_ID,
            label="Show actual size",
        )
        self.actual_size_ckbx.SetToolTip(
            wx.ToolTip("Check to display actual size of footprint.")
        )
        hbox.Add(self.actual_size_ckbx, proportion=0, flag=wx.ALL, border=0)
        vbox.Add(self.painting_title_panel, proportion=0, flag=wx.ALL, border=SPACING)
        self.painting_title_panel.Hide

        self.fp_painting_panel = FootprintPaintingPanel(fp_panel)
        vbox.Add(
            self.fp_painting_panel,
            proportion=1,
            flag=wx.ALL | wx.EXPAND,
            border=SPACING,
        )

        return fp_panel

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

        srchMenuItem = wx.MenuItem(srchMenu, SEARCH_FOOTPRINTS, "Search\tCtrl+F")
        srchMenu.Append(srchMenuItem)
        self.Bind(wx.EVT_MENU, self.OnSearch, id=SEARCH_FOOTPRINTS)

        copyMenuItem = wx.MenuItem(srchMenu, COPY_FOOTPRINTS, "Copy\tCtrl+C")
        srchMenu.Append(copyMenuItem)
        self.Bind(wx.EVT_MENU, self.OnCopy, id=COPY_FOOTPRINTS)

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
            title="Set Footprint Search Path",
            caption="Footprint Search Path",
            tip="Enter {sep}-separated list of directories in which to search for footprints.".format(
                sep=os.pathsep
            ),
        )
        dlg.Center()
        dlg.SetValue(os.pathsep.join(footprint_search_paths[KICAD]))
        if dlg.ShowModal() == wx.ID_OK:
            footprint_search_paths[KICAD] = dlg.GetValue().split(os.pathsep)
            skidl_cfg.store()  # Stores updated search path in file.
            self.cache_invalid = True  # Changing search path invalidates cache.
        dlg.Destroy()

    def OnSearch(self, event):

        # Setup indicators to show progress while scanning libraries.
        wx.BeginBusyCursor()
        progress = wx.ProgressDialog(
            "Searching Footprint Libraries",
            "Loading footprints from libraries.",
            style=wx.PD_CAN_ABORT | wx.PD_AUTO_HIDE,
        )

        # Scan libraries looking for footprints that match search string.
        self.footprints = []
        search_text = self.search_text.GetLineText(0)
        for lib_module in search_footprints_iter(
            search_text, cache_invalid=self.cache_invalid
        ):
            if lib_module[0] == "LIB":
                lib_name = lib_module[1]
                lib_idx = lib_module[2]
                total_num_libs = lib_module[3]
                progress.SetRange(total_num_libs)
                if not progress.Update(
                    lib_idx, "Reading footprint library {}...".format(lib_name)
                ):
                    # Cancel button was pressed, so abort.
                    progress.Destroy()
                    wx.EndBusyCursor()
                    return
            elif lib_module[0] == "MODULE":
                self.footprints.append(lib_module[1:])

        # Remove progress indicators after search is done.
        progress.Destroy()
        wx.EndBusyCursor()

        # Cache should be valid after running a search, so use it for further searches.
        self.cache_invalid = False

        # place libraries and parts into a table.
        grid = self.found_footprints

        # Clear any existing grid cells and add/sub rows to hold search results.
        grid.Resize(len(self.footprints))

        # Places libs and part names into table.
        for row, (lib, module_text, module_name) in enumerate(self.footprints):
            grid.SetCellValue(row, 0, lib)
            grid.SetCellValue(row, 1, module_name)

        # Initially sort table by footprint library in ascending order.
        grid.SortTable(0, 1)

        # Size the columns for their new contents.
        grid.AutoSizeColumns()

        # Cause refresh.
        self.search_panel.Layout()

        # Focus on the first footprint in the list.
        self.focus_on_found_footprints = True

    def OnSelectCell(self, event):
        # When a row of the footprint table is selected, display the data for that footprint.

        def clear_fp_panel():
            # Clear the footprint panel desc, link, and painting.
            self.fp_desc.SetDescription("")
            self.datasheet_link.SetURL(None)
            self.painting_title_panel.Hide()
            self.fp_painting_panel.footprint = None
            self.fp_painting_panel.Hide()
            self.fp_panel.Layout()

        # Get the selected row in the lib/part table and translate it to the row in the data table.
        row = self.found_footprints.GetDataRow(event.GetRow())

        # Get the text describing the footprint structure.
        try:
            module_text = self.footprints[row][1]
        except (AttributeError, IndexError):
            # No text, so hide footprint panel and return.
            clear_fp_panel()
            return

        # Parse the footprint text.
        try:
            wx.BeginBusyCursor()
            module = pym.Module.parse("\n".join(module_text))
        except Exception as e:
            # Parsing error, so hide the footprint panel and return.
            wx.EndBusyCursor()
            clear_fp_panel()
            Feedback(
                "Error while parsing {}:{}".format(
                    self.footprints[row][0], self.footprints[row][2]
                ),
                "Error",
            )
            return
        wx.EndBusyCursor()

        # Get the footprint description and tags if they exist.
        descr = ""
        tags = ""
        for line in module_text:
            try:
                descr = line.split("(descr ")[1].rsplit(")", 1)[0]
                descr = rmv_quotes(descr)
            except IndexError:
                pass
            try:
                tags = line.split("(tags ")[1].rsplit(")", 1)[0]
                tags = rmv_quotes(tags)
                tags = "\nTags: " + tags
            except IndexError:
                pass

        # Show the footprint description.
        self.fp_desc.SetDescription(descr + tags)

        # Display the link to the footprint datasheet.
        try:
            # Extract link-like text from the description.
            url = re.search("(?P<url>https?://[^\s]+)", descr).group("url")
        except AttributeError:
            # No URL found so hide the hyperlink.
            self.datasheet_link.SetURL(None)
        else:
            # URL was found, so set the hyperlink and show it.
            # Often, the link has punctuation at the end that should be removed.
            url = url.rstrip(string.punctuation)
            self.datasheet_link.SetURL(url)

        # Set the footprint that will be displayed.
        self.painting_title_panel.Show()
        self.fp_painting_panel.footprint = module
        self.fp_painting_panel.Show()

        # Re-layout the panel to account for link hide/show.
        self.fp_panel.Layout()

    def OnCopy(self, event):
        # Copy the selected footprint onto the clipboard.

        # Get any selected rows in the footprint table plus wherever the cell cursor is.
        selection = self.found_footprints.GetSelectedRows()
        selection.append(self.found_footprints.GetGridCursorRow())

        # Only process the footprint in the first selected row and ignore the rest.
        for row in selection:
            # Deselect all rows but the first.
            self.found_footprints.SelectRow(row)

            # Create a SKiDL footprint instantiation.
            file = self.found_footprints.GetCellValue(row, 0)
            fp = self.found_footprints.GetCellValue(row, 1)
            fp_inst = "footprint='{file}:{fp}')".format(**locals())

            # Make a data object to hold the SKiDL footprint instantiation.
            dataObj = wx.TextDataObject()
            dataObj.SetText(fp_inst)

            # Place the SKiDL footprint instantiation on the clipboard.
            if wx.TheClipboard.Open():
                wx.TheClipboard.SetData(dataObj)
                wx.TheClipboard.Flush()
            else:
                Feedback("Unable to open clipboard!", "Error")

            # Place only one footprint on the clipboard.
            return

    def ShowHelp(self, e):
        Feedback(
            """
1. Enter text to search for in the footprint descriptions.
2. Start the search by pressing Return or clicking on the Search button.
3. Matching footprints will appear in the table in the left-hand pane.
4. Select a row in the table to display footprint info in the right-hand pane.
5. Click the Copy button to place the selected footprint on the clipboard.
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

    #    import wx.lib.inspection
    ex = wx.App()
    SkidlFootprintSearch(None)
    #    wx.lib.inspection.InspectionTool().Show()
    ex.MainLoop()


if __name__ == "__main__":
    main()
