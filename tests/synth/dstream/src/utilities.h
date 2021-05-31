#include <mpi.h>
#include <omp.h>
#include <stdio.h>
#include <stdlib.h>
#include <limits.h>
#include <float.h>
#include <string.h>
#include <sys/sysinfo.h>
#if defined(__aarch64__)
#include <sys/syscall.h>
#endif

int name_to_colour(const char *);
int get_key();
unsigned long get_processor_and_core(int *chip, int *core);

