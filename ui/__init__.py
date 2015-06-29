# -*- coding: utf-8 -*-

import wxversion
wxversion.select("2.8")
import wx

import sys
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin
from PIL import Image
import json
from datetime import datetime

import helpers

class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        CheckListCtrlMixin.__init__(self)
        ListCtrlAutoWidthMixin.__init__(self)

class FakeARMVEFrame(wx.Frame):
    delegate = None
    tags = []
    tag_order = []
    selected_tags = set()

    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(800, 490))

        # Panels

        panel = wx.Panel(self, -1)

        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        leftPanel = wx.Panel(panel, -1)
        rightPanel = wx.Panel(panel, -1)

        # List

        self.log = wx.TextCtrl(rightPanel, -1, style=wx.TE_MULTILINE)
        self.list = CheckListCtrl(rightPanel)
        self.list.InsertColumn(0, 'Serial #', width=140)
        self.list.InsertColumn(1, 'Tipo', width=200)
        self.list.InsertColumn(2, '# Bytes + CRC', width=210)
        self.list.InsertColumn(3, 'R/O', width=40)

        self.list.OnCheckItem = self.evtItemChange
        
        # Buttons

        vbox2 = wx.BoxSizer(wx.VERTICAL)

        # ------------ #

        vbox2.Add(wx.StaticText(leftPanel, -1, 'RFID', size=(150, -1)))

        self.autoInsertion = wx.ToggleButton(leftPanel, -1, 'Autoinsertar Tags', size=(150, -1))
        self.autoInsertion.SetValue(True)
        vbox2.Add(self.autoInsertion)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.evtAutoInsertionChanged, id=self.autoInsertion.GetId())

        self.autoRemoval = wx.ToggleButton(leftPanel, -1, 'Autoexpulsar Tags', size=(150, -1))
        self.autoRemoval.SetValue(True)
        vbox2.Add(self.autoRemoval)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.evtAutoRemovalChanged, id=self.autoRemoval.GetId())

        # ------------ #

        vbox2.Add(wx.StaticText(leftPanel, -1, 'Impresora', size=(150, -1)), 0, wx.TOP, 5)

        simulateInsertion = wx.Button(leftPanel, -1, 'Simular Inserción', size=(150, -1))
        vbox2.Add(simulateInsertion)
        self.Bind(wx.EVT_BUTTON, self.evtSimulateInsertion, id=simulateInsertion.GetId())

        simulateRemoval = wx.Button(leftPanel, -1, 'Simular Expulsión', size=(150, -1))
        vbox2.Add(simulateRemoval)
        self.Bind(wx.EVT_BUTTON, self.evtSimulateRemoval, id=simulateRemoval.GetId())

        # ------------ #

        vbox2.Add(wx.StaticText(leftPanel, -1, 'Debug', size=(150, -1)), 0, wx.TOP, 5)

        self.silentInsertion = wx.ToggleButton(leftPanel, -1, 'RFID Silencioso', size=(150, -1))
        self.silentInsertion.SetValue(False)
        vbox2.Add(self.silentInsertion)
        self.Bind(wx.EVT_TOGGLEBUTTON, self.evtSilentInsertionChanged, id=self.silentInsertion.GetId())

        inspectBuffer = wx.Button(leftPanel, -1, 'Inspeccionar Buffer', size=(150, -1))
        vbox2.Add(inspectBuffer)
        self.Bind(wx.EVT_BUTTON, self.evtInspectBuffer, id=inspectBuffer.GetId())

        exportTags = wx.Button(leftPanel, -1, 'Exportar Tags', size=(150, -1))
        vbox2.Add(exportTags)
        self.Bind(wx.EVT_BUTTON, self.evtExportTags, id=exportTags.GetId())

        resetTags = wx.Button(leftPanel, -1, 'Resetear Tags', size=(150, -1))
        vbox2.Add(resetTags)
        self.Bind(wx.EVT_BUTTON, self.evtResetTags, id=resetTags.GetId())

        # Sizers

        leftPanel.SetSizer(vbox2)

        vbox.Add(self.list, 1, wx.EXPAND | wx.TOP, 3)
        vbox.Add((-1, 10))
        vbox.Add(self.log, 0.5, wx.EXPAND)
        vbox.Add((-1, 10))
        
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.DblClick, self.list)
        
        rightPanel.SetSizer(vbox)

        hbox.Add(leftPanel, 0, wx.EXPAND | wx.RIGHT, 5)
        hbox.Add(rightPanel, 1, wx.EXPAND)
        hbox.Add((3, -1))

        panel.SetSizer(hbox)

    def go_ahead(self):
        self.delegate.evt_auto_insertion_changed(self.autoInsertion.GetValue())
        self.delegate.evt_auto_removal_changed(self.autoRemoval.GetValue())
        self.delegate.evt_silent_insertion_changed(self.silentInsertion.GetValue())

        self.reload_data()
        
        self.Centre()
        self.Show(True)

    def reload_data(self):
        self.tags = self.delegate.req_tag_list()
        self.tag_order = self.tags.keys() # We left this here if we want to add a custom order later
        self.tag_order.sort(key=int)

        self.list.DeleteAllItems()

        for i in self.tag_order:
            tag_data = self.delegate.req_tag_parsed(i)

            index = self.list.InsertStringItem(sys.maxint, i)
            self.list.SetStringItem(index, 1, tag_data["type"])
            self.list.SetStringItem(index, 2, str(tag_data["length"]) + " " + str(tag_data["crc"]))
            self.list.SetStringItem(index, 3, "SI" if tag_data["is_ro"] else "NO")

            self.list.CheckItem(index, i in self.selected_tags)

    def show_image(self, image):
        image = image.resize((int(image.size[0]*0.45),int(image.size[1]*0.45)), Image.BICUBIC)
        self.imageFrame = ImageFrame(image)
        self.imageFrame.Show()

    def unselect_all(self):
        self.selected_tags = set()
        self.reload_data()

    # Printer Events

    def evtSimulateInsertion(self, event):
        self.delegate.evt_simulate_insertion()

    def evtSimulateRemoval(self, event):
        self.delegate.evt_simulate_removal()

    def evtInspectBuffer(self, event):
        wx.MessageBox("No implementado")

    # RFID Events

    def evtSilentInsertionChanged(self, event):
        self.delegate.evt_silent_insertion_changed(self.silentInsertion.GetValue())

    def evtAutoInsertionChanged(self, event):
        self.delegate.evt_auto_insertion_changed(self.autoInsertion.GetValue())

    def evtAutoRemovalChanged(self, event):
        self.delegate.evt_auto_removal_changed(self.autoRemoval.GetValue())

    def evtResetTags(self, event):
        self.delegate.evt_reset_tags()
        self.reload_data()

    def evtExportTags(self, event):
        tags = self.delegate.req_tag_list().copy()
        path = "output/tags_output_%s.json" % datetime.now().strftime("%Y%m%d_%I%M%S_%f")

        try:
            with open(path, "w+") as f:
                f.write(json.dumps(tags))
            wx.MessageBox("Tags exportados a %s" % path)
        except Exception, e:
            wx.MessageBox("Error exportando tags: %s" % str(e))

    def evtItemChange(self, index, value):
        if value == True:
            self.selected_tags.add(self.tag_order[index])
            self.delegate.evt_tag_inserted(self.tag_order[index])
        else:
            self.selected_tags.discard(self.tag_order[index])
            self.delegate.evt_tag_removed(self.tag_order[index])

    def DblClick(self, event):
        wx.MessageBox("No implementado")
 
class ImageFrame(wx.Frame):
    """ class Panel1 creates a panel with an image on it, inherits wx.Panel """
    def __init__(self, pilImage):
        # create the panel
        wx.Frame.__init__(self, None, -1, "Salida Impresora", size=(pilImage.size))
        try:
            image = wx.EmptyImage(pilImage.size[0],pilImage.size[1])
            image.SetData(pilImage.convert("RGB").tostring())
            image.SetAlphaData(pilImage.convert("RGBA").tostring()[3::4])
            bmap = wx.BitmapFromImage(image)
            wx.StaticBitmap(self, -1, bmap, (10 + bmap.GetWidth(), 5), (bmap.GetWidth(), bmap.GetHeight()))

        except IOError:
            print "Image file %s not found" % imageFile

