#!/usr/bin/python

import wx, wx.html
import sys

aboutText = """<p>Sorry, there is no information about this program. It is
running on version %(wxpy)s of <b>wxPython</b> and %(python)s of <b>Python</b>.
See <a href="http://wiki.wxpython.org">wxPython Wiki</a></p>"""    

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
        print(self.msgInput.GetValue())
        self.pushMessage("You", self.msgInput.GetValue())
        self.msgInput.SetValue("")

    def btnRecordPress(self, e):
        if self.btnRecord.GetValue() == "Record":
            print self.btnRecord.GetValue()

    def __init__(self, title):
        wx.Frame.__init__(self, None, title=title, pos=(150,150), size=(400,600), style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        panel = wx.Panel(self)
        box = wx.BoxSizer(wx.VERTICAL)

        box.AddSpacer(20)

        self.messagesList = []
        self.msgsCount = 0
        for i in range(10):
            newStaticText = wx.StaticText(panel, -1, "")
            box.Add(newStaticText, 0, wx.ALL, 10)
            self.messagesList.append(newStaticText)

        box.AddSpacer(20)
        
        self.msgInput = wx.TextCtrl(panel, style=wx.TE_PROCESS_ENTER, size=(500,40))
        self.msgInput.Bind(wx.EVT_TEXT_ENTER, self.AddUserMessage)
        box.Add(self.msgInput, 0, wx.ALL, 10)

        box.AddSpacer(20)

        self.btnRecord = wx.Button(panel, label="Record")
        self.btnRecord.Bind(wx.EVT_BUTTON, self.btnRecordPress)

        panel.SetSizer(box)
        panel.Layout()

    def OnClose(self, event):
        dlg = wx.MessageDialog(self, 
            "Do you really want to close Space Assistant?",
            "Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            self.Destroy()
        else:
            self.pushMessage("HA!", "I knew it " + str(self.msgsCount))

app = wx.App()
top = Frame("Space Assistant")
top.Show()
app.MainLoop()