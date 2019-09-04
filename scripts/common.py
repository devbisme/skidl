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
GUI components in common with multiple apps.
"""

import re

import wx
import wx.grid
import wx.lib.agw.hyperlink as hl
import wx.lib.expando

APP_SIZE = (600, 500)
BTN_SIZE = (50, -1)
SPACING = 10
TEXT_BOX_WIDTH = 200
CELL_BCK_COLOUR = wx.Colour(255, 255, 255)


def natural_sort_key(s, _nsre=re.compile("([0-9]+)")):
    """For sorting pin numbers or names."""
    return [int(text) if text.isdigit() else text.lower() for text in _nsre.split(s)]


def Feedback(msg, label):
    dlg = wx.MessageDialog(None, msg, label, wx.OK)
    dlg.ShowModal()
    dlg.Destroy()


class Description(wx.Panel):
    def __init__(self, parent, label):
        super(self.__class__, self).__init__(parent)

        vbox = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(vbox)

        vbox.Add(
            wx.StaticText(self, label=label),
            proportion=0,
            flag=wx.ALL,
            border=SPACING / 2,
        )

        self.desc = wx.TextCtrl(
            self,
            #            size=(TEXT_BOX_WIDTH, 60),
            size=(10000, 60),
            style=wx.TE_READONLY | wx.TE_MULTILINE | wx.TE_NO_VSCROLL,
        )
        vbox.Add(self.desc, proportion=0, flag=wx.ALL, border=SPACING)

        vbox.Add(
            wx.StaticLine(self, size=(10000, 2), style=wx.LI_HORIZONTAL),
            proportion=0,
            flag=wx.ALL | wx.EXPAND,
            border=SPACING / 2,
        )

    def SetDescription(self, description):
        self.desc.Remove(0, self.desc.GetLastPosition())
        if not description:
            self.Hide()
        else:
            self.desc.WriteText(description)
            self.Show()


class HyperLink(wx.Panel):
    def __init__(self, parent, label):
        super(self.__class__, self).__init__(parent)

        vbox = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(vbox)

        self.link = hl.HyperLinkCtrl(self, label=label, URL="")
        self.link.EnableRollover(True)
        vbox.Add(self.link, proportion=0, flag=wx.ALL, border=SPACING)

        vbox.Add(
            wx.StaticLine(self, size=(10000, 2), style=wx.LI_HORIZONTAL),
            proportion=0,
            flag=wx.ALL | wx.EXPAND,
            border=SPACING / 2,
        )

    def SetURL(self, url):
        self.link.SetURL(url)
        if not url:
            self.Hide()
        else:
            self.Show()


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
        self.Bind(wx.grid.EVT_GRID_LABEL_LEFT_DCLICK, self.SortColumn)
        self.SetLabelFont(self.GetLabelFont().MakeBold())
        # self.SetLabelFont(self.GetLabelFont().MakeLarger())
        self.sorting = {"col": 0, "dir": 0}
        self.sort_funcs = [lambda x: x] * len(headers)

    def Resize(self, numRows):
        if numRows == 0:
            numRows = 10
        self.ClearGrid()
        num_rows_chg = numRows - self.GetNumberRows()
        if num_rows_chg < 0:
            self.DeleteRows(0, -num_rows_chg, True)
        elif num_rows_chg > 0:
            self.AppendRows(num_rows_chg)
        self.ColourGridBackground()
        self.data_rows = list(range(numRows))

    def ColourGridBackground(self):
        for r in range(self.GetNumberRows()):
            for c in range(self.GetNumberCols()):
                self.SetCellBackgroundColour(r, c, self.BackgroundColour)

    def SetSortingIndicator(self, new_col, new_dir):
        ascending = " ▲"
        descending = " ▼"
        old_col = self.sorting["col"]
        old_dir = self.sorting["dir"]
        if old_dir != 0:
            self.SetColLabelValue(
                old_col, self.GetColLabelValue(old_col)[: -len(ascending)]
            )
        if new_dir > 0:
            self.sorting["dir"] = 1
            lbl = self.GetColLabelValue(new_col) + ascending
            self.SetColLabelValue(new_col, lbl)
        elif new_dir < 0:
            self.sorting["dir"] = -1
            lbl = self.GetColLabelValue(new_col) + descending
            self.SetColLabelValue(new_col, lbl)
        self.sorting["col"] = new_col

    def SetSortFunc(self, col, func):
        self.sort_funcs[col] = func

    def SortTable(self, sort_col, sort_dir):
        self.SetSortingIndicator(sort_col, sort_dir)
        n_rows = self.GetNumberRows()
        n_cols = self.GetNumberCols()
        tbl_vals = []
        for row in range(n_rows):
            row_vals = []
            for col in range(n_cols):
                row_vals.append(self.GetCellValue(row, col))
            row_vals.append(self.data_rows[row])
            tbl_vals.append(row_vals)

        def sort_func(x):
            return self.sort_funcs[sort_col](x[sort_col])

        tbl_vals.sort(key=sort_func, reverse=(sort_dir < 0))
        for row, row_vals in enumerate(tbl_vals):
            for col, col_val in enumerate(row_vals[:-1]):
                self.SetCellValue(row, col, col_val)
            self.data_rows[row] = row_vals[-1]

    def GetDataRow(self, row):
        return self.data_rows[row]

    def SortColumn(self, event):
        sort_col = event.GetCol()
        if sort_col != self.sorting["col"]:
            sort_dir = 1
        else:
            if self.sorting["dir"] > 0:
                sort_dir = -1
            else:
                sort_dir = 1
        self.SortTable(sort_col, sort_dir)
