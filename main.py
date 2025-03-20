import numpy as np

XMAXS = 500
XMAXR = 505
YMAX = 500
TMAX = 120.0
NTIMES = 1000
OUTPUT = 0
dt = TMAX / NTIMES
dl = 1
g = 9.81

prof = np.zeros((XMAXR, YMAX))
hauteur = np.zeros((XMAXR, YMAX))
champ = np.zeros((3, XMAXR, YMAX))
pulsation = 1.0

def laplacien(champ, x, y):
    return (champ[x + 1, y] + champ[x - 1, y] + champ[x, (y + 1) % YMAX] + champ[x, (y - 1) % YMAX] - 4 * champ[x, y]) / dl**2

def calc_c(x, y):
    return np.sqrt(g * prof[x, y])

def init():
    global prof, hauteur
    hauteur.fill(0)
    prof.fill(2.0)
    prof[XMAXS//3:XMAXS, :] = np.linspace(0.1, 3.0, YMAX)

def futur_onde(x, y):
    c = calc_c(x, y)
    champ[2, x, y] = (dt * c)**2 * laplacien(champ[1], x, y) + 2 * champ[1, x, y] - champ[0, x, y]

def gaussian(x, mu, sigma):
    return np.exp(-0.5 * ((x - mu) / sigma) ** 2)

def bords_onde_gauss(t):
    mu, sigma = YMAX / 2, YMAX * 0.04
    x_gen = XMAXS // 6
    champ[2, x_gen, YMAX//6:5*YMAX//6] = gaussian(np.arange(YMAX//6, 5*YMAX//6), mu, sigma) * np.sin(t * pulsation)

def update_onde(t):
    global champ
    champ = np.roll(champ, shift=-1, axis=0)
    for x in range(1, XMAXR - 1):
        for y in range(YMAX):
            futur_onde(x, y)
    bords_onde_gauss(t)

def update_h(t):
    global hauteur
    hauteur.fill(0)
    update_onde(t)
    hauteur[:, :] = champ[1]

def savebin(filename):
    with open(filename, "wb") as f:
        hauteur[:XMAXS, :].tofile(f)

def topython():
    for x in range(XMAXS):
        print(",".join(f"{hauteur[x, y]:.2f}" for y in range(YMAX)))

if __name__ == "__main__":
    init()
    temps = 0
    for _ in range(NTIMES):
        update_h(temps)
        if OUTPUT == 0:
            topython()
        elif OUTPUT == 1:
            savebin("data.bin")
        temps += dt
