#! /home/yuta/bin/python

############################################################
#for converting GPV_MSM binary data(already unit-precessed and regrided to 0.05x0.05) to gtool format
############################################################
 
import os,sys
from datetime import *
from   cf.io.gtool    import gtool
from   cf.util.LOGGER import *
from pylab import *
import sys

Year    = int(sys.argv[1])
MON     = int(sys.argv[2])
DAY     = int(sys.argv[3])
TIME    = int(sys.argv[4])

if int(MON)<10:
	m='0'+str(MON)
else:
        m=str(MON)

if int(DAY)<10:
        d='0'+str(DAY)
else:
        d=str(DAY)

if int(TIME)<10:
        t='0'+str(TIME)
else:
        t=str(TIME)


DATADIR='/data3/yuta/GPV_jpn/DATA/FT24/processed_bindata24/'+str(t)+'/'+str(Year)+'.'+str(m)+'/'
DATADIR2='/data3/yuta/GPV_jpn/DATA/FT24/processed_bindata24/'+str(t)+'/'+str(Year)+'.'+str(m)+'/'
outDir  = '/data3/yuta/GPV_jpn/DATA/FT24/gtooldata24/'+str(t)+'/'+str(Year)+'.'+str(m)+'/'

if os.path.exists(outDir)==False:
	os.makedirs(outDir)
	print "Directory was made..."


#precipitation

@ETA
def main(*args):


    if int(MON)<10:
        m='0'+str(MON)
    else:
        m=str(MON)

    if int(DAY)<10:
        d='0'+str(DAY)
    else:
        d=str(DAY)

    if int(TIME)<10:
        t='0'+str(TIME)
    else:
        t=str(TIME)

    ### Read args ###
    Data    = fromfile(DATADIR+'rdr_'+str(Year)+str(m)+str(d)+str(t)+'.bin', 'float32')
    varName = 'RDR'
    itemName= 'PRCP'
    gtUnit  = 'kg/m2/s'

    ### Setting ###
    
    #-- Resolution
    nX      = 500
    nY      = 440
    nZ      =   1

    #-- Time Step and deltT
    nT      = 24
    dT      = 3600  

    #-- Coordination
    GLON    = 'GLON500M' 
    GLAT    = 'GLAT440IM'
    GATM    = 'SFC1'

    #missing_value   = 1.E20
    #missing_value   = -999.


    if os.path.isdir(outDir) != True:
        raise IOError



    ### Pre-Process ###

    os.environ['F_UFMTENDIAN'] = 'big'                            # don't need ??
    outPath = os.path.join(outDir,'%s_%s%s%s%s.gt'%(varName,Year,m,d,t))


    Data    = Data.reshape(nT,nZ,nY,nX)

#    DTIME   = [ datetime(Year,1,1,0)+timedelta(seconds=dT)*i for i in range(nT) ]
    DTIME   = [ datetime.datetime(Year,MON,DAY,TIME)+datetime.timedelta(seconds=dT)*i for i in range(0,nT) ]





    ### Writing ###========================
    gtOut   = gtool(outPath,'ow')            # ow: over write


    gtOut[itemName]          = Data, DTIME 
    gtOut[itemName].TITL1    = varName
    gtOut[itemName].UNIT     = gtUnit


    gtOut[itemName].AEND1    = nX
    gtOut[itemName].AEND2    = nY
    gtOut[itemName].AEND3    = nZ

    gtOut[itemName].AITM1    = GLON
    gtOut[itemName].AITM2    = GLAT
    gtOut[itemName].AITM3    = GATM    

    gtOut.save(10) 



    print 'outPath: ', outPath
    print gtOut[itemName].header
    #=======================================



if __name__=='__main__':
    #LOG = LOGGER()
    main(*sys.argv)



