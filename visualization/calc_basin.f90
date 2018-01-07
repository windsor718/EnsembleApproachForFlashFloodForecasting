      program set_subbasin
! ===============================================
! CODE FOR: create basin mask
      implicit none
!
      integer            ::  ix, iy, jx, jy, kx, ky
      integer            ::  nx, ny
!      parameter             (nx=152)
!      parameter             (ny=128)
!
      character*128      ::  buf
      real               ::  lon0, lat0
      integer            ::  ix0, iy0
! input
      integer,allocatable::  nextX(:,:)                  !! next grid X
      integer,allocatable::  nextY(:,:)                  !! flow direction conbined

      integer            ::  ibasin
      integer,allocatable::  basin(:,:)

! file
      character*128      ::  rfile1, wfile1
! ===============================================
      call getarg(1,buf)
       read(buf,*) lon0
      call getarg(2,buf)
       read(buf,*) lat0
      call getarg(3,buf)
       read(buf,*) nx
      call getarg(4,buf)
       read(buf,*) ny

      allocate(nextx(nx,ny), nexty(nx,ny))
      allocate(basin(nx,ny))

      rfile1='./nextxy.bin'
      wfile1='./mask.bin'

      open(11, file=rfile1, form='unformatted', access='direct', recl=4*nx*ny)
      read(11,rec=1) nextX
      read(11,rec=2) nextY
      close(11)

! ==============

      ix0 = lon0
      iy0 = lat0

      basin(:,:)=-9999
      do iy=1, ny
        do ix=1, nx
          if( nextx(ix,iy)/=-9999 )then
            basin(ix,iy)=-1
            if( nextx(ix,iy)<=0 ) basin(ix,iy)=0
          endif
        end do
      end do

      basin(ix0,iy0)=1

! ===============
      do iy=1, ny
        do ix=1, nx
          if( nextx(ix,iy)>0 .and. basin(ix,iy)==-1 )then
            jx=nextx(ix,iy)
            jy=nexty(ix,iy)
            do while( basin(jx,jy)==-1 )
              kx=nextx(jx,jy)
              ky=nexty(jx,jy)
              jx=kx
              jy=ky
            end do

            ibasin=basin(jx,jy)
            basin(ix,iy)=ibasin
            jx=nextx(ix,iy)
            jy=nexty(ix,iy)
            do while( basin(jx,jy)==-1 )
              basin(jx,jy)=ibasin
              kx=nextx(jx,jy)
              ky=nexty(jx,jy)
              jx=kx
              jy=ky
            end do
          endif
        end do
      end do

      open(11, file=wfile1, form='unformatted', access='direct', recl=4*nx*ny)
      write(11,rec=1) basin
      close(11)


      end program set_subbasin
