#!/usr/bin/env python
from __future__ import annotations

import sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv, find_dotenv
import os

env_path = find_dotenv(usecwd=True)
if not env_path:
    sys.exit(f"❌  .env not found. CWD = {ROOT}")
if not load_dotenv(env_path, override=False):
    sys.exit(f"❌  Unable to load .env  ({env_path})")
if not os.getenv("AVIATIONSTACK_API_KEY"):
    sys.exit("❌  AVIATIONSTACK_API_KEY empty or misspelled in .env")

import time, json, traceback, datetime as _dt

from modules.api.fetcher import fetch_next_departures, fetch_flight
from modules.api.formatter import format_flights_list, format_single_flight

TODAY     = _dt.date.today().isoformat()
YESTERDAY = (_dt.date.today() - _dt.timedelta(days=1)).isoformat()

out = ROOT / "out"
out.mkdir(exist_ok=True)

PASS = True
def banner(txt: str) -> None:
    print(f"\n{'='*10} {txt} {'='*10}")

try:
    banner(f"Testing fetch_next_departures for BCN on {TODAY}")
    try:
        t0 = time.perf_counter()
        raw_dep = fetch_next_departures("BCN", TODAY, limit=2)
        t1 = time.perf_counter() - t0
        if not raw_dep.get("data"):
            raise RuntimeError("No departures data for TODAY")
    except Exception as e:
        print("⚠️  API rejected departures call for TODAY, trying YESTERDAY:", e)
        banner(f"Testing fetch_next_departures for BCN on {YESTERDAY}")
        t0 = time.perf_counter()
        raw_dep = fetch_next_departures("BCN", YESTERDAY, limit=2)
        t1 = time.perf_counter() - t0
        if not raw_dep.get("data"):
            print("⚠️  No departures data for YESTERDAY either, skipping.")
            raw_dep = None

    if raw_dep:
        banner(f"First API call ({t1:.3f}s) → {len(raw_dep['data'])} flights")
        t0 = time.perf_counter()
        raw_dep_cached = fetch_next_departures(
            "BCN", raw_dep.get('data')[0].get('flight_date'), limit=2
        )
        t2 = time.perf_counter() - t0
        banner(f"Cache call ({t2:.4f}s)")
        if raw_dep is raw_dep_cached and t2 < t1 * 0.2:
            print("✅  Cache hit and fast")
        else:
            print("❌  Cache miss or too slow")
            PASS = False

        formatted = format_flights_list(raw_dep)
        banner("Formatted departures [first item]")
        print(json.dumps(formatted[0], indent=2))

        (out / "departures.json").write_text(
            json.dumps(formatted, separators=(",", ":"))
        )
    else:
        print("⚠️  Skipping departures tests due to no data")

    banner(f"Testing fetch_flight VY8254 on {TODAY}")
    try:
        raw_f = fetch_flight("VY8254", TODAY)
        if not raw_f.get("data"):
            raise RuntimeError("No flight data for TODAY")
    except Exception as e:
        print("⚠️  API rejected single-flight call for TODAY, trying YESTERDAY:", e)
        banner(f"Testing fetch_flight VY8254 on {YESTERDAY}")
        raw_f = fetch_flight("VY8254", YESTERDAY)
        if not raw_f.get("data"):
            print("⚠️  No flight data for YESTERDAY either, skipping.")
            raw_f = None

    if raw_f:
        formatted_f = format_single_flight(raw_f)
        banner("Formatted single flight")
        print(json.dumps(formatted_f, indent=2))
        (out / "flight.json").write_text(
            json.dumps(formatted_f, separators=(",", ":"))
        )
    else:
        print("⚠️  Skipping single-flight tests due to no data")

    print(f"\n✅  JSON files (if any) are in {out.resolve()}")

except Exception:
    banner("Exception during test")
    traceback.print_exc()
    PASS = False

banner("FINAL RESULT")
if PASS:
    print("🎉  All permitted tests passed (within free-tier limits)!")
    sys.exit(0)
else:
    print("❌  Some tests failed or were blocked by API limits.")
    sys.exit(1)
