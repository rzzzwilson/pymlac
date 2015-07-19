# !/usr/bin/python

"""
Emulate the Keyboard (KBD).

We must emulate funny Imlac key values.
"""

# The Imlac keyboard maintains an 11-bit value representing the ASCII value of
# the pressed key and any simultaneously pressed control keys:
#
#      5   6   7   8   9  10  11  12  13  14  14
#    +---+---+---+---+---+---+---+---+---+---+---+
#    | R | C | S |       ASCII key code          |
#    +---+---+---+---+---+---+---+---+---+---+---+
#
# This 11-bit value is read into the AC when requested at the shown bit places.
# Bit 8, the ASCII high bit, is always zero on the Imlac.
#
# The R, C and S bits represent the state of the Repeat, Control and Shift keys,
# respectively.
#
# When the keyboard flag is cleard (either KCF or KRC instructions) the 8-bit
# ASCII buffer is cleared but the three status bits R, C and S are left alone.
#
##############################
#
# The wxPython event provides the following keyboard events:
#    wx.EVT_KEY_DOWN    when a key is pressed
#    wx.EVT_KEY_UP      when a key is pressed
#    wx.EVT_CHAR        when a fully modified ASCII char value is found
#
# In this code we use the UP/DOWN events to keep track of the modifiers
# and we use the CHAR event to change the key buffer value.  We do it this way
# because on the Imlac the modifiers (R, C and S flags) are seperate from the
# keyboard value and are not cleared by the KCF or KRC instructions.  This means
# Imlac code could check for the modifier flags alone at any time, so we have to
# keep track of the modifiers which DON'T raise a CHAR event.  We therefore need
# to handle the key UP/DOWN events for the modifiers.
#
# Since most modern keyboards don't have a REPEAT key (they use auto-repeat) the
# R flag will always be 0.


class Kbd(object):

    # define the keycode values for modifier keys
    KeyShift = 0x0132
    KeyControl = 0x018c

    # modifier key flags
    FlagR = 0           # REPEAT key, always 0
    FlagC = 0           # CONTROL key
    FlagS = 0           # SHIFT key


    def __init__(self):
        # initialize keyboard device
        self.clear()

        # .clear() doesn't clear flags, so
        self.FlagR = 0
        self.FlagC = 0
        self.FlagS = 0

    def handle_down_event(self, event):
        """Handle a KEY DOWN event from wxPython.

        This is only to track modifier keys.
        """

        keycode = event.GetKeyCode()

        if keycode == self.KeyShift:
            self.FlagS = 1
        elif keycode == self.KeyControl:
            self.FlagC = 1

        event.Skip()

    def handle_up_event(self, event):
        """Handle a KEY UP event from wxPython.

        This is only to track modifier keys.
        """

        keycode = event.GetKeyCode()

        if keycode == self.KeyShift:
            self.FlagS = 0
        elif keycode == self.KeyControl:
            self.FlagC = 0

        event.Skip()

    def handle_char_event(self, event):
        """Handle a CHAR key event."""

        self.buffer = event.GetKeyCode()
        self.ready = True

    def clear(self):
        """Clear keyboard buffer and READY flag."""

        self.ready = False
        self.buffer = 0

    def read(self):
        """Read keyboard buffer and modifier keys."""

        return (self.buffer & 0xff) + (self.FlagC << 9) + (self.FlagS << 8)
