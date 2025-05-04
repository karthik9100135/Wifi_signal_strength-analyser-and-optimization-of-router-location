import pandas as pd
import numpy as np
from scipy.interpolate import griddata
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def interpolate_rssi(perimeter_path, length, breadth, root=None):
    df = pd.read_csv(perimeter_path)

    x = df['x']
    y = df['y']
    rssi = df['rssi']

    grid_x, grid_y = np.mgrid[0:length:100j, 0:breadth:100j]
    grid_rssi = griddata((x, y), rssi, (grid_x, grid_y), method='cubic')

    fig, ax = plt.subplots(figsize=(6, 4))
    heatmap = ax.imshow(grid_rssi.T, extent=(0, length, 0, breadth),
                        origin='lower', cmap='viridis', alpha=0.8)
    fig.colorbar(heatmap, ax=ax, label='RSSI (dBm)')
    ax.set_title('Wi-Fi Signal Heatmap')
    ax.set_xlabel('Length (m)')
    ax.set_ylabel('Breadth (m)')

    if root:
        for widget in root.winfo_children():
            widget.destroy()
        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
    else:
        plt.show()
