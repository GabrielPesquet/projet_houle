import numpy as np 
import matplotlib.pyplot as plt 
import seaborn as sns 
from matplotlib.animation import FuncAnimation 
from sys import setrecursionlimit

setrecursionlimit(10000)

hdata= np.fromfile("data.bin", dtype=float, count=-1, sep="") 
hdata = hdata.reshape(1000,200, 200)

forme_grille = {'width_ratios': (0.9, 0.04), 'wspace': 0.2}
fig, (ax, cbar_ax) = plt.subplots(1, 2, gridspec_kw= forme_grille, figsize= (12, 12))

m = hdata.min()
M = hdata.max()

def updateheatmap(i):
    ax.cla()
    sns.heatmap(hdata[i,...], 
                ax= ax, 
                cbar= True, 
                cbar_ax= cbar_ax, 
                xticklabels=20,
                yticklabels=20,
                vmin=m,
                vmax=M,
                cmap="Blues_r",)

anim = FuncAnimation(fig = fig, func = updateheatmap, frames = 500, interval = 10, blit = False)
#anim.save("houle.mp4", fps= 10, dpi=200)
plt.show()
