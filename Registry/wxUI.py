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
import General

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


def basename(path):  # path를 잘라서 파일 이름을 추출한다
    if "/" in path:
        path = path.split("/")[-1]
    if "\\" in path:
        path = path.split("\\")[-1]
    return path


def _expand_into(dest, src):
    vbox = wx.BoxSizer(wx.VERTICAL)  # BoxSizer: subwindow를 window에 넣기 위해 사용되는 클래스
    vbox.Add(src, 1, wx.EXPAND | wx.ALL)  # src에 꽉 차게 넣는다
    dest.SetSizer(vbox)


def _format_hex(data):
    byte_format = {}
    for c in xrange(256):  # return 값이 xrange. 수정이 불가능한 순차적 접근 가능한 데이터 타입
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

    def display_value(self, data):
        self._sizer.Clear()

        view = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY)
        font1 = wx.Font(11, wx.MODERN, wx.NORMAL, wx.NORMAL, False, u'Consolas')
        view.SetFont(font1)
        view.SetValue(data)

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
        self.InsertColumn(2, "Size(byte)")
        self.InsertColumn(3, "Time")
        self.InsertColumn(4, "Data")
        self.SetColumnWidth(0, 150)
        self.SetColumnWidth(1, 150)
        self.SetColumnWidth(2, 100)
        self.SetColumnWidth(3, 200)
        self.SetColumnWidth(4, 500)

        self.files = {}
        self.values = {}

    def clear_values(self):
        self.DeleteAllItems()
        self.values = {}

    def add_file(self, entry):
        """
        add file list
        Column(0, "Name")
        Column(1, "Type")
        Column(2, "Size")
        Column(3, "Time")
        Column(4, "Data")
        """
        n = self.GetItemCount()
        if 'name' in entry:
            self.InsertItem(n, entry['name'])
            self.files[entry['name']] = entry

        else:
            self.InsertItem(n, entry['sname'])
            self.files[entry['sname']] = entry

        self.SetItem(n, 1, entry['ext'])
        self.SetItem(n, 2, str(entry['size']))
        self.SetItem(n, 3, self.timeToString(entry, 'write_date', 'write_time'))

        if 'del' in entry:
            self.SetItem(n, 4, 'DELETED FILE')

    def add_value(self, value,timestamp):
        """
        add registry value list
        Column(0, "Name")
        Column(1, "Type")
        Column(2, "Size")
        Column(3, "Time")
        Column(4, "Data")
        """
        n = self.GetItemCount()
        self.InsertItem(n, value.name())
        self.SetItem(n, 1, value.value_type_str())
        self.SetItem(n,3, str(timestamp))
        self.SetItem(n, 4, value.value())#고치기 이상하게 나옴
        self.values[value.name()] = value
        print(self.values)

    def get_value(self, valuename):
        return self.values[valuename]

    def timeToString(self, entry, date_type, time_type):
        # TODO: 계산하면서 에러있는거같으니까 수정해야한다
        time_string = str(((entry[date_type] & 65024) >> 9) + 1980) + '/' + str(
            (entry[date_type] & 480) >> 5) + '/' + str(entry[date_type] & 31) + ' - ' + str(
            (entry[time_type] & 63488) >> 11) + ':' + str(
            (entry[time_type] & 2016) >> 5) + ':' + str(
            (entry[time_type] & 31) * 2)
        return time_string


class DirTreeCtrl(wx.TreeCtrl):
    """
    Treeview control that displays the Registry key structure.
    """

    def __init__(self, *args, **kwargs):
        super(DirTreeCtrl, self).__init__(*args, **kwargs)
        self.Bind(wx.EVT_TREE_ITEM_EXPANDING, self.OnExpandDir)

        # put directory, file icon to tree
        il = wx.ImageList(16, 16)
        self.fldropenidx = il.Add(wx.ArtProvider.GetBitmap(wx.ART_FOLDER_OPEN, wx.ART_OTHER, (16, 16)))
        self.fldridx = il.Add(wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, (16, 16)))
        self.fileidx = il.Add(wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, (16, 16)))
        self.deleteidx = il.Add(wx.ArtProvider.GetBitmap(wx.ART_DELETE, wx.ART_OTHER, (16,16)))
        self.AssignImageList(il)

    # add root directory from disk Image file to TreeListCtrl
    def add_directory(self, root_dir):
        root_key = root_dir.fatTreeStructure

        root_item = self.AddRoot(root_key.current_dir['sname'])  # 루트만드는곳

        self.SetItemImage(root_item, self.fldridx, wx.TreeItemIcon_Normal)
        self.SetItemImage(root_item, self.fldropenidx, wx.TreeItemIcon_Expanded)

        self.SetItemData(root_item, {"key": root_key, "has_expanded": False})
        if len(root_key.dir_obj_list) > 0:
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

    # append sub directory, registry to tree
    def _extend_dir(self, item):
        """
        Add Directory and Registry Key to TreeCtrlList
        """
        if self.GetItemData(item)["has_expanded"]:
            return

        dir = self.GetItemData(item)["key"]
        print(dir)

        # append Directory
        if type(dir).__name__ == 'Dir': #Dir class
            try:
                for subdir in dir.dir_obj_list:
                    if 'name' in subdir.current_dir:  # long file name
                        subdir_item = self.AppendItem(item, subdir.current_dir['name'])

                    else:  # short file name
                        subdir_item = self.AppendItem(item, subdir.current_dir['sname'])

                    self.SetItemData(subdir_item, {"key": subdir,
                                                   "has_expanded": False})
                    if 'del' in subdir.current_dir:
                        self.SetItemImage(subdir_item, self.deleteidx, wx.TreeItemIcon_Normal)

                    else:
                        self.SetItemImage(subdir_item, self.fldridx, wx.TreeItemIcon_Normal)
                        self.SetItemImage(subdir_item, self.fldropenidx, wx.TreeItemIcon_Expanded)

                    if len(subdir.dir_obj_list) > 0 or len(subdir.reg_obj_list) > 0:
                        self.SetItemHasChildren(subdir_item)
            except AttributeError:
                pass

            # append registry file
            try:
                for subreg in dir.reg_obj_list:
                    # key = subreg.root()
                    # subreg_item = self.AppendItem(item, key.filename())
                    # self.SetItemData(subreg_item, {"key": key,
                    #                                "has_expanded": False})

                    subreg_item = self.AppendItem(item, subreg._filename)
                    self.SetItemData(subreg_item, {"key": subreg.root(),
                                                   "has_expanded": False})
                    self.SetItemImage(subreg_item, self.fileidx, wx.TreeItemIcon_Normal)
                    self.SetItemHasChildren(subreg_item)
            except AttributeError:
                pass

        # append registry subkeys
        elif type(dir).__name__ == 'RegistryKey':   # RegistryKey class
            try:
                for subkey in dir.subkeys():
                    subkey_item = self.AppendItem(item, subkey.name())
                    self.SetItemData(subkey_item, {"key": subkey,
                                                   "has_expanded": False})
                    self.SetItemImage(subkey_item, self.fldridx, wx.TreeItemIcon_Normal)

                    if len(subkey.subkeys()) > 0:
                        self.SetItemHasChildren(subkey_item)
            except AttributeError:
                pass

        self.GetItemData(item)["has_expanded"] = True

    # tree + onclicked (expanded)
    def OnExpandDir(self, event):
        item = event.GetItem()
        if not item.IsOk():
            item = self.GetSelection()

        if not self.GetItemData(item)["has_expanded"]:
            self._extend_dir(item)


class FilterFrame(wx.Frame):  # visualization filter

    def __init__(self, title, parent=None, btnName=""):
        wx.Frame.__init__(self, parent=parent, title=title, size=(400, 300),
                          style=wx.DEFAULT_FRAME_STYLE ^ wx.MAXIMIZE_BOX ^ wx.RESIZE_BORDER)
        panel = wx.Panel(self, -1, size=(400, 300))

        self.viewList = ['Registry File Access History', 'General File Access History', 'Internet URL History']
        self.rbox = wx.RadioBox(panel, label='View', pos=(20, 20), choices=self.viewList, majorDimension=1)
        self.rbox.Bind(wx.EVT_RADIOBOX, self.onRadioBox)

        wx.StaticText(panel, -1, "Period", pos=(25, 130))
        self.text_from = wx.TextCtrl(panel, -1, pos=(20, 155))
        self.text_from.SetHint("YYYY-MM-DD")
        wx.StaticText(panel, -1, "~", pos=(140, 160))
        self.text_to = wx.TextCtrl(panel, -1, pos=(160, 155))
        self.text_to.SetHint("YYYY-MM-DD")

        button = wx.Button(panel, label=btnName, pos=(170, 200), size=(50, 30))
        if btnName == "Draw":
            self.Bind(wx.EVT_BUTTON, self.open_html_file, button)

        elif btnName == "Export":
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

    def __init__(self, parent, fileobj=None, filename=None):
        super(RegistryFileView, self).__init__(parent, -1, size=(1280, 840))
        self._filename = filename
        self.fileobj = fileobj


        vsplitter = wx.SplitterWindow(self, -1)
        panel_left = wx.Panel(vsplitter, -1)
        self._tree = DirTreeCtrl(panel_left, -1)
        _expand_into(panel_left, self._tree)

        hsplitter = wx.SplitterWindow(vsplitter, -1)
        panel_top = wx.Panel(hsplitter, -1)

        vsplitter_data = wx.SplitterWindow(hsplitter, -1)
        panel_offset = wx.Panel(vsplitter_data, -1)
        panel_hex = wx.Panel(vsplitter_data, -1)

        self._value_list_view = ValuesListCtrl(panel_top, -1, style=wx.LC_REPORT)
        self._offset_view = DataPanel(panel_offset, -1)
        self._hex_view = DataPanel(panel_hex, -1)

        _expand_into(panel_top, self._value_list_view)
        _expand_into(panel_offset, self._offset_view)
        _expand_into(panel_hex, self._hex_view)

        vsplitter.SplitVertically(panel_left, hsplitter)
        hsplitter.SplitHorizontally(panel_top, vsplitter_data)
        vsplitter_data.SplitVertically(panel_offset, panel_hex)

        # give enough space in the data display for the hex output
        vsplitter.SetSashPosition(250, True)
        hsplitter.SetSashPosition(250, True)
        vsplitter_data.SetSashPosition(150, True)
        _expand_into(self, vsplitter)
        self.Centre()

        self._value_list_view.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnValueClicked)
        self._offset_view.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnValueClicked)
        self._hex_view.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnValueClicked)
        self._tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnDirClicked)

        if self.fileobj != None:
            # tree 생성
            self._tree.add_directory(self.fileobj)

            # vbr만큼 읽어서 초기 화면에 띄워주기
            data = self.fileobj.get_vbr_data_binary()
            offset = self.fileobj.get_offsetText(data, 0)
            hex_data = self.fileobj.get_hexText(data)
            self._offset_view.display_value(offset)
            self._hex_view.display_value(hex_data)

    def OnDirClicked(self, event):
        item = event.GetItem()
        if not item.IsOk():
            item = self._tree.GetSelection()

        key_info = self._tree.GetItemData(item)["key"]
        parent = self.GetParent()
        while parent:
            try:
                parent.SetStatusText(key_info.path())
            except AttributeError:
                pass
            parent = parent.GetParent()

        self._offset_view.clear_value()
        self._hex_view.clear_value()
        self._value_list_view.clear_values()

        # directory일 경우
        try:
            # valueListCtrl에 파일 출력
            for files in key_info.file_list:
                self._value_list_view.add_file(files)

            # '새 볼륨' 클릭하면 vbr만큼만 출력
            # TODO offset, hex Thread
            if key_info.current_dir['cluster'] == 0:
                data = self.fileobj.get_vbr_data_binary()
                offset = self.fileobj.get_offsetText(data, 0)
                hex_data = self.fileobj.get_hexText(data)
                self._offset_view.display_value(offset)
                self._hex_view.display_value(hex_data)

            # 일반 directory 클릭하면 해당 data 출력
            # TODO: offset, hex thread
            else:
                self.print_hex_data(key_info.current_dir['cluster'])
        except AttributeError:
            pass

        # registry일 경우
        try:
            for value in key_info.values():
                self._value_list_view.add_value(value,key_info.timestamp())

            #cluster = int(self.offset_to_cluster(offset))
            #self.print_hex_data(cluster)
        except AttributeError:
            pass

    def OnValueClicked(self, event):
        item = event.GetItem()

        key_info = self.fileobj.fatTreeStructure.total_file_list #파일 정보 리스트 저장 지금보니 굳이 안해도 될듯 ㅋㅋ
        self._offset_view.clear_value()
        self._hex_view.clear_value()
        for i in key_info : #for문 돌면서 name을 찾아서 클릭한 이름 가져와서 비교 후 그 entry에 있는 클러스터 정보 출력
            if i['name'] == str(item.GetText()) :
                print(i)
                self.print_hex_data(i['cluster'])
                break


        # TODO: offset, hex data 출력
        #value = self._value_list_view.get_value(item.GetText())
      #  print(self._hex_view.display_value(value))
       # print(self._offset_view.display_value(value))

    # TODO: use thread to shorten time in processing
    def print_hex_data(self, cluster):
        data = self.fileobj.get_content(cluster)
        offset = self.fileobj.get_offsetText(data, cluster)
        hex_data = self.fileobj.get_hexText(data)
        self._offset_view.display_value(offset)
        self._hex_view.display_value(hex_data)

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

    def offset_to_cluster(self, offset):
        # ((cluster - 2) * self.spc + self.first_data_sector) * self.bps
        return ((offset / self.fileobj.bps) - self.fileobj.fds) / self.fileobj.spc + 2


class RegistryFileViewer(wx.Frame):
    """
    The main RegView GUI application.
    """

    def __init__(self, parent):
        super(RegistryFileViewer, self).__init__(parent, -1, "Registry File Viewer", size=(1280, 840))
        self.CreateStatusBar()

        # 상단 메뉴바 생성
        menu_bar = wx.MenuBar()

        # 메뉴바 중 'File' 메뉴 생성
        file_menu = wx.Menu()

        # File 메뉴에 open file, export, open, exit 넣음
        _open = file_menu.Append(ID_FILE_OPEN, '&Open File')
        self.Bind(wx.EVT_MENU, self.menu_file_open, _open)
        _history = file_menu.Append(ID_HISTORY_EXPORT, '&Export')
        self.Bind(wx.EVT_MENU, self.menu_history_export, _history)
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

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._nb, 1, wx.EXPAND)
        p.SetSizer(sizer)
        self.Layout()

        # 처음 프로그램 실행했을 때 레이아웃 보여줌
        initial = RegistryFileView(self._nb)
        self._nb.AddPage(initial, basename(""))

    def _open_registry_file(self, filename):
        """
        Open a Registry file by filename into a new tab and return the window.
        """
        self.dskImg = General.RegistryImage(filename)

        # 초기 페이지 삭제
        if self._nb.GetPageText(0) == "":
            self._nb.DeletePage(0)

        view = RegistryFileView(self._nb, fileobj=self.dskImg, filename=filename)
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

    def menu_help_about(self, evt):
        wx.MessageBox("please visit our Github \n\n https://github.com/kyungsook/Forensics_Visualization", "About")

    def menu_draw_graph(self, evt):
        print("창 띄우기")
        title = 'Filter'
        frame = FilterFrame(title=title, btnName="Draw")

    def menu_history_export(self, evt):
        print("웹 히스토리 내보내기")
        title = 'Filter'
        frame = FilterFrame(title=title, btnName="Export")


if __name__ == '__main__':
    app = wx.App(False)

    frame = RegistryFileViewer(None)
    frame.Show()
    app.MainLoop()
