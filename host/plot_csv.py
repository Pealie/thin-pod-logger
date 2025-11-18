# plot_csv.py — generate plots & quick stats from vbatt_log.csv
# Usage:
# python host/plot_csv.py --csv host/vbatt_log.csv --out docs/fig/plot_vbatt.png --dmm 3.34

import argparse
import csv
import os
from statistics import mean

try:
    import matplotlib.pyplot as plt
except ImportError:
    raise SystemExit("matplotlib is required for plotting. Try: pip install matplotlib")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default=os.path.join("host", "vbatt_log.csv"))
    parser.add_argument("--out", default=os.path.join("docs", "fig", "plot_vbatt.png"))
    parser.add_argument(
        "--dmm",
        type=float,
        default=None,
        help="reference DMM VBATT in volts (optional)",
    )
    return parser.parse_args()


def load_data(csv_path: str) -> tuple[list[float], list[float]]:
    elapsed: list[float] = []
    vbatt: list[float] = []

    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                elapsed.append(float(row["elapsed_s"]))
                vbatt.append(float(row["vbatt_v"]))
            except (KeyError, ValueError):
                continue

    if not vbatt:
        raise SystemExit(
            "No data parsed — check CSV path and headers: timestamp,elapsed_s,vbatt_v"
        )

    return elapsed, vbatt


def main() -> None:
    args = parse_args()
    elapsed, vbatt = load_data(args.csv)

    v_mean = mean(vbatt)
    print(
        f"Samples: {len(vbatt)} Mean VBATT: {v_mean:.4f} V "
        f"Min: {min(vbatt):.4f} Max: {max(vbatt):.4f}"
    )

    if args.dmm is not None:
        err = (v_mean - args.dmm) / args.dmm * 100.0
        print(f"DMM ref: {args.dmm:.4f} V Mean error: {err:+.2f}%")

    plt.figure()
    plt.plot(elapsed, vbatt, label="VBATT (CSV)")
    if args.dmm is not None:
        plt.axhline(args.dmm, linestyle="--", label=f"DMM {args.dmm:.3f} V")
    plt.xlabel("Elapsed time (s)")
    plt.ylabel("VBATT (V)")
    plt.title("Thin‑Pod VBATT vs Time")
    plt.legend()
    plt.tight_layout()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    plt.savefig(args.out, dpi=150)
    print("Saved:", args.out)


if __name__ == "__main__":
    main()