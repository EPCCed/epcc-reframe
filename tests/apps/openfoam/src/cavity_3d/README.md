# OpenFOAM benchmark

The problem is three dimensional lid-driven cavity flow following, e.g.,

https://www.openfoam.com/documentation/tutorial-guide/2-incompressible-flow/2.1-lid-driven-cavity-flow

The following subdirectories should be present

drwxr-sr-x 2 kevin z19 4096 Aug 28 10:06  0
drwxr-sr-x 2 kevin z19 4096 Aug 28 10:08  constant
drwxr-sr-x 2 kevin z19 4096 Aug 28 10:10  system

We will assume we are running on CIRRUS with the default openfoam/org
module:

$ module load PrgEnv-gnu
$ module load openfoam-org

The (two-dimensional) lid-driven cavity flow tutorial should be found in

${FOAM_TUTORIALS}/incompressible/icoFoam/cavity/cavity


## System

A system of uniform resolution (288x288x288) is described in:

system/blockMeshDist

blocks
(
    hex (0 1 2 3 4 5 6 7) (288 288 288) simpleGrading (1 1 1)
);

The system has unit length, so the resolution is determined by the
number of points in each dimension. Corresponding extents appear in
the x, y, and z sections of

system/PDRblockMeshDist

If a different resolution is required, both files should be updated.

The system size 288x288x288 has been used in an attempt to saturate
single node performance (128 MPI processors). This should provide
scope for some degree of strong scaling to larger numbers of nodes.
There are also a prime factorisation involving 32x3x3 which allows
for decompositions where the number of MPI processes per node want
those factors.


### BlockMesh

The mesh is generated from blockMeshDict by running blockMesh. This
needs to be done exactly once.

$ blockMesh

Results are stored in

constant/polyMesh

The details do not depend on the parallel decomposition, and the mesh may
be re-used as long as the resolution or geometry do not change.


### Parallel decomposition

For any given number of MPI processes, a decomposition is required.
A series of files with names of the form

system/decomposeParDict0288

are provided for 288 and 576 processes. A decomposition may be
generated via

$ decomposePar -force -fileHandler collated \
               -decomposeParDict system/decomposeParDict0288

where the required decomposition has been specified on the command line.
The results of the decomposition will appear in a directory:

processors288

This is appropriate for 288 MPI processes (1 node). If a new decomposition
is required, the existing decomposition directory must be removed
(or renamed).

The decomposition process is serial, and can present a significant serial
overhead at large process count if repeated runs are required. It is
therefore efficient if the decomposition can be run only once.


## Control

Various run time parameters are provided in 

system/controlDict

The length of the run is controlled by

startTime       0;
endTime         0.0025;

This length of simulation has been selected so that the computation
takes around 10 minutes on one node.

The time step is choosen so that the Courant number remains under control
at the resolution selected for the relevant lid speed:

deltaT          0.000025;

This gives 600 iterations to reach the end time.

If the resolution is changed, some experimentation may be required to
arrive at a new time step which keeps the Courant number under control.


## Run time

At run time a

system/decomposeParDict

file must be present and consistent with the current decomposition. A
copy ot link to one of the existing files is therefore required.

The icoFoam solver is invoked by, e.g.,

srun icoFoam -fileHandler collated

and the log will appear in stdout as expected.


The Courant number at the final time should be in the region of:

Time = 0.0025

Courant Number mean: 0.007157 max: 0.07028

(to four significant figures). The exact figure appearing in the output
is decomposition dependent.

