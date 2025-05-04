import tkinter as tk
from tkinter import ttk, filedialog
import sys
import os
import threading
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from heatmap_generator import generate_heatmap
from optimize_router import optimize_router

sys.path.append(os.path.join(os.path.dirname(__file__), "core"))

from collect_perimeter import get_rssi
from interpolate_and_plot import interpolate_rssi
from perimeter_guide import PerimeterGUI
from scanner import scan_wifi_networks
from comparision import compare_rssi

root = tk.Tk()
root.title("📶 Wi-Fi Signal Strength Analyzer and Router positioning")
root.geometry("1100x700")
root.configure(bg="#f5f7fa")

tk.Label(root, text="Wi-Fi Signal Strength Analyzer and optimal Router position", font=("Helvetica", 20, "bold"), fg="#333", bg="#f5f7fa").pack(pady=20)

input_frame = tk.Frame(root, bg="#f5f7fa")
input_frame.pack(pady=5)

tk.Label(input_frame, text="SSID:", bg="#f5f7fa").grid(row=0, column=0, padx=5, pady=5, sticky='e')
ssid_entry = tk.Entry(input_frame, width=20)
ssid_entry.grid(row=0, column=1, padx=5, pady=5)
ssid_entry.insert(0, "MyWiFi")

tk.Label(input_frame, text="Room Length (m):", bg="#f5f7fa").grid(row=0, column=2, padx=5, pady=5, sticky='e')
length_entry = tk.Entry(input_frame, width=15)
length_entry.grid(row=0, column=3, padx=5, pady=5)
length_entry.insert(0, "15")

tk.Label(input_frame, text="Room Breadth (m):", bg="#f5f7fa").grid(row=0, column=4, padx=5, pady=5, sticky='e')
breadth_entry = tk.Entry(input_frame, width=10)
breadth_entry.grid(row=0, column=5, padx=5, pady=5)
breadth_entry.insert(0, "10")

tk.Label(input_frame, text="Router X:", bg="#f5f7fa").grid(row=1, column=0, padx=5, pady=5, sticky='e')
router_x_entry = tk.Entry(input_frame, width=0)
router_x_entry.grid(row=1, column=1, padx=5, pady=5)
router_x_entry.insert(0, "0")

tk.Label(input_frame, text="Router Y:", bg="#f5f7fa").grid(row=1, column=2, padx=5, pady=5, sticky='e')
router_y_entry = tk.Entry(input_frame, width=0)
router_y_entry.grid(row=1, column=3, padx=5, pady=5)
router_y_entry.insert(0, "0")

tk.Label(input_frame, text="User X:", bg="#f5f7fa").grid(row=1, column=4, padx=5, pady=5, sticky='e')
user_x_entry = tk.Entry(input_frame, width=0)
user_x_entry.grid(row=1, column=5, padx=5, pady=5)
user_x_entry.insert(0, "0")

tk.Label(input_frame, text="User Y:", bg="#f5f7fa").grid(row=1, column=6, padx=5, pady=5, sticky='e')
user_y_entry = tk.Entry(input_frame, width=0)
user_y_entry.grid(row=1, column=7, padx=5, pady=5)
user_y_entry.insert(0, "0")

results_display = tk.Text(root, height=16, width=120, wrap="word", font=("Courier", 10))
results_display.pack(padx=10, pady=10)

heatmap_container = tk.Frame(root, bg="#f5f7fa")
heatmap_container.pack(fill='x', padx=10, pady=(0, 10))

heatmap_frame = tk.Canvas(heatmap_container, height=320, bg="#ffffff", highlightthickness=0)

def validate_fields():
    fields = [length_entry, breadth_entry, router_x_entry, router_y_entry, user_x_entry, user_y_entry]
    try:
        [int(f.get()) for f in fields]
        return True
    except ValueError:
        return False

def disable_buttons(state=True):
    for btn in button_frame.winfo_children():
        btn.config(state="disabled" if state else "normal")

def run_scanner():
    disable_buttons(True)
    results_display.insert(tk.END, "🔍 Scanning available networks...\n")
    results_display.see(tk.END)
    try:
        networks = scan_wifi_networks()
        results_display.insert(tk.END, "\n".join([f"📶 {n}" for n in networks]) + "\n\n")

        def on_click(event):
         index = results_display.index(f"@{event.x},{event.y}")
         line = results_display.get(index + " linestart", index + " lineend").strip()
         if "📶" in line:
          try:
                dict_str = line.replace("📶", "").strip()
                network_info = eval(dict_str)  # Caution: Only use eval if input is trusted
                ssid_only = network_info.get("SSID", "")
                if ssid_only:
                 ssid_entry.delete(0, tk.END)
                 ssid_entry.insert(0, ssid_only)
          except Exception as e:
            results_display.insert(tk.END, f"⚠️ Failed to parse SSID: {e}\n")


        results_display.bind("<Button-1>", on_click)

    except Exception as e:
        results_display.insert(tk.END, f"❌ Error: {e}\n")
    disable_buttons(False)

def run_collector():
    try:
        length = int(length_entry.get().strip())
        breadth = int(breadth_entry.get().strip())
    except ValueError:
        results_display.insert(tk.END, "⚠️ Please enter valid room dimensions.\n")
        return

    results_display.insert(tk.END, f"\n🧭 Launching perimeter walk GUI...\n")
    results_display.see(tk.END)

    walk_window = tk.Toplevel(root)

    app = PerimeterGUI(
        ssid=ssid_entry.get(),
        length=length,
        breadth=breadth,
        router_x=int(router_x_entry.get()),
        router_y=int(router_y_entry.get()),
        user_x=int(user_x_entry.get()),
        user_y=int(user_y_entry.get()),
        master=walk_window
    )

    def wait_and_process():
        walk_window.wait_window()
        perimeter_path = os.path.join("data", "perimeter_data.csv")
        if os.path.exists(perimeter_path):
            results_display.insert(tk.END, f"📁 Collected RSSI data saved at: {perimeter_path}\n")
            interpolate_rssi(perimeter_path, length, breadth, root)
            results_display.insert(tk.END, "✅ Heatmap generated after walk.\n\n")
        else:
            results_display.insert(tk.END, "⚠️ No data found. Was the walk completed?\n\n")

    threading.Thread(target=wait_and_process, daemon=True).start()

def run_heatmap():
    csv_path = filedialog.askopenfilename(title="Select RSSI CSV", filetypes=[("CSV Files", "*.csv")])
    if not csv_path:
        results_display.insert(tk.END, "⚠️ No file selected for heatmap generation.\n")
        return

    results_display.insert(tk.END, f"🗺️ Generating heatmap: {os.path.basename(csv_path)}\n")

    def task():
        disable_buttons(True)
        try:
            length = int(length_entry.get())
            breadth = int(breadth_entry.get())
            router_x = int(router_x_entry.get())
            router_y = int(router_y_entry.get())
            user_x = int(user_x_entry.get())
            user_y = int(user_y_entry.get())

            fig = generate_heatmap(
                csv_path,
                length=length,
                breadth=breadth,
                root=None,
                router_coords=(router_x, router_y),
                user_coords=(user_x, user_y),
                return_fig=True
            )

            def embed_canvas():
                for widget in heatmap_frame.winfo_children():
                    widget.destroy()
                canvas = FigureCanvasTkAgg(fig, master=heatmap_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill='both', expand=True)
                results_display.insert(tk.END, "✅ Heatmap generated inside GUI!\n\n")

            root.after(0, embed_canvas)

        except Exception as e:
            results_display.insert(tk.END, f"❌ Failed to generate heatmap: {e}\n\n")
        finally:
            disable_buttons(False)

    threading.Thread(target=task).start()

def run_optimiser():
    file_path = filedialog.askopenfilename(title="Select CSV", filetypes=[("CSV files", "*.csv")])
    if not file_path:
        results_display.insert(tk.END, "⚠️ No file selected for optimization.\n")
        return

    results_display.insert(tk.END, "📍 Optimizing router location...\n")

    def task():
        disable_buttons(True)
        try:
            length = int(length_entry.get())
            breadth = int(breadth_entry.get())
            router_x = int(router_x_entry.get())
            router_y = int(router_y_entry.get())
            user_x = int(user_x_entry.get())
            user_y = int(user_y_entry.get())

            opt_x, opt_y = optimize_router(
                file_path,
                length=length,
                breadth=breadth
            )

            def draw():
                for widget in heatmap_frame.winfo_children():
                    widget.destroy()

                fig = generate_heatmap(
                    file_path,
                    length=length,
                    breadth=breadth,
                    root=None,
                    router_coords=(router_x, router_y),
                    user_coords=(user_x, user_y),
                    optimized_coords=(opt_x, opt_y),
                    return_fig=True
                )
                canvas = FigureCanvasTkAgg(fig, master=heatmap_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill='both', expand=True)

                results_display.insert(tk.END, f"✅ Best location: ({opt_x}, {opt_y})\n\n")

            root.after(0, draw)

        except Exception as e:
            results_display.insert(tk.END, f"❌ Optimization Error: {e}\n\n")
        disable_buttons(False)

    threading.Thread(target=task).start()

def run_compare():
    file_before = filedialog.askopenfilename(title="Select BEFORE CSV", filetypes=[("CSV Files", "*.csv")])
    if not file_before:
        results_display.insert(tk.END, "❌ No BEFORE file selected.\n")
        return

    file_after = filedialog.askopenfilename(title="Select AFTER CSV", filetypes=[("CSV Files", "*.csv")])
    if not file_after:
        results_display.insert(tk.END, "❌ No AFTER file selected.\n")
        return

    try:
        length = int(length_entry.get())
        breadth = int(breadth_entry.get())
    except ValueError:
        results_display.insert(tk.END, "⚠️ Please enter valid room dimensions.\n")
        return

    results_display.insert(tk.END, f"📈 Comparing:\n{os.path.basename(file_before)} vs {os.path.basename(file_after)}\n")

    compare_rssi(
        csv_before=file_before,
        csv_after=file_after,
        length=length,
        breadth=breadth,
        root=heatmap_frame,
        output_callback=lambda msg: results_display.insert(tk.END, msg + "\n")
    )

button_frame = tk.Frame(root, bg="#f5f7fa")
button_frame.pack(pady=15)

buttons = [
    ("📡  Scan Networks", run_scanner),
    ("📊  Collect RSSI Data", run_collector),
    ("🗺️  Generate Heatmap", run_heatmap),
    ("📍  Optimize Location", run_optimiser),
    ("📈  Compare Results", run_compare),
]

for label, command in buttons:
    tk.Button(button_frame, text=label, command=command, font=("Helvetica", 12), width=20, height=2, bg="#0078D4", fg="white").pack(side="left", padx=8)

root.mainloop()
