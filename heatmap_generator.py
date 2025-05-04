import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from scipy.ndimage import gaussian_filter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def generate_heatmap(csv_path, length=6, breadth=4, root=None, router_coords=None, user_coords=None, return_fig=False):
    df = pd.read_csv(csv_path)
    
    if not all(col in df.columns for col in ["x", "y", "rssi"]):
        raise ValueError("CSV must have columns: x, y, rssi")

    x, y, rssi = df["x"], df["y"], df["rssi"]

    # Increase resolution
    grid_x, grid_y = np.mgrid[0:length:200j, 0:breadth:200j]
    grid_rssi = griddata((x, y), rssi, (grid_x, grid_y), method='cubic')

    # Apply smoothing and clipping
    grid_rssi = gaussian_filter(grid_rssi, sigma=1.2)
    grid_rssi = np.clip(grid_rssi, -80, -55)

    fig, ax = plt.subplots(figsize=(6, 4))
    heatmap = ax.imshow(grid_rssi.T, extent=(0, length, 0, breadth), origin="lower", cmap="viridis", alpha=0.8)
    plt.colorbar(heatmap, ax=ax, label="RSSI (dBm)")
    ax.set_title("Wi-Fi Signal Heatmap")
    ax.set_xlabel("Length (m)")
    ax.set_ylabel("Breadth (m)")

    if router_coords:
        rx, ry = router_coords
        ax.plot(rx, ry, marker="o", markersize=10, color="red", label="Router")

    if user_coords:
        ux, uy = user_coords
        ax.plot(ux, uy, marker="s", markersize=8, color="blue", label="User")

    ax.legend()

    if return_fig and root:
        def draw_plot():
            canvas = FigureCanvasTkAgg(fig, master=root)
            canvas.get_tk_widget().pack(fill="both", expand=True)
            canvas.draw()
            canvas.get_tk_widget().pack()
        root.after(0, draw_plot)
    else:
        plt.tight_layout()
        plt.show()

    return fig if return_fig else None


def generate_heatmap_only(csv_path, length=6, breadth=4, router_coords=None, optimized_coords=None):
    df = pd.read_csv(csv_path)
    x, y, rssi = df["x"], df["y"], df["rssi"]

    grid_x, grid_y = np.mgrid[0:length:200j, 0:breadth:200j]
    grid_rssi = griddata((x, y), rssi, (grid_x, grid_y), method='cubic')

    # Apply smoothing and clipping
    grid_rssi = gaussian_filter(grid_rssi, sigma=1.2)
    grid_rssi = np.clip(grid_rssi, -80, -55)

    fig, ax = plt.subplots(figsize=(5.5, 4))
    heatmap = ax.imshow(grid_rssi.T, extent=(0, length, 0, breadth), origin="lower", cmap="viridis", alpha=0.85)
    ax.set_title("Wi-Fi RSSI Heatmap")
    ax.set_xlabel("Length (m)")
    ax.set_ylabel("Breadth (m)")
    plt.colorbar(heatmap, ax=ax, label="RSSI (dBm)")

    if router_coords:
        ax.plot(*router_coords, marker="o", color="red", markersize=8, label="Router")

    if optimized_coords:
        ax.plot(*optimized_coords, marker="X", color="white", markersize=10, label="Optimized Router")

    ax.legend()
    return fig
