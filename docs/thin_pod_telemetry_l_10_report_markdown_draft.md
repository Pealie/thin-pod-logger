# Thin‑Pod Telemetry: Low‑Power VBATT Sensing & Wi‑Fi Logging with Pico 2 W

**Author:** Neil Thomson  
**Level:** SCQF 10  
**Date:** 16 Nov 2025  
**Word count:** *1350*

---

## Abstract

This work implements and validates a low‑power telemetry path to monitor the supercapacitor VBATT of the Thin‑Pod harvester (AEM00941 + 5 F) during bench testing. A resistive divider (1.0 MΩ / 660 kΩ) and 100 nF RC network feed RP2040 ADC0 on a Pico 2 W. The Pico runs a TCP server (5007) streaming averaged samples every 5 s to a Windows client that logs ISO‑UTC CSV. Bring‑up required reversing client/server roles to avoid Windows inbound firewall issues and careful node wiring; typical errors (open top/bottom leg, ADC clamp) were diagnosed from data signatures. Final readings stabilised at 3.303 V vs DMM 3.340 V (≈1.1% error) at ~2 µA divider current. The pipeline is stable, reproducible, and ready to support harvester tuning.

_[Back to Contents](#contents)_

---

## Contents
- [**Abstract**](#abstract)
- [**1. Introduction**](#1-introduction)
- [**2. Background and Requirements**](#2-background--requirements)
- [**3. System Design**](#3-system-design)
  - [**3.1 System Architecture**](#31-architecture)
  - [**3.2 Hardware Design**](#32-hardware)
  - [**3.3 Software Design**](#33-software)
  - [**3.4 Risk and Ethical Considerations**](#34-risk--ethics)
- [**4. Methodology and Test Plan**](#4-methods-and-test-plan)
- [**5. Results**](#5-results)
  - [**5.1 Bring-Up Chronology and Fault Signatures**](#51-bringup-chronology-fault-signatures)
  - [**5.2 Accuracy and Stability**](#52-accuracy--stability)
  - [**5.3 Acceptance Testing**](#53-acceptance-check-readytofill)
- [**6. Analysis and Discussion**](#6-analysis--discussion)
- [**7. Conclusions and Future Work**](#7-conclusion--future-work)
- [**References**](#references-harvard)
- [**Appendix A: Bill of Materials (Excerpt)**](#appendix-a-bill-of-materials-excerpt)
- [**Appendix B: Wiring Description (Text)**](#appendix-b-wiring-text)
- [**Appendix C: Code Listings (Pointers)**](#appendix-c-code-listings-pointers)
- [**Appendix D: Sample Telemetry CSV (Excerpt)**](#appendix-d-sample-csv-excerpt)
- [**Appendix E: Useful Commands**](#appendix-e-useful-commands)
- [**Appendix F: Uncertainty Budget (Illustrative)**](#appendix-f-uncertainty-budget-illustrative)
- [**Appendix G: Change Log (Key Points)**](#appendix-g-change-log-key-points)

---

## 1. Introduction

**Context.** Thin‑Pod is a vibration‑powered sensing node intended to operate near rotating machinery. During harvester tuning, repeatable VBATT telemetry is essential to correlate mechanical adjustments (cantilever mass/position) with energy balance.

**Aim.** Build an end‑to‑end, low‑overhead telemetry path that logs VBATT to a host over Wi‑Fi with sufficient accuracy and cadence for multi‑hour runs.

**Success criteria.**
- Accuracy ≤ ±2% vs DMM.
- Cadence ≥ 1 sample/5 s, robust logging.
- Added electrical load ≤ 25 µA (mean).
- Operable with a standard Windows laptop on home Wi‑Fi.

**Contributions.** Hardware divider design and analysis; Pico 2 W telemetry server; Windows CSV logger; commissioning procedure; fault signatures; calibration options; acceptance results.

_[Back to Contents](#contents)_

---

## 2. Background & Requirements

**ADC behaviour.** RP2040 ADC is SAR with 12‑bit effective counts (MicroPython exposes 16‑bit left‑justified). Reference is the 3V3 rail, so rail tolerance/noise impact accuracy. High source impedance needs input capacitance / settle time.

**Voltage measurement.** Divider converts VBATT (~2.5–4.5 V typical) to < 3.3 V at ADC. RC forms an anti‑alias/settling network; protection diodes clamp at ~3.3 V if node is driven high.

**Networking.** UDP is simple but Windows often blocks inbound sockets; TCP client‑initiated outbound is typically allowed on private networks. CSV logging suffices for analysis.

**Constraints.** Energy budget (µA‑class), minimal code footprint, reproducibility, simple tools.

### 2.1 Requirements & Acceptance Criteria (ready‑to‑fill)

| Req | Description | Target | Evidence (section/page) | Result (value) | Pass/Fail |
|---|---|---|---|---|---|
| R1 | VBATT accuracy vs DMM | ≤ ±2% | §5.2 | *(fill)* | *(fill)* |
| R2 | Sampling cadence | ≥ 1/5 s | §4.3 | *(fill)* | *(fill)* |
| R3 | Divider overhead current | ≤ 25 µA | §3.2, §6.2 | *(fill)* | *(fill)* |
| R4 | Robust logging | UTC CSV; reconnect | §3.3, §5.1 | *(fill)* | *(fill)* |

_[Back to Contents](#contents)_

---

## 3. System Design

### 3.1 Architecture
![Figure 1 — System architecture (placeholder)](fig/fig1_architecture.png)
*Figure 1.* AEM00941 EVK → 5 F supercap (BATT) → divider node → Pico 2 W ADC0 (GP26) → TCP server (5007) → Windows client → `vbatt_log.csv`. LED heartbeat per sample.

### 3.2 Hardware
![Figure 2 — Divider & ADC front‑end schematic (placeholder)](fig/fig2_divider_adc.png)
*Figure 2.* Divider and RC network feeding RP2040 ADC0.

- **Divider:** R_TOP = 1.0 MΩ; R_BOTTOM = 660 kΩ; ratio = 660 k / 1.66 M ≈ **0.3976**.  
  Rebuild scale **VBATT_SCALE** = (R_TOP + R_BOTTOM) / R_BOTTOM ≈ **2.515**.
- **Thevenin resistance:** R_th = (Rt·Rb)/(Rt+Rb) ≈ **398 kΩ**.
- **RC settle:** C_in = 100 nF → τ ≈ 39.8 ms, 6τ ≈ 0.24 s (< 5 s cadence).
- **Divider current:** I ≈ VBATT/(Rt+Rb). At 3.3 V → ~**2.0 µA** (<< 25 µA budget).
- **Grounding/decoupling:** Common BATT− to Pico GND; 100 nF at node→GND placed near GP26.

### 3.3 Software
![Figure 3 — Network flow (placeholder)](fig/fig3_network_flow.png)
*Figure 3.* Pico 2 W (server) streaming to Windows client (CSV logger).

- **Pico (`main.py`):** MicroPython; STA Wi‑Fi; TCP **server** on 5007; average 32 ADC reads; 5 s cadence; LED blink per send; prints IP and client.
- **Laptop (`tcp_client_csv.py`):** TCP **client**; auto‑reconnect; line‑buffered CSV with `timestamp,elapsed_s,vbatt_v`.
- **Protocol decision:** TCP chosen to exploit outbound client permissions on Windows; inversion (Pico=server) avoids inbound firewall complexity.

### 3.4 Risk & Ethics
Low‑voltage system; supercaps can source high peak current—observe safe handling. ESD precautions for Pico and EVK. Data is local/non‑personal. Reproducibility prioritised via scripts and wiring notes.

_[Back to Contents](#contents)_

---

## 4. Methods and Test Plan

![Figure 4 — Wiring/breadboard photo annotated (placeholder)](fig/fig4_wiring_photo.png)
*Figure 4.* Annotated wiring to ensure the ADC node is a single row.

**Rig.** AEM00941 EVK v1.2 with 5 F/6 V cap; Pico 2 W on solderless breadboard; Windows 11 laptop on same Wi‑Fi.

**Wiring procedure.**
1. Choose one **row** as the ADC node; place GP26 jumper, 1 MΩ leg, 660 kΩ leg, and 100 nF leg **in that same row** (do not cross breadboard trench).  
2. Other resistor legs: 1 MΩ→BATT+, 660 kΩ→BATT−; 100 nF other leg→BATT−.  
3. Verify with DMM (power off): BATT+↔node ≈ 1.0 MΩ; node↔BATT− ≈ 660 kΩ.

**Network procedure.**
- Pico prints IP; laptop client connects to `PICO_IP:5007` and logs CSV.
- PowerShell rule retained for diagnostics, but not needed with client‑outbound TCP.

**Sampling.** 5 s cadence; discard first 2–3 samples after connect; average 32 counts; optional 0.2 s settle for high‑Z node.

**Calibration.** Set `R_TOP/R_BOTTOM` to actual values; optional one‑line gain trim `v_batt *= 3.34/3.303`.

**Validation.** Compare CSV to DMM at VBATT ~3.3 V for 5–10 minutes.

_[Back to Contents](#contents)_

---

## 5. Results

### 5.1 Bring‑up chronology (fault signatures)
- **Symptom:** CSV ~0.016 V → **Cause:** open top leg / node to GND only.  
- **Symptom:** CSV ~8.09 V flat → **Cause:** open bottom leg; node clamped ≈3.3 V (ADC diode).  
- **Fix:** Re‑land both resistors + GP26 + 100 nF on same node row; confirm ohms.

### 5.2 Accuracy & stability
![Figure 5 — VBATT vs time (placeholder)](fig/fig5_vbatt_time.png)
*Figure 5.* VBATT(time) from CSV; DMM checkpoints overlaid.

- DMM at BATT+: **3.340 V**.  
- CSV (post‑settle): **3.302–3.304 V**; mean ≈ **3.303 V**, σ ≈ few mV.  
- **Error:** ~**1.1 %** (under‑read), consistent with 3V3 ref and resistor tolerance.  
- Applying `v_batt *= 1.0113` aligns within <0.2%.

### 5.3 Acceptance check (ready‑to‑fill)
| Req | Target | Evidence | Result | Pass/Fail |
|---|---|---|---|---|
| R1 | ≤ ±2% | §5.2 Table/Plot | *(fill)* | *(fill)* |
| R2 | ≥ 1/5 s | §4.3 config | *(fill)* | *(fill)* |
| R3 | ≤ 25 µA | §3.2 calc | *(fill)* | *(fill)* |
| R4 | UTC CSV, reconnect | §3.3/§5.1 | *(fill)* | *(fill)* |

_[Back to Contents](#contents)_

---

## 6. Analysis & Discussion

**Error sources.** 3V3 rail ≠ 3.300 V; RP2040 ADC gain/offset; resistor tolerance (±1–5%); high‑Z node settling (mitigated by 100 nF + averaging). Breadboard wiring is a significant practical risk; signatures above enable rapid diagnosis.

**Energy impact.** Divider adds ~2 µA; negligible vs harvester but acceptable for long‑term tests. If continuous ultra‑low‑power is required in‑field, gate the divider or read intermittently.

**Alternatives.** Lower‑Z divider (100 k/68 k, ~20 µA) improves settling; micropower buffer (e.g., MCP6001) isolates ADC (~100 µA). Two‑point calibration to remove residual gain error.

_[Back to Contents](#contents)_

---

## 7. Conclusion & Future Work

The telemetry chain is operational, robust, and energy‑light. It meets accuracy, cadence, load, and logging requirements, enabling long runs during mechanical tuning. Next steps: bake in a one‑line gain trim or two‑point calibration; auto‑plots/alarms; daily log roll‑over; integrate with harvester tests (weights/position sweeps) and compute net energy margin vs duty cycles; consider lower‑Z or buffered front‑end if higher bandwidth/precision is needed.

_[Back to Contents](#contents)_

---

## References (Harvard)

- Raspberry Pi Ltd. (2023) *RP2040 Datasheet*.
- e‑peas (2023) *AEM00941 EVK v1.2 User Guide*.
- Smart‑Material Corp. (2022) *CL‑54 Energy Harvesting Circuit Datasheet*.
- MicroPython (2024) *network, socket, machine.ADC Modules*.
- Eaton (2021) *PTV Supercapacitor Datasheet*.

_[Back to Contents](#contents)_

---

## Appendix A: Bill of Materials (excerpt)

| Item | Part | Value / Notes | Qty |
|---|---|---|---|
| A1 | Pico 2 W | RP2040 + Wi‑Fi | 1 |
| A2 | Resistor (R_TOP) | 1.0 MΩ ±1% | 1 |
| A3 | Resistor (R_BOTTOM) | 660 kΩ ±1% | 1 |
| A4 | Capacitor | 100 nF C0G | 1 |
| A5 | Supercapacitor | 5 F / 6 V | 1 |
| A6 | Jumpers/breadboard | — | — |

_[Back to Contents](#contents)_

## Appendix B: Wiring (text)

- **BATT+ → 1 MΩ → node → 660 kΩ → BATT−**  
- **node → 100 nF → BATT−**, **node → Pico GP26 (ADC0)**, **Pico GND → BATT−**

_[Back to Contents](#contents)_

## Appendix C: Code Listings (pointers)

- `main.py` (Pico server, 5 s cadence, averaging 32, LED heartbeat).  
- `tcp_client_csv.py` (Windows client CSV logger, reconnect).  
*(Insert code or link to repo snippet as needed.)*

_[Back to Contents](#contents)_


## Appendix D: Sample CSV (excerpt)

```csv
timestamp,elapsed_s,vbatt_v
2025-11-16T22:34:02.046,0,3.3037
2025-11-16T22:34:07.109,5,3.3026

_[Back to Contents](#contents)_

...
```

## Appendix E: Useful Commands

- Listener check: `netstat -an | find ":5007"`  
- PowerShell (admin): `New-NetFirewallRule -DisplayName "Pico_TCP_5007" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 5007 -Profile Private`

_[Back to Contents](#contents)_

## Appendix F: Uncertainty Budget (illustrative)

| Source | Value | Sensitivity | Contribution |
|---|---|---|---|
| 3V3 ref | ±1.5% | ∂V/∂Vref | *(fill)* |
| R_TOP tol | ±1% | ∂V/∂R_TOP | *(fill)* |
| R_BOTTOM tol | ±1% | ∂V/∂R_BOTTOM | *(fill)* |
| ADC quant. | 1 LSB | ∂V/∂counts | *(fill)* |
| **Combined (RSS)** | — | — | *(fill)* |

_[Back to Contents](#contents)_


## Appendix G: Change Log (key points)

- Switched UDP→TCP; inverted roles (Pico server).  
- Fixed wiring opens; added 100 nF; changed R_BOTTOM to 660 kΩ; updated scale; achieved accuracy within  ≤ ±2%.

_[Back to Contents](#contents)_


