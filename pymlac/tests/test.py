#from wxPython.wx import *
import wx

application = wx.PySimpleApp()

dialog = wx.Frame ( None, wx.ID_ANY, 'Title Here.' )

dialog.Show ( True )

application.MainLoop()
