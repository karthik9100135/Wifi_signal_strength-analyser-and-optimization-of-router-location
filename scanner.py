import subprocess
import re
import json

def scan_wifi_networks():
    try:
        output = subprocess.check_output("netsh wlan show networks mode=bssid", shell=True, text=True)

        networks = []
        current_ssid = None
        signal_strength = None

        for line in output.split("\n"):
            ssid_match = re.match(r"\s*SSID\s+\d+\s+:\s+(.*)", line)
            if ssid_match:
                current_ssid = ssid_match.group(1)
                continue

            signal_match = re.match(r"\s*Signal\s+:\s+(\d+)%", line)
            if signal_match and current_ssid:
                signal_percent = int(signal_match.group(1))
                rssi = convert_percent_to_rssi(signal_percent)
                strength = classify_signal(signal_percent)

                networks.append({
                    "SSID": current_ssid,
                    "Signal (%)": signal_percent,
                    "RSSI (dBm)": rssi,
                    "Strength": strength
                })

        return networks

    except subprocess.CalledProcessError as e:
        return []

def convert_percent_to_rssi(percent):
    if 0 <= percent <= 100:
        # Assume a typical RSSI range of -100 dBm (0%) to -30 dBm (100%)
        min_rssi = -100
        max_rssi = -30
        return min_rssi + (percent / 100) * (max_rssi - min_rssi)
    else:
        return None

def classify_signal(percent):
    if percent >= 75:
        return "Strong"
    elif percent >= 40:
        return "Moderate"
    else:
        return "Weak"

def save_selected_ssid(ssid):
    with open("selected_ssid.json", "w") as f:
        json.dump({"selected_ssid": ssid}, f)

if __name__ == "__main__":
    results = scan_wifi_networks()
    for net in results:
        print(net)
