import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as ani
from time import sleep

XMAX = 200
YMAX = 200
TMAX = 10.0
NTIMES = 1000
OUTPUT = 0
HAUTEURDEAU = .1
dt = TMAX / NTIMES
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
    dt = min(TMAX / NTIMES, dl / np.max(c))  # Condition CFL




prof = np.zeros((XMAX, YMAX))
hauteur = np.zeros((XMAX, YMAX))
champ = np.zeros((3, XMAX, YMAX))


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
    prof[XMAX // 3 : XMAX, :] = np.linspace(0.1, HAUTEURDEAU * 0.2, YMAX)




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
    x_gen = XMAX // 6
    champ[2, x_gen, YMAX // 6 : 5 * YMAX // 6] = gaussian(
        np.arange(YMAX // 6, 5 * YMAX // 6), mu, sigma
    ) * np.sin(t * pulsation) * amplitude

def condition_bord_neumann(): # évite que le signal traverse par le bas
    champ[2, 0, :] = champ[2, 1, :]  # Bord gauche
    champ[2, XMAX-1, :] = champ[2, XMAX-2, :]  # Bord droit
    champ[2, :, 0] = champ[2, :, 1]  # Bord bas
    champ[2, :, YMAX-1] = champ[2, :, YMAX-2]  # Bord haut

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
    bords_onde_gauss(t, HAUTEURDEAU / 5)
    condition_bord_neumann()


def update_h(t):
    global hauteur
    hauteur.fill(0)
    update_onde(t)
    hauteur[:] = champ[1]


def savebin(filename):
    with open(filename, "wb") as f:
        hauteur[:XMAX, :].tofile(f)


vmin = -HAUTEURDEAU/3
vmax = HAUTEURDEAU/3
sep = ","
cmap = "viridis"  # Coloration, voir https://matplotlib.org/stable/users/explain/colors/colormaps.html


def UpdateState(frame):
    #sleep(0.0)
    temps = dt * frame
    update_h(temps)
    state.set_data(hauteur)
    print(f"{frame} -> {np.max(hauteur)}")
    return (state,)


if __name__ == "__main__":
    fig = plt.figure("Affichage", figsize=(7, 7))

    ax1 = fig.add_subplot(111)
    state = ax1.matshow(hauteur, cmap=cmap, vmin=vmin, vmax=vmax)
    ax1.set_xticks([])
    ax1.set_yticks([])

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
