#!/usr/bin/env python

"""A 'floatslider' widget for ELoss.

As the wxPython slider widget works only with integers, we need
to make a slider that appears to use floats.  Combine a textbox to
display slider value and the slider itself:

    +--------------------------------------------------------------+
    |   +--------+                                                 |
    |   |        |    -------^----------------------------------   |
    |   |        |    ------(*)---------------------------------   |
    |   |        |    -------v----------------------------------   |
    |   +--------+                                                 |
    +--------------------------------------------------------------+

Upon instantiation supply:
    parent          reference to parent widget
    name            name added to event on value change
    limits          (min, max, default) real values for slider
    internal2real   function to convert internal integer to real value
                        (real_value, display) = internal2real(internal_value)
                        where 'display' is the string to display in
                        the textbox
    real2internal   function to convert real value to internal integer
                        internal_value = real2internal(real_value)
    slidersize      slider size tuple - (width, height) in pixels
    slidertextsize  slider value text size tuple - (width, height) in pixels
    border          LEFT+RIGHT border on value text box

Methods are:
    .SetValue(value)
        Set the widget real value

    value = .GetValue()
        Get the widget real value

Events:
    EVT_FLOATSLIDER
        Triggered on widget value change:
            event.name   identifying name of the widget
            event.value  real value of the widget
"""


import sys
import wx


################################################################################
# A 'floatslider' widget
################################################################################

myEVT_FLOATSLIDER = wx.NewEventType()
EVT_FLOATSLIDER = wx.PyEventBinder(myEVT_FLOATSLIDER, 1)

class FSliderEvent(wx.PyCommandEvent):
    """Event sent from the FloatSlider widget when the slider is changed."""
    
    def __init__(self, eventType, id, name, value):
        wx.PyCommandEvent.__init__(self, eventType, id)
        self.name = name
        self.value = value

class FloatSlider(wx.Panel):

    # set platform-dependent sizes
    if sys.platform == 'win32':
        TextValueBorder = 5
        SliderSize = (175, -1)
        SliderTextSize = (37, -1)
    else:
        TextValueBorder = 5
        SliderSize = (175, -1)
        SliderTextSize = (37, -1)

    def __init__(self, parent, name, slider_limits, internal2real, real2internal,
                 slidersize=SliderSize,
                 slidertextsize=SliderTextSize,
                 border=TextValueBorder):
        """Initialize the widget.

        parent          reference to owning widget
        name            widget name, passed back in change event
        slider_limits   slider limits (real values)
        internal2real   function to convert internal to real values
                        (real_value, display) = internal2real(internal_value)
        real2internal   function to convert real to internal values
                        internal_value = real2internal(real_value)
        slidersize      tuple controlling slider size
        slidertextsize  tuple controlling text value size
        """

        wx.Panel.__init__(self, parent, wx.ID_ANY)
        self.SetBackgroundColour(wx.WHITE)

        # remember this widget name
        self.name = name

        # remember the external conversion functions
        self.internal2real = internal2real
        self.real2internal = real2internal
       
        # unpack limits, set internal state
        (min_real, max_real, def_real) = slider_limits
        min_int = real2internal(min_real)
        max_int = real2internal(max_real)
        def_int = real2internal(def_real)
        (def_real_value, def_display) = internal2real(def_int)

        # create GUI objects
        box = wx.BoxSizer(wx.HORIZONTAL)

        self.txt_value = wx.TextCtrl(self, wx.ID_ANY,
                                     value=def_display,
                                     size=slidertextsize,
                                     style=wx.TE_RIGHT)
        box.Add(self.txt_value, flag=wx.LEFT|wx.RIGHT,
                border=FloatSlider.TextValueBorder)

        self.sl_value = wx.Slider(self, wx.ID_ANY,
                                  def_int, min_int, max_int,
                                  size=slidersize,
                                  style=wx.SL_HORIZONTAL)
        box.Add(self.sl_value, flag=wx.ALIGN_CENTER_VERTICAL)

        self.SetSizerAndFit(box)

        self.value = def_real_value

        # set handler for change event
        self.sl_value.Bind(wx.EVT_SLIDER, self.onSliderChange)

    def onSliderChange(self, event):
        """Handle a change in the slider"""

        # get value of slider, update text field
        value = self.sl_value.GetValue()
        (self.value, display) = self.internal2real(value)
        self.txt_value.SetValue(display)

        # send change event
        event = FSliderEvent(myEVT_FLOATSLIDER, self.GetId(),
                             self.name, self.value)
        self.GetEventHandler().ProcessEvent(event)

    def SetValue(self, value):
        """Change displayed value.
        
        value  new real float value for the widget
        """

        self.value = value

        int_value = self.real2internal(value)
        (_, display) = self.internal2real(int_value)
        self.sl_value.SetValue(int_value)
        self.txt_value.SetValue(display)

    def GetValue(self):
        """Get displayed value."""

        return self.value



if __name__ == '__main__':
    import sys
    import traceback

    def internal2real(int_value):
        """internal -> real conversion."""

        real_value = float(int(int_value)/100.0)
        display_value = '%.2f' % real_value

        return (real_value, display_value)

    def real2internal(real_value):
        """real -> internal conversion."""

        return int(float(real_value) * 100)


    class AppFrame(wx.Frame):
        def __init__(self):
            # initialise the frame
            wx.Frame.__init__(self, None, size=(600,400), title='floatslider test')
            self.SetMinSize((600,400))
            self.panel = wx.Panel(self, wx.ID_ANY)
            self.panel.SetBackgroundColour(wx.WHITE)
            self.panel.ClearBackground()

            # create all application controls
            self.fs = FloatSlider(self, 'test', (0.01,0.5,0.2),
                                  internal2real, real2internal, slidersize=(200,20),
                                  slidertextsize=(50,-1))

            self.fs.Bind(EVT_FLOATSLIDER, self.onChange)

            # set up application window position
            self.Centre()

        def onChange(self, event):
            print(str(event.value))

    # our own handler for uncaught exceptions
    def excepthook(type, value, tb):
        msg = '\n' + '=' * 80
        msg += '\nUncaught exception:\n'
        msg += ''.join(traceback.format_exception(type, value, tb))
        msg += '=' * 80 + '\n'

        print msg
        log.critical('\n' + msg)
        sys.exit(1)

    # plug our handler into the python system
    sys.excepthook = excepthook

    # start wxPython app
    app = wx.App()
    AppFrame().Show()
    app.MainLoop()

