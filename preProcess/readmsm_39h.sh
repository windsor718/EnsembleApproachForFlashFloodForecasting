#/bin/bash
#
####################################
#for extracting data from GPV_MSM data.
#originaly coded by Kei Yoshimura sensei
#Edited by Yuta Ishitsuka
#LAST EDIT: 2015/11/11
#		edit for 24hours
####################################

#DIR=/export/raid12/gpv
#DIR=~/GPV_jpn/MSMDATA
LEADTIME=39 #set your lead time

YEAR=$1
MON=$2
DAY=$3
TIME=$4

MON=`expr $MON + 0`
DAY=`expr $DAY + 0`
TIME=`expr $TIME + 0`
if [ $MON -lt 10 ]; then
   MON=0$MON
fi
if [ $DAY -lt 10 ] ; then
   DAY=0$DAY
fi
if [ $TIME -lt 10 ] ; then
   TIME=0$TIME
fi

DIR=/data3/yuta/GPV_jpn/MSMDATA
OUTDIR1=/data3/yuta/GPV_jpn/DATA/rawdata
OUTDIR2=/data3/yuta/GPV_jpn/DATA/FT${LEADTIME}/bindata${LEADTIME}/${TIME}/${YEAR}.${MON}
OUTDIR3=/data3/yuta/GPV_jpn/DATA/FT${LEADTIME}/processed_bindata${LEADTIME}/${TIME}/${YEAR}.${MON}  #for processed data later
OUTDIR4=/data3/yuta/GPV_jpn/DATA/FT${LEADTIME}/gtooldata${LEADTIME}/${TIME}/${YEAR}.${MON}/  #for gtooldata later
WGRIB2=/home/yuta/bin/wgrib2

#################################################
#Initialize
#################################################
#Directory making

if [ $DAY -eq 01 ]; then
	if [ -e $OUTDIR2 ]; then
#		rm -r $OUTDIR2
#		mkdir $OUTDIR2
		echo 'directry exists'
	else
		mkdir $OUTDIR2
	fi
fi


if [ $DAY -eq 01 ]; then
        if [ -e $OUTDIR3 ]; then
#                rm -r $OUTDIR3
#                mkdir $OUTDIR3
		echo 'directry exists'

        else
                mkdir $OUTDIR3
        fi
fi


if [ $DAY -eq 01 ]; then
        if [ -e $OUTDIR4 ]; then
#                rm -r $OUTDIR4
#                mkdir $OUTDIR4
                echo 'directry exists'
        else
                mkdir $OUTDIR4
        fi
fi



rm ${OUTDIR2}/apcp_${YEAR}${MON}${DAY}${TIME}.bin
rm ${OUTDIR2}/tcdc_${YEAR}${MON}${DAY}${TIME}.bin
rm ${OUTDIR2}/lcdc_${YEAR}${MON}${DAY}${TIME}.bin
rm ${OUTDIR2}/pres_${YEAR}${MON}${DAY}${TIME}.bin
rm ${OUTDIR2}/vgrd_${YEAR}${MON}${DAY}${TIME}.bin
rm ${OUTDIR2}/ugrd_${YEAR}${MON}${DAY}${TIME}.bin
rm ${OUTDIR2}/tmp_${YEAR}${MON}${DAY}${TIME}.bin
rm ${OUTDIR2}/rh_${YEAR}${MON}${DAY}${TIME}.bin


touch ${OUTDIR2}/apcp_${YEAR}${MON}${DAY}${TIME}.bin
touch ${OUTDIR2}/tcdc_${YEAR}${MON}${DAY}${TIME}.bin
touch ${OUTDIR2}/lcdc_${YEAR}${MON}${DAY}${TIME}.bin
touch ${OUTDIR2}/pres_${YEAR}${MON}${DAY}${TIME}.bin
touch ${OUTDIR2}/vgrd_${YEAR}${MON}${DAY}${TIME}.bin
touch ${OUTDIR2}/ugrd_${YEAR}${MON}${DAY}${TIME}.bin
touch ${OUTDIR2}/tmp_${YEAR}${MON}${DAY}${TIME}.bin
touch ${OUTDIR2}/rh_${YEAR}${MON}${DAY}${TIME}.bin

####################################################
#dataget
####################################################

INFILE=Z__C_RJTD_${YEAR}${MON}${DAY}${TIME}0000_MSM_GPV_Rjp_Lsurf_FH00-15_grib2.bin
INFILE2=Z__C_RJTD_${YEAR}${MON}${DAY}${TIME}0000_MSM_GPV_Rjp_Lsurf_FH16-33_grib2.bin
INFILE3=Z__C_RJTD_${YEAR}${MON}${DAY}${TIME}0000_MSM_GPV_Rjp_Lsurf_FH34-39_grib2.bin

if [ ! -s ./$INFILE ] ; then
wget http://dias.tkl.iis.u-tokyo.ac.jp/gpv/data/${YEAR}${MON}${DAY}/${INFILE} || exit 8
fi
if [ ! -s ./$INFILE2 ] ; then
wget http://dias.tkl.iis.u-tokyo.ac.jp/gpv/data/${YEAR}${MON}${DAY}/${INFILE2} || exit 8
fi
if [ ! -s ./$INFILE3 ] ; then
wget http://dias.tkl.iis.u-tokyo.ac.jp/gpv/data/${YEAR}${MON}${DAY}/${INFILE3} || exit 8
fi


##################################################
#0-15hours
##################################################


#Total Precipitation [kg/m2]#
$WGRIB2 $INFILE -match ":APCP:surface" | $WGRIB2 $INFILE -i -no_header -bin ${OUTDIR1}/apcp_${YEAR}${MON}${DAY}${TIME}_raw.bin

#Totalcloudcover [%]#
$WGRIB2 $INFILE -match ":TCDC:surface" | $WGRIB2 $INFILE -i -no_header -bin ${OUTDIR1}/tcdc_${YEAR}${MON}${DAY}${TIME}_raw.bin

#Lowercloudcover [%]#
$WGRIB2 $INFILE -match ":LCDC:surface" | $WGRIB2 $INFILE -i -no_header -bin ${OUTDIR1}/lcdc_${YEAR}${MON}${DAY}${TIME}_raw.bin

#Pressure [Pa]#
$WGRIB2 $INFILE -match ":PRES:surface" | $WGRIB2 $INFILE -i -no_header -bin ${OUTDIR1}/pres_${YEAR}${MON}${DAY}${TIME}_raw.bin

#V-Component of Wind [m/s]#
$WGRIB2 $INFILE -match ":VGRD:10" | $WGRIB2 $INFILE -i -no_header -bin ${OUTDIR1}/vgrd_${YEAR}${MON}${DAY}${TIME}_raw.bin

#U-Component of Wind [m/s]#
$WGRIB2 $INFILE -match ":UGRD:10" | $WGRIB2 $INFILE -i -no_header -bin ${OUTDIR1}/ugrd_${YEAR}${MON}${DAY}${TIME}_raw.bin

        #Pressure Reduced to MSL [Pa]#
#        $WGRIB2 $INFILE -match ":PRMSL:" | $WGRIB2 $INFILE -i -no_header -bin ${OUTDIR}/prmsl_${YEAR}${MON}${DAY}${TIME}.bin

#Temperature [K]#
$WGRIB2 $INFILE -match ":TMP:1.5" | $WGRIB2 $INFILE -i -no_header -bin ${OUTDIR1}/tmp_${YEAR}${MON}${DAY}${TIME}_raw.bin

#RH Relative Humidity [%]#
$WGRIB2 $INFILE -match ":RH:1.5" | $WGRIB2 $INFILE -i -no_header -bin ${OUTDIR1}/rh_${YEAR}${MON}${DAY}${TIME}_raw.bin


	cat ${OUTDIR1}/apcp_${YEAR}${MON}${DAY}${TIME}_raw.bin >> ${OUTDIR2}/apcp_${YEAR}${MON}${DAY}${TIME}.bin
	cat ${OUTDIR1}/tcdc_${YEAR}${MON}${DAY}${TIME}_raw.bin >> ${OUTDIR2}/tcdc_${YEAR}${MON}${DAY}${TIME}.bin
	cat ${OUTDIR1}/lcdc_${YEAR}${MON}${DAY}${TIME}_raw.bin >> ${OUTDIR2}/lcdc_${YEAR}${MON}${DAY}${TIME}.bin
	cat ${OUTDIR1}/pres_${YEAR}${MON}${DAY}${TIME}_raw.bin >> ${OUTDIR2}/pres_${YEAR}${MON}${DAY}${TIME}.bin
	cat ${OUTDIR1}/vgrd_${YEAR}${MON}${DAY}${TIME}_raw.bin >> ${OUTDIR2}/vgrd_${YEAR}${MON}${DAY}${TIME}.bin
	cat ${OUTDIR1}/ugrd_${YEAR}${MON}${DAY}${TIME}_raw.bin >> ${OUTDIR2}/ugrd_${YEAR}${MON}${DAY}${TIME}.bin
	cat ${OUTDIR1}/tmp_${YEAR}${MON}${DAY}${TIME}_raw.bin >> ${OUTDIR2}/tmp_${YEAR}${MON}${DAY}${TIME}.bin
	cat ${OUTDIR1}/rh_${YEAR}${MON}${DAY}${TIME}_raw.bin >> ${OUTDIR2}/rh_${YEAR}${MON}${DAY}${TIME}.bin

################################################
#15-24hours
################################################

        
#Total Precipitation [kg/m2]#
        
$WGRIB2 $INFILE2 -match ":APCP:surface" | $WGRIB2 $INFILE2 -i -no_header -bin ${OUTDIR1}/apcp_${YEAR}${MON}${DAY}${TIME}_raw2.bin

#Totalcloudcover [%]#
$WGRIB2 $INFILE2 -match ":TCDC:surface" | $WGRIB2 $INFILE2 -i -no_header -bin ${OUTDIR1}/tcdc_${YEAR}${MON}${DAY}${TIME}_raw2.bin

#Lowercloudcover [%]#
$WGRIB2 $INFILE2 -match ":LCDC:surface" | $WGRIB2 $INFILE2 -i -no_header -bin ${OUTDIR1}/lcdc_${YEAR}${MON}${DAY}${TIME}_raw2.bin


#Pressure [Pa]#
$WGRIB2 $INFILE2 -match ":PRES:surface" | $WGRIB2 $INFILE2 -i -no_header -bin ${OUTDIR1}/pres_${YEAR}${MON}${DAY}${TIME}_raw2.bin

#V-Component of Wind [m/s]#
$WGRIB2 $INFILE2 -match ":VGRD:10" | $WGRIB2 $INFILE2 -i -no_header -bin ${OUTDIR1}/vgrd_${YEAR}${MON}${DAY}${TIME}_raw2.bin

#U-Component of Wind [m/s]#
$WGRIB2 $INFILE2 -match ":UGRD:10" | $WGRIB2 $INFILE2 -i -no_header -bin ${OUTDIR1}/ugrd_${YEAR}${MON}${DAY}${TIME}_raw2.bin

#Temperature [K]#
$WGRIB2 $INFILE2 -match ":TMP:1.5" | $WGRIB2 $INFILE2 -i -no_header -bin ${OUTDIR1}/tmp_${YEAR}${MON}${DAY}${TIME}_raw2.bin

#RH Relative Humidity [%]#
$WGRIB2 $INFILE2 -match ":RH:1.5" | $WGRIB2 $INFILE2 -i -no_header -bin ${OUTDIR1}/rh_${YEAR}${MON}${DAY}${TIME}_raw2.bin



        cat ${OUTDIR1}/apcp_${YEAR}${MON}${DAY}${TIME}_raw2.bin >> ${OUTDIR2}/apcp_${YEAR}${MON}${DAY}${TIME}.bin
        cat ${OUTDIR1}/tcdc_${YEAR}${MON}${DAY}${TIME}_raw2.bin >> ${OUTDIR2}/tcdc_${YEAR}${MON}${DAY}${TIME}.bin
        cat ${OUTDIR1}/lcdc_${YEAR}${MON}${DAY}${TIME}_raw2.bin >> ${OUTDIR2}/lcdc_${YEAR}${MON}${DAY}${TIME}.bin
        cat ${OUTDIR1}/pres_${YEAR}${MON}${DAY}${TIME}_raw2.bin >> ${OUTDIR2}/pres_${YEAR}${MON}${DAY}${TIME}.bin
        cat ${OUTDIR1}/vgrd_${YEAR}${MON}${DAY}${TIME}_raw2.bin >> ${OUTDIR2}/vgrd_${YEAR}${MON}${DAY}${TIME}.bin
        cat ${OUTDIR1}/ugrd_${YEAR}${MON}${DAY}${TIME}_raw2.bin >> ${OUTDIR2}/ugrd_${YEAR}${MON}${DAY}${TIME}.bin
        cat ${OUTDIR1}/tmp_${YEAR}${MON}${DAY}${TIME}_raw2.bin >> ${OUTDIR2}/tmp_${YEAR}${MON}${DAY}${TIME}.bin
        cat ${OUTDIR1}/rh_${YEAR}${MON}${DAY}${TIME}_raw2.bin >> ${OUTDIR2}/rh_${YEAR}${MON}${DAY}${TIME}.bin

###############################################
#34-39 hours
###############################################

#Total Precipitation [kg/m2]#

$WGRIB2 $INFILE3 -match ":APCP:surface" | $WGRIB2 $INFILE3 -i -no_header -bin ${OUTDIR1}/apcp_${YEAR}${MON}${DAY}${TIME}_raw3.bin

#Totalcloudcover [%]#
$WGRIB2 $INFILE3 -match ":TCDC:surface" | $WGRIB2 $INFILE3 -i -no_header -bin ${OUTDIR1}/tcdc_${YEAR}${MON}${DAY}${TIME}_raw3.bin

#Lowercloudcover [%]#
$WGRIB2 $INFILE3 -match ":LCDC:surface" | $WGRIB2 $INFILE3 -i -no_header -bin ${OUTDIR1}/lcdc_${YEAR}${MON}${DAY}${TIME}_raw3.bin


#Pressure [Pa]#
$WGRIB2 $INFILE3 -match ":PRES:surface" | $WGRIB2 $INFILE3 -i -no_header -bin ${OUTDIR1}/pres_${YEAR}${MON}${DAY}${TIME}_raw3.bin

#V-Component of Wind [m/s]#
$WGRIB2 $INFILE3 -match ":VGRD:10" | $WGRIB2 $INFILE3 -i -no_header -bin ${OUTDIR1}/vgrd_${YEAR}${MON}${DAY}${TIME}_raw3.bin

#U-Component of Wind [m/s]#
$WGRIB2 $INFILE3 -match ":UGRD:10" | $WGRIB2 $INFILE3 -i -no_header -bin ${OUTDIR1}/ugrd_${YEAR}${MON}${DAY}${TIME}_raw3.bin

#Temperature [K]#
$WGRIB2 $INFILE3 -match ":TMP:1.5" | $WGRIB2 $INFILE3 -i -no_header -bin ${OUTDIR1}/tmp_${YEAR}${MON}${DAY}${TIME}_raw3.bin

#RH Relative Humidity [%]#
$WGRIB2 $INFILE3 -match ":RH:1.5" | $WGRIB2 $INFILE3 -i -no_header -bin ${OUTDIR1}/rh_${YEAR}${MON}${DAY}${TIME}_raw3.bin



        cat ${OUTDIR1}/apcp_${YEAR}${MON}${DAY}${TIME}_raw3.bin >> ${OUTDIR2}/apcp_${YEAR}${MON}${DAY}${TIME}.bin
        cat ${OUTDIR1}/tcdc_${YEAR}${MON}${DAY}${TIME}_raw3.bin >> ${OUTDIR2}/tcdc_${YEAR}${MON}${DAY}${TIME}.bin
        cat ${OUTDIR1}/lcdc_${YEAR}${MON}${DAY}${TIME}_raw3.bin >> ${OUTDIR2}/lcdc_${YEAR}${MON}${DAY}${TIME}.bin
        cat ${OUTDIR1}/pres_${YEAR}${MON}${DAY}${TIME}_raw3.bin >> ${OUTDIR2}/pres_${YEAR}${MON}${DAY}${TIME}.bin
        cat ${OUTDIR1}/vgrd_${YEAR}${MON}${DAY}${TIME}_raw3.bin >> ${OUTDIR2}/vgrd_${YEAR}${MON}${DAY}${TIME}.bin
        cat ${OUTDIR1}/ugrd_${YEAR}${MON}${DAY}${TIME}_raw3.bin >> ${OUTDIR2}/ugrd_${YEAR}${MON}${DAY}${TIME}.bin
        cat ${OUTDIR1}/tmp_${YEAR}${MON}${DAY}${TIME}_raw3.bin >> ${OUTDIR2}/tmp_${YEAR}${MON}${DAY}${TIME}.bin
        cat ${OUTDIR1}/rh_${YEAR}${MON}${DAY}${TIME}_raw3.bin >> ${OUTDIR2}/rh_${YEAR}${MON}${DAY}${TIME}.bin




#############################
#delete raw files
#############################
rm ${OUTDIR1}/apcp_${YEAR}${MON}${DAY}${TIME}_raw3.bin
rm ${OUTDIR1}/tcdc_${YEAR}${MON}${DAY}${TIME}_raw3.bin
rm ${OUTDIR1}/lcdc_${YEAR}${MON}${DAY}${TIME}_raw3.bin
rm ${OUTDIR1}/pres_${YEAR}${MON}${DAY}${TIME}_raw3.bin
rm ${OUTDIR1}/vgrd_${YEAR}${MON}${DAY}${TIME}_raw3.bin
rm ${OUTDIR1}/ugrd_${YEAR}${MON}${DAY}${TIME}_raw3.bin
rm ${OUTDIR1}/tmp_${YEAR}${MON}${DAY}${TIME}_raw3.bin
rm ${OUTDIR1}/rh_${YEAR}${MON}${DAY}${TIME}_raw3.bin
rm ${OUTDIR1}/apcp_${YEAR}${MON}${DAY}${TIME}_raw2.bin
rm ${OUTDIR1}/tcdc_${YEAR}${MON}${DAY}${TIME}_raw2.bin
rm ${OUTDIR1}/lcdc_${YEAR}${MON}${DAY}${TIME}_raw2.bin
rm ${OUTDIR1}/pres_${YEAR}${MON}${DAY}${TIME}_raw2.bin
rm ${OUTDIR1}/vgrd_${YEAR}${MON}${DAY}${TIME}_raw2.bin
rm ${OUTDIR1}/ugrd_${YEAR}${MON}${DAY}${TIME}_raw2.bin 
rm ${OUTDIR1}/tmp_${YEAR}${MON}${DAY}${TIME}_raw2.bin
rm ${OUTDIR1}/rh_${YEAR}${MON}${DAY}${TIME}_raw2.bin
rm ${OUTDIR1}/apcp_${YEAR}${MON}${DAY}${TIME}_raw.bin
rm ${OUTDIR1}/tcdc_${YEAR}${MON}${DAY}${TIME}_raw.bin
rm ${OUTDIR1}/lcdc_${YEAR}${MON}${DAY}${TIME}_raw.bin
rm ${OUTDIR1}/pres_${YEAR}${MON}${DAY}${TIME}_raw.bin
rm ${OUTDIR1}/vgrd_${YEAR}${MON}${DAY}${TIME}_raw.bin
rm ${OUTDIR1}/ugrd_${YEAR}${MON}${DAY}${TIME}_raw.bin
rm ${OUTDIR1}/tmp_${YEAR}${MON}${DAY}${TIME}_raw.bin
rm ${OUTDIR1}/rh_${YEAR}${MON}${DAY}${TIME}_raw.bin






#done






#OUTPUT=${OUTDIR}/${YEAR}${MON}${DAY}${TIME}s.dat

#if [ ! -f $OUTPUT ] ; then
#echo " $WGRIB2 $INPUT1 -i -bin $OUTPUT -order raw -nh < grib2list.surf"
# $WGRIB2 $INPUT1 -i -bin $OUTPUT -order raw -nh < grib2list.surf
#fi
#
#INPUT1=${DIR}/${YEAR}${MON}${DAY}/Z__C_RJTD_${YEAR}${MON}${DAY}${TIME}0000_MSM_GPV_Rjp_L-pall_FH00-15_grib2.bin
#
#OUTPUT=${OUTDIR}/${YEAR}${MON}${DAY}${TIME}p.dat
#if [ ! -f $OUTPUT ] ; then
#echo " $WGRIB2 $INPUT1 -i -bin $OUTPUT -order raw -nh < grib2list.pall"
# $WGRIB2 $INPUT1 -i -bin $OUTPUT -order raw -nh < grib2list.pall
#fi
#m
#exit()




