MODULE FOO
INTERFACE
SUBROUTINE dummyc(x0) BIND(C, name="sync")
type(*), dimension(..) :: x0
END SUBROUTINE
END INTERFACE
contains
SUBROUTINE dummy(x0)
type(*), dimension(..) :: x0
call dummyc(x0)
END SUBROUTINE
END MODULE

PROGRAM main
    USE FOO
    IMPLICIT NONE
    integer :: before(2), after(2)

    INTEGER, parameter :: n = 4

    DOUBLE PRECISION, ALLOCATABLE :: buf(:)
    DOUBLE PRECISION :: buf2(n)

    ALLOCATE(buf(n))
    before(1) = LBOUND(buf,1)
    before(2) = UBOUND(buf,1)
    CALL dummy (buf)
    after(1) = LBOUND(buf,1)
    after(2) = UBOUND(buf,1)

    write(*,'(a20,2i5,l5)') "allocatable lbound", before(1), after(1), before(1) .EQ. after(1)
    write(*,'(a20,2i5,l5)') "allocatable ubound", before(2), after(2), before(2) .EQ. after(2)

    before(1) = LBOUND(buf2,1)
    before(2) = UBOUND(buf2,1)
    CALL dummy (buf2)
    after(1) = LBOUND(buf2,1)
    after(2) = UBOUND(buf2,1)

    write(*,'(a20,2i5,l5)') "static lbound", before(1), after(1), before(1) .EQ. after(1)
    write(*,'(a20,2i5,l5)') "static ubound", before(2), after(2), before(2) .EQ. after(2)

END PROGRAM
