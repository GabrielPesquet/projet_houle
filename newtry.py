import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as ani
from numba import njit  # Accélération des calculs avec numba

XMAX = 200
YMAX = 200
TMAX = 10.0
NTIMES = 10000
OUTPUT = 0
HAUTEURDEAU = 0.1
dt = TMAX / NTIMES
dl = 0.001
g = 9.81
pulsation = 1.0

cuves = [
    {"largeur": 0.19, "longueur": 0.39, "hauteur_max": 0.22},
    {"largeur": 0.16, "longueur": 0.79, "hauteur_max": 0.38},
    {"largeur": 0.08, "longueur": 2.0, "hauteur_max": 0.18},
    {"largeur": 0.04, "longueur": 1.0, "hauteur_max": 0.19},
]

def set_to_cuve(i):
    """ Ajuste les paramètres en fonction de la cuve sélectionnée. """
    global XMAX, YMAX, dl, HAUTEURDEAU, dt
    dl = cuves[i]["largeur"] / YMAX * 100
    XMAX = int(cuves[i]["longueur"] / cuves[i]["largeur"] * YMAX)
    HAUTEURDEAU = cuves[i]["hauteur_max"] * 2 / 30  # Facteur arbitraire
    dt = min(TMAX / NTIMES, dl / np.max(c))  # Vérification CFL

# Initialisation des tableaux
prof = np.full((XMAX, YMAX), HAUTEURDEAU)  # Hauteur d'eau uniforme
champ_old = np.zeros((XMAX, YMAX))  # État précédent
champ_new = np.zeros((XMAX, YMAX))  # État actuel

@njit(fastmath=True)
def laplacien(champ):
    """ Calcul du laplacien sans utiliser np.roll """
    lap = np.zeros_like(champ)

    for i in range(1, champ.shape[0] - 1):
        for j in range(1, champ.shape[1] - 1):
            lap[i, j] = (
                champ[i + 1, j] + champ[i - 1, j] +
                champ[i, j + 1] + champ[i, j - 1] -
                4 * champ[i, j]
            ) / dl**2

    return lap


def calc_c(prof):
    """ Calcule la célérité de l'onde """
    return np.sqrt(g * prof)

c = calc_c(prof)

# Vérification CFL
assert dt < dl / np.max(c), "Condition CFL non respectée ! Réduisez dt ou augmentez dl."

@njit(fastmath=True)
def futur_onde(champ_new, champ_old, c, dt):
    """ Mise à jour optimisée de l'onde en utilisant un schéma explicite """
    lap = laplacien(champ_old)
    champ_new[:, :] = (dt * c) ** 2 * lap + 2 * champ_old - champ_new

def gaussian(x, mu, sigma):
    """ Fonction gaussienne pour la génération d'onde """
    return np.exp(-0.5 * ((x - mu) / sigma) ** 2)

def bords_onde_gauss(champ_new, t, amplitude):
    """ Injecte une onde gaussienne aux bords """
    mu, sigma = YMAX / 2, YMAX * 0.04
    x_gen = XMAX // 6
    champ_new[x_gen, YMAX // 6 : 5 * YMAX // 6] += (
        gaussian(np.arange(YMAX // 6, 5 * YMAX // 6), mu, sigma)
        * np.sin(t * pulsation) * amplitude
    )

def update_onde(t):
    """ Mise à jour complète de l'onde """
    global champ_old, champ_new
    futur_onde(champ_new, champ_old, c, dt)
    bords_onde_gauss(champ_new, t, HAUTEURDEAU / 100)
    champ_old, champ_new = champ_new, champ_old  # Échange des buffers

def savebin(filename):
    """ Sauvegarde des données binaires """
    with open(filename, "wb") as f:
        champ_old[:XMAX, :].tofile(f)

# Paramètres d'affichage
vmin, vmax = -1.2, 1.2
cmap = "viridis"

def UpdateState(frame):
    """ Fonction d'animation """
    temps = dt * frame
    update_onde(temps)
    state.set_data(champ_old)
    return (state,)

if __name__ == "__main__":
    fig = plt.figure("Affichage", figsize=(7, 7))
    ax1 = fig.add_subplot(111)
    state = ax1.matshow(champ_old, cmap=cmap, vmin=vmin, vmax=vmax)
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
