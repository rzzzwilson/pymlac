OFILES=cpu.o dcpu.o ptr.o ptp.o memory.o kbd.o ttyin.o ttyout.o trace.o
CFILES=cpu.c dcpu.c ptr.c ptp.c memory.c kbd.c ttyin.c ttyout.c trace.c error.c
HFILES=cpu.h dcpu.h ptr.h ptp.h memory.h kbd.h ttyin.h ttyout.h trace.h error.h

CFLAGS=-shared -fPIC -O2 -Wall -ansi -pedantic -std=c99 -g

#test:	vimlac.py vimlac
#	#python vimlac.py -ptr test_add.ptp -r 040 -r 0100
#	vimlac

vimlac:	${OFILES} Makefile
	#gcc -o vimlac.so -shared -fPIC ${OFILES}
	gcc -o vimlac ${OFILES}

test_cpu:	test_cpu.c $(CFILES) $(HFILES) Makefile
	gcc -o test_cpu test_cpu.c $(CFILES)

test_ptr:	test_ptr.c ptr.c ptr.h Makefile
	gcc -o test_ptr ptr.c test_ptr.c

test_memory:	test_memory.c memory.c memory.h Makefile
	gcc -o test_memory memory.c test_memory.c

clean:
	rm -f *.pyc *.o vimlac test_ptr test_memory *~
