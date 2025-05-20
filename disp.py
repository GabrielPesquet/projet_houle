import matplotlib.pyplot as plt
import matplotlib.animation as ani
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import itertools as it
import time

# Informations sur les images à lire (ici, 200x200 en flottants dans [-1.2, 1.2], séparés par des virgules)
XMAX = 500# X
YMAX = 500# Y
N_Times = 2000
vmin = -1.2
vmax = 1.2
sep = ","
cmap = "viridis"  # Coloration, voir https://matplotlib.org/stable/users/explain/colors/colormaps.html

arr = np.zeros((XMAX, YMAX), dtype=float)

def contrast(x) : 
    x = x/0.9
    if x > 0 :
        return x**2
    else:
        return -x**2

prof = np.zeros((XMAX, YMAX))

def UpdateState(frame):
    for i in range(XMAX):
       arr[i, :] = [contrast(float(e)) for e in input().split(sep)]
    state.set_data(arr)
    """
    if frame%20==0 :
        ax2.clear()  # Clear previous frame
        ax2.plot_surface(X, Y, arr, cmap='viridis')
        #ax2.plot_surface(X, Y, -prof, cmap='grey')
        ax2.set_zlim(-3, 3)
        ax2.set_box_aspect([XMAX,YMAX,min(XMAX,YMAX)])
    """
    #print(f"{frame} -> {np.max(arr)}")
    return (state,)

fig = plt.figure("Affichage", figsize=(7, 7))

ax1 = fig.add_subplot(111)
state = ax1.matshow(arr, cmap=cmap, vmin=vmin, vmax=vmax)
ax1.set_xticks([])
ax1.set_yticks([])

#ax2 = fig.add_subplot(122, projection='3d')
#X, Y = np.meshgrid(np.arange(XMAX), np.arange(YMAX)) # sus l'ordre des arguments... c'est mieux

anim = ani.FuncAnimation(fig, UpdateState, N_Times, interval=0, blit=True, cache_frame_data=False, repeat=False)

plt.show()
print(f"Max : {np.max(arr)}")
