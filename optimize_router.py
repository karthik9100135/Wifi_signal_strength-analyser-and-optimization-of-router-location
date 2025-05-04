import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel as C
from scipy.ndimage import uniform_filter

def optimize_router(csv_path, length=6, breadth=4, root=None, router_coords=None):
    df = pd.read_csv(csv_path)
    x = df["x"]
    y = df["y"]
    rssi = df["rssi"]

    # Prepare input for GPR
    X = np.column_stack((x, y))
    y_rssi = rssi.values

    kernel = C(1.0) * RBF(length_scale=1.0)
    gpr = GaussianProcessRegressor(kernel=kernel, alpha=1e-1, normalize_y=True)
    gpr.fit(X, y_rssi)

    grid_res = 100
    gx, gy = np.meshgrid(np.linspace(0, length, grid_res), np.linspace(0, breadth, grid_res))
    test_coords = np.column_stack((gx.ravel(), gy.ravel()))

    pred_rssi = gpr.predict(test_coords).reshape(grid_res, grid_res)

    # Optional: Smooth the predicted RSSI surface
    smoothed = uniform_filter(pred_rssi, size=3)

    # Bias to discourage placing near walls
    bias = np.ones_like(smoothed)
    border = 5
    bias[:border, :] *= 0.85
    bias[-border:, :] *= 0.85
    bias[:, :border] *= 0.85
    bias[:, -border:] *= 0.85
    score = smoothed * bias

    # Find optimal router location (max score)
    best_idx = np.unravel_index(np.argmax(score), score.shape)
    opt_x = (best_idx[1] / (grid_res - 1)) * length
    opt_y = (best_idx[0] / (grid_res - 1)) * breadth

    # Plot
    fig, ax = plt.subplots(figsize=(6, 4))
    heatmap = ax.imshow(pred_rssi, extent=(0, length, 0, breadth), origin="lower", cmap="viridis", alpha=0.85)
    plt.colorbar(heatmap, ax=ax, label="Predicted RSSI (dBm)")
    ax.set_title("Optimized Router Location (GPR)")
    ax.set_xlabel("Length (m)")
    ax.set_ylabel("Breadth (m)")

    if router_coords:
        rx, ry = router_coords
        ax.plot(rx, ry, "ro", label="Current Router", markersize=9)
    ax.plot(opt_x, opt_y, "wX", label="Optimized Router", markersize=11)
    ax.legend()

    if root:
        def embed():
            for widget in root.winfo_children():
                widget.destroy()
            canvas = FigureCanvasTkAgg(fig, master=root)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
        root.after(0, embed)
    else:
        plt.tight_layout()
        plt.show()

    return round(opt_x, 2), round(opt_y, 2)
