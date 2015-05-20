#
# Simple make file just to clean this directory.
# And run the test files.
#

TESTS = $(shell ls test_*.asm|sed -e "s/\.asm//")

all:	test testX_ptr

test:	$(TESTS)

# separate because it reads a PTP file
testX_ptr:
	../iasm/iasm -l testX_ptr.lst testX_ptr.asm
	./pymlac -b ptr -ptr testX_ptr.ptp -r 040 -ptr test.txt -t 0106,0106 -r 0100
	diff pymlac.trace good_testX_ptr.trace | head -10

%:	%.ptp
	./pymlac -b ptr -ptr $< -r 040 -t 0100 -r 0100
	diff pymlac.trace good_$*.trace | head -10
	mv pymlac.trace $*.trace

%.ptp:	%.asm
	../iasm/iasm -l $*.lst $<

lst:	$(TESTS)
	../iasm/iasm -l $*.lst $<

clean:
	rm -Rf *.pyc *~ *.out test_*.ptp *.lst test_*.trace
