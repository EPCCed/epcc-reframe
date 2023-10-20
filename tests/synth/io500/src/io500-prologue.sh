# INSTRUCTIONS:
#
# The only parts of the script that may need to be modified are:
#  - setup() to configure the binary locations and MPI parameters
# Please visit https://vi4io.org/io500-info-creator/ to help generate the
# "system-information.txt" file, by pasting the output of the info-creator.
# This file contains details of your system hardware for your submission.

# This script takes its parameters from the same .ini file as io500 binary.
io500_ini="$1"          # You can set the ini file here
io500_mpirun="srun"
io500_mpiargs="--hint=nomultithread --distribution=block:block"

function setup(){
  local workdir="$1"
  local resultdir="$2"
  mkdir -p $workdir $resultdir

  lfs setstripe -c 1 $workdir
  mkdir $workdir/ior-easy $workdir/ior-hard
  mkdir $workdir/mdtest-easy $workdir/mdtest-hard
  local osts=$(lfs df $workdir | grep -c OST)
  # Try overstriping for ior-hard to improve scaling, or use wide striping
  lfs setstripe -c $((osts * 4)) $workdir/ior-hard
  # Try to use DoM if available, otherwise use default for small files
  lfs setstripe -E 64k -L mdt $workdir/mdtest-easy || true #DoM?
  lfs setstripe -E 64k -L mdt $workdir/mdtest-hard || true #DoM?

  lfs getstripe $workdir/ior-easy
  lfs getstripe $workdir/ior-hard
  lfs getstripe $workdir/mdtest-easy
  lfs getstripe $workdir/mdtest-hard
}
