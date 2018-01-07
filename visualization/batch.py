import datetime
import subprocess

"""
batch script to loop a specified code.
"""

start = "2015090806"
end   = "2015090918"
step  = 3

startDate = datetime.datetime.strptime(start,"%Y%m%d%H")
endDate   = datetime.datetime.strptime(end,"%Y%m%d%H")

#for info in ["Sanuki.info.MSM","Ishii.info.MSM","Hirakata.info.MSM"]:
for info in ["Ishii.info","Hirakata.info"]:
#for info in ["Sanuki.info"]:
    print info
    day = startDate
    while day <= endDate:
        print day
        date = day.strftime("%Y%m%d%H")
        subprocess.call(["python", "hydrograph_ENS.py", info, date])
        day = day + datetime.timedelta(hours=step)

