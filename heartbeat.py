import time
import requests
from config import BIN_ID, SERVER_URL

HEARTBEAT_INTERVAL = 10  # seconds

def send_heartbeat():
    url = f"{SERVER_URL}/api/heartbeat"
    data = {"bin_id": BIN_ID}

    try:
        response = requests.post(url, json=data, timeout=5)
        if response.status_code == 200:
            print(f"[Heartbeat] Sent OK for {BIN_ID}")
        else:
            print(f"[Heartbeat] Server error {response.status_code}: {response.text}")
    except requests.RequestException as e:
        print(f"[Heartbeat] Failed to send: {e}")

def main():
    print(f"[Heartbeat] Starting heartbeat loop for {BIN_ID}")
    print(f"[Heartbeat] Sending to {SERVER_URL}")
    while True:
        send_heartbeat()
        time.sleep(HEARTBEAT_INTERVAL)

if __name__ == "__main__":
    main()
