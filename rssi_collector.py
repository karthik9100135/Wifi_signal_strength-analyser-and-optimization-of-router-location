import subprocess
import re

def get_rssi_windows(ssid):
    try:
        output = subprocess.check_output("netsh wlan show interfaces", shell=True, text=True)
        for line in output.splitlines():
            if "Signal" in line:
                match = re.search(r"(\d+)%", line)
                if match:
                    signal_strength = int(match.group(1))
                    # Convert to approximate RSSI
                    rssi = (signal_strength / 2) - 100
                    return int(rssi)
        return -100  # Default if not found
    except Exception as e:
        return -100
