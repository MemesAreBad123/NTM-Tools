#!/usr/bin/env python3
""" 1) See available fuel types

python zirnox_grid_calc.py --list-fuels


2) Run the simulator with interactive grid entry

python zirnox_grid_calc.py --co2-mB 16000 --interactive


3) (Optional) Re-calibrate heat --> temperature using an in-game reference

python zirnox_grid_calc.py --co2-mB 16000 --interactive --calibrate """ 

"""
ZIRNOX 4x4 Fuel Grid -> Heat -> Temperature -> Pressure (HBM NTM)

What this is:
- This is a simple terminal simulator for the ZIRNOX reactor in HBM's NTM (Community).
- I'm treating each fuel rod's "heat per tick" as just "heat" for a static calculation. I'm NOT doing a time sim here.

What I input:
- CO2 (mB)
- A 4x4 grid (16 slots) of fuel rods (or empty)

What it outputs:
- Total heat (sum of rod heat)
- Core temperature (°C)
- Base pressure from CO2 (bar) using my CO2->pressure mapping
- Added pressure from temperature (bar) using my temperature->pressure schedule
- Total pressure (bar) and whether it explodes (>= 31 bar)

Important notes:
- I needed a conversion from "total heat" -> "core temperature". The mod has its own internal behavior,
  so I calibrate a single linear coefficient k using a reference point I observed in-game.
- Default calibration I use:
    16 uranium_fuel rods at 16000 mB CO2 stabilizes at ~240 C and shows 18 bar
  This gives me:
    k = (240 - 20) / (16 * 50) = 0.275
- If you want to re-calibrate, run with --calibrate and enter your own reference point.

Explosion rule:
- If total pressure >= 31 bar, I call it a blow up.

Reactor working rule:
- If CO2 < 5000 mB, I consider it "not operational" (based on my notes).
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional


# -----------------------------
# Fuel table (heat per tick treated as "heat", lifetime kept for completeness)
# -----------------------------
@dataclass(frozen=True)
class FuelSpec:
    display: str
    heat: float
    lifetime_ticks: int


FUEL_TABLE: Dict[str, FuelSpec] = {
    "natural_uranium": FuelSpec("Natural Uranium", 30.0, 250_000),
    "uranium_fuel": FuelSpec("Uranium Fuel", 50.0, 200_000),
    "thorium_fuel": FuelSpec("Thorium Fuel", 40.0, 200_000),
    "mox_fuel": FuelSpec("MOX Fuel", 75.0, 165_000),
    "plutonium_fuel": FuelSpec("Plutonium Fuel", 65.0, 175_000),
    "uranium_233": FuelSpec("Uranium 233", 100.0, 150_000),
    "uranium_235": FuelSpec("Uranium 235", 85.0, 165_000),
    "les": FuelSpec("LES", 150.0, 150_000),
    "zfb_mox": FuelSpec("ZFB MOX", 35.0, 50_000),
    "empty": FuelSpec("Empty", 0.0, 0),
}


# -----------------------------
# CO2 -> Base Pressure (bar) 
# -----------------------------
def base_pressure_from_co2_mB(co2_mB: float) -> float:
    if co2_mB <= 0:
        return 0.0

    if co2_mB >= 16000:
        return 10.0
    if co2_mB >= 15000:
        return 9.0
    if co2_mB >= 13000:
        return 8.0  # (covers 14000 and 13000)
    if co2_mB >= 11000:
        return 7.0  # (covers 12000 and 11000)
    if co2_mB >= 10000:
        return 6.0
    if co2_mB >= 9000:
        return 5.0
    if co2_mB >= 6000:
        return 4.0  # (covers 6000, 7000, 8000)
    if co2_mB >= 5000:
        return 3.0
    if co2_mB >= 3000:
        return 2.0  # (covers 3000 and 4000)
    if co2_mB >= 1000:
        return 1.0  # (covers 1000 and 2000)
    return 0.0


def operational_from_co2(co2_mB: float) -> bool:
    # I treat 5000 mB as the minimum for the reactor to "work" at all.
    return co2_mB >= 5000


# -----------------------------
# Temperature -> Added Pressure (bar) schedule (from my notes)
# -----------------------------
# I had one overlap/typo in my notes ("240 to 280"). I interpret that as "260 to 280"
# so the segments are monotonic and don't double-count.
TEMP_SEGMENTS: List[Tuple[float, float, float]] = [
    (20.0, 50.0, 1.0),
    (50.0, 120.0, 3.0),
    (120.0, 180.0, 2.0),
    (180.0, 220.0, 2.0),
    (220.0, 260.0, 2.0),
    (260.0, 280.0, 1.0),
    (280.0, 317.0, 1.0),
    (317.0, 360.0, 2.0),
    (360.0, 398.0, 1.0),
    (398.0, 419.0, 1.0),
    (419.0, 453.0, 2.0),
    (453.0, 469.0, 1.0),
    (469.0, 480.0, 0.0),
    (480.0, 488.0, 1.0),
    (488.0, 500.0, 1.0),
]


def added_pressure_from_temp_C(temp_C: float) -> float:
    if temp_C <= 20.0:
        return 0.0

    added = 0.0
    for lo, hi, delta_bar in TEMP_SEGMENTS:
        if temp_C <= lo:
            break

        span = hi - lo
        if span <= 0:
            continue

        portion = min(temp_C, hi) - lo
        if portion > 0:
            added += (portion / span) * delta_bar

        if temp_C < hi:
            break

    return added


def explodes(total_bar: float) -> bool:
    return total_bar >= 31.0


# -----------------------------
# Heat -> Temperature (calibrated)
# -----------------------------
BASE_TEMP_C = 20.0


def compute_k_from_reference(fuel_key: str, rods: float, target_temp_C: float) -> float:
    if fuel_key not in FUEL_TABLE:
        raise ValueError(f"Unknown fuel '{fuel_key}'.")
    if rods <= 0:
        raise ValueError("Number of rods must be > 0.")
    heat_per_rod = FUEL_TABLE[fuel_key].heat
    total_heat = rods * heat_per_rod
    if total_heat <= 0:
        raise ValueError("Total heat must be > 0.")
    return (target_temp_C - BASE_TEMP_C) / total_heat


def calibrate_k_interactive(default_k: float) -> float:
    print("\n=== Calibration (heat -> temperature) ===")
    print("I use: T = 20 + k * (total_heat)")
    print("If you have a known setup from the game, enter it here and I'll compute k.")
    print("Otherwise just press Enter and I'll keep the default.\n")

    fuel_in = input("Fuel key for reference (default uranium_fuel): ").strip().lower()
    fuel_key = fuel_in if fuel_in else "uranium_fuel"

    rods_in = input("Number of rods for reference (default 16): ").strip()
    rods = float(rods_in) if rods_in else 16.0

    temp_in = input("Observed stabilized core temp in C (default 240): ").strip()
    target_temp = float(temp_in) if temp_in else 240.0

    try:
        k = compute_k_from_reference(fuel_key, rods, target_temp)
    except Exception as e:
        print(f"\nCalibration failed ({e}). Falling back to default k={default_k:.6f}\n")
        return default_k

    print(f"\nComputed k = {k:.6f} (C per heat unit)")
    print("I'll use this k for the rest of this run.\n")
    return k


def temp_from_total_heat(total_heat: float, k: float) -> float:
    return BASE_TEMP_C + k * total_heat


# -----------------------------
# Grid parsing / input
# -----------------------------
def normalize_token(tok: str) -> str:
    t = tok.strip().lower().replace(" ", "_")
    return t if t else "empty"


def parse_16_slots(slots_csv: str) -> List[str]:
    raw = [s.strip() for s in slots_csv.split(",")]
    tokens = [normalize_token(t) for t in raw]
    if len(tokens) != 16:
        raise ValueError(f"--slots must contain exactly 16 comma-separated entries (got {len(tokens)}).")
    return tokens


def prompt_grid_interactive() -> List[str]:
    print("\nEnter your 4x4 grid. Use fuel keys or 'empty'.")
    print("Tip: run with --list-fuels to see all keys.\n")
    grid: List[str] = []
    for r in range(4):
        while True:
            row = input(f"Row {r+1} (4 values, comma-separated): ").strip()
            parts = [normalize_token(x) for x in row.split(",")]
            if len(parts) != 4:
                print("  Please enter exactly 4 values.")
                continue
            grid.extend(parts)
            break
    return grid


def total_heat_from_grid(grid: List[str]) -> float:
    total = 0.0
    for key in grid:
        if key not in FUEL_TABLE:
            raise ValueError(f"Unknown fuel key '{key}'. Use --list-fuels.")
        total += FUEL_TABLE[key].heat
    return total


def format_grid(grid: List[str]) -> str:
    lines = []
    for r in range(4):
        row = grid[r*4:(r+1)*4]
        lines.append(" | ".join(f"{x:14s}" for x in row))
    return "\n".join(lines)


# -----------------------------
# Main
# -----------------------------
def main() -> None:
    p = argparse.ArgumentParser(description="ZIRNOX 4x4 fuel grid calculator (HBM NTM).")

    p.add_argument("--list-fuels", action="store_true", help="Show fuel keys and exit.")
    p.add_argument("--co2-mB", type=float, default=None, help="CO2 amount in mB (ex: 16000).")

    g = p.add_mutually_exclusive_group()
    g.add_argument("--slots", type=str, default=None, help="16 comma-separated slot entries (fuel keys or empty).")
    g.add_argument("--interactive", action="store_true", help="Prompt for 4 rows of 4 slots in the terminal.")

    p.add_argument("--calibrate", action="store_true", help="Do an interactive calibration step for k.")
    p.add_argument("--k", type=float, default=None,
                   help="Override k directly (T=20+k*heat). If omitted, uses calibration default.")
    args = p.parse_args()

    if args.list_fuels:
        print("\nFuel keys you can use:")
        for key in sorted(FUEL_TABLE.keys()):
            f = FUEL_TABLE[key]
            print(f"  {key:16s} -> {f.display:16s} | heat={f.heat:g} | lifetime={f.lifetime_ticks:,}")
        print("\nUse 'empty' for blank slots.")
        return

    if args.co2_mB is None:
        raise SystemExit("Error: --co2-mB is required (unless using --list-fuels).")

    # Grid
    if args.interactive:
        grid = prompt_grid_interactive()
    elif args.slots is not None:
        grid = parse_16_slots(args.slots)
    else:
        raise SystemExit("Error: provide --interactive or --slots (16 values).")

    # Default k from your reference point: 16 uranium_fuel rods -> 240C
    default_k = compute_k_from_reference("uranium_fuel", 16.0, 240.0)

    # Choose k
    if args.k is not None:
        k = float(args.k)
    elif args.calibrate:
        k = calibrate_k_interactive(default_k)
    else:
        k = default_k

    # Compute results
    co2 = float(args.co2_mB)
    base_bar = base_pressure_from_co2_mB(co2)
    operational = operational_from_co2(co2)

    total_heat = total_heat_from_grid(grid)
    temp_C = temp_from_total_heat(total_heat, k)
    added_bar = added_pressure_from_temp_C(temp_C)
    total_bar = base_bar + added_bar
    boom = explodes(total_bar)

    # Output
    print("\n=== ZIRNOX 4x4 Grid ===")
    print(format_grid(grid))

    print("\n=== Results ===")
    print(f"CO2 (mB)                 : {co2:g}")
    print(f"Operational (CO2>=5000?) : {'YES' if operational else 'NO'}")
    print(f"Base pressure (bar)      : {base_bar:.3f}")
    print(f"Total heat               : {total_heat:.3f}")
    print(f"k (C per heat)           : {k:.6f}")
    print(f"Core temperature (C)     : {temp_C:.3f}")
    print(f"Added pressure (bar)     : {added_bar:.3f}")
    print(f"TOTAL pressure (bar)     : {total_bar:.3f}")
    print(f"Explosion (>=31 bar?)    : {'YES' if boom else 'NO'}")

    if not operational:
        print("\nNote: I consider the reactor not operational because CO2 < 5000 mB.")
    if boom:
        print("Note: Total pressure hit 31 bar or more, so this would blow up.")


if __name__ == "__main__":
    main()

