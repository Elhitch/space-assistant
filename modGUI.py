#!/usr/bin/python

import wx
import sys

class Frame(wx.Frame):

    messagesList = []

    def pushMessage(self, createdBy, msgText):
        msgToAdd = createdBy + ": " + msgText
        if self.msgsCount < 10:
            #self.messagesList.append(msgToAdd)
            for StaticTextObject in self.messagesList:
                if StaticTextObject.Label == "":
                    StaticTextObject.SetLabel(msgToAdd)
                    break
        else:
            for i in range(9):
                self.messagesList[i].SetLabel(self.messagesList[i+1].Label) 
            self.messagesList[9].SetLabel(msgToAdd)

        self.msgsCount += 1

    def AddUserMessage(self, text):
        textCtrlValue = self.msgInput.GetValue()
        if textCtrlValue != "":
            print(textCtrlValue)
            self.pushMessage("You", textCtrlValue)
            self.msgInput.SetValue("")

    def btnRecordPress(self, e):
        if self.btnRecord.Label == "Record":
            print(self.btnRecord.Label)
            self.btnRecord.SetLabel("Stop")
        else:
            print(self.btnRecord.Label)
            self.btnRecord.SetLabel("Record")

    def __init__(self, title):
        wx.Frame.__init__(self, None, title=title, pos=(150,150), size=(400,550), style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        panel = wx.Panel(self)
        verticalPanelSizer = wx.BoxSizer(wx.VERTICAL)

        verticalPanelSizer.AddSpacer(20)

        self.messagesList = []
        self.msgsCount = 0

        horizontalMessagesSizer = wx.BoxSizer(wx.HORIZONTAL)
        for i in range(10):
            newStaticText = wx.StaticText(panel, -1, "")
            #horizontalMessagesSizer.Add(newStaticText, 0, wx.ALL, 10)
            verticalPanelSizer.Add(newStaticText, 0, wx.ALL, 10)
            self.messagesList.append(newStaticText)
        verticalPanelSizer.Add(horizontalMessagesSizer, 0, wx.ALL, 10)

        verticalPanelSizer.AddSpacer(20)
        
        self.msgInput = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER, size=(500,40))
        self.msgInput.Bind(wx.EVT_TEXT_ENTER, self.AddUserMessage)
        verticalPanelSizer.Add(self.msgInput, 0, wx.ALL, 10)

        self.btnRecord = wx.Button(panel, size=(90,40), label="Record")
        self.btnRecord.Bind(wx.EVT_BUTTON, self.btnRecordPress)

        horizontalButtonSizer = wx.BoxSizer(wx.HORIZONTAL)
        horizontalButtonSizer.Add(self.btnRecord, wx.ALL, 0)
        verticalPanelSizer.Add(horizontalButtonSizer, 0, wx.ALL|wx.CENTER, 0)

        panel.SetSizer(verticalPanelSizer)
        panel.Layout()

    def OnClose(self, event):
        dlg = wx.MessageDialog(self, 
            "Do you really want to close Space Assistant?",
            "Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            self.Destroy()
            sys.exit()

# app = wx.App()
# top = Frame("Space Assistant")
# top.Show()
# app.MainLoop()