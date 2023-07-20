
cmake_minimum_required(VERSION 3.2)

set(SOURCE_FILES benchio.f90 benchutil.f90 mpiio.f90 serial.f90 build_info.f90 )

configure_file (
    "${PROJECT_SOURCE_DIR}/src/build_info.f90.in"
    "${PROJECT_SOURCE_DIR}/src/build_info.f90"
)

if ( ${USE_HDF5} )
    list(APPEND SOURCE_FILES hdf5.f90 )
    add_compile_definitions( USE_HDF5 )

endif()

if ( ${USE_NETCDF} )
    list(APPEND SOURCE_FILES netcdf.f90 )
    add_compile_definitions( USE_NETCDF )

endif()

if ( ${USE_ADIOS2} )
    list(APPEND SOURCE_FILES adios.f90 )
    add_compile_definitions( USE_ADIOS2 )
    execute_process (
    COMMAND bash -c "adios2-config --fortran-flags"
    OUTPUT_VARIABLE ADIOS2_FORTRAN_FLAGS
    )
    execute_process (
    COMMAND bash -c "adios2-config --fortran-libs"
    OUTPUT_VARIABLE ADIOS2_LINK_FLAGS
    )

    string(STRIP ${ADIOS2_FORTRAN_FLAGS} ADIOS2_FORTRAN_FLAGS )
    set( ADIOS2_FORTRAN_FLAGS2 ${ADIOS2_FORTRAN_FLAGS} )
    separate_arguments(ADIOS2_FORTRAN_FLAGS UNIX_COMMAND "${ADIOS2_FORTRAN_FLAGS}")

    string(STRIP ${ADIOS2_LINK_FLAGS} ADIOS2_LINK_FLAGS )
    set( ADIOS2_LINK_FLAGS ${ADIOS2_LINK_FLAGS} )
    separate_arguments(ADIOS2_LINK_FLAGS UNIX_COMMAND "${ADIOS2_LINK_FLAGS}")


    add_compile_options( ${ADIOS2_FORTRAN_FLAGS} )
    add_link_options( ${ADIOS2_LINK_FLAGS} )


endif()


set_source_files_properties(
  benchio.f90 adios.f90 build_info.f90 PROPERTIES Fortran_PREPROCESS ON
)


add_compile_options( -ffree-line-length-0 )

add_executable( benchio ${SOURCE_FILES})


if ( ${USE_HDF5} )
    target_link_libraries( benchio PUBLIC hdf5::hdf5_fortran )
    target_include_directories( benchio PUBLIC ${HDF5_Fortran_INCLUDE_DIRS} )

endif()

if ( ${USE_ADIOS2} )

    target_link_libraries( benchio PUBLIC MPI::MPI_Fortran)
endif()

if ( ${USE_NETCDF})
    target_link_libraries (benchio PUBLIC ${NETCDF_LIBRARIES})
    target_include_directories(  benchio PUBLIC ${NETCDF_INCLUDES})
    install(FILES adios2.xml DESTINATION share)


endif()

target_link_libraries( benchio PUBLIC MPI::MPI_Fortran )

install(TARGETS benchio )
