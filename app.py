#!/usr/bin/python
import sys
# import nltk
# import json
import importlib
import os
import subprocess
from deepspeech import Model
import threading
import wx
from pubsub import pub
import numpy as np
from modListener import Recorder
from modCore import Core
import modSpeech

# Global path variables
PATH_TO_DIR = os.path.dirname(os.path.realpath(__file__))
PATH_TO_MODEL = os.path.abspath(os.path.join(PATH_TO_DIR, '../ds-model/'))
# PATH_TO_AUDIO = os.path.abspath(os.path.join(PATH_TO_DIR, 'temp/lastCmd.wav'))

# DeepSpeech constants
DS_BEAM_WIDTH = 500
DS_LM_WEIGHT = 1.75
DS_WORD_COUNT_WEIGHT = 1.00
DS_VALID_WORD_COUNT_WEIGHT = 1.00

class ModGUI(wx.Frame):
    listenerThreadList = {
        "main": {
            "thread": None,
            "listener": None,
            "isRunning": False
        },
        "secondary": {
            "thread": None,
            "listener": None,
            "isRunning": False
        }
    }
    messagesList = []

    """ Functions to handle back-end operations """

    def SayAndLog(self, msg):
        modSpeech.say(msg)
        print("Message is: " + msg)
        self.pushMessage("SA", str(msg))

    def pushMessage(self, createdBy, msgText):
        msgToAdd = createdBy + ": " + msgText
        if self.msgsCount < 10:
            # self.messagesList.append(msgToAdd)
            for StaticTextObject in self.messagesList:
                if StaticTextObject.Label == "":
                    StaticTextObject.SetLabel(msgToAdd)
                    break
        else:
            for i in range(9):
                self.messagesList[i].SetLabel(self.messagesList[i+1].Label)
            self.messagesList[9].SetLabel(msgToAdd)

        self.msgsCount += 1
        self.UpdateWindowUI(wx.UPDATE_UI_FROMIDLE)

    def AddUIMessage(self, object, text=""):
        """
            If object is not None, then the function wasn't called by the event
            handler of the WX TextCtrl object.
        """
        if object is not None:
            textCtrlValue = self.msgInput.GetValue()
            if textCtrlValue != "":
                print(textCtrlValue)
                self.pushMessage("You", textCtrlValue)
                self.msgInput.SetValue("")
                self.ProcessCommand(textCtrlValue)
        else:
            pass
            self.pushMessage("You", text)

    def ProcessCommand(self, command):
        sentenceComposition = self.core.tagAndTokenize(command)
        nouns = self.core.find_nouns(sentenceComposition)
        """
            Pass a reversed list of nouns. In imperative sentences nouns usually are last so this should speed up the process in find_module(),
            especially if the the verb also exists as a noun, e.g. "show".
        """
        # tagged_sentence = None
        module_name = self.core.find_module(nouns[::-1])
        print(module_name)
        """
            If the command is recognised, perform further analysis to execute the specific action.
            Else, notify the user.
        """
        if module_name:
            module = importlib.import_module(f'commands.{module_name}')
            # !!! Passes the tokenized sentence as well
            modInitResult = module.initialize(sentenceComposition)
            print(f'modInitResult - {modInitResult}')
            wx.CallAfter(self.SayAndLog, modInitResult)
        else:
            wx.CallAfter(self.SayAndLog, "Sorry, I can't understand you")
        self.stopListeningThread("main", False)

    """ Following: Event handlers """

    def btnRecordPress(self, e):
        if self.btnRecord.Label == "Record":
            print(self.btnRecord.Label)
            self.stopListeningThread("secondary")
            self.createNewListeningThread("main")
            self.btnRecord.SetLabel("Stop")
        else:
            print(self.btnRecord.Label)
            self.stopListeningThread("main")
            #self.createNewListeningThread("secondary")
            self.btnRecord.SetLabel("Record")

    def OnClose(self, event):
        dlg = wx.MessageDialog(self,
                               "Do you really want to close Space Assistant?",
                               "Confirm Exit", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            self.stopListeningThread("main")
            self.stopListeningThread("secondary")
            self.Destroy()
            sys.exit()

    """ A function to create UI elements """

    def initUI(self, title):
        wx.Frame.__init__(self, None, title=title, pos=(150, 150), size=(
            400, 550), style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        panel = wx.Panel(self)
        verticalPanelSizer = wx.BoxSizer(wx.VERTICAL)

        verticalPanelSizer.AddSpacer(20)

        self.messagesList = []
        self.msgsCount = 0

        horizontalMessagesSizer = wx.BoxSizer(wx.HORIZONTAL)
        for i in range(10):
            newStaticText = wx.StaticText(panel, -1, "")
            # horizontalMessagesSizer.Add(newStaticText, 0, wx.ALL, 10)
            verticalPanelSizer.Add(newStaticText, 0, wx.ALL, 10)
            self.messagesList.append(newStaticText)
        verticalPanelSizer.Add(horizontalMessagesSizer, 0, wx.ALL, 10)

        verticalPanelSizer.AddSpacer(20)

        self.msgInput = wx.TextCtrl(
            panel, style=wx.TE_PROCESS_ENTER, size=(500, 40))
        self.msgInput.Bind(wx.EVT_TEXT_ENTER, self.AddUIMessage)
        verticalPanelSizer.Add(self.msgInput, 0, wx.ALL, 10)

        self.btnRecord = wx.Button(panel, size=(90, 40), label="Record")
        self.btnRecord.Bind(wx.EVT_BUTTON, self.btnRecordPress)

        horizontalButtonSizer = wx.BoxSizer(wx.HORIZONTAL)
        horizontalButtonSizer.Add(self.btnRecord, wx.ALL, 0)
        verticalPanelSizer.Add(horizontalButtonSizer, 0, wx.ALL | wx.CENTER, 0)

        panel.SetSizer(verticalPanelSizer)
        panel.Layout()

    def listenForAudioInput(self, whichThread):
        self.listenerThreadList[whichThread]["listener"] = Recorder(self.ds)
        if whichThread == "main":
            recognizedText = self.listenerThreadList[whichThread]["listener"].listen()
            wx.CallAfter(self.AddUIMessage, None, recognizedText)
            print("Should write this to UI: " + recognizedText)
            # self.btnRecord.SetLabel("Record")
            # if "by" in recognizedText.split():
            #     modSpeech.say("Bye bye!")
            #     self.stopListeningThread("main")
            #     self.createNewListeningThread("secondary")
            # elif recognizedText is not None:
            if recognizedText is not None:
                self.ProcessCommand(recognizedText)
        elif whichThread == "secondary":
            while self.listenerThreadList[whichThread]["isRunning"]:
                recognizedText = self.listenerThreadList[whichThread]["listener"].listen()
                if recognizedText is not None:
                    if recognizedText == "space":
                        wx.CallAfter(self.AddUIMessage, None, recognizedText)
                        wx.CallAfter(self.SayAndLog, "Hello! How can I help you?")
                        self.stopListeningThread("secondary", False)
                        self.createNewListeningThread("main")
                    # More code should come here
                # The call below doesn't work but must be programmed by other means
                # self.AddUserMessage(None, recognizedText.strip())

        # print(whichThread + " thread listener stopped")

    def createNewListeningThread(self, whichThread):
        if whichThread == "main":
            if self.listenerThreadList["secondary"]["isRunning"]:
                self.stopListeningThread("secondary")

        self.listenerThreadList[whichThread]["isRunning"] = True
        self.listenerThreadList[whichThread]["thread"] = threading.Thread(
            target=self.listenForAudioInput, args=(whichThread,))
        self.listenerThreadList[whichThread]["thread"].start()
        print("Started thread " + whichThread)

    def stopListeningThread(self, whichThread, join=True):
        if self.listenerThreadList[whichThread]["isRunning"]:
            self.listenerThreadList[whichThread]["isRunning"] = False
            self.listenerThreadList[whichThread]["listener"].stop()
            if join == True: self.listenerThreadList[whichThread]["thread"].join()
            print("Stopped thread " + whichThread)
            if whichThread == "main":
                self.createNewListeningThread("secondary")
                self.btnRecord.SetLabel("Record")

    def __init__(self, title):
        self.core = Core()
        # Create a DeepSpeech object
        dsModelPath = os.path.abspath(
            os.path.join(PATH_TO_MODEL, "output_graph.pbmm"))
        dsLMPath = os.path.abspath(os.path.join(PATH_TO_MODEL, "lm.binary"))
        dsTriePath = os.path.abspath(os.path.join(PATH_TO_MODEL, "trie"))
        self.ds = Model(dsModelPath, DS_BEAM_WIDTH)
        self.ds.enableDecoderWithLM(dsLMPath, dsTriePath, 0.75, 1.75)
        self.initUI(title)
        pub.subscribe(self.SayAndLog, "addMsg")
        self.createNewListeningThread("secondary")


if __name__ == "__main__":
    GUIApp = wx.App()
    GUIObject = ModGUI("Space Assistant")
    GUIObject.Show()
    GUIApp.MainLoop()
