################################################################################
# Makefile for the Imlac Cross Assembler (iasm).
################################################################################
# $Revision: 1.11 $
################################################################################

CCOPTS=-std=c99 -pedantic -Wall -g


all:		iasm

iasm:		Makefile iasm.h iasm.c assemble.o
		$(CC) $(CCOPTS) -o iasm iasm.c assemble.o

assemble.o:	Makefile assemble.h assemble.c
		$(CC) $(CCOPTS) -c assemble.c

clean:		
		rm -f *.o *~ core iasm *.tty *.core *.trace *.log *.lst # *.ptp

install:	all
		cp iasm ../bin

test:		all print.asm
#		iasm -l simpledisplay.lst simpledisplay.asm
#		-../bin/vimlac -bptr -iptr simpledisplay.ptp -nocorein -d 0177777 -r 040 -t 0100 -r 0100  > simpledisplay.trace
		iasm -l print.lst print.asm
		-../bin/vimlac -bptr -iptr print.ptp -nocorein -d 0177777 -r 040 -r 0100
#		iasm -l JUMPTEST.LST JUMPTEST.ASM
#		-../bin/vimlac -bptr -iptr JUMPTEST.ASM.ptp -nocorein -d 0177777 -r 040 -noclear -t 0100 -r 0100 > JUMPTEST.trace
#		../bin/vimlac -bptr -iptr 40tp_blockPunch1.0.ptp -nocorein -r 040 -otty blockpunch.tty -t 037660 -r 037660 -t 037640 -r 037640 -d 037540 -r -d 037674 -r -t 037670 -r 037670 > blockpunch.trace

chars.ptp:	chars.asm
		iasm chars.asm

reallyclean:	clean
		
