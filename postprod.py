import matplotlib.pyplot as plt
import matplotlib.animation as ani
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import itertools as it
import time

# Informations sur les images à lire 
YMAX = 500# Y
N_Times = 5000
vmin = -1.2
vmax = 1.2
sep = ","
cmap = "viridis"  # Coloration, voir https://matplotlib.org/stable/users/explain/colors/colormaps.html

arr = np.zeros((XMAX, YMAX), dtype=float)

hdata= np.fromfile("data.bin", dtype=float, count=-1, sep="") 
hdata = hdata.reshape(N_Times, XMAX, YMAX)


#vtsx[:, -1,:] = 0.
#vtsy[:,:, -1] = 0.

def contrast(x) : 
    x = x/0.9
    if x > 0 :
        return x**2
    else:
        return -x**2

def vec_contrast(x, seuil) : 
    return np.multiply(np.sign(x), np.square(x*seuil))

def videoplan(save=False, nom="", fps=5, dpi=100, speed=1): 

    def UpdateState(frame):
        arr = hcontrast[frame]
        state.set_data(arr)
    
        #if frame%20==0 :
        #    ax2.clear()  # Clear previous frame
        #    ax2.plot_surface(X, Y, arr, cmap='viridis')
        #    #ax2.plot_surface(X, Y, -prof, cmap='grey')
        #    ax2.set_zlim(-3, 3)
        #    ax2.set_box_aspect([XMAX,YMAX,min(XMAX,YMAX)])
        #    
        #    ax3.clear()
        #    ax3.quiver(X10, Y10, v10x[frame], v10y[frame], scale=.3, scale_units='xy', minlength= 0.01,  color="red")
        #    #ax3.set_box_aspect([XMAX,YMAX,min(XMAX,YMAX)])
    
        #print(f"{frame} -> {np.max(arr)}")
        return (state,)

    hcontrast = hdata #à modifier pour des contrastes plus interessants
    fig = plt.figure("Affichage", figsize=(7, 7))

    ax1 = fig.add_subplot(111)
    state = ax1.matshow(hdata[0], cmap=cmap, vmin=vmin, vmax=vmax)
    ax1.set_xticks([k for k in range(0, XMAX+1, 100)])
    ax1.set_yticks([k for k in range(0, YMAX+1, 100)])

    anim = ani.FuncAnimation(fig, UpdateState, N_Times, interval=0, blit=True, cache_frame_data=False, repeat=False)
    plt.show()
    if save : 
        anim.save(nom+".mp4", fps= 5, dpi=100)

def vue3d(temps):
    fig = plt.figure("Affichage", figsize=(7, 7))

    #ax1 = fig.add_subplot(1,1,1)
    #state = ax1.matshow(hdata[temps], cmap=cmap, vmin=vmin, vmax=vmax)
    #ax1.set_xticks([k for k in range(0, XMAX+1, 100)])
    #ax1.set_yticks([k for k in range(0, YMAX+1, 100)])

    ax2 = fig.add_subplot(1,1,1, projection = '3d')

    X, Y = np.meshgrid(np.arange(XMAX), np.arange(YMAX)) 
    
    prof_min = 0.1 
    prof_max = 4
    prof = np.array([[prof_min + (prof_max - prof_min) * y / (2*YMAX) for y in range(YMAX)] for x in range(XMAX)])

    ax2.plot_surface(X, Y, hdata[temps,::-1,:], cmap='viridis')
    ax2.plot_surface(X, Y, -prof[::-1,:], cmap='grey')
    ax2.set_zlim(-3, 3)
    ax2.set_box_aspect([XMAX,YMAX,min(XMAX,YMAX)])

    plt.show()


def champvitesses(temps):
    fig = plt.figure("Affichage", figsize=(7, 7))
    ax1 = fig.add_subplot(1,2,1)
    state = ax1.matshow(hdata[temps,::-1,], cmap=cmap, vmin=vmin, vmax=vmax)
    ax1.set_xticks([])
    ax1.set_yticks([])
    
    ax2= fig.add_subplot(1,2,2)
    
    X10, Y10 = np.meshgrid(np.arange(XMAX//10), np.arange(YMAX//10)) 
    
    dhx = np.zeros((XMAX, YMAX)) 
    dhy = np.zeros((XMAX, YMAX)) 
    dhx = np.roll(hdata[temps], 1, axis=0) - hdata[temps]
    dhy = np.roll(hdata[temps], 1, axis=1) - hdata[temps]
    dht = 0.5*(hdata[temps+1] - hdata[temps-1])
    
    d10t = dht[::10, ::10]
    d10x = dhx[::10,::10]
    d10x[-1,:] = np.zeros((1, YMAX//10))
    d10y = dhy[::10,::10]

    def v(dhx, dht):
        if abs(dht) < 1e-4 : 
            return 0.
        if abs(dhx)< 1e-4:
            return 0.
        else : return dht/dhx

    vx = -np.array([[v(d10x[i,j], d10t[i,j]) for j in range(YMAX//10)] for i in range(XMAX//10)])
    vy = -np.array([[v(d10y[i,j], d10t[i,j]) for j in range(YMAX//10)] for i in range(XMAX//10)])

    #ax2.quiver(X10, Y10, vx, vy, color='r',scale = 0.4, scale_units='xy', minlength=0.01)
    ax2.streamplot(X10, Y10, vx, vy, color='b', linewidth=None, density=1)

    plt.show()
    
def parcoursmax(deb, fin, lissage=5):
    #maxeta = [np.unravel_index(np.argmax(hdata[t, :, :]), hdata[t,:,:].shape) for t in range(deb, fin)]
    maxeta = np.zeros((fin-deb, 2))
    for t in range(deb, fin) : 
        maxeta[t-deb, 1], maxeta[t-deb, 0] = np.unravel_index(np.argmax(hdata[t, ::-1, :]), hdata[t,::-1,:].shape)

    lisseY = np.convolve(maxeta[:,1], np.ones(lissage), 'valid')[::20]/lissage
    lisseX = np.convolve(maxeta[:,0], np.ones(lissage), 'valid')[::20]/lissage
    
    fig = plt.figure(figsize=(7, 7))
    ax = fig.add_subplot()

    ax.set_xlim(0, XMAX)
    ax.set_ylim(0, YMAX)

    ax.set_xticks([k for k in range(0, XMAX+1, 100)])
    ax.set_yticks([k for k in range(0, YMAX+1, 100)])

    dfit = np.polyfit(lisseX[-30:-15], lisseY[-30:-15], 1)
    print(dfit[0], dfit[1]) 
    
    T = np.linspace(0, XMAX, 1000)

    ax.plot(lisseX, lisseY, '+', linestyle="")
    ax.plot(T, dfit[0]*T + dfit[1]*np.ones(len(T)), linestyle="--")
    ax.plot(np.ones(len(T))*XMAX/2, T, linestyle="--")

    plt.show()

def sismograph(X, Y, tdeb, tfin): 
    fig = plt.figure(figsize=(7, 7))
    ax = fig.add_subplot() 
   
    dt = 1 

    #ax.set_xticks([k*0.2 for k in range(0, 5)])
    #ax.set_yticks([t*dt for t in range(tdeb, tfin, 250)])

    T = np.linspace(tdeb*dt, tfin*dt, tfin-tdeb)
    for i in range(len(X)) : 
        ax.plot(T, hdata[tdeb:tfin,X[i], Y[i]])
    
    plt.show()


#vue3d(30)

if __name__ == "__main__" :
    #videoplan()
    """
    vue3d(100) 
    vue3d(500) 
    vue3d(1000) 
    vue3d(1500) 
    vue3d(2500) 
    vue3d(3000) 
    """

    sismograph([200, 300, 400], [200, 300, 400], 1000, 3000)
