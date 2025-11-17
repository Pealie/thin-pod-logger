# tcp_client_csv.py — Windows/macOS/Linux host CSV logger
# Connects to Pico server and logs to vbatt_log.csv


import socket, os, time
from datetime import datetime, timezone


PICO_IP = "192.168.x.y" # <-- set to Pico IP printed by Thonny
PORT = 5007
OUT_CSV = os.path.join(os.getcwd(), "vbatt_log.csv")




def run_once():
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
s.connect((PICO_IP, PORT))
print(f"Connected to {PICO_IP}:{PORT}")
need_header = not os.path.exists(OUT_CSV) or os.path.getsize(OUT_CSV) == 0


with open(OUT_CSV, "a", buffering=1) as f:
if need_header:
f.write("timestamp,elapsed_s,vbatt_v\n")


buf = b""
while True:
chunk = s.recv(1024)
if not chunk:
print("server closed")
return
buf += chunk
while b"\n" in buf:
line, buf = buf.split(b"\n", 1)
try:
t_str, v_str = line.decode().strip().split(",")
ts = datetime.now(timezone.utc).isoformat()
f.write(f"{ts},{float(t_str):.1f},{float(v_str):.4f}\n")
print(ts, t_str, v_str)
except Exception as e:
print("skip:", line, e)




if __name__ == "__main__":
while True:
try:
run_once()
except OSError as e:
print("connect failed, retrying in 2s:", e)
time.sleep(2)