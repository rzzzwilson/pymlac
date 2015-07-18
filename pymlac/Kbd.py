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

    ######
    # This string has a \000 char at the PC key ordinal position if the key is dead.
    # Anything else and the key is live and the value is the unshifted value.
    ######

    #            0   1   2   3   4   5   6   7   8   9   A   B   C   D   E   F
    KeyVal = ('\000\000\000\000\000\000\000\000\000\211\000\000\000\215\000\000' #00
              '\000\000\000\231\000\000\000\000\000\000\000\233\000\000\000\000' #01
              '\240\000\000\000\000\000\000\247\000\000\000\000\254\255\256\257' #02
              '\260\261\262\263\264\265\266\267\270\271\000\273\000\275\000\000' #03
              '\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000' #04
              '\000\000\000\000\000\000\000\000\000\000\000\000\212\000\000\000' #05
              '\000\341\342\343\344\345\346\347\350\351\352\353\354\355\356\357' #06
              '\360\361\362\363\364\365\366\367\370\371\372\000\000\000\000\377' #07
              '\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000' #08
              '\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000' #09
              '\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000' #0A
              '\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000' #0B
              '\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000' #0C
              '\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000' #0D
              '\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000' #0E
              '\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000' #0F
              '\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000' #10
              '\000\206\204\205\210\202\217\216\000\214\000\000\000\000\000\000' #11
              '\000\000\000\000\000\000\000\000\000\000\000\000\000')            #12

    ######
    # This string has the shifted values for the key, indexed by PC key number.
    ######

    #             0   1   2   3   4   5   6   7   8   9   A   B   C   D   E   F
    SKeyVal = ('\000\000\000\000\000\000\000\000\000\211\000\000\000\215\000\000'#00
               '\000\000\000\231\000\000\000\000\000\000\000\233\000\000\000\000'#01
               '\240\000\000\000\000\000\000\242\000\000\000\000\274\255\276\277'#02
               '\251\241\262\243\244\245\266\246\252\250\000\272\000\253\000\000'#03
               '\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000'#04
               '\000\000\000\000\000\000\000\000\000\000\000\000\212\000\000\000'#05
               '\000\301\302\303\304\305\306\307\310\311\312\313\314\315\316\317'#06
               '\320\321\322\323\324\325\326\327\330\331\332\000\000\000\000\377'#07
               '\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000'#08
               '\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000'#09
               '\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000'#0A
               '\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000'#0B
               '\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000'#0C
               '\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000'#0D
               '\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000'#0E
               '\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000'#0F
               '\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000\000'#10
               '\000\206\204\205\210\202\217\216\000\214\000\000\000\000\000\000'#11
               '\000\000\000\000\000\000\000\000\000\000\000\000\000')           #12

    # define the keycode values for modifier keys
    KeyShift = 0x0132
    KeyControl = 0x018c

    # modifier key flags
    FlagR = 0           # REPEAT key, always 0
    FlagC = 0           # CONTROL key
    FlagS = 0           # SHIFT key


    def __init__(self):
        self.clear()

        # .clear() doesn't clear flags
        self.FlagR = 0
        self.FlagC = 0
        self.FlagS = 0

    def handle_down_event(self, event):
        """Handle a KEY DOWN event from wxPython.

        This is only to track modifier keys.
        """

        modifiers = event.GetModifiers()
        keycode = event.GetKeyCode()

        print('DOWN: Modifiers=%04x, GetKeyCode=%04x' % (modifiers, keycode))

        if keycode == self.KeyShift:
            self.FlagS = 1
        elif keycode == self.KeyControl:
            self.FlagC = 1

        event.Skip()

    def handle_up_event(self, event):
        """Handle a KEY UP event from wxPython.

        This is only to track modifier keys.
        """

        modifiers = event.GetModifiers()
        keycode = event.GetKeyCode()

        print('  UP: Modifiers=%04x, GetKeyCode=%04x' % (modifiers, keycode))

        if keycode == self.KeyShift:
            self.FlagS = 0
        elif keycode == self.KeyControl:
            self.FlagC = 0

        event.Skip()

    def handle_char_event(self, event):
        """Handle a CHAR key event."""

        self.buffer = event.GetKeyCode()
        print('NEW: %04x' % ord(self.buffer))
        self.ready = True

    def clear(self):
        """Clear keyboard buffer and READY flag."""

        self.ready = False
        self.buffer = 0

    def read(self):
        """Read keyboard buffer and modifier keys."""

        return (self.buffer & 0xff) + (self.FlagC << 9) + (self.FlagS << 8)
