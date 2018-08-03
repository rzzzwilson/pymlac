DEVFILES = cpu.o dcpu.o ptrptp.o memory.o kb.o ttyin.o ttyout.o trace.o error.o log.o plist.o bootstrap.o display_sdl.o
CFILES = cpu.c dcpu.c ptrptp.c memory.c kb.c ttyin.c ttyout.c trace.c error.c log.c plist.c bootstrap.c display_sdl.c
HFILES = cpu.h dcpu.h ptrptp.h memory.h kb.h ttyin.h ttyout.h trace.h error.h log.h plist.h bootstrap.h display_sdl.h
OFILES = vimlac.o $(DEVFILES)

CFLAGS=-O2 -Wall -pedantic -std=c99 -g -I /usr/local/include/SDL2/ -l SDL2-2.0.0

test:	vimlac
	rm -f vimlac.log trace.out *.pbm; time ./vimlac -b ptr -ptr chars.ptp -r 040 -r 0100
#	rm -f vimlac.log trace.out *.pbm; time ./vimlac -b ptr -ptr simpledisplay.ptp -r 040 -r 0100
#	rm -f vimlac.log trace.out
#	./test_cpu CPU.test

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

#vimlac:	 $(CFILES)
#	gcc -o vimlac ${CFLAGS} $(DEVFILES) vimlac.c

clean:
	rm -f *.pyc *.o vimlac test_ptr test_memory *~ _#*#_.*
	rm -Rf *.dSYM
