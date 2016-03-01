#
# Makefile to run pyasm tests, etc.
#

test:
	cp pyasm pyasm.py
	python test_pyasm.py

debug:
	pyasm           -o default_TEST.ptp test2.asm
	pyasm -b c8lds  -o c8lds_TEST.ptp   test2.asm
	pyasm -b lc16sd -o lc16sd_TEST.ptp  test2.asm

run:
	python pyasm test.asm

clean:
	rm -f *.log pyasm.py *.lst *.ptp
