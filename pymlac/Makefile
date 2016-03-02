#
# Simple make file just to clean this directory.
# And run the test files.
#

test:
	#pymlac -b ptr -c -ptr dumpmem_test.ptp -t 0100,0110:03700,03761:03766,03777 -r 040 -r 0100
	pymlac -b ptr -c -ptr dumpmem_test.ptp -t 0100,0110:03700,03751:03754,03757:03762,03777 -r 040 -r 0100

test_debug:	
	rm -f test.ptr test.ptp CPU.test.trace test_CPU.log pymlac.trace
	python test_CPU.py dumpmem.test
#	./make_ptr > test.ptr
#	python test_CPU.py CPU.test
#	#python test_Display.py     # interactive!
#	@echo "##########  Run 'python test_Display.py' by hand!  ##########"
#	#python test_KBD.py                # interactive!
#	@echo "##########  Run 'python test_KBD.py' by hand!  ##########"
#	python test_Memory.py
#	python test_PTR_PTP.py
#	python test_TTYIN.py
#	python test_TTYOUT.py


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
