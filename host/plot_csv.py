# plot_csv_new.py — generate plots & quick stats from vbatt_log.csv

import argparse
import csv
import os
from statistics import mean

try:
    import matplotlib.pyplot as plt
except ImportError:
    raise SystemExit("matplotlib is required for plotting. Try: pip install matplotlib")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plot Thin-Pod VBATT logs and print quick stats."
    )
    parser.add_argument(
        "--csv",
        default=os.path.join("host", "vbatt_log.csv"),
        help="Path to input CSV (default: host/vbatt_log.csv)",
    )
    parser.add_argument(
        "--out",
        default=os.path.join("docs", "fig", "plot_vbatt.png"),
        help="Output PNG path (default: docs/fig/plot_vbatt.png)",
    )
    parser.add_argument(
        "--dmm",
        type=float,
        default=None,
        help="Reference DMM VBATT in volts (optional)",
    )
    parser.add_argument(
        "--warmup",
        type=float,
        default=0.0,
        help="Discard this many seconds from start (default: 0)",
    )
    parser.add_argument(
        "--vmin",
        type=float,
        default=None,
        help="Keep only samples with VBATT >= VMIN (optional)",
    )
    parser.add_argument(
        "--vmax",
        type=float,
        default=None,
        help="Keep only samples with VBATT <= VMAX (optional)",
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


def apply_filters(
    elapsed: list[float],
    vbatt: list[float],
    warmup: float,
    vmin: float | None,
    vmax: float | None,
) -> tuple[list[float], list[float]]:
    assert len(elapsed) == len(vbatt)

    t_f: list[float] = []
    v_f: list[float] = []

    for t, v in zip(elapsed, vbatt):
        if t < warmup:
            continue
        if vmin is not None and v < vmin:
            continue
        if vmax is not None and v > vmax:
            continue
        t_f.append(t)
        v_f.append(v)

    if not v_f:
        raise SystemExit(
            "All samples were filtered out — try relaxing warmup/vmin/vmax."
        )

    return t_f, v_f


def main() -> None:
    args = parse_args()
    elapsed, vbatt = load_data(args.csv)
    orig_samples = len(vbatt)

    # apply filters
    elapsed, vbatt = apply_filters(
        elapsed, vbatt, warmup=args.warmup, vmin=args.vmin, vmax=args.vmax
    )

    v_mean = mean(vbatt)
    v_min = min(vbatt)
    v_max = max(vbatt)

    print(
        f"Samples: {len(vbatt)} (from {orig_samples} raw) "
        f"Mean VBATT: {v_mean:.4f} V Min: {v_min:.4f} Max: {v_max:.4f}"
    )

    dmm_err_pct = None
    if args.dmm is not None:
        dmm_err_pct = (v_mean - args.dmm) / args.dmm * 100.0
        print(f"DMM ref: {args.dmm:.4f} V  Mean error: {dmm_err_pct:+.2f}%")

    # ---- plotting ----
    fig, ax = plt.subplots()
    ax.plot(elapsed, vbatt, label="VBATT (CSV)")

    if args.dmm is not None:
        ax.axhline(args.dmm, linestyle="--", label=f"DMM {args.dmm:.3f} V")

    ax.set_xlabel("Elapsed time (s)")
    ax.set_ylabel("VBATT (V)")
    ax.set_title("Thin-Pod VBATT vs Time")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # build stats text for annotation
    lines = [
        f"Samples: {len(vbatt)} (raw {orig_samples})",
        f"Mean: {v_mean:.4f} V",
        f"Min:  {v_min:.4f} V",
        f"Max:  {v_max:.4f} V",
    ]
    if args.dmm is not None and dmm_err_pct is not None:
        lines.append(f"DMM:  {args.dmm:.4f} V")
        lines.append(f"Mean err: {dmm_err_pct:+.2f}%")
    if args.warmup > 0:
        lines.append(f"Warmup: {args.warmup:.0f}s")
    if args.vmin is not None or args.vmax is not None:
        lines.append(
            "Range: "
            f"[{args.vmin if args.vmin is not None else '-∞'}, "
            f"{args.vmax if args.vmax is not None else '+∞'}] V"
        )

    ax.text(
        0.02,
        0.98,
        "\n".join(lines),
        transform=ax.transAxes,
        va="top",
        ha="left",
        fontsize=9,
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.7, edgecolor="grey"),
    )

    plt.tight_layout()

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    fig.savefig(args.out, dpi=150)
    print("Saved:", args.out)


if __name__ == "__main__":
    main()
