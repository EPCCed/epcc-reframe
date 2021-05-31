#include "definitions.h"
#include <unistd.h>
#include <math.h>
#include <sys/time.h>

/*-----------------------------------------------------------------------
 * INSTRUCTIONS:
 *
 *	1) STREAM requires different amounts of memory to run on different
 *           systems, depending on both the system cache size(s) and the
 *           granularity of the system timer.
 *     You should adjust the value of 'LAST_LEVEL_CACHE_SIZE' (below or
 *           passed at compile time) to allow the code to calculate how
 *           big each MPI processes' array should be. Array sizes should
 *           meet both of the following criteria:
 *       (a) Each array must be at least 4 times the size of the
 *           available last level cache memory.
 *       (b) The size should be large enough so that the 'timing calibration'
 *           output by the program is at least 20 clock-ticks.
 *           Example: most versions of Windows have a 10 millisecond timer
 *               granularity.  20 "ticks" at 10 ms/tic is 200 milliseconds.
 *               If the processor and memory are capable of 10 GB/s, this is 2 GB in 200 msec.
 *               This means the each array must be at least 1 GB.
 */

/*  Users are allowed to modify the "OFFSET" variable, which *may* change the
 *         relative alignment of the arrays (though compilers may change the
 *         effective offset by making the arrays non-contiguous on some systems).
 *      Use of non-zero values for OFFSET can be especially helpful if the
 *         array size is set to a value close to a large power of 2.
 *      OFFSET can also be set on the compile line without changing the source
 *         code using, for example, "-DOFFSET=56".
 */
#ifndef OFFSET
#   define OFFSET	0
#endif

/*
 *     To run with single-precision variables and arithmetic, simply add
 *         -DSTREAM_TYPE=float
 *     to the compile line.
 *     Note that this changes the array sizes required
 *
 *-----------------------------------------------------------------------*/



static double mysecond();
static void checkSTREAMresults(int array_size, int repeats);
static int checktick();

#ifdef _OPENMP
extern int omp_get_num_threads();
#endif

STREAM_TYPE	*a, *b, *c;


int stream_memory_task(benchmark_results *b_results, communicator world_comm, communicator node_comm, int *array_size, int cache_size, int repeats){
	int			quantum;
	int			BytesPerWord;
	int			k;
	ssize_t		j;
	STREAM_TYPE		scalar;
	double		t, times[4][repeats];

	*array_size = (cache_size*4)/node_comm.size;

	a = malloc(sizeof(STREAM_TYPE)*(*array_size+OFFSET));
	b = malloc(sizeof(STREAM_TYPE)*(*array_size+OFFSET));
	c = malloc(sizeof(STREAM_TYPE)*(*array_size+OFFSET));
	/* --- SETUP --- determine precision and check timing --- */

	//printf("STREAM version $Revision: 5.10 $\n");
	BytesPerWord = sizeof(STREAM_TYPE);


	if(world_comm.rank == ROOT){
		printf("Stream Memory Task\n");
		printf("This system uses %d bytes per array element.\n",BytesPerWord);
		printf("Array size = %llu (elements), Offset = %d (elements)\n" , (unsigned long long) *array_size, OFFSET);
		printf("Memory per array = %.1f MiB (= %.1f GiB).\n",
				BytesPerWord * ( (double) *array_size / 1024.0/1024.0),
				BytesPerWord * ( (double) *array_size / 1024.0/1024.0/1024.0));
		printf("Total memory required per process = %.1f MiB (= %.1f GiB).\n",
				(3.0 * BytesPerWord) * ( (double) *array_size / 1024.0/1024.),
				(3.0 * BytesPerWord) * ( (double) *array_size / 1024.0/1024./1024.));
		printf("Total memory required per node = %.1f MiB (= %.1f GiB).\n",
				node_comm.size * (3.0 * BytesPerWord) * ( (double) *array_size / 1024.0/1024.),
				node_comm.size * (3.0 * BytesPerWord) * ( (double) *array_size / 1024.0/1024./1024.));
		printf("Each kernel will be executed %d times.\n", repeats);
		printf(" The *best* time for each kernel (excluding the first iteration)\n");
		printf(" will be used to compute the reported bandwidth.\n");
	}

#ifdef _OPENMP
#pragma omp parallel
	{
#pragma omp master
		{
			k = omp_get_num_threads();
			//		printf ("Number of Threads requested = %i\n",k);
		}
	}
#endif

#ifdef _OPENMP
	k = 0;
#pragma omp parallel
#pragma omp atomic
	k++;
	//printf ("Number of Threads counted = %i\n",k);
#endif

	/* Get initial value for system clock. */
#pragma omp parallel for
	for (j=0; j<*array_size; j++) {
		a[j] = 1.0;
		b[j] = 2.0;
		c[j] = 0.0;
	}

	//if  ( (quantum = checktick()) >= 1)
	//	printf("Your clock granularity/precision appears to be "
	//			"%d microseconds.\n", quantum);
	//else {
	//	printf("Your clock granularity appears to be "
	//			"less than one microsecond.\n");
	//	quantum = 1;
	//}

	t = mysecond();
#pragma omp parallel for
	for (j = 0; j < *array_size; j++)
		a[j] = 2.0E0 * a[j];
	t = 1.0E6 * (mysecond() - t);

	//printf("Each test below will take on the order"
	//		" of %d microseconds.\n", (int) t  );
	//printf("   (= %d clock ticks)\n", (int) (t/quantum) );
	//printf("Increase the size of the arrays if this shows that\n");
	//printf("you are not getting at least 20 clock ticks per test.\n");

	//printf("WARNING -- The above is only a rough guideline.\n");
	//printf("For best results, please be sure you know the\n");
	//printf("precision of your system timer.\n");

	/*	--- MAIN LOOP --- repeat test cases repeats times --- */

	scalar = 3.0;
	for (k=0; k<repeats; k++)
	{
		// Add in a barrier synchronisation to ensure all processes on a node are undertaking the
		// benchmark at the same time. This ensures the node level results are fair as all
		// operations are synchronised on the node.
		MPI_Barrier(node_comm.comm);
		times[0][k] = mysecond();
#pragma omp parallel for
		for (j=0; j<*array_size; j++)
			c[j] = a[j];
		times[0][k] = mysecond() - times[0][k];
		b_results->Copy.raw_result[k] = times[0][k];

		MPI_Barrier(node_comm.comm);
		times[1][k] = mysecond();
#pragma omp parallel for
		for (j=0; j<*array_size; j++)
			b[j] = scalar*c[j];
		times[1][k] = mysecond() - times[1][k];
		b_results->Scale.raw_result[k] = times[1][k];

		MPI_Barrier(node_comm.comm);
		times[2][k] = mysecond();
#pragma omp parallel for
		for (j=0; j<*array_size; j++)
			c[j] = a[j]+b[j];
		times[2][k] = mysecond() - times[2][k];
		b_results->Add.raw_result[k] = times[2][k];

		MPI_Barrier(node_comm.comm);
		times[3][k] = mysecond();
#pragma omp parallel for
		for (j=0; j<*array_size; j++)
			a[j] = b[j]+scalar*c[j];
		times[3][k] = mysecond() - times[3][k];
		b_results->Triad.raw_result[k] = times[3][k];
	}

	/*	--- SUMMARY --- */
	/* note -- skip first iteration */
	for (k=1; k<repeats; k++) {
		b_results->Copy.avg = b_results->Copy.avg + times[0][k];
		b_results->Copy.min = MIN(b_results->Copy.min, times[0][k]);
		b_results->Copy.max = MAX(b_results->Copy.max, times[0][k]);
		b_results->Scale.avg = b_results->Scale.avg + times[1][k];
		b_results->Scale.min = MIN(b_results->Scale.min, times[1][k]);
		b_results->Scale.max = MAX(b_results->Scale.max, times[1][k]);
		b_results->Add.avg = b_results->Add.avg + times[2][k];
		b_results->Add.min = MIN(b_results->Add.min, times[2][k]);
		b_results->Add.max = MAX(b_results->Add.max, times[2][k]);
		b_results->Triad.avg = b_results->Triad.avg + times[3][k];
		b_results->Triad.min = MIN(b_results->Triad.min, times[3][k]);
		b_results->Triad.max = MAX(b_results->Triad.max, times[3][k]);
	}

	b_results->Copy.avg = b_results->Copy.avg/(double)(repeats-1);
	b_results->Scale.avg = b_results->Scale.avg/(double)(repeats-1);
	b_results->Add.avg = b_results->Add.avg/(double)(repeats-1);
	b_results->Triad.avg = b_results->Triad.avg/(double)(repeats-1);

	/* --- Check Results --- */
	checkSTREAMresults(*array_size, repeats);

	free(a);
	free(b);
	free(c);

	return 0;
}

# define	M	20

static int checktick(){
	int		i, minDelta, Delta;
	double	t1, t2, timesfound[M];

	/*  Collect a sequence of M unique time values from the system. */

	for (i = 0; i < M; i++) {
		t1 = mysecond();
		while( ((t2=mysecond()) - t1) < 1.0E-6 )
			;
		timesfound[i] = t1 = t2;
	}

	/*
	 * Determine the minimum difference between these M values.
	 * This result will be our estimate (in microseconds) for the
	 * clock granularity.
	 */

	minDelta = 1000000;
	for (i = 1; i < M; i++) {
		Delta = (int)( 1.0E6 * (timesfound[i]-timesfound[i-1]));
		minDelta = MIN(minDelta, MAX(Delta,0));
	}

	return(minDelta);
}



/* A gettimeofday routine to give access to the wall
   clock timer on most UNIX-like systems.  */
static double mysecond(){
	struct timeval tp;
	struct timezone tzp;
	int i;

	i = gettimeofday(&tp,&tzp);
	return ( (double) tp.tv_sec + (double) tp.tv_usec * 1.e-6 );
}

#ifndef abs
#define abs(a) ((a) >= 0 ? (a) : -(a))
#endif
static void checkSTREAMresults (int array_size, int repeats){
	STREAM_TYPE aj,bj,cj,scalar;
	STREAM_TYPE aSumErr,bSumErr,cSumErr;
	STREAM_TYPE aAvgErr,bAvgErr,cAvgErr;
	double epsilon;
	ssize_t	j;
	int	k,ierr,err;

	/* reproduce initialization */
	aj = 1.0;
	bj = 2.0;
	cj = 0.0;
	/* a[] is modified during timing check */
	aj = 2.0E0 * aj;
	/* now execute timing loop */
	scalar = 3.0;
	for (k=0; k<repeats; k++)
	{
		cj = aj;
		bj = scalar*cj;
		cj = aj+bj;
		aj = bj+scalar*cj;
	}

	/* accumulate deltas between observed and expected results */
	aSumErr = 0.0;
	bSumErr = 0.0;
	cSumErr = 0.0;
	for (j=0; j<array_size; j++) {
		aSumErr += abs(a[j] - aj);
		bSumErr += abs(b[j] - bj);
		cSumErr += abs(c[j] - cj);
		// if (j == 417) printf("Index 417: c[j]: %f, cj: %f\n",c[j],cj);	// MCCALPIN
	}
	aAvgErr = aSumErr / (STREAM_TYPE) array_size;
	bAvgErr = bSumErr / (STREAM_TYPE) array_size;
	cAvgErr = cSumErr / (STREAM_TYPE) array_size;

	if (sizeof(STREAM_TYPE) == 4) {
		epsilon = 1.e-6;
	}
	else if (sizeof(STREAM_TYPE) == 8) {
		epsilon = 1.e-13;
	}
	else {
		printf("WEIRD: sizeof(STREAM_TYPE) = %lu\n",sizeof(STREAM_TYPE));
		epsilon = 1.e-6;
	}

	err = 0;
	if (abs(aAvgErr/aj) > epsilon) {
		err++;
		printf ("Failed Validation on array a[], AvgRelAbsErr > epsilon (%e)\n",epsilon);
		printf ("     Expected Value: %e, AvgAbsErr: %e, AvgRelAbsErr: %e\n",aj,aAvgErr,abs(aAvgErr)/aj);
		ierr = 0;
		for (j=0; j<array_size; j++) {
			if (abs(a[j]/aj-1.0) > epsilon) {
				ierr++;
#ifdef VERBOSE
				if (ierr < 10) {
					printf("         array a: index: %ld, expected: %e, observed: %e, relative error: %e\n",
							j,aj,a[j],abs((aj-a[j])/aAvgErr));
				}
#endif
			}
		}
		printf("     For array a[], %d errors were found.\n",ierr);
	}
	if (abs(bAvgErr/bj) > epsilon) {
		err++;
		printf ("Failed Validation on array b[], AvgRelAbsErr > epsilon (%e)\n",epsilon);
		printf ("     Expected Value: %e, AvgAbsErr: %e, AvgRelAbsErr: %e\n",bj,bAvgErr,abs(bAvgErr)/bj);
		printf ("     AvgRelAbsErr > Epsilon (%e)\n",epsilon);
		ierr = 0;
		for (j=0; j<array_size; j++) {
			if (abs(b[j]/bj-1.0) > epsilon) {
				ierr++;
#ifdef VERBOSE
				if (ierr < 10) {
					printf("         array b: index: %ld, expected: %e, observed: %e, relative error: %e\n",
							j,bj,b[j],abs((bj-b[j])/bAvgErr));
				}
#endif
			}
		}
		printf("     For array b[], %d errors were found.\n",ierr);
	}
	if (abs(cAvgErr/cj) > epsilon) {
		err++;
		printf ("Failed Validation on array c[], AvgRelAbsErr > epsilon (%e)\n",epsilon);
		printf ("     Expected Value: %e, AvgAbsErr: %e, AvgRelAbsErr: %e\n",cj,cAvgErr,abs(cAvgErr)/cj);
		printf ("     AvgRelAbsErr > Epsilon (%e)\n",epsilon);
		ierr = 0;
		for (j=0; j<array_size; j++) {
			if (abs(c[j]/cj-1.0) > epsilon) {
				ierr++;
#ifdef VERBOSE
				if (ierr < 10) {
					printf("         array c: index: %ld, expected: %e, observed: %e, relative error: %e\n",
							j,cj,c[j],abs((cj-c[j])/cAvgErr));
				}
#endif
			}
		}
		printf("     For array c[], %d errors were found.\n",ierr);
	}

#ifdef VERBOSE
	printf ("Results Validation Verbose Results: \n");
	printf ("    Expected a(1), b(1), c(1): %f %f %f \n",aj,bj,cj);
	printf ("    Observed a(1), b(1), c(1): %f %f %f \n",a[1],b[1],c[1]);
	printf ("    Rel Errors on a, b, c:     %e %e %e \n",abs(aAvgErr/aj),abs(bAvgErr/bj),abs(cAvgErr/cj));
#endif
}


