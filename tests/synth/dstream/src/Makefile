SRCMPI	= streams_memory_task.c main_program.c utilities.c
OBJMPI	=$(SRCMPI:.c=.o)

CC     = cc

LIBS    =

LDFLAGS = -fopenmp
CFLAGS = $(LDFLAGS) -g  -O3 -ffreestanding -fopenmp $(PP)

PRGMPI	= distributed_streams

main:	$(PRGMPI) 

%.o:%.c	Makefile
	$(CC) -c $(CFLAGS) $<

$(PRGMPI):$(OBJMPI) Makefile definitions.h
	$(CC) $(LDFLAGS) -o $@ $(OBJMPI) $(LIBS)
	rm -fr *.o

lean:
	rm -fr $(TMP) $(OBJMPI) $(PRGMPI) core
