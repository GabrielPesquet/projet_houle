import numpy as np 
import matplotlib.pyplot as plt 

hdata = np.fromfile("data.bin", dtype=float, count=-1, sep="")
hdata = hdata.reshape(1000, 200, 200)

xsis1, ysis1 = 0, 180
xsis2, ysis2 = 0, 100

hsis1 = hdata[:,xsis1, ysis1]
hsis2 = hdata[:,xsis2, ysis2]
fig, ax = plt.subplots(1, 2, figsize=(20, 10))

T = np.linspace(0, 120, 1000)

ax[0].plot(T, hsis1)
ax[1].plot(T, hsis2)

plt.show()
