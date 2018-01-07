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

"""
visualize precipitation and discharge as hyetograph and hydrograph.
also analyze statistical values.
"""

sns.set(context="paper",style="whitegrid")

initFile  = ConfigParser.SafeConfigParser()
initFile.read(sys.argv[1])

FT        = 39 # step (tRes*FT = lead time)

obsStartDate = "2015090800"
obsEndDate   = "2015091123"
obsStartDate = dt.datetime.strptime(obsStartDate,"%Y%m%d%H")
obsEndDate   = dt.datetime.strptime(obsEndDate,"%Y%m%d%H")


#basic setting
obsPrcpDir   = "/data3/yuta/GPV_jpn/DATA/FT24/gtooldata24/%02d/%04d.%02d/"
obsPrcpFile  = "RDR_%04d%02d%02d%02d.gt"

simPrcpDir   = "/data3/yuta/GPV_jpn/DATA/FT39/gtooldata39/%02d/%04d.%02d/"
simPrcpFile  = "Ens_%s_%04d%02d%02d%02d.gt"
msmPrcpDir   = "/data3/yuta/GPV_jpn/DATA/FT39/gtooldata39/%02d/%04d.%02d/"
msmPrcpFile  = "PRCP_%04d%02d%02d%02d.gt"

dscgDir      = "/data4/yuta/camaOut/Ens5_newriv/%04d/%02d/%02d/%02d/e_%s/"
msmDscgDir   = "/data4/yuta/camaOut/MSM5_newriv/%04d/%02d/%02d/%02d/"
dscgFile     = "outflw%04d.bin"

refDscgDir   = "/data4/yuta/camaOut/RDR5_newriv/%04d/%02d/%02d/%02d/"
refDscgFile  = "outflw%04d.bin"

obsExecStep  = 24 #hour
simExecStep  = 39 #hour
tRes         = 1  #hour
tFreq        = 6  #hour

outDir       = "./figure"
stName       = initFile.get("stationInfo","stName")

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

#drawing setting
prcpYticks = map(int,initFile.get("stationInfo","pYticks").split(","))
dscgYticks = map(int,initFile.get("stationInfo","dYticks").split(","))
pMax      = 60
dMax      = float(initFile.get("stationInfo","dMax"))

#advanced setting
idxStart  = 0
idxEnd    = 39 #[idxStart:idxEnd]

buf       = 3
prcpC     = 3600


def setDate(sDate,eDate):
    start = dt.datetime.strptime(sDate,"%Y%m%d%H")
    end   = dt.datetime.strptime(eDate,"%Y%m%d%H")
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

        if ens == "ref" or ens == "msm":
            dPath = os.path.join(Dir%(year,mon,day,hour), File%(year))
        else:
            dPath = os.path.join(Dir%(year,mon,day,hour,ens), File%(year))
#        print dPath
        data  = np.fromfile(dPath,np.float32).reshape(-1,ny,nx)[idxStart:idxEnd,lat,lon]
#        print data.shape
        if date == startDate:
            dscg = data
        else:
            dscg = np.concatenate((dscg,data))

        if dscg.shape[0] > FT:
            dscg = dscg[0:FT]
#            print "formatted.",dscg.shape

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
#    print "Nash-Sutcliffe coef. is: ", NS

    return NS


def RMSE(obs,sim):
    SE   = (sim - obs)**2
    MSE  = SE.mean()
    RMSE = MSE**0.5

#    print "RMSE is: ", RMSE

    return RMSE

def MAE(obs,sim):
    MAE = (np.absolute(obs-sim)).mean()

#    print "MAE is: ", MAE
    return MAE

def corrCoef(obs,sim):
    cf = np.corrcoef(obs,sim)

#    print "corr. coef. is: ", cf[0][1]
    return cf[0][1]

def hyetohydro():
#    fig       = plt.figure(figsize=(24.27,15))
    
    ax1     = plt.subplot(2,1,1)
    lat,lon  = uparea()
    mask     = np.ma.masked_less(makeMask(lat,lon),1)
    diff    = (obsEndDate - obsStartDate)
    obsSpan = ((diff.seconds/3600+diff.days*24)+1)/tRes #hour
    obsPrcp = basinPrcp(obsPrcpDir,obsPrcpFile,obsExecStep,obsSpan,obsStartDate,obsEndDate,mask)
    obsPrcp.columns = ["obs"]
    simPrcp = basinPrcpEns(simPrcpDir,simPrcpFile,simExecStep,FT,startDate,endDate,"ctl",mask)
    msmPrcp = basinPrcp(msmPrcpDir,msmPrcpFile,simExecStep,FT,startDate,endDate,mask).rename(columns={0:"msm"})
    for ens in range(1,50+1):
        ens = "%02d" % ens
        ensPrcp = basinPrcpEns(simPrcpDir,simPrcpFile,simExecStep,FT,startDate,endDate,ens,mask)
        simPrcp = pd.concat([simPrcp,ensPrcp],axis=1)
    prcpDf  = pd.concat([obsPrcp,simPrcp,msmPrcp],axis=1)
    ensStd  = simPrcp.std(axis=1)
    ensAvg  = simPrcp.mean(axis=1)
    sigmaB = ensAvg.values - ensStd.values
    sigmaU = ensAvg.values + ensStd.values
    d      = {"avg":ensAvg.values,"sigb":sigmaB,"sigu":sigmaU}
    param  = pd.DataFrame(data=d,index=simPrcp.index)
    prcpDf = pd.concat([prcpDf,param],axis=1)

    tshape  = prcpDf["obs"].shape[0]
    durat   = tshape*tRes
    t       = 0
    cnt     = 0
    tindx   = [] #for date label
    xRange  = [] #for date label
    dummy   = []
    while t < durat:
        if cnt % 2 == 0:
            date = obsStartDate + dt.timedelta(hours=t*tRes)
            tindx.append(date.strftime("%m/%d %H:00"))
        else:
            date = "" #dummy
            tindx.append(date)
        xRange.append(t)
        dummy.append("")
        t = t + tFreq
        cnt = cnt + 1

    obsTRange = []
    [ obsTRange.append( obsStartDate + dt.timedelta(hours=t*tRes)) for i in range(durat) ]
    obsTRange = np.array(obsTRange)
#    simTRange = []
#    [ simTRange.append( startDate + dt.timedelta(hours=t*tRes)) for i in range(FT) ]
#    simTRange=np.array(simTRange)
    plt.plot(prcpDf["obs"].values,color="#283747",linewidth=3,linestyle="--",label="Radar")
#    plt.plot(prcpDf["ctl"].values,color="gray",linewidth=0.25,linestyle="-",label="ECMWF_EPS")
    plt.plot(prcpDf["msm"].values,color="orange",linewidth=1,linestyle="-",label="MSM")
    for ens in range(1,50+1):
        ens = "%02d" % ens
#        plt.plot(prcpDf[ens].values,color="gray",linewidth=0.25,linestyle="-")
    plt.plot(prcpDf["avg"].values,color="#1E8449",linewidth=2,linestyle="-",label="ensMean")
    plt.plot(prcpDf["sigb"].values,color="#303F9F",linewidth=0.5,linestyle="-",alpha=0.5)
    plt.plot(prcpDf["sigu"].values,color="#303F9F",linewidth=0.5,linestyle="-",alpha=0.5)
    x = np.arange(0,prcpDf.index.shape[0],1)
    plt.fill_between(x,prcpDf["sigu"].values,prcpDf["sigb"].values,where=np.isfinite(prcpDf["sigu"].values),alpha=0.1,facecolor="#303F9F",linewidth=0)
    plt.xticks(xRange,dummy)
    plt.xlim(0,obsPrcp.shape[0])
    plt.yticks(prcpYticks,fontsize=25)
    plt.ylim(pMax,0)
    plt.ylabel("Precip.[mm/h]",fontsize=30)
    plt.legend(loc="lower left",frameon=True,fontsize=25)
    plt.title(stName,fontsize=40)
    
    #statitical values
#    prcpCC  = corrCoef(obsPrcp["obs"][startDate:endDate].values,simPrcp["sim"][startDate:endDate].values)
#    prcpMAE = MAE(obsPrcp["obs"][startDate:endDate].values,simPrcp["sim"][startDate:endDate].values)
#    volume  = float(simPrcp["sim"][startDate:endDate].values.sum()/obsPrcp["obs"][startDate:endDate].values.sum())

#    tStr = "PRCP(39h)\nCorr.Coef:%.2f\nMAE:%.2f\nVolumeError:%.2f" % (prcpCC,prcpMAE,volume)
#    prop = dict(boxstyle="round",facecolor="wheat",alpha=0.75)
#    ax1.text(1-0.14,0.95,tStr,transform=ax1.transAxes,fontsize=20,verticalalignment="top",bbox=prop)

    ax2       = plt.subplot(2,1,2)
    dscgSim   = discharge(dscgDir,dscgFile,simExecStep,FT,startDate,endDate,"ctl")
    dscgMsm   = discharge(msmDscgDir,dscgFile,simExecStep,FT,startDate,endDate,"msm")
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
    dscgDf    = pd.concat([dscgObs,dscgSim,dscgMsm,dscgRef,param],axis=1)
    
    MAEa = []
    cfa  = []
#    plt.plot(dscgDf["ctl"].values,color="gray",linewidth=0.25,label="sim. EPS")
    plt.plot(dscgDf["msm"].values,color="orange",linewidth=1,label="MSM")
    NS   = pd.DataFrame([nashSutcliffe(dscgDf["obs"][startDate:endDate].values,dscgDf["ctl"][startDate:endDate].values)],columns=["ctl"],index=["NS"])
    mae  = pd.DataFrame([MAE(dscgDf["obs"][startDate:endDate].values,dscgDf["ctl"][startDate:endDate].values)],columns=["ctl"],index=["MAE"])
    maeV = MAE(dscgDf["obs"][startDate:endDate].values,dscgDf["ctl"][startDate:endDate].values)
    cf   = pd.DataFrame([corrCoef(dscgDf["obs"][startDate:endDate].values,dscgDf["ctl"][startDate:endDate].values)],columns=["ctl"],index=["cf"])
    cfV  = corrCoef(dscgDf["obs"][startDate:endDate].values,dscgDf["ctl"][startDate:endDate].values)
    MAEa.append(maeV)
    cfa.append(cfV)

    print "="*80
    print startDate
    print "mae: ",mae.values
    cf   = pd.DataFrame([corrCoef(dscgDf["obs"][startDate:endDate].values,dscgDf["ctl"][startDate:endDate].values)],columns=["ctl"],index=["cf"])
    print "corr.coef: ",cf.values
    for ens in range(1,50+1):
        ens  = "%02d" % ens
        nse  = pd.DataFrame([nashSutcliffe(dscgDf["obs"][startDate:endDate].values,dscgDf[ens][startDate:endDate].values)],columns=[ens],index=["NS"])
        NS   = pd.concat([NS,nse],axis=0)
        maee = pd.DataFrame([MAE(dscgDf["obs"][startDate:endDate].values,dscgDf[ens][startDate:endDate].values)],columns=[ens],index=["MAE"])
        maeV = MAE(dscgDf["obs"][startDate:endDate].values,dscgDf[ens][startDate:endDate].values)
        mae  = pd.concat([mae,maee],axis=0)
        cfe  = pd.DataFrame([corrCoef(dscgDf["obs"][startDate:endDate].values,dscgDf[ens][startDate:endDate].values)],columns=[ens],index=["cf"])
        cfV  = corrCoef(dscgDf["obs"][startDate:endDate].values,dscgDf[ens][startDate:endDate].values)
        cf   = pd.concat([cf,cfe],axis=0)
        MAEa.append(maeV)
        cfa.append(cfV)

#        plt.plot(dscgDf[ens].values,color="gray",linewidth=0.25,linestyle="-")

    print "mae median: ", np.median(np.array(MAEa))
    print "cf median: ", np.median(np.array(cfa))

    plt.plot(dscgDf["avg"].values,color="#1E8449",linestyle="-",linewidth=2,label="ensMean")
    plt.fill_between(x,dscgDf["sigu"].values,dscgDf["sigb"].values,where=np.isfinite(dscgDf["sigu"].values),alpha=0.1,facecolor="#303F9F",linewidth=0)
    plt.plot(dscgDf["ref"].values,color="#3498DB",linestyle=":",linewidth=3,label="sim. RDR")
    plt.plot(dscgDf["obs"].values,color="#283747",linestyle="--",linewidth=3,label="obs.")
    plt.plot(dscgDf["sigu"].values,color="#303F9F",linestyle="-",linewidth=0.5,alpha=0.5)
    plt.plot(dscgDf["sigb"].values,color="#303F9F",linestyle="-",linewidth=0.5,alpha=0.5)
    plt.ylim(0,dMax)
    plt.xlim(0,obsPrcp.shape[0])
    plt.xticks(xRange,tindx,fontsize=25)
    plt.xticks(rotation=52.5)
    plt.yticks(dscgYticks,fontsize=25)
    plt.ylabel("Discharge [m3/s]",fontsize=30)
    plt.xlabel("Date [UTC]",fontsize=30)
    
#    plt.legend(loc="lower left",frameon=True,fontsize=25)

    # threshold values
    x = np.arange(0,dscgDf["obs"].shape[0],1)
    y = np.ones((dscgDf["obs"].shape[0]))*threshold
    plt.plot(x,y,color="#C0392B",linewidth=1.5,linestyle="-.")

    EXCD   = []
    PEAK   = []

    obsTme = dscgDf["obs"][startDate:floodDate].idxmax(axis=1)

    case   = dscgSim["ctl"][startDate:floodDate].max(axis=1)
    EXCD.append(case)
    time   = dscgSim["ctl"][startDate:floodDate].idxmax(axis=1)
    peak   = (time - obsTme).days*24 + (time - obsTme).seconds/3600
    PEAK.append(peak)
    print "CTL run exceeds?: ", case > threshold
    for ens in range(1,50+1):
        ens = "%02d"%ens
        case   = dscgSim[ens][startDate:floodDate].max(axis=1)
        time   = dscgSim[ens][startDate:floodDate].idxmax(axis=1)
        peak   = (time - obsTme).days*24 + (time - obsTme).seconds/3600
        EXCD.append(case)
        PEAK.append(peak)
    excd = np.array(EXCD)
    peak = np.array(PEAK)

    number = (np.where(excd>threshold)[0]).shape[0]
    frac   = number/51.

    print "Initial time at: %s"%startDate.strftime("%Y/%m/%d %H:00")
    print "exceed number: %d"%number
    print "its fraction: %.2f"%frac
#    print PEAK



    
    # statistical values
#    NS   = nashSutcliffe(dscgDf["obs"][startDate:endDate].values,dscgDf["sim"][startDate:endDate].values)
#    rmse = RMSE(dscgDf["obs"][startDate:endDate].values,dscgDf["sim"][startDate:endDate].values)
#    mae  = MAE(dscgDf["obs"][startDate:endDate].values,dscgDf["sim"][startDate:endDate].values)
#    cf   = corrCoef(dscgDf["obs"][startDate:endDate].values,dscgDf["sim"][startDate:endDate].values)

#    refNS   =  nashSutcliffe(dscgDf["obs"][startDate:endDate].values,dscgDf["ref"][startDate:endDate].values)
#    refRmse = RMSE(dscgDf["obs"][startDate:endDate].values,dscgDf["ref"][startDate:endDate].values)
#    refMae  = MAE(dscgDf["obs"][startDate:endDate].values,dscgDf["ref"][startDate:endDate].values)
#    refCf   = corrCoef(dscgDf["obs"][startDate:endDate].values,dscgDf["ref"][startDate:endDate].values)

#    tStr    = "MSM(39h)\nNashSutcliffe:%.2f\nCorr.Coef:%.2f\nMAE:%2.f" % (NS,cf,mae)
#    tStrRef = "RDR(39h)\nNashSutcliffe:%.2f\nCorr.Coef:%.2f\nMAE:%2.f" % (refNS,refCf,refMae)
#    prop    = dict(boxstyle="round",facecolor="wheat",alpha=0.75)
#    propRef = dict(boxstyle="round",facecolor="#3498DB",alpha=0.75)
#    ax2.text(1-0.15,0.95,tStr,transform=ax2.transAxes,fontsize=20,verticalalignment="top",bbox=prop)
#    ax2.text(1-0.15,0.65,tStrRef,transform=ax2.transAxes,fontsize=20,verticalalignment="top",bbox=propRef)
    

    outPath = os.path.join(outDir,outFile)
#    plt.savefig(outPath,bbox_inches="tight",pad_inches=0.025)
#    plt.show()
#    plt.close()
    

def hyetohydro_nolegend():
#    fig       = plt.figure(figsize=(24.27,15))
    
    ax1     = plt.subplot(2,1,1)
    lat,lon  = uparea()
    mask     = np.ma.masked_less(makeMask(lat,lon),1)
    diff    = (obsEndDate - obsStartDate)
    obsSpan = ((diff.seconds/3600+diff.days*24)+1)/tRes #hour
    obsPrcp = basinPrcp(obsPrcpDir,obsPrcpFile,obsExecStep,obsSpan,obsStartDate,obsEndDate,mask)
    obsPrcp.columns = ["obs"]
    simPrcp = basinPrcpEns(simPrcpDir,simPrcpFile,simExecStep,FT,startDate,endDate,"ctl",mask)
    msmPrcp = basinPrcp(msmPrcpDir,msmPrcpFile,simExecStep,FT,startDate,endDate,mask).rename(columns={0:"msm"})
    for ens in range(1,50+1):
        ens = "%02d" % ens
        ensPrcp = basinPrcpEns(simPrcpDir,simPrcpFile,simExecStep,FT,startDate,endDate,ens,mask)
        simPrcp = pd.concat([simPrcp,ensPrcp],axis=1)
    prcpDf  = pd.concat([obsPrcp,simPrcp,msmPrcp],axis=1)
    ensStd  = simPrcp.std(axis=1)
    ensAvg  = simPrcp.mean(axis=1)
    sigmaB = ensAvg.values - ensStd.values
    sigmaU = ensAvg.values + ensStd.values
    d      = {"avg":ensAvg.values,"sigb":sigmaB,"sigu":sigmaU}
    param  = pd.DataFrame(data=d,index=simPrcp.index)
    prcpDf = pd.concat([prcpDf,param],axis=1)

    tshape  = prcpDf["obs"].shape[0]
    durat   = tshape*tRes
    t       = 0
    cnt     = 0
    tindx   = [] #for date label
    xRange  = [] #for date label
    dummy   = []
    while t < durat:
        if cnt % 2 == 0:
            date = obsStartDate + dt.timedelta(hours=t*tRes)
            tindx.append(date.strftime("%m/%d %H:00"))
        else:
            date = "" #dummy
            tindx.append(date)
        xRange.append(t)
        dummy.append("")
        t = t + tFreq
        cnt = cnt + 1

    obsTRange = []
    [ obsTRange.append( obsStartDate + dt.timedelta(hours=t*tRes)) for i in range(durat) ]
    obsTRange = np.array(obsTRange)
#    simTRange = []
#    [ simTRange.append( startDate + dt.timedelta(hours=t*tRes)) for i in range(FT) ]
#    simTRange=np.array(simTRange)
    plt.plot(prcpDf["obs"].values,color="#283747",linewidth=3,linestyle="--")
#    plt.plot(prcpDf["ctl"].values,color="gray",linewidth=0.25,linestyle="-")
    plt.plot(prcpDf["msm"].values,color="orange",linewidth=1,linestyle="-")
    for ens in range(1,50+1):
        ens = "%02d" % ens
#        plt.plot(prcpDf[ens].values,color="gray",linewidth=0.25,linestyle="-")
    plt.plot(prcpDf["avg"].values,color="#1E8449",linewidth=2,linestyle="-")
    plt.plot(prcpDf["sigb"].values,color="#303F9F",linewidth=0.5,linestyle="-",alpha=0.5)
    plt.plot(prcpDf["sigu"].values,color="#303F9F",linewidth=0.5,linestyle="-",alpha=0.5)
    x = np.arange(0,prcpDf.index.shape[0],1)
    plt.fill_between(x,prcpDf["sigu"].values,prcpDf["sigb"].values,where=np.isfinite(prcpDf["sigu"].values),alpha=0.1,facecolor="#303F9F",linewidth=0)
    plt.xticks(xRange,dummy)
    plt.xlim(0,obsPrcp.shape[0])
    plt.yticks(prcpYticks,fontsize=25)
    plt.ylim(pMax,0)
    plt.ylabel("Precip.[mm/h]",fontsize=30)
    plt.legend(loc="lower left",frameon=True,fontsize=25)
    plt.title(stName,fontsize=40)
    
    #statitical values
#    prcpCC  = corrCoef(obsPrcp["obs"][startDate:endDate].values,simPrcp["sim"][startDate:endDate].values)
#    prcpMAE = MAE(obsPrcp["obs"][startDate:endDate].values,simPrcp["sim"][startDate:endDate].values)
#    volume  = float(simPrcp["sim"][startDate:endDate].values.sum()/obsPrcp["obs"][startDate:endDate].values.sum())

#    tStr = "PRCP(39h)\nCorr.Coef:%.2f\nMAE:%.2f\nVolumeError:%.2f" % (prcpCC,prcpMAE,volume)
#    prop = dict(boxstyle="round",facecolor="wheat",alpha=0.75)
#    ax1.text(1-0.14,0.95,tStr,transform=ax1.transAxes,fontsize=20,verticalalignment="top",bbox=prop)

    ax2       = plt.subplot(2,1,2)
    dscgSim   = discharge(dscgDir,dscgFile,simExecStep,FT,startDate,endDate,"ctl")
    dscgMsm   = discharge(msmDscgDir,dscgFile,simExecStep,FT,startDate,endDate,"msm")
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
    dscgDf    = pd.concat([dscgObs,dscgSim,dscgMsm,dscgRef,param],axis=1)
    
    MAEa = []
    cfa  = []
#    plt.plot(dscgDf["ctl"].values,color="gray",linewidth=0.25)
    plt.plot(dscgDf["msm"].values,color="orange",linewidth=1)
    NS   = pd.DataFrame([nashSutcliffe(dscgDf["obs"][startDate:endDate].values,dscgDf["ctl"][startDate:endDate].values)],columns=["ctl"],index=["NS"])
    mae  = pd.DataFrame([MAE(dscgDf["obs"][startDate:endDate].values,dscgDf["ctl"][startDate:endDate].values)],columns=["ctl"],index=["MAE"])
    maeV = MAE(dscgDf["obs"][startDate:endDate].values,dscgDf["ctl"][startDate:endDate].values)
    print "="*80
    print startDate
    print "mae: ",mae.values
    cf   = pd.DataFrame([corrCoef(dscgDf["obs"][startDate:endDate].values,dscgDf["ctl"][startDate:endDate].values)],columns=["ctl"],index=["cf"])
    cfV  = corrCoef(dscgDf["obs"][startDate:endDate].values,dscgDf["ctl"][startDate:endDate].values)
    MAEa.append(maeV)
    cfa.append(cfV)
    print "corr.coef: ",cf.values
    for ens in range(1,50+1):
        ens  = "%02d" % ens
        nse  = pd.DataFrame([nashSutcliffe(dscgDf["obs"][startDate:endDate].values,dscgDf[ens][startDate:endDate].values)],columns=[ens],index=["NS"])
        NS   = pd.concat([NS,nse],axis=0)
        maee = pd.DataFrame([MAE(dscgDf["obs"][startDate:endDate].values,dscgDf[ens][startDate:endDate].values)],columns=[ens],index=["MAE"])
        maeV = MAE(dscgDf["obs"][startDate:endDate].values,dscgDf[ens][startDate:endDate].values)
        mae  = pd.concat([mae,maee],axis=0)
        cfe  = pd.DataFrame([corrCoef(dscgDf["obs"][startDate:endDate].values,dscgDf[ens][startDate:endDate].values)],columns=[ens],index=["cf"])
        cfV  = corrCoef(dscgDf["obs"][startDate:endDate].values,dscgDf[ens][startDate:endDate].values)
        cf   = pd.concat([cf,cfe],axis=0)
        MAEa.append(maeV)
        cfa.append(cfV)

#        plt.plot(dscgDf[ens].values,color="gray",linewidth=0.25,linestyle="-")

    print "mae median: ", np.median(np.array(MAEa))
    print "cf median: ", np.median(np.array(cfa))

    plt.plot(dscgDf["avg"].values,color="#1E8449",linestyle="-",linewidth=2)
    plt.fill_between(x,dscgDf["sigu"].values,dscgDf["sigb"].values,where=np.isfinite(dscgDf["sigu"].values),alpha=0.1,facecolor="#303F9F",linewidth=0)
    plt.plot(dscgDf["ref"].values,color="#3498DB",linestyle=":",linewidth=3)
    plt.plot(dscgDf["obs"].values,color="#283747",linestyle="--",linewidth=3)
    plt.plot(dscgDf["sigb"].values,color="#303F9F",linestyle="-",linewidth=0.5,alpha=0.5)
    plt.plot(dscgDf["sigu"].values,color="#303F9F",linestyle="-",linewidth=0.5,alpha=0.5)
    plt.ylim(0,dMax)
    plt.xlim(0,obsPrcp.shape[0])
    plt.xticks(xRange,tindx,fontsize=25)
    plt.xticks(rotation=52.5)
    plt.yticks(dscgYticks,fontsize=25)
    plt.ylabel("Discharge [m3/s]",fontsize=30)
    plt.xlabel("Date [UTC]",fontsize=30)
    
#    plt.legend(loc="lower left",frameon=True,fontsize=25)

    # threshold values
    x = np.arange(0,dscgDf["obs"].shape[0],1)
    y = np.ones((dscgDf["obs"].shape[0]))*threshold
    plt.plot(x,y,color="#C0392B",linewidth=1.5,linestyle="-.")

    EXCD   = []
    PEAK   = []

    obsTme = dscgDf["obs"][startDate:floodDate].idxmax(axis=1)

    case   = dscgSim["ctl"][startDate:floodDate].max(axis=1)
    EXCD.append(case)
    time   = dscgSim["ctl"][startDate:floodDate].idxmax(axis=1)
    print "CTL run exceeds?: ", case > threshold
    peak   = (time - obsTme).days*24 + (time - obsTme).seconds/3600
    PEAK.append(peak)

    for ens in range(1,50+1):
        ens = "%02d"%ens
        case   = dscgSim[ens][startDate:floodDate].max(axis=1)
        time   = dscgSim[ens][startDate:floodDate].idxmax(axis=1)
        peak   = (time - obsTme).days*24 + (time - obsTme).seconds/3600
        EXCD.append(case)
        PEAK.append(peak)
    excd = np.array(EXCD)
    peak = np.array(PEAK)

    number = (np.where(excd>threshold)[0]).shape[0]
    frac   = number/51.

    print "Initial time at: %s"%startDate.strftime("%Y/%m/%d %H:00")
    print "exceed number: %d"%number
    print "its fraction: %.2f"%frac
#    print PEAK



    
    # statistical values
#    NS   = nashSutcliffe(dscgDf["obs"][startDate:endDate].values,dscgDf["sim"][startDate:endDate].values)
#    rmse = RMSE(dscgDf["obs"][startDate:endDate].values,dscgDf["sim"][startDate:endDate].values)
#    mae  = MAE(dscgDf["obs"][startDate:endDate].values,dscgDf["sim"][startDate:endDate].values)
#    cf   = corrCoef(dscgDf["obs"][startDate:endDate].values,dscgDf["sim"][startDate:endDate].values)

#    refNS   =  nashSutcliffe(dscgDf["obs"][startDate:endDate].values,dscgDf["ref"][startDate:endDate].values)
#    refRmse = RMSE(dscgDf["obs"][startDate:endDate].values,dscgDf["ref"][startDate:endDate].values)
#    refMae  = MAE(dscgDf["obs"][startDate:endDate].values,dscgDf["ref"][startDate:endDate].values)
#    refCf   = corrCoef(dscgDf["obs"][startDate:endDate].values,dscgDf["ref"][startDate:endDate].values)

#    tStr    = "MSM(39h)\nNashSutcliffe:%.2f\nCorr.Coef:%.2f\nMAE:%2.f" % (NS,cf,mae)
#    tStrRef = "RDR(39h)\nNashSutcliffe:%.2f\nCorr.Coef:%.2f\nMAE:%2.f" % (refNS,refCf,refMae)
#    prop    = dict(boxstyle="round",facecolor="wheat",alpha=0.75)
#    propRef = dict(boxstyle="round",facecolor="#3498DB",alpha=0.75)
#    ax2.text(1-0.15,0.95,tStr,transform=ax2.transAxes,fontsize=20,verticalalignment="top",bbox=prop)
#    ax2.text(1-0.15,0.65,tStrRef,transform=ax2.transAxes,fontsize=20,verticalalignment="top",bbox=propRef)
    

if __name__ == "__main__":
    fig       = plt.figure(figsize=(24.27,15))
    cnt = 0
    for start in ["2015090806","2015090818","2015090906","2015090918"]:
        startDate = dt.datetime.strptime(start,"%Y%m%d%H")
        endDate   = startDate + dt.timedelta(hours=FT-1)
        year      = startDate.year
        mon       = startDate.month
        day       = startDate.day
        hour      = startDate.hour
        outFile      = "hyehyd_ENS_%s_%04d%02d%02d%02d"%(stName,year,mon,day,hour)
        if cnt == 0:
            hyetohydro()
        else:
            hyetohydro_nolegend()
        cnt = cnt + 1
    plt.legend(loc="lower left",frameon=True,fontsize=25)
    outFile = "hyehyd_ALL_2015090806_2015090918_%s" % stName
    outPath = outPath = os.path.join(outDir,outFile)
    plt.savefig(outPath,bbox_inches="tight",pad_inches=0.025)
    plt.show()
