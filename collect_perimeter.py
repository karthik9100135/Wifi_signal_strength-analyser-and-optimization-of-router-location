import time
import subprocess
import csv
import os
import datetime

ROOM_WIDTH = 5
ROOM_HEIGHT = 4
TIME_PER_WALL = 10

walls = [
    ("bottom", ROOM_WIDTH),
    ("right", ROOM_HEIGHT),
    ("top", ROOM_WIDTH),
    ("left", ROOM_HEIGHT),
]

def get_unique_csv_path():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"perimeter_data_{timestamp}.csv"
    return os.path.join("..", "data", filename)

def get_rssi(ssid):
    try:
        result = subprocess.check_output(["nmcli", "-f", "SSID,SIGNAL", "dev", "wifi"])
        lines = result.decode().split("\n")
        for line in lines:
            if ssid in line:
                signal = int(line.strip().split()[-1])
                return signal
    except Exception:
        pass
    return None

def walk_and_collect(ssid):
    data = []
    x, y = 0, 0

    for wall, length in walls:
        steps = TIME_PER_WALL
        dx, dy = 0, 0

        if wall == "bottom":
            dx = length / steps
        elif wall == "right":
            dy = length / steps
        elif wall == "top":
            dx = -length / steps
        elif wall == "left":
            dy = -length / steps

        for _ in range(steps):
            rssi = get_rssi(ssid)
            if rssi:
                data.append([x, y, rssi])
            x += dx
            y += dy
            time.sleep(1)

    csv_path = get_unique_csv_path()
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)

    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["x", "y", "rssi"])
        writer.writerows(data)

    print(f"✅ Saved to {csv_path} with {len(data)} points.")

if __name__ == "__main__":
    ssid = input("Enter SSID to scan: ")
    walk_and_collect(ssid)
