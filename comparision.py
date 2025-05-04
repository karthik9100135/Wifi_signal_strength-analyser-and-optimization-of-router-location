import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.interpolate import griddata

def compare_rssi(csv_before, csv_after, length, breadth, root, output_callback=None):
    def load_and_interpolate(csv_path):
        df = pd.read_csv(csv_path)
        x, y, rssi = df["x"], df["y"], df["rssi"]
        grid_x, grid_y = np.mgrid[0:length:100j, 0:breadth:100j]
        grid_rssi = griddata((x, y), rssi, (grid_x, grid_y), method="cubic")
        return df, grid_rssi

    def embed_plot_in_gui(fig, root):
        for widget in root.winfo_children():
            widget.destroy()
        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True, pady=10)

    def compute_stats(df):
        avg_rssi = np.nanmean(df["rssi"])
        std_rssi = np.nanstd(df["rssi"])
        strong_coverage_pct = np.sum(df["rssi"] > -65) / len(df) * 100
        return avg_rssi, std_rssi, strong_coverage_pct

    try:
        df_before, grid_before = load_and_interpolate(csv_before)
        df_after, grid_after = load_and_interpolate(csv_after)

        # Plot heatmaps
        fig, axs = plt.subplots(1, 2, figsize=(12, 5))
        im1 = axs[0].imshow(grid_before.T, extent=(0, length, 0, breadth), origin="lower", cmap="viridis")
        axs[0].set_title("📶 Before Router Relocation")
        axs[0].set_xlabel("Length (m)")
        axs[0].set_ylabel("Breadth (m)")
        plt.colorbar(im1, ax=axs[0], label="RSSI (dBm)")

        im2 = axs[1].imshow(grid_after.T, extent=(0, length, 0, breadth), origin="lower", cmap="viridis")
        axs[1].set_title("📶 After Router Relocation")
        axs[1].set_xlabel("Length (m)")
        axs[1].set_ylabel("Breadth (m)")
        plt.colorbar(im2, ax=axs[1], label="RSSI (dBm)")

        embed_plot_in_gui(fig, root)

      
        avg_before, std_before, cov_before = compute_stats(df_before)
        avg_after, std_after, cov_after = compute_stats(df_after)
        delta = avg_after - avg_before
        pct = (delta / abs(avg_before)) * 100 if avg_before != 0 else 0

        stats_msg = (
            f"\n📊 Signal Stats Summary:\n"
            f"🛑 Before Relocation:\n"
            f"• Average RSSI:         {avg_before:.2f} dBm\n"
            f"• Std Deviation:        {std_before:.2f}\n"
            f"• Strong Coverage:      {cov_before:.1f}% (> -65 dBm)\n\n"
            f"✅ After Relocation:\n"
            f"• Average RSSI:         {avg_after:.2f} dBm\n"
            f"• Std Deviation:        {std_after:.2f}\n"
            f"• Strong Coverage:      {cov_after:.1f}% (> -65 dBm)\n\n"
            f"📈 Improvement:\n"
            f"• Avg RSSI Gain:        {delta:+.2f} dBm ({pct:.1f}%)"
        )

        if output_callback:
            output_callback(stats_msg)

        return avg_before, avg_after, delta, pct

    except Exception as e:
        if output_callback:
            output_callback(f"❌ Comparison failed: {e}")
        return None, None, None, None
