from datetime import datetime
from typing import Dict, Any, List

def _now_timestamp() -> str:
    return datetime.utcnow().isoformat() + "Z" # utcnow is deprecated in Python 3.11, but we are using 3.10.11


def format_single_flight(raw: Dict[str, Any]) -> Dict[str, Any]:
    data = raw.get("data", [])
    ts = _now_timestamp()
    if not data:
        return {"error": "no data available", "last_updated": ts}

    f = data[0]
    dep = f.get("departure", {})
    arr = f.get("arrival", {})
    fl = f.get("flight", {})

    return {
        "last_updated": ts,
        "flight": {
            "airline": f.get("airline", {}).get("name"),
            "flight_number": fl.get("iata"),
            "flight_date": f.get("flight_date"),
            "icao": fl.get("icao"),
            "registration": f.get("aircraft", {}).get("registration"),
            "status": f.get("flight_status"),
            "delay": {
                "departure": dep.get("delay"),
                "arrival": arr.get("delay"),
            },
        },
        "departure": {
            "airport_iata": dep.get("iata"),
            "airport_name": dep.get("airport"),
            "scheduled": dep.get("scheduled"),
            "actual": dep.get("actual"),
            "terminal": dep.get("terminal"),
            "gate": dep.get("gate"),
            "baggage": dep.get("baggage"),
        },
        "arrival": {
            "airport_iata": arr.get("iata"),
            "airport_name": arr.get("airport"),
            "scheduled": arr.get("scheduled"),
            "estimated": arr.get("estimated"),
            "actual": arr.get("actual"),
            "terminal": arr.get("terminal"),
            "gate": arr.get("gate"),
            "baggage": arr.get("baggage"),
        }
    }


def format_flights_list(raw: Dict[str, Any]) -> List[Dict[str, Any]]:
    entries = raw.get("data", [])
    ts = _now_timestamp()
    formatted: List[Dict[str, Any]] = []

    for f in entries:
        dep = f.get("departure", {})
        arr = f.get("arrival", {})
        fl  = f.get("flight", {})

        formatted.append({
            "last_updated": ts,
            "flight_number": fl.get("iata"),
            "status": f.get("flight_status"),
            "delay": {
                "departure": dep.get("delay"),
                "arrival": arr.get("delay"),
            },
            "departure_time": dep.get("scheduled"),
            "arrival_time": arr.get("scheduled"),
            "origin": {
                "iata": dep.get("iata"),
                "name": dep.get("airport"),
            },
            "destination": {
                "iata": arr.get("iata"),
                "name": arr.get("airport"),
            },
            "terminal": {
                "departure": dep.get("terminal"),
                "arrival": arr.get("terminal"),
            },
            "gate": {
                "departure": dep.get("gate"),
                "arrival": arr.get("gate"),
            },
            "baggage": {
                "departure": dep.get("baggage"),
                "arrival": arr.get("baggage"),
            },
        })

    return formatted


def format_realtime(raw: Dict[str, Any]) -> Dict[str, Any]:
    data = raw.get("data", [])
    ts = _now_timestamp()
    if not data:
        return {"error": "no data available", "last_updated": ts}

    f = data[0]
    position = f.get("live", {})

    return {
        "last_updated": ts,
        "flight_number": f.get("flight", {}).get("iata"),
        "position": {
            "latitude": position.get("latitude"),
            "longitude": position.get("longitude"),
            "altitude": position.get("altitude"),
            "speed": position.get("speed"),
            "heading": position.get("direction"),
        }
    }
