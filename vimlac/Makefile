DEVFILES = cpu.o dcpu.o ptrptp.o memory.o kb.o ttyin.o ttyout.o trace.o error.o log.o plist.o bootstrap.o
CFILES = cpu.c dcpu.c ptrptp.c memory.c kb.c ttyin.c ttyout.c trace.c error.c log.c plist.c bootstrap.c
HFILES = cpu.h dcpu.h ptrptp.h memory.h kb.h ttyin.h ttyout.h trace.h error.h log.h plist.h bootstrap.h
OFILES = vimlac.o $(DEVFILES)

CFLAGS=-O2 -Wall -ansi -pedantic -std=c99 -g

test:	test_cpu
	rm -f vimlac.log trace.out
	./test_cpu CPU.test

test_cpu:	test_cpu.c $(DEVFILES) Makefile
	gcc -o test_cpu ${CFLAGS} $(DEVFILES) test_cpu.c

vimlac:	${OFILES} Makefile
	gcc -o vimlac ${CFLAGS} ${OFILES}

test_ptr:	test_ptr.c ptrptp.c error.c Makefile
	gcc -o test_ptr ${CFLAGS} error.c ptrptp.c test_ptr.c
	./test_ptr

test_plist:	test_plist.c $(DEVFILES) Makefile
	gcc -o test_plist ${CFLAGS} -lcunit $(DEVFILES) test_plist.c
	./test_plist

test_memory:	test_memory.c memory.c memory.h Makefile
	gcc -o test_memory ${CFLAGS} memory.c test_memory.c

vimlac:	 $(CFILES)
	gcc -o vimlac ${CFLAGS} $(DEVFILES) vimlac.c

clean:
	rm -f *.pyc *.o vimlac test_ptr test_memory *~ _#*#_.*
