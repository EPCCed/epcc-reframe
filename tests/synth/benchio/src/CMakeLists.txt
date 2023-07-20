cmake_minimum_required(VERSION 3.2)

project( benchio LANGUAGES Fortran )
cmake_policy(SET CMP0074 NEW)

option(USE_HDF5 "Test HDF5 write" OFF )
option(USE_NETCDF "Test NETCDF write" OFF )
option(USE_ADIOS2 "Test ADIOS2 write" OFF )

if ( ${USE_HDF5} )
    find_package(HDF5 COMPONENTS Fortran HL)
endif()

if ( ${USE_NETCDF} )
    set (NETCDF_F90 "YES")
    list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_LIST_DIR}/cmake")
    
    find_package (NetCDF REQUIRED)

endif()


find_package(MPI REQUIRED)

add_subdirectory(src)
