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
import ConfigParser

sns.set(context="paper",style="whitegrid")

initFile  = ConfigParser.SafeConfigParser()
initFile.read(sys.argv[1])

FT        = 39 # step (tRes*FT = lead time)

obsStartDate = "2015090709"
obsEndDate   = "2015091123"
obsStartDate = dt.datetime.strptime(obsStartDate,"%Y%m%d%H")
obsEndDate   = dt.datetime.strptime(obsEndDate,"%Y%m%d%H")

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
stName       = initFile.get("stationInfo","stName")
outFile      = "%s_scores_EPS" % (stName)

obsFile      = "./observed_discharge_kinu.csv"

#domain
north     = 46
south     = 24
west      = 123
east      = 148

matOrder  = "SN"
res       = 0.05
nx        = 500
ny        = 440
#observation point
latDeg    = int(initFile.get("stationInfo","latDeg"))
latMin    = int(initFile.get("stationInfo","latMin"))
latSec    = int(initFile.get("stationInfo","latSec"))

lonDeg    = int(initFile.get("stationInfo","lonDeg"))
lonMin    = int(initFile.get("stationInfo","lonMin"))
lonSec    = int(initFile.get("stationInfo","lonSec"))
upaDir    = "/data3/yuta/CaMa-Flood_v3.6.2_FlPd/map/region_jpn5km"
upaFile   = "uparea.bin"

uarea     = float(initFile.get("stationInfo","uarea")) #[km2]

floodDate = dt.datetime.strptime("2015090921","%Y%m%d%H") #UTC

try:
    threshold = float(initFile.get("stationInfo","threshold"))
except:
    threshold = np.nan

#advanced setting
idxStart  = 0
idxEnd    = 39 #[idxStart:idxEnd]

buf       = 3
prcpC     = 3600


def setDate():
    start = dt.datetime.strptime(startDate,"%Y%m%d%H")
    end   = dt.datetime.strptime(endDate,"%Y%m%d%H")
    return start, end


def calcDeg(degree,minute,second):
    DEG=float(degree)+(float(minute)/60)+(float(second)/3600)
    return DEG


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

#    print "LatGrid:%d LonGrid:%d"%(LAT,LON)
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


def basinPrcp(Dir,File,step,FT,startDate,endDate,mask):
#    print "read precipitation."
    date = startDate
    while date <= endDate:
        year = date.year
        mon  = date.month
        day  = date.day
        hour = date.hour

        dPath = os.path.join(Dir%(hour,year,mon), File%(year,mon,day,hour))
#        print dPath
        if matOrder == "SN":
            data  = gtopen(dPath).vars["PRCP"][:][:,0,::-1,:]
        elif matOrder == "NS":
            data  = gtopen(dPath).vars["PRCP"][:][:,0,::-1,:]
        else:
            raise KeyError
#        print data.shape

        if date == startDate:
            prcp = data
        else:
            prcp = np.concatenate((prcp,data))

        if prcp.shape[0] > FT:
            prcp = prcp[0:FT]
#            print "formatted.", prcp.shape
            break

        date = date + dt.timedelta(hours=step)

    mPrcp    = prcp*mask*prcpC

    mPrcpAvg = np.nanmean(mPrcp,axis=(1,2))

    tindx = []
    for t in range(0,FT):
        date = startDate + dt.timedelta(hours=t*tRes)
        tindx.append(date)

    mPrcpAvgDf = pd.DataFrame(mPrcpAvg,index=tindx)

    return mPrcpAvgDf


def basinPrcpEns(Dir,File,step,FT,startDate,endDate,ens,mask):
#    print "read precipitation."
    date = startDate
    while date <= endDate:
        year = date.year
        mon  = date.month
        day  = date.day
        hour = date.hour

        dPath = os.path.join(Dir%(hour,year,mon), File%(ens,year,mon,day,hour))
#        print dPath
        if matOrder == "SN":
            data  = gtopen(dPath).vars["PRCP"][:][:,0,::-1,:]
        elif matOrder == "NS":
            data  = gtopen(dPath).vars["PRCP"][:][:,0,::-1,:]
        else:
            raise KeyError
#        print data.shape

        if date == startDate:
            prcp = data
        else:
            prcp = np.concatenate((prcp,data))

        if prcp.shape[0] > FT:
            prcp = prcp[0:FT]
#            print "formatted.", prcp.shape
            break

        date = date + dt.timedelta(hours=step)

    mPrcp    = prcp*mask*prcpC

    mPrcpAvg = np.nanmean(mPrcp,axis=(1,2))

    tindx = []
    for t in range(0,FT):
        date = startDate + dt.timedelta(hours=t*tRes)
        tindx.append(date)

    mPrcpAvgDf = pd.DataFrame(mPrcpAvg,index=tindx,columns=[ens])

    return mPrcpAvgDf


def readDscgObsFile(FT):
    data    = pd.read_csv("./observed_discharge_Kinu.csv",header=0,index_col=0,parse_dates=True)
    obsData = data[stName]
    # JST
    sDate   = obsStartDate + dt.timedelta(hours=9) + dt.timedelta(hours=1)
    eDate   = obsEndDate + dt.timedelta(hours=9) + dt.timedelta(hours=1) # plus 1 to read latter value in the one dt.
    obsData = obsData[sDate:eDate]

    tindx   = []
    for t in range(0,FT):
        date = obsStartDate + dt.timedelta(hours=t*tRes)
        tindx.append(date)

    obsDataDf = pd.DataFrame(obsData.values,index=tindx)

    return obsDataDf
    

def discharge(Dir,File,execStep,FT,startDate,endDate,ens):
#    print "read discharge."
    lat,lon = uparea()
    date = startDate
    while date <= endDate:
        year = date.year
        mon  = date.month
        day  = date.day
        hour = date.hour

        if ens == "ref":
            dPath = os.path.join(Dir%(year,mon,day,hour), File%(year))
        else:
            dPath = os.path.join(Dir%(year,mon,day,hour,ens), File%(year))
        data  = np.fromfile(dPath,np.float32).reshape(-1,ny,nx)[idxStart:idxEnd,lat,lon]
        if date == startDate:
            dscg = data
        else:
            dscg = np.concatenate((dscg,data))

        if dscg.shape[0] >= FT:
            dscg = dscg[0:FT]
            break

        date = date + dt.timedelta(hours=execStep)

    tindx = []
    for t in range(0,FT):
        date = startDate + dt.timedelta(hours=t*tRes)
        tindx.append(date)

    dscgDf = pd.DataFrame(dscg,index=tindx,columns=[ens])

    return dscgDf
    

def nashSutcliffe(obs,sim):
    obsAvg = np.ones((obs.shape[0]))*obs.mean()

    mother = ((obs-obsAvg)**2).sum()
    son    = ((sim-obs)**2).sum()

    NS     = 1 - (son/mother)
    print "Nash-Sutcliffe coef. is: ", NS

    return NS


def RMSE(obs,sim):
    SE   = (sim - obs)**2
    MSE  = SE.mean()
    RMSE = MSE**0.5

    print "RMSE is: ", RMSE

    return RMSE


def MAE(obs,sim):
    MAE = (np.absolute(obs-sim)).mean()

    print "MAE is: ", MAE
    return MAE


def corrCoef(obs,sim):
    cf = np.corrcoef(obs,sim)

    print "corr. coef. is: ", cf[0][1]
    return cf[0][1]


def scores(startDate,endDate):
    lat,lon = uparea()
    diff    = (obsEndDate - obsStartDate)
    obsSpan = ((diff.seconds/3600+diff.days*24)+1)/tRes #hour
    mask    = np.ma.masked_less(makeMask(lat,lon),1)
    obsPrcp = basinPrcp(obsPrcpDir,obsPrcpFile,obsExecStep,obsSpan,obsStartDate,obsEndDate,mask)
    obsPrcp.columns = ["obs"]
    simPrcp = basinPrcpEns(simPrcpDir,simPrcpFile,simExecStep,FT,startDate,endDate,"ctl",mask)
    for ens in range(1,50+1):
        ens = "%02d" % ens
        ensPrcp = basinPrcpEns(simPrcpDir,simPrcpFile,simExecStep,FT,startDate,endDate,ens,mask)
        simPrcp = pd.concat([simPrcp,ensPrcp],axis=1)
    prcpDf  = pd.concat([obsPrcp,simPrcp],axis=1)

    veVal = prcpDf["ctl"][startDate:endDate].values.sum()/prcpDf["obs"][startDate:endDate].values.sum()
    ve    = pd.DataFrame([veVal],columns=["ctl"],index=[startDate])
    for ens in range(1,50+1):
        ens    = "%02d" % ens
        veVale = prcpDf[ens][startDate:endDate].values.sum()/prcpDf["obs"][startDate:endDate].values.sum()
        vee    = pd.DataFrame([veVale],columns=[ens],index=[startDate])
        ve     = pd.concat([ve,vee],axis=1)

    dscgSim   = discharge(dscgDir,dscgFile,simExecStep,FT,startDate,endDate,"ctl")
    for ens in range(1,50+1):
        ens = "%02d" % ens
        dscgEns = discharge(dscgDir,dscgFile,simExecStep,FT,startDate,endDate,ens)
        dscgSim = pd.concat([dscgSim,dscgEns],axis=1)

    ensStd  = dscgSim.std(axis=1)
    ensAvg  = dscgSim.mean(axis=1)
    sigmaB = ensAvg.values - ensStd.values
    sigmaU = ensAvg.values + ensStd.values
    d      = {"avg":ensAvg.values,"sigb":sigmaB,"sigu":sigmaU}
    param  = pd.DataFrame(data=d,index=dscgSim.index)

    dscgObs   = readDscgObsFile(obsSpan)
    dscgObs.columns = ["obs"]
    dscgRef   = discharge(refDscgDir,refDscgFile,obsExecStep,obsSpan,obsStartDate,obsEndDate,"ref")
    dscgDf    = pd.concat([dscgObs,dscgSim,dscgRef,param],axis=1)
    
    NS   = pd.DataFrame([nashSutcliffe(dscgDf["obs"][startDate:endDate].values,dscgDf["ctl"][startDate:endDate].values)],columns=["ctl"],index=[startDate])
    mae  = pd.DataFrame([MAE(dscgDf["obs"][startDate:endDate].values,dscgDf["ctl"][startDate:endDate].values)],columns=["ctl"],index=[startDate])
    cf   = pd.DataFrame([corrCoef(dscgDf["obs"][startDate:endDate].values,dscgDf["ctl"][startDate:endDate].values)],columns=["ctl"],index=[startDate])
    for ens in range(1,50+1):
        ens  = "%02d" % ens
        nse  = pd.DataFrame([nashSutcliffe(dscgDf["obs"][startDate:endDate].values,dscgDf[ens][startDate:endDate].values)],columns=[ens],index=[startDate])
        NS   = pd.concat([NS,nse],axis=1)
        maee = pd.DataFrame([MAE(dscgDf["obs"][startDate:endDate].values,dscgDf[ens][startDate:endDate].values)],columns=[ens],index=[startDate])
        mae  = pd.concat([mae,maee],axis=1)
        cfe  = pd.DataFrame([corrCoef(dscgDf["obs"][startDate:endDate].values,dscgDf[ens][startDate:endDate].values)],columns=[ens],index=[startDate])
        cf   = pd.concat([cf,cfe],axis=1)

    return ve,NS,mae,cf


def main():
    startDate = dt.datetime.strptime("2015090806","%Y%m%d%H")
    finDate   = dt.datetime.strptime("2015090918","%Y%m%d%H")
    date      = startDate
    while date <= finDate:
        print date
        endDate = date + dt.timedelta(hours=FT-1)
        VE,NS,mae,cf = scores(date,endDate)
        if date == startDate:
            VEscores  = VE
            NSscores  = NS
            maescores = mae
            cfscores  = cf
        else:
            VEscores  = pd.concat([VEscores,VE],axis=0)
            NSscores  = pd.concat([NSscores,NS],axis=0)
            maescores = pd.concat([maescores,mae],axis=0)
            cfscores  = pd.concat([cfscores,cf],axis=0)
        date = date + dt.timedelta(hours=12)

    plt.figure(figsize=(15,18))
    tindx = []
    [ tindx.append(VEscores.index[i].strftime("%m/%d %H:00")) for i in range(0,4) ]
    print "====VE===="
    print VEscores.median(axis=1)
    print "====NS===="
    print NSscores.median(axis=1)
    print "===mae===="
    print maescores.median(axis=1)
    print "====cf===="
    print cfscores.median(axis=1)
    ax1 = plt.subplot(1,2,1)
    bplot = plt.boxplot(maescores.values.T,notch=False,patch_artist=True)
    plt.xticks([1,2,3,4],tindx,fontsize=35,rotation=57.5)
    plt.yticks([0,1500,3000,4500,6000,7500],fontsize=35)
    for i in bplot["boxes"]:
        i.set(facecolor="white",alpha=0.5)
    for i in bplot["medians"]:
        plt.setp(i,color="#A93226",linewidth=3)
    for i in bplot["caps"]:
        plt.setp(i,linewidth=2.5,color="#17202A")
    for i in bplot["whiskers"]:
        plt.setp(i,linewidth=2.5,color="#17202A")
#    plt.xlabel("Date",fontsize=40)
    plt.ylabel("MAE [m3/s]",fontsize=40)
    plt.ylim(0,7500)
    plt.tight_layout()

    ax2 = plt.subplot(1,2,2)
    bplot = plt.boxplot(cfscores.values.T,notch=False,patch_artist=True)
    plt.xticks([1,2,3,4],tindx,fontsize=35,rotation=57.5)
    plt.yticks([-1.0,-0.75,-0.5,-0.25,0,0.25,0.5,0.75,1.0],fontsize=35)
    for i in bplot["boxes"]:
        i.set(facecolor="white",alpha=0.5)
    for i in bplot["medians"]:
        plt.setp(i,color="#A93226",linewidth=3)
    for i in bplot["caps"]:
        plt.setp(i,linewidth=2.5,color="#17202A")
    for i in bplot["whiskers"]:
        plt.setp(i,linewidth=2.5,color="#17202A")
#    plt.xlabel("Date",fontsize=40)
    plt.ylabel("Correlation Coefficient",fontsize=40)
    plt.ylim(-1,1)
    plt.tight_layout()
#    plt.suptitle(stName,fontsize=30)
    plt.savefig("scores_ens_"+stName,bbox_inches="tight",pad_inches=0.025)
    plt.show()

if __name__ == "__main__":
    main()
