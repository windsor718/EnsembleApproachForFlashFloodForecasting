#!/usr/bin/python
#to process RDR data into MATSIRO format.
#same as preprocess39.py but tailored for RDR_GPV.

from pylab import *
import sys
import shutil
import os
from cf import biIntp

YEAR=int(sys.argv[1])
MON=int(sys.argv[2])
DAY=int(sys.argv[3])
TIME=int(sys.argv[4])

if MON < 10:
        MON='0'+str(MON)
else:
        MON=MON

if DAY < 10:
        DAY='0'+str(DAY)
else:
        DAY=DAY

if TIME < 10:
        TIME='0'+str(TIME)
else:
        TIME=TIME

DATADIR='/data3/yuta/GPV_jpn/DATA/FT24/bindata24/'+str(TIME)+'/'+str(YEAR)+'.'+str(MON)+'/'
OUTDIR='/data3/yuta/GPV_jpn/DATA/FT24/processed_bindata24/'+str(TIME)+'/'+str(YEAR)+'.'+str(MON)+'/'

if os.path.exists(OUTDIR) == False:
	os.makedirs(OUTDIR)
	print "Directory was made."

lon=arange(118,150,0.0125)
lat=arange(20,47.888,0.0083)     #before regridding

LON=arange(123.024,147.976,0.05)
LAT=arange(24.024,46.024,0.05)                            #after regridding





#Precipitation conversion kg/m^2 => kg/m^2/s [0.0125x0.0083...]=>[0.05x0.05]

INFILE1=DATADIR+'rdr_'+str(YEAR)+str(MON)+str(DAY)+str(TIME)+'.bin'
prcp=fromfile(INFILE1,'float32').reshape(24,3360,2560)

#array=zeros((505,481))
#intarray=array.reshape(1,505,-1)
#t_prcp=concatenate([intarray,prcp],axis=0)

P=prcp[:]/3600

PRCP=biIntp(lat,lon,P,LAT,LON)

print str(YEAR)+str(MON)+str(DAY)
print PRCP.shape

PRCPf=PRCP.flatten()
print PRCPf.shape

PRCPf.astype('float32').tofile(OUTDIR+'rdr_'+str(YEAR)+str(MON)+str(DAY)+str(TIME)+'.bin')

