!
! DGEMV simple benchmark
!    Multiple runs of DGEMV with matix/vectors of specified size, both
!    transpose and non-transpose versions. Outputs performance in Gflop/s.
!
! Usage:
!    dgemv_benchmark.x <matrix rows> <matrix columns> <repititions>
! 
! Based on original C program by A. Jackson, EPCC
!
! A. Turner, EPCC, The University of Edinburgh
!
program dgemv_benchmark
   use, intrinsic :: iso_fortran_env
   implicit none

   integer, parameter :: dp = REAL64

   integer(4) :: i, j
   integer(8) :: crate, cstart, cend
   real(kind=dp) :: etime, flops
   character(100) :: arg
   
   integer(4) :: n, m, lda, incx, incy, nrun
   real(kind=dp) :: alpha, beta
   real(kind=dp), dimension(:,:), allocatable :: a
   real(kind=dp), dimension(:), allocatable :: xn, yn, xt, yt

   ! Read in parameters
   call get_command_argument(1, arg)
   read(arg,*) m
   call get_command_argument(2, arg)
   read(arg,*) n
   call get_command_argument(3, arg)
   read(arg,*) nrun

   ! Initialise values
   alpha = 1.0_dp
   beta = 1.0_dp
   incx = 1
   incy = 1
   lda = m

   ! Allocate and assign arrays
   allocate(a(lda,n))
   allocate(xn(n))
   allocate(yn(m))
   allocate(xt(m))
   allocate(yt(n))
   do i = 1, m
      do j = 1, n
        a(i,j) = real((i-1)*n + j, dp)
      end do
   end do
   do i = 1, n
      xn(i) = real(i*2 + 1, dp)
      yt(i) = 1.0_dp
   end do
   do j = 1, m
      xt(i) = real(i*2 + 1, dp)
      yn(i) = 1.0_dp
   end do

   ! Warm up
   call dgemv('N', m, n, alpha, a, lda, xn, incx, beta, yn, incy)
   call dgemv('N', m, n, alpha, a, lda, xn, incx, beta, yn, incy)
   call dgemv('N', m, n, alpha, a, lda, xn, incx, beta, yn, incy)
   call dgemv('T', m, n, alpha, a, lda, xt, incx, beta, yt, incy)
   call dgemv('T', m, n, alpha, a, lda, xt, incx, beta, yt, incy)
   call dgemv('T', m, n, alpha, a, lda, xt, incx, beta, yt, incy)
   
   ! ********* Start of non-transpose benchmark ***********
   ! Initialise clock
   call system_clock(count_rate=crate)

   ! Run the benchmark
   call system_clock(cstart)
   do i = 1, nrun
      call dgemv('N', m, n, alpha, a, lda, xn, incx, beta, yn, incy)
   end do
   call system_clock(cend)

   ! Compute execution time
   etime = real(cend - cstart, dp) / real(crate, dp)

   ! Compute Gflops
   flops = 2.0 * real(m * (n+1), dp)
   flops = real(nrun, dp) * flops / (etime * 1000.0_dp**3)

   write(*,'(a, e13.5)') "Normal = ", flops
   ! ********* End of non-transpose benchmark ***********

   ! ********* Start of transpose benchmark ***********
   ! Run the benchmark
   call system_clock(cstart)
   do i = 1, nrun
      call dgemv('T', m, n, alpha, a, lda, xt, incx, beta, yt, incy)
   end do
   call system_clock(cend)

   ! Compute execution time
   etime = real(cend - cstart, dp) / real(crate, dp)

   ! Compute Gflops
   flops = 2.0 * real(n * (m+1), dp)
   flops = real(nrun, dp) * flops / (etime * 1000.0_dp**3)

   write(*,'(a, e13.5)') "Transpose = ", flops
   ! ********* End of transpose benchmark ***********

   deallocate(a)
   deallocate(xn)
   deallocate(yn)
   deallocate(xt)
   deallocate(yt)

end program dgemv_benchmark
