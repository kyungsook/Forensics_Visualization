#!/usr/bin/env python

#    This file is part of python-registry.
#
#   Copyright 2011 Will Ballenthin <william.ballenthin@mandiant.com>
#                    while at Mandiant <http://www.mandiant.com>
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
from __future__ import print_function
from __future__ import unicode_literals

import sys
import os
import wx
import wx.html
import Registry
import drawGraph
import webbrowser
import export

ID_FILE_OPEN = wx.NewIdRef()
ID_FILE_SESSION_SAVE = wx.NewIdRef()
ID_FILE_SESSION_OPEN = wx.NewIdRef()
ID_TAB_CLOSE = wx.NewIdRef()
ID_FILE_EXIT = wx.NewIdRef()
ID_HELP_ABOUT = wx.NewIdRef()
ID_DRAW_GRAPH = wx.NewIdRef()
ID_HISTORY_EXPORT = wx.NewIdRef()

offset_text = '0000000'
hex_text = '11111111'


def nop(*args, **kwargs):
    pass


def basename(path): #path를 잘라서 파일 이름을 추출한다
    if "/" in path:
        path = path.split("/")[-1]
    if "\\" in path:
        path = path.split("\\")[-1]
    return path


def _expand_into(dest, src):
    vbox = wx.BoxSizer(wx.VERTICAL) #BoxSizer: subwindow를 window에 넣기 위해 사용되는 클래스
    vbox.Add(src, 1, wx.EXPAND | wx.ALL)    #src에 꽉 차게 넣는다
    dest.SetSizer(vbox)


def _format_hex(data):
    byte_format = {}
    for c in xrange(256):   #return 값이 xrange. 수정이 불가능한 순차적 접근 가능한 데이터 타입
        if c > 126:
            byte_format[c] = '.'
        elif len(repr(chr(c))) == 3 and chr(c):
            byte_format[c] = chr(c)
        else:
            byte_format[c] = '.'

    def format_bytes(s):
        return "".join([byte_format[ord(c)] for c in s])

    def dump(src, length=16):
        N = 0
        result = ''
        while src:
            s, src = src[:length], src[length:]
            hexa = ' '.join(["%02X" % ord(x) for x in s])
            s = format_bytes(s)
            result += "%04X   %-*s   %s\n" % (N, length * 3, hexa, s)
            N += length
        return result
    return dump(data)


class DataPanel(wx.Panel):
    """
    Displays the contents of a Registry value.
    Shows a text string where appropriate, or a hex dump.
    """
    def __init__(self, *args, **kwargs):
        super(DataPanel, self).__init__(*args, **kwargs)
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self._sizer)

    def display_value(self, value):
        self._sizer.Clear()

        view = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY)
        view.SetValue(offset_text)

        self._sizer.Add(view, 1, wx.EXPAND)
        self._sizer.Layout()

    def clear_value(self):
        self._sizer.Clear()
        self._sizer.Add(wx.Panel(self, -1), 1, wx.EXPAND)
        self._sizer.Layout()

class ImagePanel(wx.Panel):
    """
        Displays the contents of a Registry value.
        Shows a text string where appropriate, or a hex dump.
        """

    def __init__(self, *args, **kwargs):
        super(ImagePanel, self).__init__(*args, **kwargs)
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self._sizer)



class ValuesListCtrl(wx.ListCtrl):
    """
    Shows a list of values associated with a Registry key.
    """
    def __init__(self, *args, **kwargs):
        super(ValuesListCtrl, self).__init__(*args, **kwargs)
        self.InsertColumn(0, "Name")
        self.InsertColumn(1, "Type")
        self.InsertColumn(2, "Size")
        self.InsertColumn(3, "Time")
        self.InsertColumn(4, "Data")
        self.SetColumnWidth(0, 100)
        self.SetColumnWidth(1, 100)
        self.SetColumnWidth(2, 100)
        self.SetColumnWidth(3, 100)
        self.SetColumnWidth(4, 300)

        self.values = {}

    def clear_values(self):
        self.DeleteAllItems()
        self.values = {}

    def add_value(self, value):
        n = self.GetItemCount()
        self.InsertStringItem(n, value.name())
        self.SetStringItem(n, 1, value.value_type_str())
        self.values[value.name()] = value

    def get_value(self, valuename):
        return self.values[valuename]

class RegistryTreeCtrl(wx.TreeCtrl):
    """
    Treeview control that displays the Registry key structure.
    """
    def __init__(self, *args, **kwargs):
        super(RegistryTreeCtrl, self).__init__(*args, **kwargs)
        self.Bind(wx.EVT_TREE_ITEM_EXPANDING, self.OnExpandKey)

    def add_registry(self, registry):
        """
        Add the registry to the control as the (a?) root element.
        """
        root_key = registry.root()
        root_item = self.AddRoot(root_key.name())
        self.SetPyData(root_item, {"key": root_key,
                                   "has_expanded": False})

        if len(root_key.subkeys()) > 0:
            self.SetItemHasChildren(root_item)

    def delete_registry(self):
        """
        Removes all elements from the control.
        """
        self.DeleteAllItems()

    def select_path(self, path):
        """
        Take a Registry key path separated by back slashes and select
        that key. The path should not contain the root key name.
        If the key is not found, the most specific ancestor key is selected.
        """
        parts = path.split("\\")
        node = self.GetRootItem()

        for part in parts:
            self._extend(node)
            (node, cookie) = self.GetFirstChild(node)

            cont = True
            while node and cont:
                key = self.GetPyData(node)["key"]
                if key.name() == part:
                    self.SelectItem(node)
                    cont = False
                else:
                    node = self.GetNextSibling(node)

    def _extend(self, item):
        """
        Lazily parse and add children items to the tree.
        """
        if self.GetPyData(item)["has_expanded"]:
            return

        key = self.GetPyData(item)["key"]

        for subkey in key.subkeys():
            subkey_item = self.AppendItem(item, subkey.name())
            self.SetPyData(subkey_item, {"key": subkey,
                                         "has_expanded": False})

            if len(subkey.subkeys()) > 0:
                self.SetItemHasChildren(subkey_item)

        self.GetPyData(item)["has_expanded"] = True

    def OnExpandKey(self, event):
        item = event.GetItem()
        if not item.IsOk():
            item = self.GetSelection()

        if not self.GetPyData(item)["has_expanded"]:
            self._extend(item)

class FilterFrame(wx.Frame):    # visualization filter

    def __init__(self, title, parent=None):
        wx.Frame.__init__(self, parent=parent, title=title, size =(400, 300),
                          style=wx.DEFAULT_FRAME_STYLE^wx.MAXIMIZE_BOX^wx.RESIZE_BORDER)
        panel = wx.Panel(self, -1, size =(400, 300))

        self.viewList = ['Registry File Access History', 'General File Access History', 'Internet URL History']
        self.rbox = wx.RadioBox(panel, label='View', pos=(20, 20), choices=self.viewList, majorDimension=1)
        self.rbox.Bind(wx.EVT_RADIOBOX, self.onRadioBox)

        wx.StaticText(panel, -1, "Period", pos=(25, 130))
        self.text_from = wx.TextCtrl(panel, -1, pos=(20, 155))
        self.text_from.SetHint("YYYY-MM-DD")
        wx.StaticText(panel, -1, "~", pos=(140, 160))
        self.text_to = wx.TextCtrl(panel, -1, pos=(160, 155))
        self.text_to.SetHint("YYYY-MM-DD")

        button = wx.Button(panel, label="Draw", pos=(170, 200), size=(50, 30))
        self.Bind(wx.EVT_BUTTON, self.open_html_file, button)
        self.Show()

    def open_html_file(self, event):
        tableName = ""
        date_from = self.text_from.GetValue()
        date_to = self.text_to.GetValue()

        myGraph = drawGraph.Graph(date_from, date_to)

        if self.rbox.GetStringSelection() == self.viewList[0]:
            tableName = "Hive"
        elif self.rbox.GetStringSelection() == self.viewList[1]:
            tableName = "General"
        elif self.rbox.GetStringSelection() == self.viewList[2]:
            tableName = "urls"

        myGraph.get_total_key()
        myGraph.draw_graph_html(tableName)

        filepath = "UserRecord.html"

        # open raw html
        webbrowser.open_new_tab(filepath)

        # open html on new window
        # frm = MyHtmlFrame(None, filepath)
        # frm.Show()

    def onRadioBox(self, event):
        if self.rbox.GetStringSelection() == self.viewList[0]:
            print("hive")
        elif self.rbox.GetStringSelection() == self.viewList[1]:
            print("general file")
        elif self.rbox.GetStringSelection() == self.viewList[2]:
            print("urls")

class FilterFrame2(wx.Frame):   # web history export filter

    def __init__(self, title, parent=None):
        wx.Frame.__init__(self, parent=parent, title=title, size =(400, 300),
                          style=wx.DEFAULT_FRAME_STYLE^wx.MAXIMIZE_BOX^wx.RESIZE_BORDER)
        panel = wx.Panel(self, -1, size =(400, 300))

        self.viewList = ['Registry File Access History', 'General File Access History', 'Internet URL History']
        self.rbox = wx.RadioBox(panel, label='View', pos=(20, 20), choices=self.viewList, majorDimension=1)
        self.rbox.Bind(wx.EVT_RADIOBOX, self.onRadioBox)

        wx.StaticText(panel, -1, "Period", pos=(25, 130))
        self.text_from = wx.TextCtrl(panel, -1, pos=(20, 155))
        self.text_from.SetHint("YYYY-MM-DD")
        wx.StaticText(panel, -1, "~", pos=(140, 160))
        self.text_to = wx.TextCtrl(panel, -1, pos=(160, 155))
        self.text_to.SetHint("YYYY-MM-DD")

        button = wx.Button(panel, label="Export", pos=(170, 200), size=(50, 30))
        self.Bind(wx.EVT_BUTTON, self.export_file, button)
        self.Show()

    def export_file(self, event):
        date_from = self.text_from.GetValue()
        date_to = self.text_to.GetValue()

        if self.rbox.GetStringSelection() == self.viewList[0]:
            export.export_history('Hive', date_from, date_to)
            print("hive")
        elif self.rbox.GetStringSelection() == self.viewList[1]:
            export.export_history('GeneralFile', date_from, date_to)
            print("general file")
        elif self.rbox.GetStringSelection() == self.viewList[2]:
            export.export_history('urls', date_from, date_to)
            print("urls")
        print("export success!")

    def onRadioBox(self, event):
        if self.rbox.GetStringSelection() == self.viewList[0]:
            print("hive")
        elif self.rbox.GetStringSelection() == self.viewList[1]:
            print("general file")
        elif self.rbox.GetStringSelection() == self.viewList[2]:
            print("urls")


class MyHtmlFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(
            self,
            parent,
            -1,
            title,
            size=(600, 400)
        )

        # Use current window as container of the Html Frame
        html = wx.html.HtmlWindow(self)

        # if "gtk2" in wx.PlatformInfo:
        #     html.SetStandardFonts()

        # Alternatively render raw HTML with the SetPage method
        # html.SetPage("<h4>Hello World</h4>")
        # Render a local HTML file
        html.LoadPage("UserRecord.html")


class RegistryFileView(wx.Panel):
    """
    A three-paned display of the RegistryTreeCtrl, ValueListCtrl, and DataPanel.
    """
    def __init__(self, parent, registry, filename):
        super(RegistryFileView, self).__init__(parent, -1, size=(800, 600))
        self._filename = filename

        vsplitter = wx.SplitterWindow(self, -1)
        panel_left = wx.Panel(vsplitter, -1)
        self._tree = RegistryTreeCtrl(panel_left, -1)
        _expand_into(panel_left, self._tree)

        hsplitter = wx.SplitterWindow(vsplitter, -1)
        panel_top = wx.Panel(hsplitter, -1)
        #panel_bottom = wx.Panel(hsplitter, -1)

        vsplitter_data = wx.SplitterWindow(hsplitter, -1)
        panel_offset = wx.Panel(vsplitter_data, -1)
        panel_hex = wx.Panel(vsplitter_data, -1)


        self._value_list_view = ValuesListCtrl(panel_top, -1, style=wx.LC_REPORT)
        self._offset_view = DataPanel(panel_offset, -1)
        self._hex_view = DataPanel(panel_hex, -1)

        _expand_into(panel_top,    self._value_list_view)
        _expand_into(panel_offset, self._offset_view)
        _expand_into(panel_hex, self._hex_view)

        vsplitter.SplitVertically(panel_left, hsplitter)
        hsplitter.SplitHorizontally(panel_top, vsplitter_data)
        vsplitter_data.SplitVertically(panel_offset, panel_hex)

        # give enough space in the data display for the hex output
        hsplitter.SetSashPosition(250, True)
        vsplitter.SetSashPosition(325, True)
        vsplitter_data.SetSashPosition(800, True)
        _expand_into(self, vsplitter)
        self.Centre()

        self._value_list_view.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnValueSelected)
        self._offset_view.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnValueSelected)
        self._hex_view.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnValueSelected)
        self._tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnKeySelected)

        self._tree.add_registry(registry)

    def OnKeySelected(self, event):
        item = event.GetItem()
        if not item.IsOk():
            item = self._tree.GetSelection()

        key = self._tree.GetPyData(item)["key"]

        parent = self.GetParent()
        while parent:
            try:
                parent.SetStatusText(key.path())
            except AttributeError:
                pass
            parent = parent.GetParent()

        self._offset_view.clear_value()
        self._hex_view.clear_value()
        self._value_list_view.clear_values()

        for value in key.values():
            self._value_list_view.add_value(value)
            # self._offset_view.add_value(value)
            # self._hex_view.add_value(value)

    def OnValueSelected(self, event):
        item = event.GetItem()

        value = self._value_list_view.get_value(item.GetText())
        self._hex_view.display_value(value)
        self._offset_view.display_value(value)

    def filename(self):
        """
        Return the filename of the current Registry file as a string.
        """
        return self._filename

    def selected_path(self):
        """
        Return the Registry key path of the currently selected item.
        """
        item = self._tree.GetSelection()
        if item:
            return self._tree.GetPyData(item)["key"].path()
        return False

    def select_path(self, path):
        """
        Select a Registry key path specified as a string in the relevant panes.
        """
        self._tree.select_path(path)


class RegistryFileViewer(wx.Frame):
    """
    The main RegView GUI application.
    """
    def __init__(self, parent, files):
        super(RegistryFileViewer, self).__init__(parent, -1, "Registry File Viewer", size=(800, 600))
        self.CreateStatusBar()

        menu_bar = wx.MenuBar() #상단 메뉴바 생성

        file_menu = wx.Menu()   #메뉴바 중 'File' 메뉴 생성
        _open = file_menu.Append(ID_FILE_OPEN, '&Open File')    #File 메뉴에 open file, save, open, exit 넣음
        self.Bind(wx.EVT_MENU, self.menu_file_open, _open)
        _history = file_menu.Append(ID_HISTORY_EXPORT, '&Export')
        self.Bind(wx.EVT_MENU, self.menu_history_export, _history)
        # file_menu.AppendSeparator()
        # _session_save = file_menu.Append(ID_FILE_SESSION_SAVE, '&Save Session')
        # self.Bind(wx.EVT_MENU, self.menu_file_session_save, _session_save)
        # _session_open = file_menu.Append(ID_FILE_SESSION_OPEN, '&Open Session')
        # self.Bind(wx.EVT_MENU, self.menu_file_session_open, _session_open)
        file_menu.AppendSeparator()
        _exit = file_menu.Append(ID_FILE_EXIT, '&Exit Program')
        self.Bind(wx.EVT_MENU, self.menu_file_exit, _exit)
        menu_bar.Append(file_menu, "&File")

        vis_menu = wx.Menu()
        _graph = vis_menu.Append(ID_DRAW_GRAPH, '&Draw Graph')
        self.Bind(wx.EVT_MENU, self.menu_draw_graph, _graph)
        menu_bar.Append(vis_menu, "&Visualization")

        help_menu = wx.Menu()
        _about = help_menu.Append(ID_HELP_ABOUT, '&About')
        self.Bind(wx.EVT_MENU, self.menu_help_about, _about)
        menu_bar.Append(help_menu, "&Help")
        self.SetMenuBar(menu_bar)

        p = wx.Panel(self)
        self._nb = wx.Notebook(p)

        for filename in files:
            self._open_registry_file(filename)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._nb, 1, wx.EXPAND)
        p.SetSizer(sizer)
        self.Layout()

    def _open_registry_file(self, filename):
        """
        Open a Registry file by filename into a new tab and return the window.
        """
        with open(filename, "rb") as f:
            registry = Registry.Registry(f)
            view = RegistryFileView(self._nb, registry=registry, filename=filename)
            self._nb.AddPage(view, basename(filename))
            return view
        # TODO handle error

    def menu_file_open(self, evt):
        dialog = wx.FileDialog(None, "Choose Registry File", "", "", "*", wx.FD_OPEN)
        if dialog.ShowModal() != wx.ID_OK:
            return
        filename = os.path.join(dialog.GetDirectory(), dialog.GetFilename())
        self._open_registry_file(filename)

    def menu_file_exit(self, evt):
        sys.exit(0)

    def menu_file_session_open(self, evt):
        self._nb.DeleteAllPages()

        dialog = wx.FileDialog(None, "Open Session File", "", "", "*", wx.OPEN)
        if dialog.ShowModal() != wx.ID_OK:
            return
        filename = os.path.join(dialog.GetDirectory(), dialog.GetFilename())
        with open(filename, "rb") as f:
            t = f.read()

            lines = t.split("\n")

            if len(lines) % 2 != 1:  # there is a trailing newline
                self.SetStatusText("Malformed session file!")
                return

            while len(lines) > 1:
                filename = lines.pop(0)
                path = lines.pop(0)

                view = self._open_registry_file(filename)
                view.select_path(path.partition("\\")[2])

            self.SetStatusText("Opened session")

    def menu_file_session_save(self, evt):
        dialog = wx.FileDialog(None, "Save Session File", "", "", "*", wx.SAVE)
        if dialog.ShowModal() != wx.ID_OK:
            return
        filename = os.path.join(dialog.GetDirectory(), dialog.GetFilename())
        with open(filename, "wb") as f:
            for i in range(0, self._nb.GetPageCount()):
                page = self._nb.GetPage(i)
                f.write(page.filename() + "\n")

                path = page.selected_path()
                if path:
                    f.write(path)
                f.write("\n")
            self.SetStatusText("Saved session")
        # TODO handle error


    def menu_help_about(self, evt):
        wx.MessageBox("please visit our Github \n\n https://github.com/kyungsook/Forensics_Visualization", "About")

    def menu_draw_graph(self, evt):
        print("창 띄우기")
        title = 'Filter'
        frame = FilterFrame(title = title)

    def menu_history_export(self, evt):
        print("웹 히스토리 내보내기")
        title = 'Filter'
        frame = FilterFrame2(title=title)




if __name__ == '__main__':
    app = wx.App(False)

    filenames = []
    filenames = sys.argv[1:]

    frame = RegistryFileViewer(None, filenames)
    frame.Show()
    app.MainLoop()
