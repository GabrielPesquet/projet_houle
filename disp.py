import matplotlib.pyplot as plt
import matplotlib.animation as ani
import numpy as np
import itertools as it
import time

# Informations sur les images à lire (ici, 200x200 en flottants dans [-1.2, 1.2], séparés par des virgules)
N_Lgn = 500 # X
N_Col = 500 # Y
N_Times = 1000
vmin = -1.2
vmax = 1.2
sep = ","
cmap = "viridis"  # Coloration, voir https://matplotlib.org/stable/users/explain/colors/colormaps.html

arr = np.zeros((N_Lgn, N_Col), dtype=float)

def UpdateState(frame):
    for i in range(N_Lgn):
       arr[i, :] = [float(e) for e in input().split(sep)]
    state.set_data(arr)
    print(f"{frame} -> {np.max(arr)}")
    return (state,)

fig = plt.figure("Affichage", figsize=(7, 7))

ax1 = fig.add_subplot(111)
state = ax1.matshow(arr, cmap=cmap, vmin=vmin, vmax=vmax)
ax1.set_xticks([])
ax1.set_yticks([])

anim = ani.FuncAnimation(fig, UpdateState, 1000, interval=0, blit=True, cache_frame_data=False, repeat=False)

plt.show()
print(f"Max : {np.max(arr)}")
