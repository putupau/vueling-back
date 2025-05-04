from __future__ import annotations
import os, time, json, hashlib
from functools import lru_cache
from typing import Any, Dict

import requests
from dotenv import load_dotenv

load_dotenv()

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
BASE_URL = os.getenv("BASE_URL", "https://api.aviationstack.com/v1")
API_KEY = os.getenv("AVIATIONSTACK_API_KEY")
AIRLINE_IATA = os.getenv("AIRLINE_IATA", "VY")
DEFAULT_LIMIT = os.getenv("DEFAULT_LIMIT",5)
CACHE_TTL = os.getenv("CACHE_TTL", "60")

DEFAULT_LIMIT = int(DEFAULT_LIMIT)
CACHE_TTL = int(CACHE_TTL)

if not API_KEY:
    raise RuntimeError("AVIATIONSTACK_API_KEY is missing in your environment")

# --------------------------------------------------------------------------- #
# HTTP session with default headers and params
# --------------------------------------------------------------------------- #
_session: requests.Session | None = None
def _get_session() -> requests.Session:
    """Create a requests session with default headers and params."""
    global _session
    
    if _session is None:
        _session = requests.Session()
        _session.headers.update({"Accept": "application/json"})
        _session.params = {"access_key": API_KEY}
    
    return _session

# --------------------------------------------------------------------------- #
# API call with error handling
# --------------------------------------------------------------------------- #
def _call_api(endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
    url = f"{BASE_URL}/{endpoint}" 
    try:
        r = _get_session().get(url, params=params, timeout=15)
        r.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(f"API request failed: {exc}") from exc
    return r.json()

# --------------------------------------------------------------------------- #
# TTL‑aware memoisation: one key per <endpoint+params+ttl_bucket>
# --------------------------------------------------------------------------- #
def _ttl_key(endpoint: str, params: Dict[str, Any]) -> str:
    bucket = int(time.time() // CACHE_TTL)
    raw = f"{endpoint}:{json.dumps(params, sort_keys=True)}:{bucket}"
    return hashlib.sha1(raw.encode()).hexdigest()


@lru_cache(maxsize=128)
def _cached_call(ttl_key: str, endpoint: str, frozen_params: str) -> Dict[str, Any]:
    return _call_api(endpoint, json.loads(frozen_params))


def _fetch(endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
    key  = _ttl_key(endpoint, params)
    return _cached_call(key, endpoint, json.dumps(params, sort_keys=True))
    

# --------------------------------------------------------------------------- #
# Public helpers
# --------------------------------------------------------------------------- #
def fetch_next_departures(airport_iata: str, flight_date: str, limit: int = DEFAULT_LIMIT):
    return _fetch("flights", {
        "departure_airport_iata": airport_iata,
        # "airline_iata": AIRLINE_IATA,
        # "flight_status": "active",
        "limit": limit,
    })


def fetch_flight(flight_iata: str, flight_date: str) -> Dict[str, Any]:
    """
    For free tier: return realtime position/status if active, else data empty.
    """
    # Use same endpoint as realtime_position to respect free-tier
    return fetch_realtime_position(flight_iata)


def fetch_next_arrivals(airport_iata: str, flight_date: str, limit: int = DEFAULT_LIMIT) -> Dict[str, Any]:
    params = {
        "arrival_airport_iata": airport_iata,
        "airline_iata": AIRLINE_IATA,
        "limit": limit,
        "flight_status": "active"
    }
    cache_key = f"next_arr:{airport_iata}:{flight_date}:{limit}"
    serialized = "&".join(f"{k}={v}" for k, v in params.items())
    return _cached_call(cache_key, "flights", serialized)


def fetch_realtime_position(flight_iata: str) -> Dict[str, Any]:
    return _call_api(
        "flights",
        {
            "flight_iata": flight_iata,
            "airline_iata": AIRLINE_IATA,
            "flight_status": "active"
        },
    )

