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
GUI components in common with multiple apps.
"""

import re

import wx
import wx.grid
import wx.lib.agw.hyperlink as hl
import wx.lib.expando
import wx.lib.newevent

MINIMUM_PANE_SIZE = 300
SPACING = 5

# IDs for part and footprint panels.
PART_PANEL_ID = wx.NewId()
FOOTPRINT_PANEL_ID = wx.NewId()

# Events for part and footprint panels to cooperate with each other.
# Request footprint panel to send selected footprint.
RequestFootprintEvent, EVT_REQUEST_FOOTPRINT = wx.lib.newevent.NewEvent()
# Send selected footprint to part panel.
SendFootprintEvent, EVT_SEND_FOOTPRINT = wx.lib.newevent.NewEvent()
# Send search terms from part panel to footprint panel.
SendSearchTermsEvent, EVT_SEND_SEARCH_TERMS = wx.lib.newevent.NewEvent()


def is_dark_mode():
    window_colour = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)
    luminance = sum([c * f for c, f in zip(window_colour, [0.299, 0.587, 0.114])])
    return luminance < 128


def box_it(window, title_text):
    panel = wx.Panel(window.GetParent())
    window.Reparent(panel)
    sbox = wx.StaticBox(panel, label=title_text)
    box = wx.StaticBoxSizer(sbox, wx.VERTICAL)
    box.Add(window, proportion=1, flag=wx.ALL | wx.EXPAND, border=0)
    panel.SetSizer(box)
    return panel


def stack_it(*windows):
    """Stack windows vertically."""

    stack = wx.Panel(windows[0].GetParent())
    for window in windows:
        window.Reparent(stack)

    sizer = wx.BoxSizer(wx.VERTICAL)
    for window in windows[:-1]:
        sizer.Add(window, proportion=1, flag=wx.BOTTOM | wx.EXPAND, border=SPACING)
    sizer.Add(windows[-1], proportion=1, flag=wx.ALL | wx.EXPAND, border=0)

    stack.SetSizer(sizer)

    return stack


def add_title(window, title_text, location):
    """Add title to top/bottom of a window."""

    titled_window = wx.Panel(window.GetParent())
    window.Reparent(titled_window)

    title = wx.StaticText(
        titled_window, label=title_text, style=wx.ALIGN_CENTRE_HORIZONTAL
    )

    if is_dark_mode():
        title.SetBackgroundColour(wx.Colour(128, 128, 128))
        title.SetForegroundColour(wx.Colour(55, 55, 55))
    else:
        title.SetBackgroundColour(wx.Colour(128, 128, 128))
        title.SetForegroundColour(wx.Colour(200, 200, 200))

    title.SetFont(title.GetFont().MakeLarger().MakeBold().MakeItalic())
    box = wx.BoxSizer(wx.VERTICAL)

    if location == wx.TOP:
        box.Add(title, proportion=0, flag=wx.BOTTOM | wx.EXPAND, border=SPACING)
        box.Add(window, proportion=1, flag=wx.ALL | wx.EXPAND, border=0)
    else:
        box.Add(window, proportion=1, flag=wx.ALL | wx.EXPAND, border=0)
        box.Add(title, proportion=0, flag=wx.TOP | wx.EXPAND, border=SPACING)

    titled_window.SetSizer(box)

    return titled_window


def add_border(window, location):
    """Add border line to one side of a window."""

    bordered_window = wx.Panel(window.GetParent())
    window.Reparent(bordered_window)

    if location in (wx.TOP, wx.BOTTOM):
        border = wx.StaticLine(bordered_window, size=(-1, 2))
        box = wx.BoxSizer(wx.VERTICAL)
    else:
        border = wx.StaticLine(bordered_window, size=(2, -1))
        box = wx.BoxSizer(wx.HORIZONTAL)

    tip = wx.ToolTip("Drag sash to resize panes.")
    tip.SetDelay(0)
    border.SetToolTip(tip)

    if location == wx.TOP:
        box.Add(border, proportion=0, flag=wx.BOTTOM | wx.EXPAND, border=SPACING)
        box.Add(window, proportion=1, flag=wx.ALL | wx.EXPAND, border=0)
    elif location == wx.LEFT:
        box.Add(border, proportion=0, flag=wx.RIGHT | wx.EXPAND, border=SPACING)
        box.Add(window, proportion=1, flag=wx.ALL | wx.EXPAND, border=0)
    elif location == wx.BOTTOM:
        box.Add(window, proportion=1, flag=wx.ALL | wx.EXPAND, border=0)
        box.Add(border, proportion=0, flag=wx.TOP | wx.EXPAND, border=SPACING)
    else:
        box.Add(window, proportion=1, flag=wx.ALL | wx.EXPAND, border=0)
        box.Add(border, proportion=0, flag=wx.LEFT | wx.EXPAND, border=SPACING)

    bordered_window.SetSizer(box)

    return bordered_window


def Feedback(msg, label):
    """Show a dialog with a message and an OK button."""

    dlg = wx.MessageDialog(None, msg, label, wx.OK)
    dlg.ShowModal()
    dlg.Destroy()


class Description(wx.Panel):
    """Class for showing a text description in a TextCtrl box."""

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
            self, size=(10000, 60), style=wx.TE_READONLY | wx.TE_MULTILINE
        )
        vbox.Add(self.desc, proportion=0, flag=wx.ALL, border=SPACING)

        vbox.Add(
            wx.StaticLine(self, size=(10000, 2), style=wx.LI_HORIZONTAL),
            proportion=0,
            flag=wx.ALL | wx.EXPAND,
            border=SPACING / 2,
        )

    def SetDescription(self, description):
        """Set the description shown in the text box."""

        self.desc.Remove(0, self.desc.GetLastPosition())
        if not description:
            self.Hide()
        else:
            self.desc.WriteText(description)
            self.Show()


class HyperLink(wx.Panel):
    """Class for showing a clickable hyperlink."""

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
        """Set the URL for the clickable hyperlink."""

        self.link.SetURL(url)
        if not url:
            self.Hide()
        else:
            self.Show()


class TextEntryDialog(wx.Dialog):
    """Class for entering text in a dialog window."""

    def __init__(self, parent, title, caption, tip=None):

        # Create dialog window.
        style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        super(self.__class__, self).__init__(parent, -1, title, style=style)

        # Create text label describing the purpose of the window.
        text = wx.StaticText(self, -1, caption)

        # Create text entry box.
        self.input = wx.lib.expando.ExpandoTextCtrl(
            self, size=(int(0.75 * parent.GetSize()[0]), -1), style=wx.TE_PROCESS_ENTER
        )
        self.input.Bind(wx.EVT_TEXT_ENTER, self.OnEnter)

        # Add tool tip to text entry box.
        if tip:
            self.input.SetToolTip(wx.ToolTip(tip))

        # Add OK and Cancel buttons.
        buttons = self.CreateButtonSizer(wx.OK | wx.CANCEL)

        # Arrange all the items in the window.
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(text, 0, wx.ALL, 5)
        sizer.Add(self.input, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(buttons, 0, wx.EXPAND | wx.ALL, 5)
        self.SetSizerAndFit(sizer)

    def OnEnter(self, event):
        """End modal if enter is hit in input text control."""
        self.EndModal(wx.ID_OK)

    def SetValue(self, value):
        """Set the initial value shown in the text box."""
        self.input.SetValue(value.strip().rstrip())
        self.input.SetFocus()
        self.input.SetInsertionPointEnd()
        self.Fit()

    def GetValue(self):
        """Get the value entered in the text box."""
        return self.input.GetValue().strip().rstrip()


class MyGrid(wx.grid.Grid):
    """Class for displaying tabular data about parts, pins, footprints."""

    DEFAULT_NUM_ROWS = 10
    SPACER = "  "  # Spacer for begin/end of column labels.
    ASCENDING = " ▲"  # Indicator that column is sorted in ascending order.
    DESCENDING = " ▼"  # Indicator that column is sorted in descending order.

    def __init__(self, parent, headers):

        # Create grid with a column for each header label.
        super(self.__class__, self).__init__()
        self.Create(parent)
        self.CreateGrid(
            numRows=self.DEFAULT_NUM_ROWS,
            numCols=len(headers),
            selmode=wx.grid.Grid.SelectRows,
        )

        # Set table attributes.
        if is_dark_mode():
            # Set cell background and cursor colors for dark mode.
            self.BackgroundColour = wx.Colour(20, 20, 20)
            self.SetCellHighlightColour(wx.Colour(235, 235, 235))
        else:
            # Set cell background and cursor colors for light mode.
            self.BackgroundColour = wx.Colour(255, 255, 255)
            self.SetCellHighlightColour(wx.Colour(20, 20, 20))
        self.HideRowLabels()  # Hide row labels 1, 2, 3...
        self.EnableEditing(False)  # User can't edit values in table.
        self.SetDefaultCellBackgroundColour(parent.GetBackgroundColour())
        self.ColourGridBackground()
        self.SetSelectionMode(wx.grid.Grid.GridSelectionModes.SelectRows)
        self.SetLabelFont(self.GetLabelFont().MakeBold())
        self.SetTabBehaviour(wx.grid.Grid.Tab_Leave)

        # Set column header labels.
        for col, lbl in enumerate(headers):
            self.SetColLabelValue(col, self.SPACER + lbl + self.SPACER)

        # Set the initial column to sort by and the sorting direction.
        self.sorting = {"col": 0, "dir": 0}

        # Set sorting function for each column.
        self.sort_funcs = [lambda x: x] * len(headers)

        # Set event that triggers sorting of the table rows.
        self.Bind(wx.grid.EVT_GRID_LABEL_LEFT_DCLICK, self.OnSort)

        # Set event that copies selected cells to the clipboard.
        self.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.OnCopy)

    def Resize(self, numRows=0):
        """Clear the table and resize the number of rows."""

        if numRows == 0:
            numRows = self.DEFAULT_NUM_ROWS
        self.ClearGrid()
        num_rows_chg = numRows - self.GetNumberRows()
        if num_rows_chg < 0:
            self.DeleteRows(0, -num_rows_chg, True)
        elif num_rows_chg > 0:
            self.AppendRows(num_rows_chg)
        self.SetSortingIndicator(0, 0)  # No sorting at the start.
        self.ColourGridBackground()

        # Create a list of row indices that will be sorted along with the
        # table. Then when data moves to a different row, the index associated
        # with that row will indicate the index into the original data set.
        self.data_row_indices = list(range(numRows))

    def ColourGridBackground(self):
        """Set the background color of all the cells in the table."""

        for r in range(self.GetNumberRows()):
            for c in range(self.GetNumberCols()):
                self.SetCellBackgroundColour(r, c, self.BackgroundColour)

    def SetSortingIndicator(self, new_col, new_dir):
        """Set the sorting indicator for a given table column."""

        # Remove sorting indicator from old column label.
        old_col = self.sorting["col"]
        self.SetColLabelValue(
            old_col, self.GetColLabelValue(old_col)[: -len(self.SPACER)] + self.SPACER
        )

        # Set the sorting indicator for the new column.
        if new_dir < 0:
            indicator = self.DESCENDING
        elif new_dir == 0:
            indicator = self.SPACER
        else:
            indicator = self.ASCENDING
        self.SetColLabelValue(
            new_col, self.GetColLabelValue(new_col)[: -len(indicator)] + indicator
        )
        self.sorting["dir"] = new_dir
        self.sorting["col"] = new_col

    def SetSortFunc(self, col, func):
        """Set the sorting function for a particular table column."""

        self.sort_funcs[col] = func

    def SortTable(self, sort_col, sort_dir):
        """Sort the table rows based on the values in a particular column."""

        self.SetSortingIndicator(sort_col, sort_dir)
        n_rows = self.GetNumberRows()
        n_cols = self.GetNumberCols()

        # Copy rows of data from the cells of the table into a sortable list.
        tbl_vals = []
        for row in range(n_rows):
            row_vals = []
            for col in range(n_cols):
                row_vals.append(self.GetCellValue(row, col))
            # Append the index of the original row location to each row of data.
            # This is used to find the original data values after the rows have
            # been moved during sorting.
            row_vals.append(self.data_row_indices[row])
            tbl_vals.append(row_vals)  # Append row of values to list.

        # This function will extract the value from the sorting column
        # of a row of data, apply the sorting function for that column to
        # the data, and return the result to the Python sort routine.
        def sort_func(data_row):
            return self.sort_funcs[sort_col](data_row[sort_col])

        # Sort the list of data rows based on the values in one of the columns.
        tbl_vals.sort(key=sort_func, reverse=(sort_dir < 0))

        # Re-enter the data into the cells of the table.
        for row, row_vals in enumerate(tbl_vals):
            for col, col_val in enumerate(row_vals[:-1]):
                self.SetCellValue(row, col, col_val)
            # Update the indices for where the data in each row of the table
            # came from in the original data set.
            self.data_row_indices[row] = row_vals[-1]

    def GetDataRowIndex(self, tbl_row):
        """
        For a given row in the table of cells, return the index of the row
        in the original set of data used to create the table.
        """
        return self.data_row_indices[tbl_row]

    def OnSort(self, event):
        """Sort the table based on which column header is clicked."""

        sort_col = event.GetCol()
        if sort_col != self.sorting["col"]:
            # If a new column was selected for sorting, always start in ascending mode.
            sort_dir = 1
        else:
            # If the same sorting column was selected, then toggle the sorting direction.
            sort_dir = -self.sorting["dir"] or 1  # If dir==0, then set it to 1.

        # Sor the data in the table of cells.
        self.SortTable(sort_col, sort_dir)

    def OnCopy(self, event):
        num_rows = self.GetNumberRows()
        num_cols = self.GetNumberCols()
        cells = []
        for cell in self.GetSelectedCells():
            cells.append((cell[0], cell[1]))
        for selrow in self.GetSelectedRows():
            for c in range(num_cols):
                cells.append((selrow, c))
        for selcol in self.GetSelectedCols():
            for r in range(num_rows):
                cells.append((r, selcol))
        for topleft, bottomright in zip(
            self.GetSelectionBlockTopLeft(), self.GetSelectionBlockBottomRight()
        ):
            for r in range(topleft[0], bottomright[0] + 1):
                for c in range(topleft[1], bottomright[1] + 1):
                    cells.append((r, c))

        cells.sort()

        prev_row = cells[0][0]  # First row in cell coords.
        vals = ""
        for row, col in cells:
            if row != prev_row:
                vals += "\n"
            vals += '"' + str(self.GetCellValue(row, col)) + '"' + ", "
            prev_row = row

        # Make a data object to hold the cell values.
        dataObj = wx.TextDataObject()
        dataObj.SetText(vals[:-2])  # Strip off last ", "

        # Place the cell values on the clipboard.
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(dataObj)
            wx.TheClipboard.Flush()
        else:
            Feedback("Unable to open clipboard!", "Error")
