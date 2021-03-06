STATUS
======

Development is occurring mainly in the **pymlac** subdirectory.  Some
development of tools occurs in the **pyasm** directory.

The CPU has been tested.  The papertape reader/punch device and the TTY devices
(input and output) seem to work.  The display instructions and device are now
being tested.

Testing is stalled a little as the chosen GUIs (wxpython or pyQt) have problems
being installed on OSX.  Testing continues with the display being simulated by
writing a PPM graphics file for each refresh of the display.  Slow, but it
means testing can proceed.

I'm still thinking about what graphics framework to use for the display.  I may
just choose something simple that just shows the screen and forget about
anything showing the address lights, etc.  This fits in with the CLI approach
used in **pymlac**.

The Imlac
=========

When I was doing post-graduate study at Sydney University one fun machine I
worked on was an `Imlac PDS-4 <http://en.wikipedia.org/wiki/Imlac_PDS-1>`_ .

This was a 16 bit vector graphics minicomputer with a general purpose main CPU
and a specialised display CPU - all implemented with 7400 series chips.  It had
real core memory, a papertape reader/punch, a trackball and a lightpen.  Later
on it acquired 8-inch floppy drives but few people used these as they were too
unreliable.  Besides, there's just something about papertape!

The attraction of the machine was its simplicity, its graphics capability and
that it ran `Spacewar! <http://en.wikipedia.org/wiki/Spacewar!>`_  I have many
fond memories of this machine.  It was the first machine that I programmed in
assembler.

The Imlac has long since gone from the university.
No one knows what happened to it.

There is a little information online:

* Tom Uban's `Imlac picture gallery <http://www.ubanproductions.com/imlac.html>`_ and `software library <http://www.ubanproductions.com/imlac_sw.html>`_
* The `Blinkenlights <http://www.blinkenlights.com/classiccmp/imlac/>`_ archive of Imlac information
* Imlac at `old-computers.com <http://www.old-computers.com/museum/computer.asp?st=1&c=1295>`_
* Inevitably, there is an `Imlac Facebook page <http://www.facebook.com/pages/Imlac-PDS-1/124593560918139>`_
* A working Imlac emulator is `here <http://rottedbits.blogspot.com/2013/05/an-introduction-to-imlac-pds-1.html>`_
* Some information from `chilton-computing.org.uk <http://www.chilton-computing.org.uk/acd/icf/terminals/p008.htm>`_

It's a little sad to see this machine fade from memory.  I wrote an emulator for
the Imlac in C with an X display window quite a while ago, but didn't proceed
with it, possibly because it would only run on Linux.  Now I would like to
experiment with a rewrite in Python and use wxPython or pySide for the graphics.
This repository holds the code.

Overview
--------

The Imlac was a simple machine that was driven in the old style: the user sat at
the screen and loaded a papertape, set the PC address and then pressed the RUN
button.  Observing the address lights as the program ran could tell you
something about the operation of your code.  To debug your program you could
paddle around in core and look at the contents of various addresses.  Really
steam-powered stuff!

Since core memory is non-volatile it was possible to switch the machine off and
turn it on days later and find your program and data still in memory.  This
emulator recreates this behaviour by writing the contents of core memory to a
file when terminating.  This *core* file is read in when the emulator starts.
This way we can emulate the behaviour of core memory.

To emulate this style of operation as much as possible, the console version of
pymlac takes a series of *operations* arguments that are performed left to
right.  These operations are things such as loading a papertape into the reader,
examining memory contents, setting the data switches or setting the machine run
address.

Console usage
-------------

The console version of pymlac is used:

::

    pymlac [ <option> ]*


That is, the user may specify zero or more options interspersed in any manner
required.  The options are:

::

    -b (ptr | tty | none)         sets the bootstrap ROM code:
                                      ptr   uses the papertape bootstrap ROM
                                      tty   uses the teletype bootstrap ROM
                                      none  uses no bootstrap ROM
    
    -c                            clears core including bootstrap ROM, if write enabled
    
    -cf <filename>                sets the name of the core file to read and write
                                  (default file is 'pymlac.core')
    
    -d <value>                    sets the console data switches to the <value>
    
    -h                            prints this help
    
    -ptp <file>                   loads a file on to the papertape punch device
    
    -ptr <file>                   loads a file on to the papertape reader device
    
    -r (<address> | pc)           executes from <address> or the current PC contents
    
    -s <setfile>                  sets memory adress values from <setfile>
    
    -t (<range>[:<range2>[:...]] | off) controls the execution trace:
                                      -t 0100                trace from address 0100 (octal)
                                      -t 0100,0200           trace from 0100 octal to 200 decimal
                                      -y 0100,0200:0210,0300 trace 0100 to 0200 and 0210 to 0300
                                      -t off                 turns trace off
    
    -ttyin <file>                 loads a file on to the teletype reader device
    
    -ttyout <file>                loads a file on to the teletype writer device
    
    -v <viewfile>                 views contents of memory addresses from file
    
    -w (on | off)                 controls ROM write property:
                                      -w on     ROM addresses are writable
                                      -w off    ROM addresses are write protected

For example, if we wanted the pymlac machine to load a papertape file and run at
address 0100 with trace between 0110 and 0120 we would do:

::

    pymlac -b ptr -ptr test.ptp -r 040 -t 0110,0120 -r 0100

This would load the corefile, set the ROM to the papertape bootstrap, load the
file test.ptp on the papertape reader and start execution at address 040 (the
normal bootstrap ROM start address).  The bootstrap runs and loads the papertape
into memory and the machine then halts.  The trace is set to be within the
address range [0110, 0120] and the machine starts execution at 0100 and then
again halts.  The core file is saved.

Given the persistence of the emulated core contents, the above single command
could have been executed in this manner:

::

    pymlac -b ptr -ptr test.ptp -r 040

    pymlac -t 0110,0120 -r 0100

If we wanted to use an existing core file from yesterday that contained a
program that reads a data file from the TTY reader and we wanted to look at the
contents of some parts of memory after running the program, we would do:

::

    pymlac -ttyin data.tty -r 0100 -v read_memory

This would load the existing core file, mount the data file on the TTY reader,
start execution at 0100, after which the machine halts.  Then the contents of
memory addresses specified in the file **read_memory** is displayed.  The core
file is saved.

And finally, if we just want to set some memory values in core, we would do:

::

    pymlac -s setdatafile

Which loads the existing core file, sets some addresses to values given in the
file **setdatafile** and then saves the core file.

File formats and implementation notes
-------------------------------------

There are some details on papertape file formats and implementation notes
in `the wiki <https://github.com/rzzzwilson/pymlac/wiki>`_.
