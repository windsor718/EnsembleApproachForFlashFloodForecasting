#!/usr/bin/python
###########################################
#for calculating Long wave down and short wave down
#Reference:http://meteocrop.dc.affrc.go.jp/real/pdf/new_dat_info.pdf
#Reference:meteorology in water environment, Junsei Kondo
#Author:Yuta Ishitsuka
###########################################


from pylab import *
import sys

FT=39

YEAR=int(sys.argv[1])
MON=int(sys.argv[2])
DAY=int(sys.argv[3])
TIME=int(sys.argv[4])

if MON<10:
	mon='0'+str(MON)
else:
	mon=MON
if DAY<10:
	day='0'+str(DAY)
else:
	day=DAY
if TIME<10:
	time='0'+str(TIME)
else:
	time=TIME
print mon

#MONTH=[31,28,31,30,31,30,31,31,30,31,30,31]

DATADIR='/data3/yuta/GPV_jpn/DATA/FT'+str(FT)+'/processed_bindata'+str(FT)+'/'+str(time)+'/'+str(YEAR)+'.'+str(mon)+'/'
OUTDIR='/data3/yuta/GPV_jpn/DATA/FT'+str(FT)+'/processed_bindata'+str(FT)+'/'+str(time)+'/'+str(YEAR)+'.'+str(mon)+'/'

#SWD=[]
SWDA=[]
#SSRD=[]
#LWD=[]
LWDA=[]
#SLRD=[]

#################################
#parametars
#################################
I=1365 #Wm-2
SB=5.67*10**(-8)
pi=3.141593
beta=0.1
albd=0.2
count=0		#count dummy
count2=0
################################
#openfiles
################################
PRES=fromfile(DATADIR+'pres_'+str(YEAR)+str(mon)+str(day)+str(time)+'.bin','float32').reshape(FT,440,500)
TMP=fromfile(DATADIR+'tmp_'+str(YEAR)+str(mon)+str(day)+str(time)+'.bin','float32').reshape(FT,440,500)
RH=fromfile(DATADIR+'rh_'+str(YEAR)+str(mon)+str(day)+str(time)+'.bin','float32').reshape(FT,440,500)
LCDC=fromfile(DATADIR+'lcdc_'+str(YEAR)+str(mon)+str(day)+str(time)+'.bin','float32').reshape(FT,440,500) #warning!
TCDC=fromfile(DATADIR+'tcdc_'+str(YEAR)+str(mon)+str(day)+str(time)+'.bin','float32').reshape(FT,440,500) #warning!


##############################
#1.calculate the amount of horizontal solar radiation at upper edge of atmosphre
##############################
#DOY=sum(MONTH[0:int(MON)-1])+DAY
DOY=30.36*(int(mon)-1)+DAY
ita=(2*pi/365)*DOY
alpha=4.871+ita+0.033*sin(ita)
delta=math.asin(0.398*sin(alpha))
d_d=1.00011+0.034221*cos(ita)+0.00128*sin(ita)+0.000719*cos(2*ita)+0.000077*sin(2*ita)

for l in range(0,440):
	SWD=[]
	LWD=[]
	for lon in range(0,500):
################################
#1-sub calculate precipitable water and the effective amount of water vapor
################################

###################################
#1.1Calculate the daily mean
##################################
                sum1=0
                sum2=0
                sum3=0
                sum4=0
                sum5=0
                for hour in range(0,FT):
                        data1=PRES[hour,l,lon]
                        sum1=sum1+data1
                        data2=TMP[hour,l,lon]
                        sum2=sum2+data2
                        data3=RH[hour,l,lon]
                        sum3=sum3+data3
                        data4=LCDC[hour,l,lon]
                        sum4=sum4+data4
                        data5=TCDC[hour,l,lon]
                        sum5=sum5+data5

                pres=sum1/FT
                tmp=sum2/FT
                rh=sum3/FT
                lcdc=sum4/FT
                tcdc=sum5/FT

		E=6.11*10**(7.5*(tmp-273.15)/(237.3-273.15+tmp)) 
		 
		Ep=E*rh
		
		Tdew=(237.3*math.log(Ep/6.108,10))/(7.5-math.log(Ep/6.108,10))
		logpw=0.0312*Tdew-0.0963
		logtop=0.0315*Tdew-0.1836


		
		lat=(22.425+(0.05*l))*(pi/180) #check
		#if (-tan(lat)*tan(delta))>1:
		#	h=0			#check
		#elif (-tan(lat)*tan(delta))<-1:
		#	h=pi			#check
		#else:
		h=math.acos(-tan(lat)*tan(delta))
			
		Sd=(I/pi)*d_d*(h*sin(lat)*sin(delta)+sin(h)*cos(lat)*cos(delta))
##############################
#2.calculate global solar radiation
##############################
		latdel=lat-delta
		hlfpi=pi/2
			
		if latdel<hlfpi:
#			print 'ok'
#			mn=(pres[hour,l,lon]/1013)*(1/cos(latdel))
			mn=1/cos(latdel)
#			k3=1.402-0.06*math.log(beta+0.02,10)-0.1*((mn-0.91)**(1.0/2.0))
			kk=1.402-0.06*math.log(beta+0.02,10)-0.1*((mn-0.91)**(0.5))
			md=mn*kk*(pres/1013)
		else:
			print 'no'
			mn=1000000000000000000000 #infinite
			k3=1.402-0.06*math.log(beta+0.02,10)-0.1*(mn-0.91)**(0.5)
			md=k3*mn #check 10000
			count2=count2+1
				
		j=(0.066+0.34*(beta)**(0.5))*(albd-0.15)
		i=0.014*(md+7+2*logpw)*logpw
		F1=0.056+0.16*(beta)**(0.5)
		if beta<=0.3:
			C=0.21-0.2*beta
		else:
			C=0.15

		Sdf=Sd*(C+(0.7*10**(-md*F1)))*(1-i)*(1+j) #sunny day

		x=tcdc-0.4*math.exp(-3*lcdc)
		if tcdc>=0.3:
			y=1.70*math.log((1.22-1.02*x),10)+0.521*x+0.846
		else:
			y=1
		
		swd=y*Sdf

		if swd != swd:
                        print 'OMG!'
                        print str(hour)+' '+str(l)+' '+str(lon)
			print kk
			print 1.402-0.06*math.log(beta+0.02,10)- 0.1*((mn-0.91)**(1/2))
			print md
			print 'CHECK!'
#		print swd
		if lon == 0:
			SWD.append(swd)
#			print array(SWD[0]).shape
		else:
			SWD[0]=c_[array(SWD[0]),swd]
#		print array(SWD[0]).shape



#		if lon == 220:
#			 print 'E='+str(E)
#			 print 'Ep='+str(Ep)
#			 print 'logpw='+str(logpw)
#			 print 'pw='+str(e**logpw)
#			 print 'Sdf='+str(Sdf)
#			 print 'swd='+str(swd)			
#############################
#3.calculate Long wave down
#############################
		B=swd/Sdf
			
		if B>=0.0323:
			LC=(0.03*B**(3))-(0.30*B**(2))+1.25*B-0.04 #cloud parametar
		else:
			LC=0
		Ldf_sT4=0.74+0.19*logtop+0.07*(logtop**(2))
		Ld=SB*(tmp**(4))*(1-LC*(1-Ldf_sT4)) 
		
		if lon == 0:
			LWD.append(Ld)
		else:
			LWD[0]=c_[array(LWD[0]),Ld]
		
		count=count+1
#	print 'SWD'
#	print array(SWD[0]).shape
#	print 'LWD'
#	print array(LWD[0]).shape

##############################
#Write data
##############################
	
	if l == 0:
		SWDA.append(array(SWD[0]))
		LWDA.append(array(LWD[0]))
	else:
		SWDA[0]=concatenate((array(SWDA[0]),array(SWD[0])),axis=0)
		LWDA[0]=concatenate((array(LWDA[0]),array(LWD[0])),axis=0)
#		print 'SWDA'
#		print array(SWDA[0]).shape
#		print 'LWDA'
#		print array(LWDA[0]).shape
#		print '===================='
#	print SWDA
#print '============================================================================================='
#SSRD.append(array(SWDA[0]))
#SLRD.append(array(LWDA[0]))
#print 'SSRD'
#print array(SSRD).shape
#print 'SLRD'
#print array(SLRD).shape	
#print '==================='
#			print str(24*440*500-count)+"roops left. move to next roop."
#print "LAST ROOP"


#SWD=array(SWD,'float32').reshape(24,440,500)
#LWD=array(LWD,'float32').reshape(24,440,500)

#imshow(SWD[3])
#imshow(LWD[6])

SWDAf=array(SWDA).flatten()
LWDAf=array(LWDA).flatten()

SWDAf.astype('float32').tofile(OUTDIR+'swd_'+str(YEAR)+str(mon)+str(day)+str(time)+'.bin')
LWDAf.astype('float32').tofile(OUTDIR+'lwd_'+str(YEAR)+str(mon)+str(day)+str(time)+'.bin')

print count2
print "done!plz check results."

#end

