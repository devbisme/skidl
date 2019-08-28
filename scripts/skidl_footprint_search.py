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
import re
import string
from collections import defaultdict, namedtuple

import pykicad.module as pym
import wx
import wx.grid
import wx.lib.agw.hyperlink as hl
import wx.lib.expando

from footprint_painter import FootprintPainter
from skidl import (KICAD, footprint_search_paths, rmv_quotes,
                   search_footprints_iter, skidl_cfg)

APP_TITLE = "SKiDL Footprint Search"

APP_EXIT = 1
SHOW_HELP = 3
SHOW_ABOUT = 4
SEARCH_PATH = 5
SEARCH_FOOTPRINTS = 6
COPY_FOOTPRINTS = 7
PAINT_ACTUAL_SIZE_CKBX_ID = 8

APP_SIZE = (600, 500)
BTN_SIZE = (50, -1)
SPACING = 10
TEXT_BOX_WIDTH = 200
CELL_BCK_COLOUR = wx.Colour(255, 255, 255)


class TextEntryDialog(wx.Dialog):
    def __init__(self, parent, title, caption, tip=None):
        style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        super(TextEntryDialog, self).__init__(parent, -1, title, style=style)
        text = wx.StaticText(self, -1, caption)
        self.input = wx.lib.expando.ExpandoTextCtrl(
            self, size=(int(0.75 * parent.GetSize()[0]), -1), style=wx.TE_PROCESS_ENTER
        )
        self.input.Bind(wx.EVT_TEXT_ENTER, self.OnEnter)
        if tip:
            self.input.SetToolTip(wx.ToolTip(tip))
        buttons = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(text, 0, wx.ALL, 5)
        sizer.Add(self.input, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(buttons, 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizerAndFit(sizer)

    def OnEnter(self, event):
        """End modal if enter is hit in input text control."""
        self.EndModal(wx.ID_OK)

    def SetValue(self, value):
        self.input.SetValue(value.strip().rstrip())
        self.input.SetFocus()
        self.input.SetInsertionPointEnd()
        self.Fit()

    def GetValue(self):
        return self.input.GetValue().strip().rstrip()


class MyGrid(wx.grid.Grid):
    def __init__(self, parent, headers, bck_colour):
        super(self.__class__, self).__init__()
        self.Create(parent)
        self.CreateGrid(
            numRows=10, numCols=len(headers), selmode=wx.grid.Grid.SelectRows
        )
        self.HideRowLabels()
        self.EnableEditing(False)
        for col, lbl in enumerate(headers):
            self.SetColLabelValue(col, lbl)
        self.SetDefaultCellBackgroundColour(parent.GetBackgroundColour())
        self.BackgroundColour = bck_colour
        self.ColourGridBackground()
        self.SetSelectionMode(wx.grid.Grid.GridSelectionModes.SelectRows)

    def Resize(self, numRows):
        self.ClearGrid()
        num_rows_chg = numRows - self.GetNumberRows()
        if num_rows_chg < 0:
            self.DeleteRows(0, -num_rows_chg, True)
        elif num_rows_chg > 0:
            self.AppendRows(num_rows_chg)
        self.ColourGridBackground()

    def ColourGridBackground(self):
        for r in range(self.GetNumberRows()):
            for c in range(self.GetNumberCols()):
                self.SetCellBackgroundColour(r, c, self.BackgroundColour)


class FootprintPaintingPanel(wx.Panel):
    def __init__(self, parent):
        super(self.__class__, self).__init__(parent)
        self.footprint = None

        # Repaint the footprint panel whenever the "show actual size" checkbox changes.
        self.paint_actual_size_ckbx = wx.FindWindowById(PAINT_ACTUAL_SIZE_CKBX_ID, parent)
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
            self.footprint.paint(wx.PaintDC(self), self.paint_actual_size_ckbx.GetValue())
        else:
            self.ClearBackground()

    def OnSize(self, event):
        if self.footprint:
            self.Refresh()  # Causes repaint of the entire footprint panel.
            self.footprint.paint(wx.ClientDC(self), self.paint_actual_size_ckbx.GetValue())
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

        self.SetSize(APP_SIZE)
        self.SetTitle(APP_TITLE)
        self.Center()
        self.Show(True)

    def InitMainPanels(self):
        # Main panel holds two subpanels.
        main_panel = wx.Panel(self)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        main_panel.SetSizer(hbox)

        # Subpanel for search text box and footprint table.
        self.search_panel = self.InitSearchPanel(main_panel)
        hbox.Add(
            self.search_panel, proportion=1, flag=wx.ALL | wx.EXPAND, border=SPACING
        )

        # Divider.
        hbox.Add(
            wx.StaticLine(main_panel, size=(2, -1), style=wx.LI_VERTICAL),
            proportion=0,
            flag=wx.ALL | wx.EXPAND,
            border=0,
        )

        # Subpanel for footprint painting.
        self.fp_panel = self.InitFootprintPanel(main_panel)
        hbox.Add(self.fp_panel, proportion=1, flag=wx.ALL | wx.EXPAND, border=0)

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
        vbox.Add(
            wx.StaticText(fp_panel, label="Footprint Description/Tags"),
            proportion=0,
            flag=wx.ALL,
            border=SPACING,
        )
        self.fp_desc = wx.TextCtrl(
            fp_panel,
            size=(TEXT_BOX_WIDTH, 60),
            style=wx.TE_READONLY | wx.TE_MULTILINE | wx.TE_NO_VSCROLL,
        )
        vbox.Add(self.fp_desc, proportion=0, flag=wx.ALL | wx.EXPAND, border=SPACING)

        # Hyperlink for highlighted part datasheet.
        vbox.Add(
            wx.StaticLine(fp_panel, size=(-1, 2), style=wx.LI_HORIZONTAL),
            proportion=0,
            flag=wx.ALL | wx.EXPAND,
            border=5,
        )
        self.datasheet_link = hl.HyperLinkCtrl(fp_panel, label="Datasheet", URL="")
        self.datasheet_link.EnableRollover(True)
        vbox.Add(self.datasheet_link, proportion=0, flag=wx.ALL, border=SPACING)
        # Hide the inactive link *after* adding it to the sizer so it's placed correctly.
        self.datasheet_link.Hide()

        # Divider.
        vbox.Add(
            wx.StaticLine(fp_panel, size=(-1, 2), style=wx.LI_HORIZONTAL),
            proportion=0,
            flag=wx.ALL | wx.EXPAND,
            border=5,
        )

        # Footprint painting.
        painting_title_panel = wx.Panel(fp_panel)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        painting_title_panel.SetSizer(hbox)
        hbox.Add(
            wx.StaticText(painting_title_panel, label="Footprint"),
            proportion=0,
            flag=wx.ALL,
            border=0,
        )
        hbox.AddSpacer(3*SPACING)
        self.actual_size_ckbx = wx.CheckBox(painting_title_panel, id=PAINT_ACTUAL_SIZE_CKBX_ID, label="Show actual size")
        self.actual_size_ckbx.SetToolTip(
            wx.ToolTip('Check to display actual size of footprint.'))
        hbox.Add(self.actual_size_ckbx, proportion=0, flag=wx.ALL, border=0)
        vbox.Add(painting_title_panel, proportion=0, flag=wx.ALL, border=SPACING)
        self.fp_painting_panel = FootprintPaintingPanel(fp_panel)
        vbox.Add(
            self.fp_painting_panel, proportion=1, flag=wx.ALL | wx.EXPAND, border=SPACING
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

            # Invalidate footprint cache after changing footprint search path.
            self.cache_invalid = True

        dlg.Destroy()

    def OnSearch(self, event):
        # Scan libraries looking for footprints that match search string.
        progress = wx.ProgressDialog(
            "Searching Footprint Libraries", "Loading footprints from libraries."
        )
        self.footprints = set()
        search_text = self.search_text.GetLineText(0)
        for lib_module in search_footprints_iter(search_text, cache_invalid=self.cache_invalid):
            if lib_module[0] == "LIB":
                lib_name = lib_module[1]
                lib_idx = lib_module[2]
                total_num_libs = lib_module[3]
                progress.SetRange(total_num_libs)
                progress.Update(
                    lib_idx, "Reading footprint library {}...".format(lib_name)
                )
            elif lib_module[0] == "MODULE":
                self.footprints.add(lib_module[1:])

        # Cache should be valid after running a search, so use it for further searches.
        self.cache_invalid = False

        # Sort parts by libraries and part names.
        self.footprints = sorted(
            list(self.footprints), key=lambda x: "/".join([x[0], x[2]])
        )

        # place libraries and parts into a table.
        grid = self.found_footprints

        # Clear any existing grid cells and add/sub rows to hold search results.
        grid.Resize(len(self.footprints))

        # Places libs and part names into table.
        for row, (lib, module_text, module_name) in enumerate(self.footprints):
            grid.SetCellValue(row, 0, lib)
            grid.SetCellValue(row, 1, module_name)

        # Size the columns for their new contents.
        grid.AutoSizeColumns()

        self.search_panel.Layout()

        grid.SelectRow(0)
        #grid.GoToCell(0, 1) # Causes program to hang!

    def OnSelectCell(self, event):
        # When a row of the footprint table is selected, display the data for that footprint.

        def natural_sort_key(s, _nsre=re.compile("([0-9]+)")):
            return [
                int(text) if text.isdigit() else text.lower() for text in _nsre.split(s)
            ]

        # Get any selected rows in the lib/part table plus wherever the cell cursor is.
        selection = [event.GetRow()]
        #selection = self.found_footprints.GetSelectedRows()
        #selection.append(self.found_footprints.GetGridCursorRow())

        # Only process the footprint in the first selected row and ignore the rest.
        for row in selection:

            module_text = self.footprints[row][1]
            try:
                module = pym.Module.parse("\n".join(module_text))
            except Exception as e:
                self.Feedback("Error while parsing {}:{}".format(self.footprints[row][0], self.footprints[row][2]), "Error")
                continue

            descr = "???"
            tags = "???"
            for line in module_text:
                try:
                    descr = line.split("(descr ")[1].rsplit(")", 1)[0]
                    descr = rmv_quotes(descr)
                except IndexError:
                    pass
                try:
                    tags = line.split("(tags ")[1].rsplit(")", 1)[0]
                    tags = rmv_quotes(tags)
                except IndexError:
                    pass

            # Show the part description.
            self.fp_desc.Remove(0, self.fp_desc.GetLastPosition())
            desc = descr[:]
            if tags != "???":
                desc += "\nTags: " + rmv_quotes(tags)
            self.fp_desc.WriteText(desc)

            # Display the link to the footprint datasheet.
            try:
                # Extract link-like text from the description.
                url = re.search("(?P<url>https?://[^\s]+)", descr).group("url")
                # Often, the link has punctuation at the end that should be removed.
                url = url.rstrip(string.punctuation)
            except AttributeError:
                # No URL found so hide the hyperlink.
                self.datasheet_link.SetURL(None)
                self.datasheet_link.Hide()
            else:
                # URL was found, so set the hyperlink and show it.
                self.datasheet_link.SetURL(url)
                self.datasheet_link.Show()

            # Set the footprint that will be displayed.
            self.fp_painting_panel.footprint = module

            # Re-layout the panel to account for link hide/show.
            self.fp_panel.Layout()

            # Return after processing only one footprint.
            return

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

    def Feedback(self, msg, label):
        dlg = wx.MessageDialog(self, msg, label, wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def ShowHelp(self, e):
        self.Feedback(
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
        self.Feedback(
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
    SkidlFootprintSearch(None)
    ex.MainLoop()


if __name__ == "__main__":
    main()
