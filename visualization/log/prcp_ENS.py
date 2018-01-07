#/usr/bin/env python
import os
import sys
import numpy as np
import pandas as pd
import seaborn as sns
import datetime as dt
import subprocess
import matplotlib.pyplot as plt
from gtool import gtopen
from mpl_toolkits.basemap import Basemap
import matplotlib.cm as cm
import matplotlib.colors as colors

sns.set(context="paper",style="whitegrid",font_scale=2)
FT        = 39 # step (tRes*FT = lead time)
startDate = sys.argv[1]
startDate = dt.datetime.strptime(startDate,"%Y%m%d%H")
endDate   = startDate + dt.timedelta(hours=FT-1)

obsStartDate = "2015090709"
obsEndDate   = "2015091123"
obsStartDate = dt.datetime.strptime(obsStartDate,"%Y%m%d%H")
obsEndDate   = dt.datetime.strptime(obsEndDate,"%Y%m%d%H")

year      = startDate.year
mon       = startDate.month
day       = startDate.day
hour      = startDate.hour

#basic setting
obsPrcpDir   = "/data3/yuta/GPV_jpn/DATA/FT24/gtooldata24/%02d/%04d.%02d/"
obsPrcpFile  = "RDR_%04d%02d%02d%02d.gt"

simPrcpDir   = "/data3/yuta/GPV_jpn/DATA/FT39/gtooldata39/%02d/%04d.%02d/"
simPrcpFile  = "Ens_%s_%04d%02d%02d%02d.gt"

dscgDir      = "/data4/yuta/camaOut/Ens5_newriv/%04d/%02d/%02d/%02d/e_%s/"
dscgFile     = "outflw%04d.bin"

refDscgDir   = "/data4/yuta/camaOut/RDR5_newriv/%04d/%02d/%02d/%02d/"
refDscgFile  = "outflw%04d.bin"

obsExecStep  = 24 #hour
simExecStep  = 39 #hour
tRes         = 1  #hour
tFreq        = 6  #hour

outDir       = "./figure"

#domain
north     = 46
south     = 24
west      = 123
east      = 148

matOrder  = "SN"
res       = 0.05
nx        = 500
ny        = 440

#target
n         = 38
s         = 34
w         = 138
e         = 141

#observation point
latDeg    = 36
latMin    = 1
latSec    = 18

lonDeg    = 139
lonMin    = 59
lonSec    = 6
upaDir    = "/data3/yuta/CaMa-Flood_v3.6.2_FlPd/map/region_jpn5km"
upaFile   = "uparea.bin"

uarea     = 1740.10 #[km2]

#advanced setting
idxStart  = 0
idxEnd    = 39 #[idxStart:idxEnd]

meriSpace = 2
paraSpace = 2

buf       = 3
prcpC     = 3600


def setDate():
    start = dt.datetime.strptime(startDate,"%Y%m%d%H")
    end   = dt.datetime.strptime(endDate,"%Y%m%d%H")
    return start, end


def calcDeg(degree,minute,second):
    DEG=float(degree)+(float(minute)/60)+(float(second)/3600)
    return DEG


def setBasemap():
    plt.figure(figsize=(15,15))
    map = Basemap(resolution="h",llcrnrlat=s,llcrnrlon=w,urcrnrlat=n,urcrnrlon=e)
    map.drawcoastlines(zorder=0)
    parallels = np.arange(s,n,meriSpace)
    map.drawparallels(parallels,labels=[True,False,False,False],zorder=0)
    meridians = np.arange(w,e,paraSpace)
    map.drawmeridians(meridians,labels=[False,False,False,True],zorder=0)
    map.drawrivers()
    ys  = int((north - n)/res)
    ye  = int((north - s)/res)
    xs  = int((w - west)/res)
    xe  = int((e - west)/res)
    return map,ys,ye,xs,xe


def uparea():
    ERR = 1e+20
    LAT  = -9999
    LON  = -9999
    cnt  = 0

    lat  = calcDeg(latDeg,latMin,latSec)
    lon  = calcDeg(lonDeg,lonMin,lonSec)

    gridLat = int((north - lat)/res)
    gridLon = int((lon - west)/res)

    upaPath = os.path.join(upaDir,upaFile)
    umap = np.fromfile(os.path.join(upaDir,upaPath),np.float32).reshape(ny,nx)

    for i in range(-buf,buf+1):
        for j in range(-buf,buf+1):
            marea = umap[gridLat+i,gridLon+j]/(1000*1000)
            error = ((marea - uarea)**2)**0.5
            if cnt == 0 or error < ERR:
                ERR = error
                LAT = gridLat+i
                LON = gridLon+j
            cnt = cnt + 1

    return LAT,LON


def makeMask(lat,lon):
    if os.path.exists("./mask") == False:
        os.makedirs("./mask")

    fortLon = lon + 1
    fortLat = lat + 1

    crrDir  = os.getcwd()
    os.chdir(upaDir)
    subprocess.call([crrDir+"/calc_basin.o",str(fortLon),str(fortLat),str(nx),str(ny)])
    subprocess.call(["mv","./mask.bin",crrDir+"/mask/"])
    os.chdir(crrDir)

    mask = np.fromfile("./mask/mask.bin",np.int32).reshape(1,ny,nx)

    return mask


def basinPrcp(Dir,File,step,FT,startDate,endDate):
    date = startDate
    while date <= endDate:
        year = date.year
        mon  = date.month
        day  = date.day
        hour = date.hour

        dPath = os.path.join(Dir%(hour,year,mon), File%(year,mon,day,hour))
        if matOrder == "SN":
            data  = gtopen(dPath).vars["PRCP"][:][:,0,::-1,:]
        elif matOrder == "NS":
            data  = gtopen(dPath).vars["PRCP"][:][:,0,::-1,:]
        else:
            raise KeyError

        if date == startDate:
            prcp = data
        else:
            prcp = np.concatenate((prcp,data))

        if prcp.shape[0] > FT:
            prcp = prcp[0:FT]
            break
        
        date = date + dt.timedelta(hours=step)

    mPrcp    = prcp*prcpC

    return mPrcp


def basinPrcpEns(Dir,File,step,FT,startDate,endDate,ens):
    date = startDate
    while date <= endDate:
        year = date.year
        mon  = date.month
        day  = date.day
        hour = date.hour

        dPath = os.path.join(Dir%(hour,year,mon), File%(ens,year,mon,day,hour))
        if matOrder == "SN":
            data  = gtopen(dPath).vars["PRCP"][:][:,0,::-1,:]
        elif matOrder == "NS":
            data  = gtopen(dPath).vars["PRCP"][:][:,0,::-1,:]
        else:
            raise KeyError

        if date == startDate:
            prcp = data
        else:
            prcp = np.concatenate((prcp,data))

        if prcp.shape[0] > FT:
            prcp = prcp[0:FT]
            break

        date = date + dt.timedelta(hours=step)

    mPrcp    = prcp*prcpC

    return mPrcp


def corrCoef(obs,sim):
    cf = np.corrcoef(obs,sim)

    print "corr. coef. is: ", cf[0][1]
    return cf[0][1]

def hyetohydro():
    
    lat,lon  = uparea()
    mask     = makeMask(lat,lon)[0]
    mask[np.where(mask<1)] = 0

    obsPrcp = basinPrcp(obsPrcpDir,obsPrcpFile,obsExecStep,FT,startDate,endDate)
    simPrcp = basinPrcpEns(simPrcpDir,simPrcpFile,simExecStep,FT,startDate,endDate,"ctl")
    cf = corrCoef(obsPrcp.sum(axis=0).flatten(),simPrcp.sum(axis=0).flatten())
    draw(obsPrcp,simPrcp,mask,"ctl")
    for ens in range(1,50+1):
        ens = "%02d" % ens
        ensPrcp = basinPrcpEns(simPrcpDir,simPrcpFile,simExecStep,FT,startDate,endDate,ens)
        cf  = corrCoef(obsPrcp.sum(axis=0).flatten(),ensPrcp.sum(axis=0).flatten())
        draw(obsPrcp,ensPrcp,mask,ens)


def draw(obsPrcp,ensPrcp,mask,num):
    cumObs  = obsPrcp.sum(axis=0)
    cumSim  = ensPrcp.sum(axis=0)

    x = np.arange(w,e,res)
    y = np.arange(s,n,res)
    X,Y = np.meshgrid(x,y)
    norm = [0,100,250,500,600,700,800]
    norml = colors.BoundaryNorm(norm,256)

    map,ys,ye,xs,xe = setBasemap()
    map.contour(X,Y,mask[ys:ye,xs:xe][::-1,:],colors="k",linewidths=0.5,origin="lower",zorder=1)
    map.imshow(np.ma.masked_equal(cumObs[ys:ye,xs:xe],0),origin="upper",norm=norml,cmap=cm.CMRmap_r,alpha=0.7,zorder=2)
    cbar=plt.colorbar(shrink=0.7,extend="max")
    cbar.ax.tick_params(labelsize=20)
    plt.title("RDR [39h cumrative] IT:"+startDate.strftime("%Y/%m/%d %H:00")+"[UTC]")
    plt.savefig("./figure/RDR_cum_"+startDate.strftime("%Y%m%d%H"))
    plt.close()

    map,ys,ye,xs,xe = setBasemap()
    map.contour(X,Y,mask[ys:ye,xs:xe][::-1,:],colors="k",linewidths=0.5,origin="lower",zorder=1)
    map.imshow(np.ma.masked_equal(cumSim[ys:ye,xs:xe],0),origin="upper",norm=norml,cmap=cm.CMRmap_r,alpha=0.7,zorder=2)
#    map.imshow(np.ma.masked_equal(cumSim[ys:ye,xs:xe],0),origin="upper",cmap=cm.CMRmap_r,alpha=0.7,zorder=2)
    cbar=plt.colorbar(shrink=0.7,extend="max")
    cbar.ax.tick_params(labelsize=20)
    plt.title("ENS [39h cumrative] IT:"+startDate.strftime("%Y/%m/%d %H:00")+"[UTC]")
    plt.savefig("./figure/ENS_cum_umnorm_"+num+"_"+startDate.strftime("%Y%m%d%H"))
#    plt.show()
    plt.close()

    map,ys,ye,xs,xe = setBasemap()
    norm = [-300,-200,-100,-50,0,50,100,200,300]
    norml = colors.BoundaryNorm(norm,256)
    map.contour(X,Y,mask[ys:ye,xs:xe][::-1,:],colors="k",linewidths=0.5,origin="lower",zorder=1)
    map.imshow(np.ma.masked_equal((cumSim-cumObs)[ys:ye,xs:xe],0),origin="upper",norm=norml,cmap=cm.PuOr,alpha=0.7,zorder=2)
#    map.imshow(np.ma.masked_equal((cumSim-cumObs)[ys:ye,xs:xe],0),origin="upper",cmap=cm.PuOr,alpha=0.7,zorder=2)
    cbar=plt.colorbar(shrink=0.7,extend="both")
    cbar.ax.tick_params(labelsize=20)
    plt.title("ENS - RDR [39h cumurative] IT:"+startDate.strftime("%Y/%m/%d %H:00")+"[UTC]")
    plt.savefig("./figure/ENS-RDR_cum_unnorm_"+num+"_"+startDate.strftime("%Y%m%d%H"))
    plt.close()

if __name__ == "__main__":
    hyetohydro()
