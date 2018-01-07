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

FT=39

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


DATADIR='/data3/yuta/GPV_jpn/DATA/FT'+str(FT)+'/processed_bindata'+str(FT)+'/'+str(t)+'/'+str(Year)+'.'+str(m)+'/'
DATADIR2='/data3/yuta/GPV_jpn/DATA/FT'+str(FT)+'/processed_bindata'+str(FT)+'/'+str(t)+'/'+str(Year)+'.'+str(m)+'/'
outDir  = '/data3/yuta/GPV_jpn/DATA/FT'+str(FT)+'/gtooldata'+str(FT)+'/'+str(t)+'/'+str(Year)+'.'+str(m)+'/'

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
    Data    = fromfile(DATADIR+'prcp_'+str(Year)+str(m)+str(d)+str(t)+'.bin', 'float32')
    varName = 'PRCP'
    itemName= 'PRCP'
    gtUnit  = 'kg/m2/s'

    ### Setting ###
    
    #-- Resolution
    nX      = 500
    nY      = 440
    nZ      =   1

    #-- Time Step and deltT
    nT      = FT
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


#Pressure

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
    Data    = fromfile(DATADIR+'pres_'+str(Year)+str(m)+str(d)+str(t)+'.bin', 'float32')
    varName = 'PS'
    itemName= 'PS'
    gtUnit  = 'hPa'

    ### Setting ###

    #-- Resolution
    nX      = 500
    nY      = 440
    nZ      =   1

    #-- Time Step and deltT
    nT      = FT
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
    outPath = os.path.join(outDir,'%s_%i%s%s%s.gt'%(varName,Year,m,d,t))


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

#Relative Humidity

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

    Data    = fromfile(DATADIR+'rh_'+str(Year)+str(m)+str(d)+str(t)+'.bin', 'float32')
    varName = 'RH'
    itemName= 'RH'
    gtUnit  = 'kg/kg'

    ### Setting ###

    #-- Resolution
    nX      = 500
    nY      = 440
    nZ      =   1

    #-- Time Step and deltT
    nT      = FT
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
    outPath = os.path.join(outDir,'%s_%i%s%s%s.gt'%(varName,Year,m,d,t))


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

#Total cloud cover

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
    Data    = fromfile(DATADIR+'tcdc_'+str(Year)+str(m)+str(d)+str(t)+'.bin', 'float32')
    varName = 'CCOVER'
    itemName= 'CCOVER'
    gtUnit  = 'kg/kg'


    ### Setting ###
 
   #resolution
    nX      = 500
    nY      = 440
    nZ      =   1

    #-- Time Step and deltT
    nT      = FT
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
    outPath = os.path.join(outDir,'%s_%i%s%s%s.gt'%(varName,Year,m,d,t))


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


#temperature

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
    Data    = fromfile(DATADIR+'tmp_'+str(Year)+str(m)+str(d)+str(t)+'.bin', 'float32')
    varName = 'T'
    itemName= 'T'
    gtUnit  = 'kg/kg'
 
   ### Setting ###

    #-- Resolution
    nX      = 500
    nY      = 440
    nZ      =   1

    #-- Time Step and deltT
    nT      = FT
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
    outPath = os.path.join(outDir,'%s_%i%s%s%s.gt'%(varName,Year,m,d,t))


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



#U-component(east-west) of wind

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
    Data    = fromfile(DATADIR+'ugrd_'+str(Year)+str(m)+str(d)+str(t)+'.bin', 'float32')
    varName = 'U'
    itemName= 'U'
    gtUnit  = 'm/s'

    ### Setting ###

    #-- Resolution
    nX      = 500
    nY      = 440
    nZ      =   1

    #-- Time Step and deltT
    nT      = FT
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
    outPath = os.path.join(outDir,'%s_%i%s%s%s.gt'%(varName,Year,m,d,t))


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



#V-component(nouth-south) of wind

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
    Data    = fromfile(DATADIR+'vgrd_'+str(Year)+str(m)+str(d)+str(t)+'.bin', 'float32')
    varName = 'V'
    itemName= 'V'
    gtUnit  = 'm/s'

    ### Setting ###

    #-- Resolution
    nX      = 500
    nY      = 440
    nZ      =   1

    #-- Time Step and deltT
    nT      = FT
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
    outPath = os.path.join(outDir,'%s_%i%s%s%s.gt'%(varName,Year,m,d,t))


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


#Specific humidity

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
    Data    = fromfile(DATADIR+'q_'+str(Year)+str(m)+str(d)+str(t)+'.bin', 'float32')
    varName = 'Q'
    itemName= 'Q'
    gtUnit  = 'kg/kg'

    ### Setting ###

    #-- Resolution
    nX      = 500
    nY      = 440
    nZ      =   1


    #-- Time Step and deltT
    nT      = FT
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
    outPath = os.path.join(outDir,'%s_%i%s%s%s.gt'%(varName,Year,m,d,t))


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


#Long wave down

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
    Data    = fromfile(DATADIR2+'lwd_'+str(Year)+str(m)+str(d)+str(t)+'.bin', 'float32')
    varName = 'SLRD'
    itemName= 'SLRD'
    gtUnit  = 'W/m2'

    ### Setting ###

    #-- Resolution
    nX      = 500
    nY      = 440
    nZ      = 1

    #-- time step and deltT
    nT      = 1
    dT      = 60*60*24

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
    outPath = os.path.join(outDir,'%s_%i%s%s%s.gt'%(varName,Year,m,d,t))


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


#Long wave down

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
    Data    = fromfile(DATADIR2+'swd_'+str(Year)+str(m)+str(d)+str(t)+'.bin', 'float32')
    varName = 'SSRD'
    itemName= 'SSRD'
    gtUnit  = 'W/m2'

    ### Setting ###

    #-- Resolution
    nX      = 500
    nY      = 440
    nZ      = 1

    #-- time step and deltT
    nT      = 1
    dT      = 60*60*24


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
    outPath = os.path.join(outDir,'%s_%i%s%s%s.gt'%(varName,Year,m,d,t))


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


