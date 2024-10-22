import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Create a figure and axis
fig, ax = plt.subplots()

# Set up a line object which will be updated in the animation
xdata, ydata = [], []
line, = ax.plot([], [], lw=2)

# Set axis limits
ax.set_xlim(0, 2 * np.pi)
ax.set_ylim(-1, 1)

# Initialization function: plot the background of each frame
def init():
    line.set_data([], [])
    return line,

# Animation function: this is called sequentially to update the frame
def update(frame):
    xdata.append(frame)
    ydata.append(np.sin(frame))
    line.set_data(xdata, ydata)
    return line,

# Create the animation object
ani = FuncAnimation(fig, update, frames=np.linspace(0, 2 * np.pi, 128),
                    init_func=init, blit=True)

# Show the animation
plt.show()