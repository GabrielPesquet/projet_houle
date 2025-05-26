import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as ani
from time import sleep
from mpl_toolkits.mplot3d import Axes3D

XMAX = 600
YMAX = 400
TMAX = 10.0
NTIMES = 1000
OUTPUT = 0
HAUTEURDEAU = .2
dt = TMAX / NTIMES
STEP = 1 # le pas de downsampling dans l'affichage 3D
dl = 0.02
g = 9.81
pulsation = 5.0


cuves = [
    {"largeur": 0.19, "longueur": 0.39, "hauteur_max": 0.22},
    {"largeur": 0.16, "longueur": 0.79, "hauteur_max": 0.38},
    {"largeur": 0.08, "longueur": 2.0, "hauteur_max": 0.18},
    {"largeur": 0.04, "longueur": 1.0, "hauteur_max": 0.19},
]


def set_to_cuve(i):
    global XMAX, YMAX, dl, HAUTEURDEAU, dt
    dl = cuves[i]["largeur"] / YMAX * 100
    XMAX = int(cuves[i]["longueur"] / cuves[i]["largeur"] * YMAX)
    print(f"X : {XMAX}, Y:{YMAX}")
    HAUTEURDEAU = cuves[i]["hauteur_max"] * 2 / 30  # Arbitraire pour l'instant
    #dt = min(TMAX / NTIMES, dl / np.max(c))  # Condition CFL



def does_deferle(x, y):
    # Condition de déferlement la plus simple : 
    return hauteur[y][x] > 1/7 * prof[y][x]


def laplacien(champ):
    lap = (np.roll(champ, 1, axis=0) + np.roll(champ, -1, axis=0) +
           np.roll(champ, 1, axis=1) + np.roll(champ, -1, axis=1) -
           4 * champ) / dl**2
    return lap


def calc_c(prof):
    return np.sqrt(g * prof)



def init():
    global prof, hauteur
    hauteur.fill(0)
    prof.fill(HAUTEURDEAU)
    # Plan incliné
    prof[:, 0 : XMAX] = np.repeat(np.linspace(HAUTEURDEAU, HAUTEURDEAU * 1, YMAX)[:, np.newaxis], XMAX, axis=1)
    init_test_submerged_breakwater()

def init_test_reflexion():
    global prof
    left = 3 * XMAX//4
    right = left + XMAX//16
    for x in range(left, right) :
        for y in range(YMAX):
            prof[y][x] = HAUTEURDEAU - (x-left)/(right-left) * HAUTEURDEAU * 1

def init_test_submerged_breakwater():
    global prof
    left = 2 * XMAX//4
    right = left + XMAX//5
    mid = (left+right)/2
    for x in range(left, right) :
        for y in range(YMAX):
            prof[y][x] = HAUTEURDEAU - (x-left)*(x-right)/((mid-left)*(mid-right)) * HAUTEURDEAU * 0.8

# set_to_cuve(0)


prof = np.zeros((YMAX, XMAX))
hauteur = np.zeros((YMAX, XMAX))
champ = np.zeros((3, YMAX, XMAX))
points_de_deferlement = np.zeros((YMAX, XMAX))

init()
c = calc_c(prof)
#set_to_cuve(0)
#print(dt)
dt = min(TMAX / NTIMES, dl / np.max(c))
#print(dt)





def calcul_courant(x, y):
    c = calc_c(x, y)
    nombre_de_courant = c*dt/dl
    print(f"Courant : {nombre_de_courant}")

def futur_onde():
    global champ
    champ[2] = (dt * c)**2 * laplacien(champ[1]) + 2 * champ[1] - champ[0]


def gaussian(x, mu, sigma):
    return np.exp(-0.5 * ((x - mu) / sigma) ** 2)


def bords_onde_gauss(t, amplitude):
    mu, sigma = YMAX / 2, YMAX * 0.04
    x_gen = 1
    champ[2, YMAX // 6 : 5 * YMAX // 6, x_gen] = gaussian(
        np.arange(YMAX // 6, 5 * YMAX // 6), mu, sigma
    ) * np.sin(t * pulsation) * amplitude

def condition_bord_neumann(): # évite que le signal traverse par le bas
    champ[2, 0, :] = champ[2, 1, :]  # Bord bas
    champ[2, YMAX-1, :] = champ[2, YMAX-2, :]  # Bord haut
    champ[2, :, 0] = champ[2, :, 1]  # Bord gauche
    champ[2, :, XMAX-1] = champ[2, :, XMAX-2]  # Bord droit

def condition_bord_dirichlet(): # marche pas trop
    champ[1, 0, :] = 0  # Bord gauche
    champ[1, XMAX-1, :] = 0  # Bord droit
    champ[1, :, 0] = 0  # Bord bas
    champ[1, :, YMAX-1] = 0  # Bord haut

def update_onde(t):
    global champ
    assert dt < dl / np.max(c)
    #print(dt, dl/np.max(c))
    champ = np.roll(champ, shift=-1, axis=0)
    futur_onde()
    bords_onde_gauss(t, HAUTEURDEAU / 3) # A /7 on aurait un déferlement à la source...
    condition_bord_neumann()


def update_h(t):
    global hauteur
    hauteur.fill(0)
    update_onde(t)
    hauteur[:] = champ[1]


def savebin(filename):
    with open(filename, "wb") as f:
        hauteur[:XMAX, :].tofile(f)


vmin = -HAUTEURDEAU/5
vmax = HAUTEURDEAU/5
cmap = "viridis"  # Coloration, voir https://matplotlib.org/stable/users/explain/colors/colormaps.html


def UpdateState(frame):
    #sleep(0.0)
    temps = dt * frame
    update_h(temps)
    state.set_data(hauteur)
    if frame%20 == 0 :
        ax2.clear()  # Clear previous frame
        ax2.plot_surface(X[::STEP], Y[::STEP], hauteur[::STEP], cmap='viridis', alpha=0.7)
        ax2.plot_surface(X[::STEP], Y[::STEP], -prof[::STEP], cmap='grey', alpha = 0.6)
        
        ponts_deferl = [(x, y) for x in range(XMAX) for y in range(YMAX) if does_deferle(x, y)]
        if ponts_deferl:
            x_deferl, y_deferl = zip(*ponts_deferl)  # Décompacte en deux listes
        else:
            x_deferl, y_deferl = [], []
        z_deferl = np.array([hauteur[y_deferl[i]][x_deferl[i]] for i in range(len(x_deferl))])
        print(f"Nb déferl : {len(z_deferl)}")
        ax2.scatter(x_deferl, y_deferl, z_deferl, color="black" )
        ax2.set_zlim(-.3, .3)
        ax2.set_box_aspect([XMAX,YMAX,min(XMAX,YMAX)])
        print(f"{frame} -> {np.max(hauteur)}")
    return (state,)


if __name__ == "__main__":
    fig = plt.figure("Affichage", figsize=(20, 10))

    ax1 = fig.add_subplot(121)
    state = ax1.matshow(hauteur, cmap=cmap, vmin=vmin, vmax=vmax, alpha = 0.8)
    # ax1.set_xticks([])
    # ax1.set_yticks([])
    ax1.set_xlabel(f"Abscisse entre 0 et {dl*XMAX}m")
    ax1.set_ylabel(f"Ordonnée entre 0 et {dl*YMAX}m")

    ax2 = fig.add_subplot(122, projection='3d')
    X, Y = np.meshgrid(np.arange(XMAX), np.arange(YMAX)) # sus l'ordre des arguments... c'est mieux
    print(np.shape(X))
    print(np.shape(Y))
    print(np.shape(hauteur))
    surf3D = ax2.plot_surface(X[::STEP], Y[::STEP], hauteur[::STEP], cmap = 'viridis')

    anim = ani.FuncAnimation(
        fig,
        UpdateState,
        NTIMES,
        interval=0,
        blit=True,
        cache_frame_data=False,
        repeat=False,
    )

    plt.show()
    print(f"Max : {np.max(hauteur)}")
