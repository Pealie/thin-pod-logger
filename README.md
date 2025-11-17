# Thin‑Pod Telemetry Logger

Low‑power VBATT sensing and Wi‑Fi logging for the Thin‑Pod energy‑harvesting bench rig.

---

## Overview

This mini‑project streams the supercapacitor **VBATT** from an **AEM00941 EVK v1.2 + 5 F** cap to a host over Wi‑Fi using a **Raspberry Pi Pico 2 W**. A high‑impedance divider and small RC feed the RP2350 ADC; a MicroPython script serves data over TCP; a tiny Python client logs to CSV on your laptop/desktop (or Pi Zero 2 W).

**Highlights**

* ~**2 µA** divider overhead (1.0 MΩ // 660 kΩ) — harvester‑friendly.
* **5 s** default cadence; LED heartbeat on send.
* **TCP** stream → **CSV** (`timestamp,elapsed_s,vbatt_v`) with auto‑reconnect.
* Fault‑tolerant bring‑up (clear wiring signatures and firewall‑proof flow).

> This repo is a self‑contained “telemetry side‑quest” to support Thin‑Pod harvester tuning. It doesn’t require the UWB radio or ADXL1005 to operate.

---

## System Architecture

```
AEM00941 EVK ── 5F/6V supercap (BATT)
        │
        ├─ BATT+ ─ 1.0 MΩ ─┐
        │                  ├─ (ADC node) ── GP26/ADC0 (Pico 2 W)
        └─ BATT− ─ 660 kΩ ─┘
                          ║
                       100 nF → BATT−

Pico 2 W (MicroPython) ──TCP:5007──▶ Host (Python client) → vbatt_log.csv
```

*See also: `docs/fig/fig1_architecture.png` (placeholder).*

---

## Hardware

* **Energy harvester:** e‑peas **AEM00941 EVK v1.2** (BATT terminals)
  *(Alt. for later experiments: Smart‑Material CL‑54; wiring differs.)*
* **Supercapacitor:** **5.0 F / 6 V** (e.g., Eaton PTV‑6R0V505‑R)
* **Telemetry MCU:** **Raspberry Pi Pico 2 W** (RP2350 + Wi‑Fi)
* **Divider & RC:**

  * R_TOP = **1.0 MΩ** (±1%)
  * R_BOTTOM = **660 kΩ** (±1%) *(680 kΩ also fine; update code)*
  * C_NODE = **100 nF** (C0G/NP0 preferred)
* **Breadboard/jumpers**, common ground (AEM **BATT− ↔ Pico GND**)

**Design numbers**

* Scale factor: `VBATT_SCALE = (R_TOP + R_BOTTOM) / R_BOTTOM = 2.515` (for 1M / 660k)
* ADC node at VBATT=3.34 V: ~**1.33 V**
* RC settle τ ≈ **39.8 ms** → 6τ ≈ 0.24 s (well below 5 s cadence)
* Divider current at 3.3 V: ~**2.0 µA**

---

## Wiring

Choose **one single breadboard row** as the **ADC node** and place all of these into that row:

* GP26 (Pico ADC0) jumper,
* One leg of **1.0 MΩ** (other leg to **BATT+**),
* One leg of **660 kΩ** (other leg to **BATT−**),
* One leg of **100 nF** (other leg to **BATT−**).

> **Common mistakes**: landing parts across the center trench (node becomes two rows), missing the common ground, or swapping the divider legs — see **Troubleshooting**.

---

## Software

### Requirements

* **Pico 2 W** with **MicroPython** firmware (latest stable).
* **Python 3.10+** on the host (Windows/macOS/Linux/Raspberry Pi).
* Optional: **Thonny** for Pico file transfer/console.

### Files (this repo)

```
thin-pod-telemetry/
├─ README.md # see README in the other canvas (or reuse this repo's version)
├─ LICENSE # MIT license
$1├─ requirements.txt
├─ pico/
│ └─ main.py # MicroPython TCP server on Pico 2 W (ADC streaming)
├─ host/
│ └─ tcp_client_csv.py # Host CSV logger (connects to Pico)
├─ docs/
│ └─ fig/
│ └─ .gitkeep
└─ data/
└─ .gitkeep```

---

## Quick Start

1. **Wire it** exactly as in the diagram (single node row; common ground).

2. **Pico**: open `pico/main.py` and edit:

   ```python
   SSID = "<your_wifi_ssid>"
   PWD  = "<your_wifi_password>"
   R_TOP = 1_000_000
   R_BOTTOM = 660_000   # 680000 if using 680 kΩ
   INTERVAL = 5         # seconds between samples
   ```

   Save to the Pico as **`main.py`**. Reboot or power from a wall adapter. Thonny will print **Pico IP** and `listening on 5007`.

3. **Host**: open `host/tcp_client_csv.py` and set the **Pico IP** printed by Thonny:

   ```python
   PICO_IP = "192.168.x.y"  # from Pico console
   PORT = 5007
   ```

   Run:

   ```bash
   cd host
   python tcp_client_csv.py
   ```

   You should see `Connected to ...` and rows streaming; a **`vbatt_log.csv`** appears in `host/`.

> On Windows, no firewall changes are normally required because the host initiates the outbound TCP connection.

**Notes**

Keep AEM BATT− ↔ Pico GND common.

With 1M/660k and 100 nF at the node, start-up blips are normal; the Pico script discards the first few samples and waits SETTLE_S.

Calibrate by updating R_TOP/R_BOTTOM, ADC_REF, or CAL_GAIN.

---

## Calibration (optional but recommended)

Pick one of these simple options:

**A. Measured resistors**
Measure R_TOP and R_BOTTOM with a DMM and set those exact values in `main.py`.

**B. One‑line gain trim**
If DMM says 3.340 V while CSV shows 3.303 V:

```python
CAL_GAIN = 3.340/3.303  # ≈ 1.0113
v_batt *= CAL_GAIN
```

**C. ADC ref tweak**
Treat 3V3 as `ADC_REF` and set:

```python
ADC_REF = 3.337
ADC_SCALE = ADC_REF / 4095.0
```

**D. Two‑point fit**
Capture readings near 0 V and ~3.5 V; compute `v_batt = a*raw + b` and apply.

---

## Troubleshooting

**No data / connect errors**

* Ensure Pico prints an IP and `listening on 5007`.
* Host must use that **Pico IP**.
* Check: `netstat -an | find ":5007"` (should see an ESTABLISHED connection while streaming).

**CSV ~0.00 V**

* ADC node is effectively at **GND**: open **1.0 MΩ** leg or node landed on a GND row. Check BATT+↔node ≈ 1.0 MΩ.

**CSV ~8.09 V (flat)**

* ADC node clamped near **3.3 V**: open **660 kΩ** leg / node not pulling down. Check node↔BATT− ≈ 660 kΩ.

**Start‑up blips/zeros**

* Normal while RC settles; the first 2–3 samples can be discarded or add a 0.2 s settle before averaging.

**Windows inbound rule confusion**

* Not needed with this flow (host is the client). If roles are ever inverted, use PowerShell:

  ```powershell
  New-NetFirewallRule -DisplayName "Pico_TCP_5007" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 5007 -Profile Private
  ```

---

## Acceptance (ready‑to‑fill)

| Req | Description           | Target             | Evidence  | Result   | Pass/Fail |
| --- | --------------------- | ------------------ | --------- | -------- | --------- |
| R1  | VBATT accuracy vs DMM | ≤ ±2%              | Results § | *(fill)* | *(fill)*  |
| R2  | Sampling cadence      | ≥ 1/5 s            | Config §  | *(fill)* | *(fill)*  |
| R3  | Divider overhead      | ≤ 25 µA            | Design §  | *(fill)* | *(fill)*  |
| R4  | Robust logging        | UTC CSV; reconnect | Demo §    | *(fill)* | *(fill)*  |

---

## Roadmap / Future Work

* Auto‑plots and thresholds (Matplotlib) and daily log roll‑over.
* Optional lower‑Z divider (100 kΩ/68 kΩ + 100 nF) or op‑amp buffer for precision.
* Integrate telemetry with harvester duty‑cycle experiments (weights/position sweeps).
* Containerised host tools (`uv`/`pipx`, minimal venv) and Makefile targets.

---

## Safety & Notes

* Supercaps can deliver high peak currents — avoid shorts; respect polarity.
* Share ground between AEM EVK and Pico.
* This is a bench‑test tool; field firmware may gate or duty‑cycle the divider to save energy.

---

## License

MIT for software, CC‑BY for docs 

---

## Acknowledgements

* e‑peas AEM00941 EVK v1.2, Eaton PTV supercapacitors.
* MicroPython & Raspberry Pi Pico team.

---

## Credits

Built by **Neil Thomson** as part of the Thin‑Pod project. Feedback and PRs welcome.
