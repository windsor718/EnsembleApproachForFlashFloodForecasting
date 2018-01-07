#!/usr/bin/python
###########################################
#for processing rawdata(GPV) for gtool format
#and regrid to [0.05x0.05]
#and calculating specific humidity Q 
#GPVdata: [MSM]
#Author:Yuta Ishitsuka
###########################################



from pylab import *
import sys
import shutil
from cf import biIntp

##LEAD TIME or FORECAST TIME
FT=39

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

DATADIR='/data3/yuta/GPV_jpn/DATA/FT'+str(FT)+'/bindata'+str(FT)+'/'+str(TIME)+'/'+str(YEAR)+'.'+str(MON)+'/'
OUTDIR='/data3/yuta/GPV_jpn/DATA/FT'+str(FT)+'/processed_bindata'+str(FT)+'/'+str(TIME)+'/'+str(YEAR)+'.'+str(MON)+'/'

lon=arange(120.03125,150.09,0.0625)
lat=arange(22.425,47.63,0.05)     #before regridding

LON=arange(123.024,147.976,0.05)
LAT=arange(24.024,46.024,0.05)				  #after regridding





#Precipitation conversion kg/m^2 => kg/m^2/s [0.05x0.0625]=>[0.05x0.05]

INFILE1=DATADIR+'apcp_'+str(YEAR)+str(MON)+str(DAY)+str(TIME)+'.bin'
prcp=fromfile(INFILE1,'float32').reshape(FT,505,481)

#array=zeros((505,481))
#intarray=array.reshape(1,505,-1)
#t_prcp=concatenate([intarray,prcp],axis=0)

P=prcp[:]/3600

PRCP=biIntp(lat,lon,P,LAT,LON)

print PRCP.shape

PRCPf=PRCP.flatten()
print PRCPf.shape

PRCPf.astype('float32').tofile(OUTDIR+'prcp_'+str(YEAR)+str(MON)+str(DAY)+str(TIME)+'.bin')


#Air Pressure conversion Pa => hPa [0.05x0.0625]=>[0.05x0.05]

INFILE2=DATADIR+'pres_'+str(YEAR)+str(MON)+str(DAY)+str(TIME)+'.bin'
pres=fromfile(INFILE2,'float32').reshape(FT+1,505,481)

PRES=pres[:]/100

PRESSURE=biIntp(lat,lon,PRES[0:FT,:,:],LAT,LON)
print PRESSURE.shape
PRESSUREf=PRESSURE[0:FT,:,:].flatten()
print PRESSUREf.shape

PRESSUREf.astype('float32').tofile(OUTDIR+'pres_'+str(YEAR)+str(MON)+str(DAY)+str(TIME)+'.bin')

#Relative Humidity conversion % => kg/kg [0.05x0.0625]=>[0.05x0.05]

INFILE3=DATADIR+'rh_'+str(YEAR)+str(MON)+str(DAY)+str(TIME)+'.bin'
rh=fromfile(INFILE3,'float32').reshape(FT+1,505,481)

RH=rh[:]/100

RHc=biIntp(lat,lon,RH[0:FT,:,:],LAT,LON)
print RHc.shape
RHcf=RHc[0:FT,:,:].flatten()
print RHcf.shape
RHcf.astype('float32').tofile(OUTDIR+'rh_'+str(YEAR)+str(MON)+str(DAY)+str(TIME)+'.bin')

#Total Cloud Cover conversion % => kg/kg [0.05x0.0625]=>[0.05x0.05]

INFILE4=DATADIR+'tcdc_'+str(YEAR)+str(MON)+str(DAY)+str(TIME)+'.bin'
tcdc=fromfile(INFILE4,'float32').reshape(FT+1,505,481)

TCDC=tcdc[:]/100
tcdc_p=tcdc

TCDCc=biIntp(lat,lon,TCDC[0:FT,:,:],LAT,LON)
#TCDC_p=biIntp(lat,lon,TCDC,LAT,LON)
print TCDCc.shape
#print TCDC_p.shape
TCDCcf=TCDCc[0:FT,:,:].flatten()
#TCDC_pf=TCDC_p.flatten()
print TCDCcf.shape
#print TCDC_pf.shape
TCDCcf.astype('float32').tofile(OUTDIR+'tcdc_'+str(YEAR)+str(MON)+str(DAY)+str(TIME)+'.bin')
#TCDC_pf.astype('float32').tofile(OUTDIR+'tcdcp_'+str(YEAR)+str(MON)+str(DAY)+str(TIME)+'.bin')

#Lower CCOV resize
INFILE8=DATADIR+'lcdc_'+str(YEAR)+str(MON)+str(DAY)+str(TIME)+'.bin'
lcdc=fromfile(INFILE8,'float32').reshape(FT+1,505,481)

Lcdc=lcdc[:]/100

LCDC=biIntp(lat,lon,Lcdc[0:FT,:,:],LAT,LON)
print LCDC.shape

LCDCf=LCDC[0:FT,:,:].flatten()

print LCDCf.shape
LCDCf.astype('float32').tofile(OUTDIR+'lcdc_'+str(YEAR)+str(MON)+str(DAY)+str(TIME)+'.bin')

#Mid CCOV resize

#INFILE9=DATADIR+'mcdc_'+str(YEAR)+str(MON)+str(DAY)+str(TIME)+'.bin'
#mcdc=fromfile(INFILE9,'float32').reshape(24,505,481)

#MCDC=biIntp(lat,lon,mcdc,LAT,LON)
#print MCDC.shape

#MCDCf=MCDC.flatten()
#print MCDCf.shape
#MCDCf.astype('float32').tofile(OUTDIR+'mcdc_'+str(YEAR)+str(MON)+str(DAY)+str(TIME)+'.bin')

#High CCOV resize

#INFILE10=DATADIR+'hcdc_'+str(YEAR)+str(MON)+str(DAY)+str(TIME)+'.bin'
#hcdc=fromfile(INFILE9,'float32').reshape(24,505,481)

#HCDC=biIntp(lat,lon,hcdc,LAT,LON)
#print HCDC.shape

#HCDCf=HCDC.flatten()
#print HCDCf.shape
#HCDCf.astype('float32').tofile(OUTDIR+'hcdc_'+str(YEAR)+str(MON)+str(DAY)+str(TIME)+'.bin')




#notnecessary converted bindata just regrid

#shutil.copy (DATADIR+'prmsl_'+str(YEAR)+str(MON)+str(DAY)+str(TIME)+'.bin', OUTDIR+'prmsl_'+str(YEAR)+str(MON)+str(DAY)+str(TIME)+'.bin')
#Don't need?

#shutil.copy (DATADIR+'tmp_'+str(YEAR)+str(MON)+str(DAY)+str(TIME)+'.bin', OUTDIR+'tmp_'+str(YEAR)+str(MON)+str(DAY)+str(TIME)+'.bin')
INFILE5=DATADIR+'tmp_'+str(YEAR)+str(MON)+str(DAY)+str(TIME)+'.bin'
tmp=fromfile(INFILE5,'float32').reshape(FT+1,505,481)

TMP=biIntp(lat,lon,tmp[0:FT,:,:],LAT,LON)
print TMP.shape

TMPf=TMP[0:FT,:,:].flatten()
print TMPf.shape
TMPf.astype('float32').tofile(OUTDIR+'tmp_'+str(YEAR)+str(MON)+str(DAY)+str(TIME)+'.bin')

#shutil.copy (DATADIR+'ugrd_'+str(YEAR)+str(MON)+str(DAY)+str(TIME)+'.bin', OUTDIR+'ugrd_'+str(YEAR)+str(MON)+str(DAY)+str(TIME)+'.bin')
INFILE6=DATADIR+'ugrd_'+str(YEAR)+str(MON)+str(DAY)+str(TIME)+'.bin'
ugrd=fromfile(INFILE6,'float32').reshape(FT+1,505,481)

UGRD=biIntp(lat,lon,ugrd[0:FT,:,:],LAT,LON)
print UGRD.shape

UGRDf=UGRD[0:FT,:,:].flatten()
print UGRDf.shape
UGRDf.astype('float32').tofile(OUTDIR+'ugrd_'+str(YEAR)+str(MON)+str(DAY)+str(TIME)+'.bin')

#shutil.copy (DATADIR+'vgrd_'+str(YEAR)+str(MON)+str(DAY)+str(TIME)+'.bin', OUTDIR+'vgrd_'+str(YEAR)+str(MON)+str(DAY)+str(TIME)+'.bin')
INFILE7=DATADIR+'vgrd_'+str(YEAR)+str(MON)+str(DAY)+str(TIME)+'.bin'
vgrd=fromfile(INFILE7,'float32').reshape(FT+1,505,481)

VGRD=biIntp(lat,lon,vgrd[0:FT,:,:],LAT,LON)
print VGRD.shape

VGRDf=VGRD[0:FT,:,:].flatten()
print VGRDf.shape
VGRDf.astype('float32').tofile(OUTDIR+'vgrd_'+str(YEAR)+str(MON)+str(DAY)+str(TIME)+'.bin')

#Calculate Specific humidity

E=6.11*10**(7.5*(TMP-273.15)/(237.3-273.15+TMP))
Ep=E*RHc
q=622*Ep/(PRESSURE-0.378*Ep) #g/kg
Q=q/1000 #kg/kg

#print TMP
#T=TMP-273.15
#print T
#a0=6.1077
#a1=4.4365*10**-1
#a2=1.4289*10**-2
#a3=2.6506*10**-4
#a4=3.0312*10**-6
#a5=2.0340*10**-8
#a6=6.1368*10**-11
#e=a0+T*(a1+T*(a2+T*(a3+T+(a4+T*(a5+T*a6)))))
#print e
#ph=RHc*e


#print ph
#x=ph/PRESSURE
#print x
#Mh=18.01534
#Md=28.9644
#
##Q=(x*Mh)/(x*Mh+(1-x)*Md)
#print Q
#print Q.max()
print Q.shape
#
Qf=Q.flatten()
print Qf.shape

Qf.astype('float32').tofile(OUTDIR+'q_'+str(YEAR)+str(MON)+str(DAY)+str(TIME)+'.bin')


print "done!"
print "check resolution."

