#include "utilities.h"

// The routine convert a string (name) into a number
// for use in a MPI_Comm_split call (where the number is
// known as a colour). It is effectively a hashing function
// for strings but is not necessarily robust (i.e. does not
// guarantee it is collision free) for all strings, but it
// should be reasonable for strings that different by small
// amounts (i.e the name of nodes where they different by a
// number of set of numbers and letters, for instance
// login01,login02..., or cn01q94,cn02q43, etc...)
/*int name_to_colour(const char *name){
  int res;
  int small_multiplier = 5;
  int large_multiplier = 1l;
  const char *p;

  res = 0;
  for(p=name; *p ; p++){
    // Guard against integer overflow.
    if (small_multiplier > 0 && (res * small_multiplier) > (INT_MAX / small_multiplier)) {
      // If overflow looks likely (due to the calculation above) then
      // simply flip the result to make it negative
      res = -res;
    }else{
      // If overflow is not going to happen then undertake the calculation
      res = (small_multiplier * res);
    }
    // Add on the new character here.
    res = res + *p;
    res = res % large_multiplier;
    printf("%c %d\n",*p,res);
  }
  // If we have ended up with a negative result, invert it to make it positive because
  // the functionality (in MPI) that we will use this for requires the int to be positive.
  if( res < 0 ){
    res = -res;
  }
  return res;
}*/

// The routine convert a string (name) into a number
// for use in a MPI_Comm_split call (where the number is
// known as a colour). It is effectively a hashing function
// for strings but is not necessarily robust (i.e. does not
// guarantee it is collision free) for all strings, but it
// should be reasonable for strings that different by small
// amounts (i.e the name of nodes where they different by a
// number of set of numbers and letters, for instance
// login01,login02..., or cn01q94,cn02q43, etc...)
int name_to_colour(const char *name) {
    int small_multiplier = 31;
    int large_multiplier = 1e9 + 9;
    int res = 0;
    int power = 1;
    const char *p;
    for(p=name; *p ; p++){
        res = (res + (*p + 1) * power) % large_multiplier;
	if(res < 0){
		res = - res;
	}
	power = (power * small_multiplier) % large_multiplier;
    }
    return res;
}

// Get an integer key for a process based on the name of the
// node this process is running on. This is useful for creating
// communicators for all the processes running on a node.
int get_key(){

  char name[MPI_MAX_PROCESSOR_NAME];
  int len;
  int lpar_key;

  MPI_Get_processor_name(name, &len);
  lpar_key = name_to_colour(name);
  return lpar_key;

}

#if defined(__aarch64__)
// TODO: This might be general enough to provide the functionality for any system
// regardless of processor type given we aren't worried about thread/process migration.
// Test on Intel systems and see if we can get rid of the architecture specificity
// of the code.
unsigned long get_processor_and_core(int *chip, int *core){
  return syscall(SYS_getcpu, core, chip, NULL);
}
// TODO: Add in AMD function
#else
// If we're not on an ARM processor assume we're on an intel processor and use the
// rdtscp instruction.
unsigned long get_processor_and_core(int *chip, int *core){
  unsigned long a,d,c;
  __asm__ volatile("rdtscp" : "=a" (a), "=d" (d), "=c" (c));
  *chip = (c & 0xFFF000)>>12;
  *core = c & 0xFFF;
  return ((unsigned long)a) | (((unsigned long)d) << 32);;
}
#endif
