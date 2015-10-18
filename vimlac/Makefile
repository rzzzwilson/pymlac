DEVFILES = cpu.o dcpu.o ptr.o ptp.o memory.o kb.o ttyin.o ttyout.o trace.o error.o log.o
OFILES = vimlac.o $(DEVFILES)

#CFLAGS=-fPIC -O2 -Wall -ansi -pedantic -std=c99 -g
CFLAGS=-O2 -Wall -ansi -pedantic -std=c99 -g

test:	test_cpu
	rm -f vimlac.log
	./test_cpu CPU.test

vimlac:	${OFILES} Makefile
	gcc -o vimlac ${CFLAGS} ${OFILES}

test_ptr:	test_ptr.c ptr.c ptr.h Makefile
	gcc -o test_ptr ${CFLAGS} ptr.c test_ptr.c

test_cpu:	test_cpu.c $(DEVFILES) Makefile
	gcc -o test_cpu ${CFLAGS} $(DEVFILES) test_cpu.c

test_memory:	test_memory.c memory.c memory.h Makefile
	gcc -o test_memory ${CFLAGS} memory.c test_memory.c

clean:
	rm -f *.pyc *.o vimlac test_ptr test_memory *~ _#*#_.*
