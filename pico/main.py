# main.py — Pico 2 W (MicroPython)
led = Pin("LED", Pin.OUT)
adc = ADC(ADC_PIN)


srv = socket.socket()
try:
try:
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
except Exception:
pass
srv.bind(("0.0.0.0", PORT))
srv.listen(1)
print("listening on", PORT)


while True:
conn, addr = srv.accept()
print("client:", addr)
t0 = time.time()


# warmup/settle
time.sleep(SETTLE_S)
for _ in range(DISCARD):
_ = adc.read_u16()
time.sleep(0.02)


try:
while True:
# average a few samples for stability
acc = 0
N = 32
for _ in range(N):
acc += (adc.read_u16() >> 4) # 16->12 bit
raw = acc / N
v_adc = raw * ADC_SCALE
v_batt = v_adc * VBATT_SCALE * CAL_GAIN
t_rel = time.time() - t0


line = f"{t_rel:.1f},{v_batt:.4f}\n"
conn.send(line.encode())


# blink heartbeat
led.on(); time.sleep(0.06); led.off()


time.sleep(INTERVAL)
except OSError:
try: conn.close()
except: pass
print("client closed; waiting…")
except Exception as e:
try: conn.close()
except: pass
print("error:", e)
finally:
try: srv.close()
except: pass




if __name__ == "__main__":
serve()