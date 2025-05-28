import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as ani
from time import sleep
from mpl_toolkits.mplot3d import Axes3D
import netCDF4 as nc
from scipy.ndimage import zoom

# Ouvrir le fichier NetCDF
file_path = 'penmarch.nc'
dataset = nc.Dataset(file_path)

# Explorer les variables disponibles
print(dataset.variables.keys())

# Supposons que les variables 'lat', 'lon', et 'elevation' sont présentes
lat = dataset.variables['latitude'][:]
lon = dataset.variables['longitude'][:]
elevation = dataset.variables['elevation'][:]

# lat = zoom(lat, zoom=5, order=2) # interpolation à un ordre pour augmenter les infos de bathymétrie
# lon = zoom(lon, zoom=5, order=2) # interpolation à un ordre pour augmenter les infos de bathymétrie

# Afficher les dimensions des données
print("lat, lon, elevantion shape : ", lat.shape, lon.shape, elevation.shape)

# Tracer un graphique simple de la bathymétrie
plt.figure(figsize=(10, 6))
plt.contourf(lon, lat, elevation, cmap='viridis')
plt.colorbar(label='Profondeur (m)')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('Bathymétrie')
plt.show()


zoom_factor = 5

elevation[np.isnan(elevation)] = 0.  # Replace NaNs with 0
elevation = zoom(elevation, zoom=zoom_factor, order=1) # interpolation à un ordre pour augmenter les infos de bathymétrie

print(elevation)
# Fermer le dataset
dataset.close()

latitude_range = max(lat) - min(lat)
longitude_range = max(lon) - min(lon)


XMAX = 500 # longitude
YMAX = 500
TMAX = 10000.0
NTIMES = 100000
OUTPUT = 0
HAUTEURDEAU = .2 # sensé être inutilisé ici
AMPL = 2. # houle de 2m
dt = TMAX / NTIMES
STEP = 1 # le pas de downsampling dans l'affichage 3D
dl = 2
g = 9.81
pulsation = 2*np.pi/10 # houle avec période de T = 10s

longitude_moyenne = 48 * np.pi / 180 # à la louche
dl = longitude_range / XMAX * np.cos(longitude_moyenne) * 111.32 * 1000 # cf formule
print(f"dl : {dl}")


X = np.arange(0, XMAX)
Y = np.arange(0, YMAX)


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
    for x in range(XMAX):
        for y in range(YMAX):
            #print(prof[y][x])
            assert prof[y][x] < 1000
    return np.sqrt(g * abs(prof)) # WARNING au abs



def init():
    global prof, hauteur
    hauteur.fill(0)
    prof.fill(0)
    # Plan incliné
    init_brest()


def init_brest():
    global prof
    for x in range(XMAX): 
        for y in range(YMAX):
            prof[y][x] = - elevation[y][x]
            if np.isnan(prof[y][x]):
                prof[y][x] = -12
            print("", end="")
    

# set_to_cuve(0)


prof = np.zeros((YMAX, XMAX))
print(prof.shape)
hauteur = np.zeros((YMAX, XMAX))
champ = np.zeros((3, YMAX, XMAX))
points_de_deferlement = np.zeros((YMAX, XMAX))

init()
c = calc_c(prof)
#set_to_cuve(0)
#print(dt)
dt = min(TMAX / NTIMES, dl / np.max(c) * 0.6) # nombre de courant minimal qu'on impose : 0.6
#print(dt)



def calc_H_sur_lambd(): 
    H = prof
    T = 2*np.pi / pulsation
    lambd = T * c
    return H / lambd

def calcul_courant(x, y):
    c = calc_c(x, y) # probablement pas nécessaire
    nombre_de_courant = c*dt/dl
    print(f"Courant : {nombre_de_courant}")

def futur_onde():
    global champ
    champ[2] = (dt * c)**2 * laplacien(champ[1]) + 2 * champ[1] - champ[0]


def gaussian(x, mu, sigma):
    return np.exp(-0.5 * ((x - mu) / sigma) ** 2)


def bords_onde_gauss(t, amplitude):
    mu, sigma = YMAX / 2, YMAX * 0.1 # On élargit beaucoup pour Brest !
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
    if not dt<dl/np.max(c) :
        print(f"Problème de courant : dt : {dt}, quot : {dl/np.max(c)}, dl : {dl}, c max : {np.max(c)}")
        assert False
    #print(dt, dl/np.max(c))
    champ = np.roll(champ, shift=-1, axis=0)
    futur_onde()
    bords_onde_gauss(t, AMPL) # 2m de houle pour Brest !
    condition_bord_neumann()


def update_h(t):
    global hauteur
    hauteur.fill(0)
    update_onde(t)
    attenuation = 0
    points_deferl_mask = (champ[1] > prof*1/7)
    
    num_deferl_mask_points = np.sum(points_deferl == True)
    print("Number of déferl points masqués :", num_deferl_mask_points)
    champ[1] = champ[1] * (1 - points_deferl_mask + points_deferl_mask * attenuation)
    hauteur[:] = champ[1]


def savebin(filename):
    with open(filename, "wb") as f:
        hauteur[:XMAX, :].tofile(f)


vmin = -AMPL # hauteur pour la 2d
vmax = AMPL # dans tous les cas, ça correspond au déferlement
cmap = "viridis"  # Coloration, voir https://matplotlib.org/stable/users/explain/colors/colormaps.html


points_terre = (prof <= 0).astype(float) # Numpy boolean masking
H_lambd = calc_H_sur_lambd()
print(H_lambd)

print("Points terre shape : ", points_terre.shape)

valeurs = H_lambd.flatten()

# # Création de l'histogramme
# plt.hist(valeurs, bins=30, edgecolor='black', alpha=0.7)

# # Ajout de labels
# plt.xlabel("Valeurs de la matrice")
# plt.ylabel("Fréquence")
# plt.title("Histogramme des H / lambda, supposés << 1 (basse profondeur)")

# plt.show()

# print(f"x_terre.len : {len(count)}")


def UpdateState(frame):
    #sleep(0.0)
    global hauteur
    temps = dt * frame
    update_h(temps)
    state.set_data(hauteur)
    points_deferl = (abs(hauteur) > 1/7 * abs(prof)).astype(float) # Numpy boolean masking
    
    # if frame%2==0: 
    #     points_deferl = np.ones_like(hauteur)

    state_deferl.set_data(points_deferl)
    
    num_deferl_points = np.sum(points_deferl == 1.0)
    print("Number of déferl points:", num_deferl_points)
    #ax1.imshow(points_terre, cmap="Greens")


    # if frame%1000 == 0 :
    #     ax2.clear()  # Clear previous frame
    #     ax2.plot_surface(X[::STEP], Y[::STEP], hauteur[::STEP], cmap='viridis', alpha=0.7)
    #     ax2.plot_surface(X[::STEP], Y[::STEP], -prof[::STEP], cmap='grey')
    #     ponts_deferl = [(x, y) for x in range(XMAX) for y in range(YMAX) if does_deferle(x, y)]
    #     if ponts_deferl:
    #         x_deferl, y_deferl = zip(*ponts_deferl)  # Décompacte en deux listes
    #     else:
    #         x_deferl, y_deferl = [], []
    #     z_deferl = [prof[y_deferl[i]][x_deferl[i]] for i in range(len(x_deferl))]
    #     ax2.scatter(x_deferl, y_deferl, z_deferl, color="red" )
    #     ax2.set_zlim(-200, 200)
    #     ax2.set_box_aspect([XMAX,YMAX,min(XMAX,YMAX)])
    #     print(f"{frame} -> {np.max(hauteur)}")
    return (state, state_deferl)


if __name__ == "__main__":
    fig = plt.figure("Affichage", figsize=(20, 10))

    ax1 = fig.add_subplot(121)
    ax1.imshow(points_terre, cmap="Greens")
    state = ax1.matshow(hauteur, cmap=cmap, vmin=vmin, vmax=vmax, alpha = 0.5)
    points_deferl = (abs(hauteur) > 1/7 * abs(prof)).astype(float) # Numpy boolean masking
    state_deferl = ax1.matshow(points_deferl, cmap="grey", alpha = 0.7, vmin=0., vmax=1.)

    ax1.invert_yaxis()
    # ax1.set_xticks([])
    # ax1.set_yticks([])
    ax1.set_xlabel(f"Abscisse entre 0 et {dl*XMAX}m")
    ax1.set_ylabel(f"Ordonnée entre 0 et {dl*YMAX}m")

    
    # ax3 = fig.add_subplot(221)
    # ax1.imshow(points_terre, cmap="Greens")

    ax2 = fig.add_subplot(122, projection='3d')
    X_meshed, Y_meshed= np.meshgrid(X, Y) # sus l'ordre des arguments... c'est mieux
    print("X, Y, hauteur_meshed shape : ")
    print(np.shape(X))
    print(np.shape(Y))
    print(np.shape(X_meshed))
    print(np.shape(Y_meshed))
    print(np.shape(hauteur))
    surf3D = ax2.plot_surface(X_meshed, Y_meshed, hauteur, cmap = 'viridis')

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
