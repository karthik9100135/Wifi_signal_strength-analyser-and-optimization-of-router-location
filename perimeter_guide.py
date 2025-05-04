import tkinter as tk
from tkinter import ttk
import csv
import os
import time
import threading
import datetime
from rssi_collector import get_rssi_windows

def get_unique_csv_path():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"perimeter_data_{timestamp}.csv"
    return os.path.join("data", filename)

class PerimeterGUI:
    def __init__(self, ssid, length, breadth, router_x, router_y, user_x, user_y, master):
        self.ssid = ssid
        self.length = length
        self.breadth = breadth
        self.router_x = router_x
        self.router_y = router_y
        self.user_x = user_x
        self.user_y = user_y
        self.stop_flag = threading.Event()
        self.last_saved_csv = None

        self.window = tk.Toplevel(master)
        self.window.title("📡 Perimeter Walk Data Collection")
        self.window.geometry("400x300")
        self.window.protocol("WM_DELETE_WINDOW", self.stop_collection)

        self.status_label = ttk.Label(self.window, text="Press Start to begin RSSI collection.")
        self.status_label.pack(pady=10)

        self.start_button = ttk.Button(self.window, text="▶️ Start", command=self.start_collection)
        self.start_button.pack(pady=5)

        self.stop_button = ttk.Button(self.window, text="⏹️ Stop", command=self.stop_collection, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

    def start_collection(self):
        self.stop_flag.clear()
        self.status_label.config(text="Collecting RSSI... Move along the perimeter.")
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        threading.Thread(target=self.collect_data).start()

    def stop_collection(self):
        self.stop_flag.set()
        self.status_label.config(text="🛑 Stopping...")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def collect_data(self):
        points = self._generate_perimeter_points()
        csv_path = get_unique_csv_path()
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)

        try:
            with open(csv_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["x", "y", "rssi"])

                for x, y in points:
                    if self.stop_flag.is_set():
                        break

                    rssi = get_rssi_windows(self.ssid)
                    writer.writerow([x, y, rssi])
                    self._update_status(f"✔️ RSSI at ({x},{y}) = {rssi} dBm")
                    time.sleep(1.5)

            self.last_saved_csv = csv_path
            self._update_status(f"✅ Collection complete.\nSaved to: {csv_path}")
        except Exception as e:
            self._update_status(f"❌ Error: {e}")
        finally:
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)

    def _update_status(self, message):
        self.status_label.after(0, lambda: self.status_label.config(text=message))

    def _generate_perimeter_points(self):
        points = []
        for x in range(self.length + 1):
            points.append((x, 0))
        for y in range(1, self.breadth + 1):
            points.append((self.length, y))
        for x in range(self.length - 1, -1, -1):
            points.append((x, self.breadth))
        for y in range(self.breadth - 1, 0, -1):
            points.append((0, y))
        return points
