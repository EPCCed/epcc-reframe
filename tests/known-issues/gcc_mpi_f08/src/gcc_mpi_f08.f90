module foo
  interface
    subroutine dummyc(x0) bind(c, name="sync")
      type(*), dimension(..) :: x0
    end subroutine
  end interface
  contains
    subroutine dummy(x0)
      type(*), dimension(..) :: x0
      call dummyc(x0)
    end subroutine
end module

program main
    use foo
    implicit none
    integer :: before(2), after(2)

    integer, parameter :: n = 4

    double precision, allocatable :: buf(:)
    double precision :: buf2(n)

    allocate(buf(n))
    before(1) = lbound(buf,1)
    before(2) = ubound(buf,1)
    call dummy (buf)
    after(1) = lbound(buf,1)
    after(2) = ubound(buf,1)

    write(*,'(a20,2i5,l5)') "allocatable lbound", before(1), after(1), before(1) .eq. after(1)
    write(*,'(a20,2i5,l5)') "allocatable ubound", before(2), after(2), before(2) .eq. after(2)

    before(1) = lbound(buf2,1)
    before(2) = ubound(buf2,1)
    call dummy (buf2)
    after(1) = lbound(buf2,1)
    after(2) = ubound(buf2,1)

    write(*,'(a20,2i5,l5)') "static lbound", before(1), after(1), before(1) .eq. after(1)
    write(*,'(a20,2i5,l5)') "static ubound", before(2), after(2), before(2) .eq. after(2)
end program
