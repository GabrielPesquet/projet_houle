import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as ani

XMAX = 200
YMAX = 200
TMAX = 10.0
NTIMES = 100
OUTPUT = 0
HAUTEURDEAU = 1.0
dt = TMAX / NTIMES
dl = 1.0
g = 9.81

cuves = [
    {"largeur": 0.19, "longueur": 0.39, "hauteur_max": 0.22},
    {"largeur": 0.16, "longueur": 0.79, "hauteur_max": 0.38},
    {"largeur": 0.08, "longueur": 2.0, "hauteur_max": 0.18},
    {"largeur": 0.04, "longueur": 1.0, "hauteur_max": 0.19},
]


def set_to_cuve(i):
    global XMAX, YMAX, dl, HAUTEURDEAU
    dl = cuves[i]["largeur"] / YMAX * 100
    XMAX = int(cuves[i]["longueur"] / cuves[i]["largeur"] * YMAX)
    print(f"X : {XMAX}, Y:{YMAX}")
    HAUTEURDEAU = cuves[i]["hauteur_max"] * 2 / 3  # Arbitraire pour l'instant


set_to_cuve(0)

prof = np.zeros((XMAX, YMAX))
hauteur = np.zeros((XMAX, YMAX))
champ = np.zeros((3, XMAX, YMAX))
pulsation = 1.0


def laplacien(champ, x, y):
    return (
        champ[x + 1, y]
        + champ[x - 1, y]
        + champ[x, (y + 1) % YMAX]
        + champ[x, (y - 1) % YMAX]
        - 4 * champ[x, y]
    ) / dl**2


def calc_c(x, y):
    return np.sqrt(g * prof[x, y])


def init():
    global prof, hauteur
    hauteur.fill(0)
    prof.fill(HAUTEURDEAU)
    # Plan incliné
    prof[XMAX // 3 : XMAX, :] = np.linspace(0.0, HAUTEURDEAU * 0.8, YMAX)

def calcul_courant(x, y):
    c = calc_c(x, y)
    nombre_de_courant = c*dt/dl
    print(f"Courant : {nombre_de_courant}")

def futur_onde(x, y):
    c = calc_c(x, y)
    champ[2, x, y] = (
        (dt * c) ** 2 * laplacien(champ[1], x, y) + 2 * champ[1, x, y] - champ[0, x, y]
    )


def gaussian(x, mu, sigma):
    return np.exp(-0.5 * ((x - mu) / sigma) ** 2)


def bords_onde_gauss(t):
    mu, sigma = YMAX / 2, YMAX * 0.04
    x_gen = XMAX // 6
    champ[2, x_gen, YMAX // 6 : 5 * YMAX // 6] = gaussian(
        np.arange(YMAX // 6, 5 * YMAX // 6), mu, sigma
    ) * np.sin(t * pulsation)


def update_onde(t):
    global champ
    champ = np.roll(champ, shift=-1, axis=0)
    for x in range(1, XMAX - 1):
        for y in range(YMAX):
            futur_onde(x, y)
    bords_onde_gauss(t)
    calcul_courant(int(XMAX/2), int(YMAX/2))




def update_h(t):
    global hauteur
    hauteur.fill(0)
    update_onde(t)
    hauteur[:, :] = champ[1]


def savebin(filename):
    with open(filename, "wb") as f:
        hauteur[:XMAX, :].tofile(f)


vmin = -1.2
vmax = 1.2
sep = ","
cmap = "viridis"  # Coloration, voir https://matplotlib.org/stable/users/explain/colors/colormaps.html


def UpdateState(frame):
    temps = dt * frame
    update_h(temps)
    state.set_data(hauteur)
    print(f"{frame} -> {np.max(hauteur)}")
    return (state,)


if __name__ == "__main__":
    init()
    fig = plt.figure("Affichage", figsize=(7, 7))

    ax1 = fig.add_subplot(111)
    state = ax1.matshow(hauteur, cmap=cmap, vmin=vmin, vmax=vmax)
    ax1.set_xticks([])
    ax1.set_yticks([])

    anim = ani.FuncAnimation(
        fig,
        UpdateState,
        1000,
        interval=0,
        blit=True,
        cache_frame_data=False,
        repeat=False,
    )

    plt.show()
    print(f"Max : {np.max(hauteur)}")
