#
# Simple make file just to clean this directory.
# And run the test files.
#
PYTHON=python3

test:	
	rm -f test.ptr test.ptp CPU.test.trace test_CPU.log pymlac.trace
	$(PYTHON) test_CPU.py dumpmem.test
	./make_ptr > test.ptr
	$(PYTHON) test_CPU.py CPU.test
#	#$(PYTHON) test_Display.py     # interactive!
	@echo "##########  Run '$(PYTHON) test_Display.py' by hand!  ##########"
#	#$(PYTHON) test_KBD.py                # interactive!
	@echo "##########  Run '$(PYTHON) test_KBD.py' by hand!  ##########"
	$(PYTHON) test_Memory.py
	$(PYTHON) test_PTR_PTP.py
	$(PYTHON) test_TTYIN.py
	$(PYTHON) test_TTYOUT.py

test_debug:
	#pymlac -b ptr -c -ptr dumpmem_test_c8lds.ptp -t 040,045:050,052:055,060:065,066:071,077:03700,03767:03772,03777 -r 040 -t 0100,0110 -r 0100
	pymlac -b tty -c -ttyin dumpmem_test_c8lds.ptp -t 040,045:050,052:055,060:063,077:03700,03767:03772,03777 -r 040 -t 0100,0110 -r 0100


%:	%.ptp
	./pymlac -b ptr -ptr $< -r 040 -t 0100 -r 0100
	diff pymlac.trace good_$*.trace | head -10
	mv pymlac.trace $*.trace

%.ptp:	%.asm
	../iasm/iasm -l $*.lst $<

lst:	$(TESTS)
	../iasm/iasm -l $*.lst $<

clean:
	rm -Rf *.pyc *~ *.out test_*.ptp *.lst test_*.trace _#*#_.* CPU.test.trace.* test.ptr
