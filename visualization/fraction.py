import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime

"""
visualize the time series of flooded members.
"""
sns.set_style("whitegrid")
sns.set_context("paper")


ishii = [32,40,50,51]
hirakata = [36,46,51,51]

sDate = datetime.datetime(2015,9,8,6)
date = []
[ date.append((sDate + datetime.timedelta(hours=12*d)).strftime("%Y/%m/%d %H:00")) for d in range(0,4)]

x = np.array([0,3,6,9])
plt.figure(figsize=(11,11))
plt.bar(x-0.5,ishii,align="center",color="#2E86C1",label="Ishii",width=1,alpha=0.75)
plt.bar(x+0.5,hirakata,align="center",color="#E74C3C",label="Hirakata",width=1,alpha=0.75)
plt.ylim(0,51.5)
plt.xticks(x,date,rotation=20,fontsize=17.5)
plt.ylabel("Number of flooded members",fontsize=20)
plt.yticks(fontsize=15)
plt.xlabel("Date (UTC)",fontsize=20)
plt.legend(fontsize=15,frameon=True)
plt.subplots_adjust(bottom=0.2)
plt.savefig("./floodMembers",bbox_anchor="tight",bbox_inches=0)
plt.show()
