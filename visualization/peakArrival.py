import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime

"""
visualize the difference of peak arrival time.
those difference values are derived from hydrograph_ALL.py
"""

sns.set_style("whitegrid")

ensAt090806 = [-5, -7, -7, 0, -1, -2, 0, -3, 0, -16, 0, -1, -10, -1, -7, -11, -7, 0, -7, -7, -6, -7, -10, -1, -14, -12, 0, -8, -6, -6, -12, -6, -3, -1, -7, 0, 0, -13, -9, 0, 0, -8, -11, -7, -8, -7, -11, 0, -1, -12, 0]

ensAt090818 = [-7, -9, -2, -10, 1, -6, -13, -11, -7, 1, -3, 1, -2, -7, -8, 1, -8, -1, -11, 0, 1, -10, 1, -1, -8, 1, -7, 0, 1, -1, -3, 1, -1, -2, -2, -6, 1, -7, -8, -7, -1, -7, -8, -9, -13, -8, -10, -1, -8, -1, 0]

ensAt090906 = [-7, -8, -7, -7, -8, -7, -8, -8, -7, -8, -7, -7, -3, -7, -7, -6, -8, -7, -8, -8, -6, -7, -7, -8, -7, -6, -8, -7, -9, -7, -8, -5, -7, -7, -7, -8, -7, -7, -7, -8, -8, -7, -8, -8, -7, -7, -7, -8, -7, -8, -7]

ensAt090918 = [1, 1, 1, -1, -2, -1, -1, 1, 1, 1, 1, -1, 1, -1, 1, 1, -2, -1, 1, 1, -2, -2, 1, 1, 1, 1, -1, -2, -1, 1, -1, -2, 1, -2, 1, 1, -1, 1, -2, -2, 1, 1, 1, -1, 1, -1, 1, 1, 1, 1, -2]


FT = [36,33,30,27,24,21,18,15,12,9,6,3,0]
tc = ["36","33","30","27","24","21","18","15","12","09","06","03","00"] 
MSM = [-9,3,5,-2,2,-2,-1,-8,-9,-9,1,-4,-2]

sDate = datetime.datetime(2015,9,8,6)
date = []
[ date.append((sDate + datetime.timedelta(hours=12*d)).strftime("%Y/%m/%d %H:00")) for d in range(0,4)]
print date

def constDataFrame(d,FT,dName):
    df = pd.DataFrame(d,index=FT,columns=[dName])
    return df

def Ens():
    FT = [36,24,12,0]
    for i in range(0,50+1):
        ens = "%02d" % i
        d = [ensAt090806[i],ensAt090818[i],ensAt090906[i],ensAt090918[i]]
        df = constDataFrame(d,FT,str(ens))
        if i == 0:
            DF = df
        else:
            DF = pd.concat([DF,df],axis=1)

    return DF

def Msm():
    d  = MSM
    DF = constDataFrame(d,FT,"MSM")
    return DF

def main():

    ENS = Ens()
    MSM = Msm()

    data = pd.concat([MSM,ENS],axis=1).sort_index(ascending=False)
    Min  = np.array([min(ensAt090806),min(ensAt090818),min(ensAt090906),min(ensAt090918)])
    Max  = np.array([max(ensAt090806),max(ensAt090818),max(ensAt090906),max(ensAt090918)])
    print Min,Max
    lx   = np.array([0,4,8,12])

    ens = np.ones((51,len(FT)))
    for i in range(0,50+1):
        e = "%02d" % i
        ens[i] = data[e].values


    fig = plt.figure(figsize=(14,14))

    xd = np.arange(-5,15,1)
    y=xd*0
    plt.plot(xd,y,linewidth=2,color="gray")
    plt.plot(lx,Min,linewidth=2,color="k",alpha=0.75)
    plt.plot(lx,Max,linewidth=2,color="k",alpha=0.75)

    x = np.arange(0,13,1)
    
    bplot = plt.boxplot(ens,positions=x,notch=False,sym="+",patch_artist=True)
    for i in bplot["boxes"]:
        i.set(facecolor="#303F9F",alpha=0.5)
    for i in bplot["medians"]:
        plt.setp(i,color="#A93226",linewidth=2)
    for i in bplot["caps"]:
        plt.setp(i,linewidth=2,color="#17202A")
    for i in bplot["whiskers"]:
        plt.setp(i,linewidth=2,color="#17202A")
    
    bp, = plt.plot([1,1],color="#303F9F",linewidth=10,alpha=0.5)
#    plt.scatter(x,data["MSM"].values,edgecolors="k",linewidth=1,c="#E67E22",s=300,alpha=0.5,label="MSM")
    plt.legend(frameon=True,fontsize=20)
    plt.xticks(lx,date,fontsize=20,rotation=20)
    plt.yticks(fontsize=20)
    plt.ylim(-17,17)
    plt.yticks([-15,-12,-9,-6,-3,0,3,6,9,12,15])
    plt.xlabel("Date (UTC)",fontsize=25)
    plt.ylabel("Diff. of peak arrival time\n(sim.-obs.) [h]",fontsize=25)
    bp.set_visible(False)
    plt.figtext(0.025,0.185,"early",fontsize=20)
    plt.figtext(0.030,0.875,"late",fontsize=20)
#    plt.title("Difference of Peak Arrival Time\n( Sim.- Obs. ) [h]",fontsize=30)
    plt.subplots_adjust(bottom=0.2)
    plt.savefig("./figure/peakArrival",bbox_anchor="tight",bbox_inches=0)
    plt.show()

if __name__ == "__main__":
    main()
    
