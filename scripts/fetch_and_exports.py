from __future__ import annotations
import argparse, json, sys, base64, datetime, pathlib, os
from modules.api.fetcher import fetch_flight, fetch_next_departures, fetch_next_arrivals, fetch_realtime_position
from modules.api.formatter import format_single_flight, format_flights_list, format_realtime


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
TTL = int(os.getenv("CACHE_TTL", 60))

def _timestamp() -> str:
    return datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

def _json_still_valid(path: pathlib.Path) -> bool:
    return path.exists() and (datetime.datetime.utcnow() -
           datetime.datetime.utcfromtimestamp(path.stat().st_mtime)).seconds < TTL

def _write_json(data, out_path: pathlib.Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, separators=(",", ":")))
    print(f"JSON saved to {out_path}")

def _encode_b64(data) -> str:
    return base64.urlsafe_b64encode(json.dumps(data, separators=(",", ":")).encode()).decode()


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
def build_cli() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser("Fetch aviation data and export to JSON for offline sharing")
    sub = p.add_subparsers(dest="cmd", required=True)

    # single flight ---------------------------------------------------------- #
    f = sub.add_parser("flight", help="single flight by IATA code")
    f.add_argument("flight_iata")
    f.add_argument("flight_date")

    # departures / arrivals -------------------------------------------------- #
    for kind in ("departures", "arrivals"):
        g = sub.add_parser(kind, help=f"next {kind} for airport")
        g.add_argument("airport_iata")
        g.add_argument("flight_date")
        g.add_argument("--limit", type=int, default=5)

    # realtime --------------------------------------------------------------- #
    r = sub.add_parser("realtime", help="live position for active flight")
    r.add_argument("flight_iata")

    # shared flags ----------------------------------------------------------- #
    p.add_argument("-o", "--output", type=pathlib.Path,
                   help="output path (default ./out/<kind>-<timestamp>.json)")
    p.add_argument("--b64", action="store_true",
                   help="print Base64‑encoded payload for QR code generators")
    return p


def main(argv=None) -> None:
    args = build_cli().parse_args(argv)
    if args.output is None:
        args.output = pathlib.Path("out") / f"{args.cmd}.json"

    if _json_still_valid(args.output):
        print(f"Recent file found (<{TTL}s) – skip API call.")
        if args.b64:
            print(_encode_b64(json.loads(args.output.read_text())))
        return

    # ---------- dispatch ---------------------------------------------------- #
    if args.cmd == "flight":
        raw  = fetch_flight(args.flight_iata, args.flight_date)
        data = format_single_flight(raw)

    elif args.cmd == "departures":
        raw  = fetch_next_departures(args.airport_iata, args.flight_date, args.limit)
        data = format_flights_list(raw)

    elif args.cmd == "arrivals":
        raw  = fetch_next_arrivals(args.airport_iata, args.flight_date, args.limit)
        data = format_flights_list(raw)

    elif args.cmd == "realtime":
        raw  = fetch_realtime_position(args.flight_iata)
        data = format_realtime(raw)

    else:
        sys.exit("Unknown command")

    _write_json(data, args.output)

    if args.b64:
        print(_encode_b64(data))


if __name__ == "__main__":
    main()