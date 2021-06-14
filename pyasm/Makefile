#
# Makefile to run pyasm tests, etc.
#

test:
	python3 test_pyasm.py

debug:
	rm -Rf default_TEST.lst c8lds_TEST.lst lc16sd_TEST.lst default_TEST.ptp c8lds_TEST.ptp lc16sd_TEST.ptp
	pyasm           -l default_TEST.lst  -o default_TEST.ptp test2.asm
	pyasm -b c8lds  -l c8lds_TEST.lst    -o c8lds_TEST.ptp   test2.asm
	pyasm -b lc16sd -l lc16sd_TEST.lst   -o lc16sd_TEST.ptp  test2.asm
	@../idasm/loadptp.py default_TEST.ptp
	@../idasm/loadptp.py c8lds_TEST.ptp
	@../idasm/loadptp.py lc16sd_TEST.ptp

run:
	python3 pyasm test.asm

clean:
	rm -f *.log pyasm.py *.lst *.ptp *.pyc
